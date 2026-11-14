
from ollama import chat


def generate_answer(question, context):

    response = chat(
        model="llama3.2:1b",
        messages=[
            {
                "role": "system",
                "content": "Answer the user's question using only the provided context. If the answer is not available in the context, say you cannot find it in the document."
            },
            {
                "role": "user",
                "content": f"""
                Context:
                {context}

                Question:
                {question}
                """
            }
        ]
    )

    return response.message.content
