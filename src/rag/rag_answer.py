import requests

from src.rag.query_vector_index import search


OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"


def build_context(results):
    context_parts = []

    for result in results:
        context_parts.append(result["text"])

    return "\n".join(context_parts)


def call_ollama(prompt):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        },
        timeout=120,
    )

    response.raise_for_status()

    return response.json()["response"]


def generate_answer(question, context):
    prompt = f"""
You are a healthcare data assistant for a medical imaging data platform.

Use ONLY the retrieved context.

Important:
- If the context says "CHEST CT scan", then the body part is CHEST and the modality is CT.
- Do not add assumptions about diseases or diagnosis.
- Do not say the answer is missing if the answer appears directly in the context.
- Keep the answer concise and factual.

Retrieved context:
{context}

Question:
{question}

Answer:
"""

    return call_ollama(prompt)


def answer_question(question, top_k=5):
    results = search(question, top_k=top_k)

    context = build_context(results)

    answer = generate_answer(question, context)

    return {
        "question": question,
        "answer": answer,
        "context": context,
        "sources": results,
    }


def main():
    question = "What body part was scanned?"

    response = answer_question(question)

    print("Question:")
    print(response["question"])

    print("\nAnswer:")
    print(response["answer"])

    print("\nRetrieved Context:")
    print(response["context"])


if __name__ == "__main__":
    main()