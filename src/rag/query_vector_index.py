from pathlib import Path

import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer


INDEX_PATH = Path("data/processed/faiss_index.bin")
METADATA_PATH = Path("data/processed/faiss_metadata.csv")

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def search(query, top_k=5):
    model = SentenceTransformer(MODEL_NAME)

    index = faiss.read_index(str(INDEX_PATH))
    metadata_df = pd.read_csv(METADATA_PATH)

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype("float32")

    scores, indices = index.search(query_embedding, top_k)

    results = []

    for score, index_id in zip(scores[0], indices[0]):
        row = metadata_df.iloc[index_id]

        results.append(
            {
                "score": float(score),
                "document_type": row["document_type"],
                "source_id": row["source_id"],
                "text": row["text"],
            }
        )

    return results


def main():
    query = "What body part was scanned?"

    results = search(query)

    print(f"Query: {query}")
    print("\nTop Results:")

    for i, result in enumerate(results, start=1):
        print(f"\nResult {i}")
        print(f"Score: {result['score']}")
        print(f"Type: {result['document_type']}")
        print(f"Source: {result['source_id']}")
        print(f"Text: {result['text']}")


if __name__ == "__main__":
    main()