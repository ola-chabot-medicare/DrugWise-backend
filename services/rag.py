"""
RAG service - search ChromaDB Cloud for relevant FDA docs
based on user question, then format them into context for LLM.
"""
from config.chroma import get_collection
from utils.logger import logger


""" 1. Function Signature """
def retrieve_context(question: str, n_results: int = 5) -> str:
    """
    Search ChromaDB for most relevant FDA documents matching the question.
    - question
    - n_results = retrieve top 5 most relevant documents
    - return: a formatted string of FDA context for LLM
    """


    """ 2. Query ChromaDB Cloud with try/except """
    try: 
        collection = get_collection()      # get ChromaDB Cloud collection
        
        # query() turn question -> vector, then find closest documents
        results =  collection.query(
            query_texts =  [question],
            n_results = n_results,
            include = ["documents", "metadatas"]       # what to return with each result
        )


        
        """ 3. Format results into readable context
        This format raw ChromaDB results into something GPT can read like:

        [1] Advil (ibuprofen):
        Brand: Advil | Warnings: Do not use if allergic...

        [2] Motrin (ibuprofen):
        Brand: Motrin | Adverse Reactions: Nausea, dizziness...
        """

        docs = results["documents"][0]
        metas =  results["metadatas"][0]

        # Build a numbered list of relevant FDA documents
        context_parts = []
        for i, (doc, meta) in enumerate(zip(docs, metas), start = 1):
            brand = meta.get("brand_name", "Unknown")
            generic = meta.get("generic_name", "Unknown")
            # Trim each document to 600 chars to keep total context manageable
            context_parts.append(f"[{i}] {brand} ({generic}):\n{doc[:600]}")

        # Join all documents into one big context string separated by blank lines
        context = "\n\n".join(context_parts)
        logger.info(f"Retrieved {len(docs)} documents for query: {question[:50]}")
        return context

    except Exception as e:
        # If ChromaDB is down or query fails, return empty string
        # LLM fall back to its own knowledge instead of crashing
        logger.error(f"ChromaDB query failed: {e}")
        return ""
