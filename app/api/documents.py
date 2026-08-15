from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.models import Document, Chunk
from app.db.session import SessionLocal

from app.ingestion.pdf import extract_text_from_pdf
from app.ingestion.chunking import create_chunks_from_pages

from app.llm.embeddings import generate_embedding

router = APIRouter(prefix="/documents", tags=["documents"])


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


class DocumentCreate(BaseModel):
    filename: str
    document_type: str | None = None

@router.get("")
def list_documents(db: Session = Depends(get_db)):
    documents = db.query(Document).order_by(Document.id).all()

    return [
        {
            "id": document.id,
            "filename": document.filename,
            "document_type": document.document_type,
            "created_at": document.created_at,
        }
        for document in documents
    ]

@router.get("/{document_id}")
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return {
        "id": document.id,
        "filename": document.filename,
        "document_type": document.document_type,
        "created_at": document.created_at,
    }

@router.get("/{document_id}/text")
def get_document_text(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    file_path = UPLOAD_DIR / document.filename

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="PDF file not found",
        )

    return extract_text_from_pdf(str(file_path))

@router.post("")
def create_document(
    document_data: DocumentCreate,
    db: Session = Depends(get_db),
):
    document = Document(
        filename=document_data.filename,
        document_type=document_data.document_type,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return {
        "id": document.id,
        "filename": document.filename,
        "document_type": document.document_type,
        "created_at": document.created_at,
    }

UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported",
        )

    file_path = UPLOAD_DIR / file.filename

    with file_path.open("wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            buffer.write(chunk)

    document = Document(
        filename=file.filename,
        document_type="pdf",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return {
        "id": document.id,
        "filename": document.filename,
        "document_type": document.document_type,
        "path": str(file_path),
    }

@router.post("/{document_id}/ingest")
def ingest_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    file_path = UPLOAD_DIR / document.filename

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="PDF file not found",
        )

    # Extract text from PDF
    extracted = extract_text_from_pdf(str(file_path))

    # Create chunks
    chunks_data = create_chunks_from_pages(
        extracted["pages"]
    )

    # IMPORTANT:
    # Ștergem chunks-urile vechi ale documentului
    db.query(Chunk).filter(
        Chunk.document_id == document.id
    ).delete(
        synchronize_session=False
    )

    # Save chunks
    chunks = []

    for chunk_data in chunks_data:
        chunk = Chunk(
            document_id=document.id,
            content=chunk_data["content"],
            chunk_index=chunk_data["chunk_index"],
            page_number=chunk_data["page_number"],
        )

        db.add(chunk)
        chunks.append(chunk)

    db.commit()

    return {
        "document_id": document.id,
        "page_count": extracted["page_count"],
        "chunk_count": len(chunks),
    }

@router.post("/{document_id}/embed")
def embed_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    chunks = (
        db.query(Chunk)
        .filter(Chunk.document_id == document_id)
        .order_by(Chunk.chunk_index)
        .all()
    )

    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="Document has no chunks",
        )

    for chunk in chunks:
        chunk.embedding = generate_embedding(chunk.content)

    db.commit()

    return {
        "document_id": document_id,
        "chunk_count": len(chunks),
        "embedded": True,
    }