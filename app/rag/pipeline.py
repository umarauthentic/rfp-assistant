import logging

from app.config import get_settings
from app.rag.llm import get_llm_client
from app.rag.models import QueryResponse, ResponseTag, SearchResult
from app.rag.vector_store import FaissStore

logger = logging.getLogger(__name__)
INSUFFICIENT_INFORMATION = "I could not find sufficient information in the provided data."


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


def _filter_results_by_score(
    results: list[SearchResult],
    min_score: float,
) -> list[SearchResult]:
    return [result for result in results if result.score >= min_score]


def _make_response_tags(
    memory_matches: list[SearchResult],
    document_matches: list[SearchResult],
) -> list[ResponseTag]:
    tags: list[ResponseTag] = []
    seen: set[tuple[str, str]] = set()

    for result in memory_matches:
        tag_value = result.metadata.get("question") or result.id
        key = ("memory", tag_value)
        if key in seen:
            continue
        seen.add(key)
        tags.append(
            ResponseTag(
                label="Saved answer",
                tag_type="memory",
                value=tag_value,
                score=result.score,
                match_id=result.id,
            )
        )

    for result in document_matches:
        source = result.metadata.get("source") or result.metadata.get("path") or result.id
        chunk_index = result.metadata.get("chunk_index")
        label = str(source)
        if isinstance(chunk_index, int):
            label = f"{label} #{chunk_index + 1}"

        key = ("document", label)
        if key in seen:
            continue
        seen.add(key)
        tags.append(
            ResponseTag(
                label=label,
                tag_type="document",
                value=str(source),
                score=result.score,
                match_id=result.id,
            )
        )

    return tags[:6]


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
        memory_matches = _filter_results_by_score(
            memory_store.search(query, settings.top_k_qa),
            settings.min_qa_score,
        )

    if use_documents:
        document_store = FaissStore("documents", settings.vector_path)
        document_matches = _filter_results_by_score(
            document_store.search(query, settings.top_k_docs),
            settings.min_doc_score,
        )

    best_memory_score = memory_matches[0].score if memory_matches else 0.0
    logger.info("Best memory score: %.3f", best_memory_score)

    # Strong memory match: return saved answer directly
    if memory_matches:
        saved_answer = memory_matches[0].metadata.get("answer", "")

        if saved_answer:
            return QueryResponse(
                answer=saved_answer,
                from_memory=True,
                memory_matches=memory_matches,
                document_matches=document_matches,
                response_tags=_make_response_tags(memory_matches, document_matches),
            )

    if not memory_matches and not document_matches:
        return QueryResponse(
            answer=INSUFFICIENT_INFORMATION,
            from_memory=False,
            memory_matches=[],
            document_matches=[],
            response_tags=[],
        )

    memory_context = _format_memory_context(memory_matches)
    document_context = _format_document_context(document_matches)

    prompt = f"""
    You are an RFP answer generator.

    Your job is to draft customer-ready RFP answers using ONLY the provided context.

    STRICT RULES:
    1. Keep the answer as close as possible to the wording and meaning of the source context.
    2. Choose the clearest natural format for the answer based on the QUESTION and source context.
    3. Use a concise paragraph for direct, narrative, yes/no, or single-topic answers.
    4. Use bullet points only when the answer contains distinct items that are easier to scan as a list, or when the QUESTION asks for a list.
    5. Do not split one continuous answer into bullets just because it contains multiple facts.
    6. ONLY use facts explicitly written in the context.
    7. DO NOT infer, interpret, explain, or generalize.
    8. DO NOT add marketing claims, assumptions, or unsupported benefits.
    9. Preserve exact numbers, percentages, certifications, product names, dates, and values.
    10. Do NOT mention row names, sheet names, file names, sources, or internal references in the answer text.
    11. Prefer memory context when it directly answers the question.
    12. Follow any formatting instructions provided in the QUESTION.
    13. If information is not explicitly present, say:
    "{INSUFFICIENT_INFORMATION}"
    14. DO NOT use phrases like:
       - "can be inferred"
       - "suggests"
       - "implies"
       - "it is clear"
       - "indicates"

    MEMORY CONTEXT:
    {memory_context if memory_context else "No relevant saved answers found."}

    DOCUMENT CONTEXT:
    {document_context if document_context else "No relevant document context found."}

    QUESTION:
    {query}

    ANSWER:
    """.strip()

    llm = get_llm_client()
    answer = llm.generate(prompt)

    return QueryResponse(
        answer=answer,
        from_memory=False,
        memory_matches=memory_matches,
        document_matches=document_matches,
        response_tags=_make_response_tags(memory_matches, document_matches),
    )
