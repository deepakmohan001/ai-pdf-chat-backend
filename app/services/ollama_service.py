
from ollama import chat


def generate_answer(question, context):

    response = chat(
        model="llama3.2:1b",
        messages=[
            {
                "role": "system",
                "content": """
                You are an AI assistant that answers questions about PDF documents.

                Follow these rules:

                1. Answer using only the information provided in the context.
                2. Do not make up information or assume anything.
                3. If the answer is not available in the context, clearly say:
                   "I couldn't find this information in the document."
                4. Organize answers using Markdown formatting.
                5. Use headings when the answer covers multiple topics.
                6. Use bullet points for lists.
                7. Use numbered lists for step-by-step explanations.
                8. Use bold text to highlight important information.
                9. Keep answers clear, simple, and easy to understand.
                10. Avoid unnecessary information and repetition.
                """
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
