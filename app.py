from faq_engine import FAQEngine


def main():
    print("CONTEXT-AWARE STUDENT FAQ RETRIEVAL")
    print("Model: TF-IDF + cosine similarity (lightweight; no PyTorch required)")
    print("Type 'exit' to stop.")
    engine = FAQEngine(threshold=0.18)
    while True:
        query = input("\nYour question: ").strip()
        if query.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        result = engine.ask(query)
        print("\nAnswer:", result["message"])
        if result.get("best_score") is not None:
            print(f"Similarity score: {result['best_score']:.3f}")
        print("\nTop matches:")
        for item in result["results"]:
            print(f"- [{item['score']:.3f}] {item['question']}")


if __name__ == "__main__":
    main()
