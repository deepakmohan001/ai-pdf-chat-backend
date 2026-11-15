from pypdf import PdfReader
from app.services.chunking import split_text_into_chunks

pdf_path = r"uploads\3aa8005e-4d92-4e4a-94e2-9d45e1a94e62.pdf"

reader = PdfReader(pdf_path)

text = ""

for page in reader.pages:
    page_text = page.extract_text()

    if page_text:
        text += page_text + "\n"


# NEW CODE: Inspect extracted PDF lines
lines = text.splitlines()

for index, line in enumerate(lines):
    print(f"{index}: {line.strip()}")


# Existing chunking code
chunks = split_text_into_chunks(text)

print("Total chunks:", len(chunks))

for index, chunk in enumerate(chunks):
    print(f"\n{'=' * 50}")
    print(f"CHUNK {index + 1}")
    print(f"Word count: {len(chunk.split())}")
    print("=" * 50)
    print(chunk)