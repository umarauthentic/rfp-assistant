from app.main import ingest_documents


if __name__ == "__main__":
    result = ingest_documents()
    print(
        f"Indexed {result['files_indexed']} file(s) "
        f"and {result['chunks_indexed']} chunk(s)."
    )
