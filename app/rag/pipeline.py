from app.config import get_settings
from app.rag.llm import OllamaClient
from app.rag.models import QueryResponse, SearchResult
from app.rag.vector_store import FaissStore


def _clean_text(text: str) -> str:
    if not text:
        return ""

    remove_terms = [
        "Sheet:",
        "Row",
        "Unnamed:",
        "|",
    ]

    for term in remove_terms:
        text = text.replace(term, " ")

    return " ".join(text.split()).strip()


def _format_document_context(results: list[SearchResult]) -> str:
    if not results:
        return ""

    return "\n\n".join(_clean_text(r.text) for r in results)


def _format_memory_context(results: list[SearchResult]) -> str:
    if not results:
        return ""

    chunks = []

    for r in results:
        question = r.metadata.get("question", "")
        answer = r.metadata.get("answer", "")

        if answer:
            chunks.append(f"Saved Question: {question}\nSaved Answer: {answer}")

    return "\n\n".join(chunks)


def answer_query(
    query: str,
    use_memory: bool = True,
    use_documents: bool = True,
) -> QueryResponse:
    settings = get_settings()

    memory_matches = []
    document_matches = []

    if use_memory:
        memory_store = FaissStore("qa_memory", settings.vector_path)
        memory_matches = memory_store.search(query, settings.top_k_qa)

    if use_documents:
        document_store = FaissStore("documents", settings.vector_path)
        document_matches = document_store.search(query, settings.top_k_docs)

    best_memory_score = memory_matches[0].score if memory_matches else 0.0
    print("Best memory score:", best_memory_score)

    # Strong memory match: return saved answer directly
    if memory_matches and best_memory_score >= settings.min_qa_score:
        saved_answer = memory_matches[0].metadata.get("answer", "")

        if saved_answer:
            return QueryResponse(
                answer=saved_answer,
                from_memory=True,
                memory_matches=memory_matches,
                document_matches=document_matches,
            )

    memory_context = _format_memory_context(memory_matches)
    document_context = _format_document_context(document_matches)

    prompt = f"""
    You are an RFP answer generator.

    Your job is to answer using ONLY factual information from the provided context.

    STRICT RULES:
    1. ONLY use facts explicitly written in the context.
    2. DO NOT infer, interpret, explain, or generalize.
    3. DO NOT use phrases like:
       - "can be inferred"
       - "suggests"
       - "implies"
       - "it is clear"
       - "indicates"
    4. DO NOT add commentary or assumptions.
    5. Use natural, professional language.
    6. Preserve exact numbers, percentages, certifications, and values.
    7. Do NOT mention row names, sheet names, file names, sources, or internal references.
    8. Prefer memory context when it directly answers the question.
    9. Follow any formatting instructions provided in the QUESTION.
    10. If no formatting is requested, respond in a concise human-readable paragraph.
    11. If information is not explicitly present, say:
    "I could not find sufficient information in the provided data."

    MEMORY CONTEXT:
    {memory_context if memory_context else "No relevant saved answers found."}

    DOCUMENT CONTEXT:
    {document_context if document_context else "No relevant document context found."}

    QUESTION:
    {query}

    ANSWER:
    """.strip()

    llm = OllamaClient()
    answer = llm.generate(prompt)

    return QueryResponse(
        answer=answer,
        from_memory=False,
        memory_matches=memory_matches,
        document_matches=document_matches,
    )
