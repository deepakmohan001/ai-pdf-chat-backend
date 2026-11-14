from sentence_transformers import SentenceTransformer

# Load the free embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Convert text into an embedding
text = "Python is a programming language."

embedding = model.encode(text)

print("Embedding generated successfully!")
print("Total dimensions:", len(embedding))
print("First 10 values:", embedding[:10])

from sentence_transformers import SentenceTransformer, util

# Load the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Two example sentences
text1 = "Python is a programming language."
text2 = "I completed my MCA degree."
# Generate embeddings
embedding1 = model.encode(text1)
embedding2 = model.encode(text2)

# Calculate cosine similarity
similarity = util.cos_sim(embedding1, embedding2)

print("Cosine Similarity:", similarity.item())
