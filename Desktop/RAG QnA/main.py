import argparse
from src.ingest import ingest_pdfs_to_vectorstore
from src.query import PDFQASystem

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, required=True, choices=["ingest", "query"])
    parser.add_argument("--pdf_folder", type=str, default="data/pdfs")
    parser.add_argument("--vector_dir", type=str, default="embeddings_store")
    parser.add_argument("--model_path", type=str, required=True)
    parser.add_argument("--embedding_model", type=str, default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--top_k", type=int, default=6, help="Number of retrieved chunks to consider (RAG)")
    parser.add_argument("--max_tokens", type=int, default=128, help="Max tokens for LLM generation per pass")
    parser.add_argument("--detailed", action="store_true", help="Return a more detailed, synthesized answer")
    args = parser.parse_args()

    if args.mode == "ingest":
        ingest_pdfs_to_vectorstore(
            pdf_folder=args.pdf_folder,
            persist_directory=args.vector_dir,
            embedding_model_name=args.embedding_model,
        )
    elif args.mode == "query":
        qa = PDFQASystem(
            model_path=args.model_path,
            embedding_model_name=args.embedding_model,
            vector_store_dir=args.vector_dir,
        )
        print("Enter your question (type 'exit' to quit):")
        while True:
            q = input("Q> ")
            if q.strip().lower() in ("exit", "quit"):
                break
            inline_detailed = False
            if q.strip().endswith(" --detailed"):
                q = q.rstrip()
                q = q[: -len(" --detailed")].rstrip()
                inline_detailed = True

            ans = qa.answer_question(
                q,
                top_k=args.top_k,
                max_tokens=args.max_tokens,
                detailed=(args.detailed or inline_detailed),
            )
            print("A>", ans)
    else:
        raise ValueError("Invalid mode")

if __name__ == "__main__":
    main()
