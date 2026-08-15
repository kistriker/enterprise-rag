import re

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Chunk
from app.llm.embeddings import generate_embedding
from app.llm.ollama import generate_answer


router = APIRouter(
    prefix="/query",
    tags=["query"],
)


class QueryRequest(BaseModel):
    question: str
    document_id: int | None = None
    top_k: int = 3


def tokenize(text: str) -> set[str]:
    """
    Transformă textul într-un set simplu de cuvinte.
    Păstrăm diacriticele.
    """
    return set(
        re.findall(
            r"\b[\wăâîșțĂÂÎȘȚ]+\b",
            text.lower(),
        )
    )


def lexical_score(question: str, content: str) -> float:
    """
    Calculează relevanța lexicală dintre întrebare și chunk.

    Cuvintele mai lungi și mai specifice primesc o greutate mai mare.
    """
    question_tokens = tokenize(question)
    content_tokens = tokenize(content)

    if not question_tokens:
        return 0.0

    score = 0.0
    total_weight = 0.0

    for token in question_tokens:
        # Ignorăm cuvintele foarte scurte,
        # deoarece sunt de obicei mai puțin informative.
        if len(token) < 4:
            continue

        weight = min(len(token) / 10, 2.0)

        total_weight += weight

        if token in content_tokens:
            score += weight

    if total_weight == 0:
        return 0.0

    return score / total_weight


@router.post("")
def query_documents(
    request: QueryRequest,
    db: Session = Depends(get_db),
):
    # 1. Transformăm întrebarea în embedding
    query_embedding = generate_embedding(request.question)

    # 2. Calculăm distanța cosine
    distance = Chunk.embedding.cosine_distance(query_embedding)

    # 3. Construim query-ul pentru pgvector
    query = (
        db.query(
            Chunk,
            distance.label("distance"),
        )
        .filter(Chunk.embedding.is_not(None))
    )

    # 4. Dacă avem document_id, căutăm doar în acel document
    if request.document_id is not None:
        query = query.filter(
            Chunk.document_id == request.document_id
        )

    # 5. Luăm mai mulți candidați decât top_k.
    #
    # Exemplu:
    # top_k = 3
    # candidate_limit = 9
    #
    # Astfel putem recupera un chunk relevant care
    # nu a intrat direct în primele 3 rezultate.
    candidate_limit = max(request.top_k * 3, 9)

    results = (
        query
        .order_by(distance)
        .limit(candidate_limit)
        .all()
    )

    # 6. Reranking
    reranked_results = []

    for chunk, distance_value in results:
        semantic_score = 1 - float(distance_value)

        lexical = lexical_score(
            request.question,
            chunk.content,
        )

        # Combinație între:
        # 70% semantic similarity
        # 30% lexical overlap
        final_score = (
            0.70 * semantic_score
            + 0.30 * lexical
        )

        reranked_results.append(
            {
                "chunk": chunk,
                "distance": distance_value,
                "semantic_score": semantic_score,
                "lexical_score": lexical,
                "final_score": final_score,
            }
        )

    # 7. Sortăm după scorul final
    reranked_results.sort(
        key=lambda item: item["final_score"],
        reverse=True,
    )

    # 8. Păstrăm doar top_k
    selected_results = reranked_results[:request.top_k]

    # 9. Construim contextul pentru LLM
    context_parts = []

    for item in selected_results:
        chunk = item["chunk"]

        context_parts.append(
            f"[Chunk {chunk.id} | Pagina {chunk.page_number}]\n"
            f"{chunk.content}"
        )

    context = "\n\n".join(context_parts)

    # 10. Construim promptul
    prompt = f"""
Ești un asistent AI pentru un sistem Enterprise RAG.

IMPORTANT:
Răspunde DIRECT cu răspunsul final.
NU afișa raționamentul.
NU explica cum ai găsit răspunsul.
NU începe cu "Okay", "Let's", "Sure" sau alte expresii.
NU repeta întrebarea.
NU include tag-uri precum <think> sau </think>.

Folosește DOAR informațiile din CONTEXT.

Dacă răspunsul există în context, răspunde clar și concis.

Dacă informația nu există în context, spune exact:
"Nu există suficiente informații în document."

Nu inventa informații care nu apar în context.

Răspunde în aceeași limbă ca întrebarea.

Maximum 2 propoziții, cu excepția cazului în care întrebarea cere o listă.

CONTEXT:
{context}

ÎNTREBARE:
{request.question}

RĂSPUNS FINAL:
""".strip()

    # 11. Trimitem contextul către Qwen
    answer = generate_answer(prompt)

    # 12. Returnăm răspunsul și sursele
    sources = [
        {
            "chunk_id": item["chunk"].id,
            "document_id": item["chunk"].document_id,
            "chunk_index": item["chunk"].chunk_index,
            "page_number": item["chunk"].page_number,
            "score": round(item["final_score"], 4),
        }
        for item in selected_results
    ]

    return {
        "question": request.question,
        "answer": answer,
        "sources": sources,
    }