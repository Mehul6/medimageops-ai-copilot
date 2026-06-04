from pathlib import Path

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer


DOCUMENTS_PATH = Path("data/processed/rag_documents.csv")
INDEX_PATH = Path("data/processed/faiss_index.bin")
METADATA_PATH = Path("data/processed/faiss_metadata.csv")

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def main():
    documents_df = pd.read_csv(DOCUMENTS_PATH)

    if documents_df.empty:
        raise ValueError("No RAG documents found.")

    texts = documents_df["text"].tolist()

    print(f"Loaded {len(texts)} documents")

    model = SentenceTransformer(MODEL_NAME)

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    embeddings = embeddings.astype("float32")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, str(INDEX_PATH))

    documents_df.to_csv(
        METADATA_PATH,
        index=False,
    )

    print(f"Created FAISS index with {index.ntotal} vectors")
    print(f"Saved index to {INDEX_PATH}")
    print(f"Saved metadata to {METADATA_PATH}")


if __name__ == "__main__":
    main()