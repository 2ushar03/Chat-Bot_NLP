from src.llama_wrapper import LlamaModelWrapper
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma


class PDFQASystem:
    def __init__(
        self,
        model_path: str,
        embedding_model_name: str,
        vector_store_dir: str,
    ):
        self.llama = LlamaModelWrapper(model_path=model_path)
        self.embedder = HuggingFaceEmbeddings(model_name=embedding_model_name)
        self.vectordb = Chroma(persist_directory=vector_store_dir, embedding_function=self.embedder)

    def _truncate_contexts(self, contexts: list[str], max_chars: int) -> list[str]:
        """Truncate combined contexts to approximately max_chars by
        dropping the longest contexts until we fit. This keeps prompts below
        the Llama model's context window (rough estimate using characters).
        """
        if not contexts:
            return contexts
        cur = contexts.copy()
        while sum(len(c) for c in cur) > max_chars and len(cur) > 1:
            cur.pop(max(range(len(cur)), key=lambda i: len(cur[i])))
        if sum(len(c) for c in cur) > max_chars:
            last = cur[-1]
            cur[-1] = last[: max_chars - sum(len(c) for c in cur[:-1])]
        return cur

    def answer_question(
        self,
        question: str,
        top_k: int = 6,
        max_tokens: int = 128,
        detailed: bool = False,
    ) -> str:
        """Answer a question using multi-pass retrieval + generation.

        Strategy:
        - Retrieve up to `top_k` chunks from the vector DB.
        - Group chunks into batches that fit the prompt-size budget.
        - For each batch, ask the model to produce a partial answer.
        - Synthesize all partial answers into a final comprehensive answer.

        Set `detailed=True` to request a more exhaustive final synthesis (uses
        larger final max_tokens).
        """
        docs_and_scores = self.vectordb.similarity_search_with_score(question, k=top_k)
        contexts = [doc.page_content for doc, _ in docs_and_scores]
        if not contexts:
            return "No relevant context found."
        batch_budget = 1400
        batches: list[list[str]] = []
        cur_batch: list[str] = []
        cur_len = 0
        for c in contexts:
            if cur_len + len(c) > batch_budget and cur_batch:
                batches.append(cur_batch)
                cur_batch = [c]
                cur_len = len(c)
            else:
                cur_batch.append(c)
                cur_len += len(c)
        if cur_batch:
            batches.append(cur_batch)

        partial_answers: list[str] = []
        for i, batch in enumerate(batches):
            prefix = (
                f"You are a helpful assistant. Use the following context (batch {i+1} of {len(batches)})"
                " to answer the question succinctly.\n\n"
            )
            ctx_prompt = "\n\n---\n".join(batch)
            prompt = prefix + ctx_prompt + "\n\nQuestion: " + question + "\nPartial Answer:"
            context_window = 512
            est_prompt_tokens = max(1, len(prompt) // 4)
            safe_max = max(16, min(128, context_window - est_prompt_tokens - 8))

            part = self.llama.generate(prompt, max_tokens=safe_max, temperature=0.0)
            partial_answers.append(part)
        if len(partial_answers) == 1 and not detailed:
            return partial_answers[0]
        synth_prefix = (
            "You are an expert assistant. Combine the following partial answers into a single, coherent, and complete answer to the question."
            " Keep any source references if present.\n\n"
        )
        synth_ctx = "\n\n---\n".join(
            [f"Partial answer {i+1}:\n{p}" for i, p in enumerate(partial_answers)]
        )
        final_prefix_and_question_len = len(synth_prefix) + len("\n\nQuestion: ") + len(question)
        est_prompt_tokens = (final_prefix_and_question_len + len(synth_ctx)) // 4
        if est_prompt_tokens > context_window - 32:
            max_chars_per_partial = 600
            compressed = [p[:max_chars_per_partial] for p in partial_answers]
            compressed = compressed[-3:]
            synth_ctx = "\n\n---\n".join(
                [f"Partial answer {i+1}:\n{p}" for i, p in enumerate(compressed, start=len(partial_answers)-len(compressed)+1)]
            )
            synth_ctx = "(NOTE: partial answers truncated to fit model context)\n\n" + synth_ctx

        final_prompt = synth_prefix + synth_ctx + "\n\nQuestion: " + question + "\nFinal Answer:"
        final_max = 256 if detailed else 160
        est_prompt_tokens = max(1, len(final_prompt) // 4)
        remaining = context_window - est_prompt_tokens - 8
        if remaining < 8:
            short_parts = []
            for p in partial_answers[-2:]:
                short_parts.append(p[:200])
            synth_ctx = "\n\n---\n".join([f"Partial answer:\n{p}" for p in short_parts])
            synth_ctx = "(NOTE: partial answers aggressively truncated)\n\n" + synth_ctx
            final_prompt = synth_prefix + synth_ctx + "\n\nQuestion: " + question + "\nFinal Answer:"
            est_prompt_tokens = max(1, len(final_prompt) // 4)
            remaining = context_window - est_prompt_tokens - 8

        safe_final_max = max(8, min(final_max, remaining))

        final = self.llama.generate(final_prompt, max_tokens=safe_final_max, temperature=0.0)
        return final
