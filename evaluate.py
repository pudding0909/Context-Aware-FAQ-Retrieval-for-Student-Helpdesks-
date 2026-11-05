from pathlib import Path
import pandas as pd
from faq_engine import FAQEngine

ROOT = Path(__file__).resolve().parent
TEST_PATH = ROOT / "data" / "test_queries.csv"

def main():
    tests = pd.read_csv(TEST_PATH).dropna(subset=["query", "expected_faq_id"])
    engine = FAQEngine(threshold=0.0)
    top1_hits = top3_hits = 0
    reciprocal_ranks = []
    for _, test in tests.iterrows():
        result = engine.ask(str(test["query"]), top_k=3)
        expected = int(test["expected_faq_id"])
        ids = [item["faq_id"] for item in result["results"]]
        rank = ids.index(expected) + 1 if expected in ids else None
        top1_hits += int(rank == 1)
        top3_hits += int(rank is not None)
        reciprocal_ranks.append(1 / rank if rank else 0)
    n = len(tests)
    print("LEVEL 4: EVALUATION")
    print("Test queries:", n)
    print(f"Top-1 accuracy: {top1_hits / n:.2%}")
    print(f"Top-3 accuracy: {top3_hits / n:.2%}")
    print(f"Mean Reciprocal Rank (MRR): {sum(reciprocal_ranks) / n:.3f}")
    print("These scores are based on the included sample test set; verify with your faculty/institution data.")

if __name__ == "__main__":
    main()
