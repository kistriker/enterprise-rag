import pymupdf


def extract_text_from_pdf(file_path: str) -> dict:
    document = pymupdf.open(file_path)

    pages = []

    try:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text()

            print(f"PAGE {page_number}:")
            print(repr(text))

            pages.append(
                {
                    "page_number": page_number,
                    "text": text,
                }
            )
    finally:
        document.close()

    return {
        "pages": pages,
        "page_count": len(pages),
    }