from typing import List
import httpx
import os


def get_context(question: str, min_chunks: int = 3, max_chunks: int = 6) -> List[str]:
    """
    Retrieve context chunks for a given question from the retrieval API.

    Calls the retrieval API to get relevant context chunks based on semantic search.
    Uses RETRIEVAL_API_URL environment variable or defaults to localhost:8000.

    Args:
        question: The user's question
        min_chunks: Minimum number of chunks to retrieve (default: 3)
        max_chunks: Maximum number of chunks to retrieve (default: 6)

    Returns:
        List of context strings (max 6 chunks as per plan)
    """
    # Use environment variable for retrieval API URL (for Docker compatibility)
    retrieval_base_url = os.getenv("RETRIEVAL_API_URL", "http://localhost:8000")
    retrieval_url = f"{retrieval_base_url}/retrieve"

    payload = {
        "query": question,
        "min_chunks": min_chunks,
        "max_chunks": max_chunks
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                retrieval_url,
                json=payload,
                headers={
                    "accept": "application/json",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()

            # Parse response
            result = response.json()

            # Handle the specific response format from your retrieval API
            # Expected format: {"query": "...", "chunks": [{"text": "...", ...}, ...]}
            if isinstance(result, dict) and "chunks" in result:
                chunks = result["chunks"]
                # Extract the "text" field from each chunk
                context_texts = []
                for chunk in chunks:
                    if isinstance(chunk, dict) and "text" in chunk:
                        context_texts.append(chunk["text"])
                    elif isinstance(chunk, str):
                        context_texts.append(chunk)
                return context_texts

            # Fallback: if result is a list of strings, return directly
            if isinstance(result, list):
                return [str(item) for item in result]

            # Fallback: convert to string
            return [str(result)]

    except httpx.HTTPError as e:
        print(f"Error calling retrieval API: {e}")
        # Return empty list on error - let the LLM handle no context scenario
        return []
    except Exception as e:
        print(f"Unexpected error in get_context: {e}")
        return []
