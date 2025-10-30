from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import logging
from .milvus_client import MilvusClient
from .entity_extractor import EntityExtractor
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RetrievalService:
    def __init__(
        self,
        milvus_host: str = "localhost",
        milvus_port: str = "19530",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """Initialize retrieval service"""
        # Initialize embedding model
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)

        # Initialize Milvus client
        self.milvus_client = MilvusClient(host=milvus_host, port=milvus_port)
        self.milvus_client.connect()
        self.milvus_client.create_collection(
            embedding_dim=self.embedding_model.get_sentence_embedding_dimension()
        )

        # Initialize entity extractor
        self.entity_extractor = EntityExtractor()

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        embedding = self.embedding_model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def semantic_search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Direct semantic search"""
        query_embedding = self.generate_embedding(query)
        results = self.milvus_client.search(query_embedding, top_k=top_k)

        chunks = []
        for hits in results:
            for hit in hits:
                chunks.append({
                    "id": hit.id,
                    "distance": hit.distance,
                    "document_id": hit.document_id,
                    "page_number": hit.page_number,
                    "text": hit.text,
                    "person_names": json.loads(hit.person_names),
                    "location_names": json.loads(hit.location_names),
                    "organization_names": json.loads(hit.organization_names),
                    "date_entities": json.loads(hit.date_entities),
                    "other_entities": json.loads(hit.other_entities)
                })
        return chunks

    def entity_based_search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search by extracting entities from query and matching with chunk metadata.
        Since Milvus doesn't support substring matching, we fetch candidates and filter in Python.
        """
        # Extract entities from query
        query_entities = self.entity_extractor.extract_entities(query)

        person_names = json.loads(query_entities["person_names"])
        location_names = json.loads(query_entities["location_names"])
        organization_names = json.loads(query_entities["organization_names"])
        date_entities = json.loads(query_entities["date_entities"])
        other_entities = json.loads(query_entities["other_entities"])

        logger.info(f"Extracted entities from query: persons={person_names}, "
                   f"locations={location_names}, orgs={organization_names}, "
                   f"dates={date_entities}, others={other_entities}")

        # If no entities found, return empty
        if not (person_names or location_names or organization_names or date_entities or other_entities):
            logger.info("No entities found in query, returning empty results")
            return []

        # Get more candidates using semantic search
        query_embedding = self.generate_embedding(query)
        candidates = self.milvus_client.search(query_embedding, top_k=top_k * 5)

        # Filter candidates based on entity matches
        matched_chunks = []
        for hits in candidates:
            for hit in hits:
                chunk_person_names = json.loads(hit.person_names)
                chunk_location_names = json.loads(hit.location_names)
                chunk_org_names = json.loads(hit.organization_names)
                chunk_date_entities = json.loads(hit.date_entities)
                chunk_other_entities = json.loads(hit.other_entities)

                # Check if any query entity matches chunk entities (case-insensitive, substring)
                match_found = False

                # Check person names
                for query_person in person_names:
                    clean_query = query_person.split('(')[0].strip()
                    for chunk_person in chunk_person_names:
                        if clean_query in chunk_person or chunk_person in clean_query:
                            match_found = True
                            break
                    if match_found:
                        break

                # Check locations
                if not match_found:
                    for query_loc in location_names:
                        clean_query = query_loc.split('(')[0].strip()
                        for chunk_loc in chunk_location_names:
                            if clean_query in chunk_loc or chunk_loc in clean_query:
                                match_found = True
                                break
                        if match_found:
                            break

                # Check organizations
                if not match_found:
                    for query_org in organization_names:
                        clean_query = query_org.split('(')[0].strip()
                        for chunk_org in chunk_org_names:
                            if clean_query in chunk_org or chunk_org in clean_query:
                                match_found = True
                                break
                        if match_found:
                            break

                # Check dates
                if not match_found:
                    for query_date in date_entities:
                        for chunk_date in chunk_date_entities:
                            if query_date in chunk_date or chunk_date in query_date:
                                match_found = True
                                break
                        if match_found:
                            break

                # Check other entities
                if not match_found:
                    for query_other in other_entities:
                        for chunk_other in chunk_other_entities:
                            if query_other in chunk_other or chunk_other in query_other:
                                match_found = True
                                break
                        if match_found:
                            break

                if match_found:
                    matched_chunks.append({
                        "id": hit.id,
                        "distance": hit.distance,
                        "document_id": hit.document_id,
                        "page_number": hit.page_number,
                        "text": hit.text,
                        "person_names": chunk_person_names,
                        "location_names": chunk_location_names,
                        "organization_names": chunk_org_names,
                        "date_entities": chunk_date_entities,
                        "other_entities": chunk_other_entities
                    })

        # Sort by semantic similarity (lower distance is better)
        matched_chunks.sort(key=lambda x: x["distance"])

        logger.info(f"Found {len(matched_chunks)} entity-matched chunks")
        return matched_chunks[:top_k]

    def retrieve(self, query: str, min_chunks: int = 3, max_chunks: int = 6) -> Dict[str, Any]:
        """
        Retrieve chunks using hybrid approach:
        1. Direct semantic search (top 3)
        2. Entity-based search with semantic ranking (top 3)
        3. Combine and deduplicate (min 3, max 6)
        """
        logger.info(f"Processing query: {query}")

        # 1. Direct semantic search
        semantic_chunks = self.semantic_search(query, top_k=3)
        logger.info(f"Found {len(semantic_chunks)} chunks from semantic search")

        # 2. Entity-based search
        entity_chunks = self.entity_based_search(query, top_k=3)
        logger.info(f"Found {len(entity_chunks)} chunks from entity-based search")

        # 3. Combine and deduplicate
        seen_ids = set()
        combined_chunks = []

        # Add semantic search results first
        for chunk in semantic_chunks:
            if chunk["id"] not in seen_ids:
                seen_ids.add(chunk["id"])
                chunk["source"] = "semantic_search"
                combined_chunks.append(chunk)

        # Add entity-based results
        for chunk in entity_chunks:
            if chunk["id"] not in seen_ids:
                seen_ids.add(chunk["id"])
                chunk["source"] = "entity_search"
                combined_chunks.append(chunk)

        # Ensure min and max constraints
        total_chunks = len(combined_chunks)

        if total_chunks < min_chunks:
            logger.warning(f"Only found {total_chunks} chunks, less than minimum {min_chunks}")

        final_chunks = combined_chunks[:max_chunks]

        logger.info(f"Returning {len(final_chunks)} chunks after deduplication")

        return {
            "query": query,
            "total_results": len(final_chunks),
            "semantic_count": len(semantic_chunks),
            "entity_count": len(entity_chunks),
            "chunks": final_chunks
        }
