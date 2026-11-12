
text = """
Python is a programming language.
FastAPI is used to build APIs.
MongoDB is a NoSQL database.
React is a JavaScript library.
Django is a Python framework.
"""

words = text.split()

chunk_size = 5
overlap = 2

chunks = []

start = 0

while start < len(words):
    chunk = words[start:start + chunk_size]
    chunks.append(" ".join(chunk))

    start += chunk_size - overlap

for index, chunk in enumerate(chunks, start=1):
    print(f"Chunk {index}: {chunk}")
