
from sentence_transformers import SentenceTransformer

# Load the free embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Convert text into an embedding
text = "Python is a programming language."

embedding = model.encode(text)

print("Embedding generated successfully!")
print("Total dimensions:", len(embedding))
print("First 10 values:", embedding[:10])
