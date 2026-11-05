from pathlib import Path
import re
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
INDEX_DIR = ROOT / "saved_index"
INDEX_DIR.mkdir(exist_ok=True)
FAQ_PATHS = sorted(DATA_DIR.glob("faq_dataset_*.csv"))
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def clean_text(text):
    """Normalize FAQ and user text consistently before embedding."""
    text = str(text).strip().lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\brevaluation\b", "re evaluation", text)
    text = re.sub(r"\badmit card\b", "hall ticket", text)
    text = re.sub(r"\bstudent id\b", "college id", text)
    if "attendance" in text:
        text += " minimum required eligibility percentage"
    return re.sub(r"\s+", " ", text).strip()


class FAQEngine:
    """FAQ retrieval using all-MiniLM-L6-v2 embeddings and cosine similarity."""

    def __init__(self, threshold=0.42, model_name=MODEL_NAME):
        self.threshold = float(threshold)
        self.model_name = model_name
        self.dataset_paths = list(FAQ_PATHS)
        if not self.dataset_paths:
            raise FileNotFoundError("No FAQ datasets found in the data folder.")
        frames = [pd.read_csv(path).fillna("") for path in self.dataset_paths]
        self.faqs = pd.concat(frames, ignore_index=True).reset_index(drop=True)
        required = {"faq_id", "question", "answer", "category"}
        missing = required - set(self.faqs.columns)
        if missing:
            raise ValueError(f"Missing columns in FAQ dataset: {sorted(missing)}")
        if self.faqs.empty:
            raise ValueError("FAQ datasets are empty.")
        self.faqs["question"] = self.faqs["question"].astype(str)

        # The model is downloaded from Hugging Face the first time it runs.
        self.model = SentenceTransformer(self.model_name)
        self.index_path = INDEX_DIR / "faq_embeddings.npy"
        self.metadata_path = INDEX_DIR / "faq_index_metadata.csv"
        self._build_or_load_index()

    def _build_or_load_index(self):
        cleaned_questions = self.faqs["question"].map(clean_text).tolist()
        can_load = self.index_path.exists() and self.metadata_path.exists()
        if can_load:
            try:
                old_meta = pd.read_csv(self.metadata_path)
                same_questions = (
                    len(old_meta) == len(self.faqs)
                    and old_meta["question"].astype(str).tolist() == self.faqs["question"].astype(str).tolist()
                )
                saved = np.load(self.index_path)
                if same_questions and saved.shape == (len(self.faqs), 384):
                    self.question_embeddings = saved.astype(np.float32)
                    return
            except Exception:
                pass

        self.question_embeddings = self.model.encode(
            cleaned_questions,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True,
            batch_size=32,
        ).astype(np.float32)
        np.save(self.index_path, self.question_embeddings)
        self.faqs[["faq_id", "question", "answer", "category"]].to_csv(self.metadata_path, index=False)

    def ask(self, query, top_k=3):
        query = clean_text(query)
        if not query:
            return {"found": False, "message": "Please enter a question.", "best_score": None, "results": []}
        query_embedding = self.model.encode(
            [query], convert_to_numpy=True, normalize_embeddings=True
        )[0].astype(np.float32)
        # Both vectors are L2-normalized, so dot product equals cosine similarity.
        scores = self.question_embeddings @ query_embedding
        k = max(1, min(int(top_k), len(self.faqs)))
        order = np.argsort(scores)[::-1][:k]
        results = []
        for idx in order:
            row = self.faqs.iloc[int(idx)]
            results.append({
                "faq_id": int(row["faq_id"]),
                "question": str(row["question"]),
                "answer": str(row["answer"]),
                "category": str(row["category"]),
                "score": float(scores[idx]),
            })
        if not results:
            return {"found": False, "message": "No FAQ records are available.", "best_score": None, "results": []}
        best = results[0]
        found = best["score"] >= self.threshold
        message = best["answer"] if found else "I couldn't find a close enough match in the FAQ dataset. Please rephrase your question or contact the relevant college office."
        return {"found": found, "message": message, "best_score": best["score"], "results": results}
