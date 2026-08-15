import re


def normalize_text(text: str) -> str:
    """
    Normalizează textul extras din PDF fără să piardă
    structura logică a documentului.
    """

    # Normalizează newline-urile
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Elimină spațiile de la finalul liniilor
    text = "\n".join(
        line.rstrip()
        for line in text.splitlines()
    )

    # Prea multe linii goale -> maximum 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def split_into_paragraphs(text: str) -> list[str]:
    """
    Încearcă să păstreze paragrafele naturale ale documentului.
    """

    text = normalize_text(text)

    if not text:
        return []

    paragraphs = re.split(
        r"\n\s*\n",
        text,
    )

    return [
        paragraph.strip()
        for paragraph in paragraphs
        if paragraph.strip()
    ]


def chunk_text(
    text: str,
    chunk_size: int = 1200,
    overlap: int = 150,
) -> list[str]:
    """
    Creează chunks pentru documente generale.

    Preferă să păstreze paragrafele întregi.
    Dacă un paragraf este prea mare, îl împarte
    pe propoziții / caractere.
    """

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than 0"
        )

    if overlap < 0:
        raise ValueError(
            "overlap cannot be negative"
        )

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    paragraphs = split_into_paragraphs(text)

    if not paragraphs:
        return []

    chunks = []
    current = ""

    for paragraph in paragraphs:

        # Dacă paragraful încape în chunk-ul curent
        if len(current) + len(paragraph) + 2 <= chunk_size:
            if current:
                current += "\n\n"

            current += paragraph
            continue

        # Salvăm chunk-ul curent
        if current:
            chunks.append(current.strip())

        # Dacă paragraful este prea mare,
        # îl împărțim separat
        if len(paragraph) > chunk_size:
            large_chunks = split_large_text(
                paragraph,
                chunk_size,
                overlap,
            )

            chunks.extend(large_chunks)

            current = ""
        else:
            current = paragraph

    # Ultimul chunk
    if current:
        chunks.append(current.strip())

    return chunks


def split_large_text(
    text: str,
    chunk_size: int,
    overlap: int,
) -> list[str]:
    """
    Împarte un text foarte lung folosind propoziții
    atunci când este posibil.
    """

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text,
    )

    chunks = []
    current = ""

    for sentence in sentences:

        if (
            current
            and len(current) + len(sentence) + 1
            > chunk_size
        ):
            chunks.append(current.strip())

            # Overlap din finalul chunk-ului anterior
            overlap_text = current[-overlap:]

            current = (
                overlap_text.strip()
                + " "
                + sentence
            )

        else:
            if current:
                current += " "

            current += sentence

    if current:
        chunks.append(current.strip())

    return chunks


def create_chunks_from_pages(
    pages: list[dict],
    chunk_size: int = 1200,
    overlap: int = 150,
) -> list[dict]:
    """
    Creează chunks din paginile PDF-ului.

    Păstrăm:
    - conținutul
    - pagina
    - indexul chunk-ului

    Nu presupunem nimic despre tipul documentului.
    """

    chunks = []
    chunk_index = 0

    for page in pages:

        page_chunks = chunk_text(
            page["text"],
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for chunk in page_chunks:

            chunks.append(
                {
                    "content": chunk,
                    "page_number": page["page_number"],
                    "chunk_index": chunk_index,
                }
            )

            chunk_index += 1

    return chunks