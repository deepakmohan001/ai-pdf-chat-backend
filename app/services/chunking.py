def split_text_into_chunks(text, chunk_size=500, overlap=50):

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        chunk = words[start:start + chunk_size]

        chunks.append(" ".join(chunk))

        start += chunk_size - overlap

    return chunks
