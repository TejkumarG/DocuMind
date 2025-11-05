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
        PURE Entity-based search (NO semantic search at this stage!)

        Step 1: Extract entities from query
        Step 2: Get ALL chunks from Milvus
        Step 3: Filter chunks by entity match in Python
        Step 4: Sort by entity match count (no semantic distance)
        Step 5: Return top_k chunks
        """
        # Extract entities from query
        query_entities = self.entity_extractor.extract_entities(query)

        person_names = json.loads(query_entities["person_names"])
        location_names = json.loads(query_entities["location_names"])
        organization_names = json.loads(query_entities["organization_names"])
        date_entities = json.loads(query_entities["date_entities"])
        file_numbers = json.loads(query_entities["file_numbers"])
        other_entities = json.loads(query_entities["other_entities"])

        logger.info(f"Extracted entities from query: persons={person_names}, "
                   f"locations={location_names}, orgs={organization_names}, "
                   f"dates={date_entities}, files={file_numbers}, others={other_entities}")

        # If no entities found, return empty
        if not (person_names or location_names or organization_names or date_entities or file_numbers or other_entities):
            logger.info("No entities found in query, returning empty results")
            return []

        # Get ALL chunks from Milvus (NO semantic search!)
        all_chunks = self.milvus_client.query_all()
        logger.info(f"Retrieved {len(all_chunks)} total chunks for entity filtering")

        # Filter ALL chunks based on entity matches and COUNT how many entities match
        matched_chunks = []
        for chunk in all_chunks:
                chunk_person_names = json.loads(chunk["person_names"])
                chunk_location_names = json.loads(chunk["location_names"])
                chunk_org_names = json.loads(chunk["organization_names"])
                chunk_date_entities = json.loads(chunk["date_entities"])
                chunk_file_numbers = json.loads(chunk["file_numbers"])
                chunk_other_entities = json.loads(chunk["other_entities"])

                # COUNT how many query entities match this chunk
                entity_match_count = 0

                # Check file numbers FIRST (highest priority - exact match)
                for query_file in file_numbers:
                    for chunk_file in chunk_file_numbers:
                        if query_file == chunk_file:  # Exact match for file numbers
                            entity_match_count += 10  # Weight file number matches heavily!
                            break

                # Check person names
                for query_person in person_names:
                    clean_query = query_person.split('(')[0].strip()
                    for chunk_person in chunk_person_names:
                        if clean_query in chunk_person or chunk_person in clean_query:
                            entity_match_count += 1
                            break

                # Check locations
                for query_loc in location_names:
                    clean_query = query_loc.split('(')[0].strip()
                    for chunk_loc in chunk_location_names:
                        if clean_query in chunk_loc or chunk_loc in clean_query:
                            entity_match_count += 1
                            break

                # Check organizations
                for query_org in organization_names:
                    clean_query = query_org.split('(')[0].strip()
                    for chunk_org in chunk_org_names:
                        if clean_query in chunk_org or chunk_org in clean_query:
                            entity_match_count += 1
                            break

                # Check dates
                for query_date in date_entities:
                    for chunk_date in chunk_date_entities:
                        if query_date in chunk_date or chunk_date in query_date:
                            entity_match_count += 1
                            break

                # Check other entities
                for query_other in other_entities:
                    for chunk_other in chunk_other_entities:
                        if query_other in chunk_other or chunk_other in query_other:
                            entity_match_count += 1
                            break

                # Only add chunks that have at least 1 entity match
                if entity_match_count > 0:
                    matched_chunks.append({
                        "id": chunk["id"],
                        "distance": 0.0,  # No semantic distance in pure entity search
                        "document_id": chunk["document_id"],
                        "page_number": chunk["page_number"],
                        "text": chunk["text"],
                        "person_names": chunk_person_names,
                        "location_names": chunk_location_names,
                        "organization_names": chunk_org_names,
                        "date_entities": chunk_date_entities,
                        "file_numbers": chunk_file_numbers,
                        "other_entities": chunk_other_entities,
                        "entity_match_count": entity_match_count
                    })

        # Sort ONLY by entity match count (descending) - NO semantic distance!
        matched_chunks.sort(key=lambda x: -x["entity_match_count"])

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

    def retrieve_scenario_1(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Scenario 1: Direct Semantic with Document Expansion
        1. Do semantic search on ALL documents → Get top 3
        2. Extract document_ids from those 3 chunks
        3. Do semantic search ONLY within those document_ids → Get top 5
        4. Return top 5 chunks (original 3 will be in top 5 anyway)
        """
        logger.info(f"Scenario 1 (Direct Semantic): Step 1 - Semantic search on ALL documents")

        # Step 1: Get top 3 from ALL documents
        initial_chunks = self.semantic_search(query, top_k=3)

        # Step 2: Extract document_ids
        document_ids = list(set([chunk["document_id"] for chunk in initial_chunks]))
        logger.info(f"Scenario 1: Found {len(document_ids)} documents from initial search")

        # Step 3: Do semantic search ONLY within those documents
        doc_filter = " or ".join([f'document_id == "{doc_id}"' for doc_id in document_ids])
        logger.info(f"Scenario 1: Step 2 - Semantic search within {len(document_ids)} documents")

        query_embedding = self.generate_embedding(query)

        # Get more chunks from those documents
        search_limit = min(len(document_ids) * 10, 50)  # 10 per doc, max 50
        filtered_results = self.milvus_client.search_with_filter(
            query_embedding,
            filter_expr=doc_filter,
            top_k=search_limit
        )

        # Collect results
        expanded_chunks = []
        for hits in filtered_results:
            for hit in hits:
                expanded_chunks.append({
                    "id": hit.id,
                    "distance": hit.distance,
                    "document_id": hit.document_id,
                    "page_number": hit.page_number,
                    "text": hit.text,
                    "person_names": json.loads(hit.person_names),
                    "location_names": json.loads(hit.location_names),
                    "organization_names": json.loads(hit.organization_names),
                    "date_entities": json.loads(hit.date_entities),
                    "other_entities": json.loads(hit.other_entities),
                    "source": "scenario_1"
                })

        # Sort by distance and return top K
        expanded_chunks.sort(key=lambda x: x["distance"])
        final_chunks = expanded_chunks[:top_k]

        logger.info(f"Scenario 1: Returning {len(final_chunks)} chunks")
        return final_chunks

    def retrieve_scenario_2(self, query: str, entity_chunks: int = 2, document_chunks: int = 2) -> List[Dict[str, Any]]:
        """
        Scenario 2: Entity-first filtering with document expansion

        Returns 4 chunks total:
        - 2 chunks: Best entity-matched chunks (top 2 from all entity matches)
        - 2 chunks: Best semantic chunks from ALL entity-matched documents

        Steps:
        1. Extract entities from query
        2. Find ALL chunks that contain those entities (e.g., 23 chunks)
        3. Take top 2 entity chunks (best entity match)
        4. Extract document_ids from ALL 23 entity-matched chunks → e.g., 15 unique documents
        5. Do semantic search across ALL chunks from those 15 documents (e.g., 300 chunks)
        6. Take top 2 semantic chunks
        7. Return 2 + 2 = 4 chunks
        """
        logger.info(f"Scenario 2: Starting (entity_chunks={entity_chunks}, document_chunks={document_chunks})")

        # 1. Extract entities from query
        query_entities = self.entity_extractor.extract_entities(query)
        person_names = json.loads(query_entities["person_names"])
        location_names = json.loads(query_entities["location_names"])
        organization_names = json.loads(query_entities["organization_names"])
        date_entities = json.loads(query_entities["date_entities"])
        file_numbers = json.loads(query_entities["file_numbers"])
        other_entities = json.loads(query_entities["other_entities"])

        has_entities = bool(person_names or location_names or organization_names or date_entities or file_numbers or other_entities)

        logger.info(f"Scenario 2: Extracted entities - persons={person_names}, locations={location_names}, "
                   f"orgs={organization_names}, dates={date_entities}, files={file_numbers}, others={other_entities}")

        # 2. If NO entities, return empty list
        if not has_entities:
            logger.info("Scenario 2: No entities found, returning empty list")
            return []

        # 3. Find ALL chunks that contain entities (not just top 2)
        all_entity_matched_chunks = self.entity_based_search(query, top_k=100)  # Get ALL entity matches
        logger.info(f"Scenario 2: Found {len(all_entity_matched_chunks)} total entity-matched chunks")

        if not all_entity_matched_chunks:
            logger.info("Scenario 2: No entity matches found, returning empty list")
            return []

        # 4. Take top 2 entity chunks (best entity match)
        top_entity_chunks = all_entity_matched_chunks[:entity_chunks]
        logger.info(f"Scenario 2: Selected top {len(top_entity_chunks)} entity chunks")

        # Mark these as entity-containing chunks
        for chunk in top_entity_chunks:
            chunk["source"] = "scenario_2_entity"

        # 5. Extract document_ids from ALL entity-matched chunks (not just top 2)
        all_entity_document_ids = list(set([chunk["document_id"] for chunk in all_entity_matched_chunks]))
        logger.info(f"Scenario 2: Found entities in {len(all_entity_document_ids)} unique documents from {len(all_entity_matched_chunks)} chunks")

        # 6. Do semantic search across ALL chunks from those documents
        doc_filter = " or ".join([f'document_id == "{doc_id}"' for doc_id in all_entity_document_ids])
        logger.info(f"Scenario 2: Doing semantic search across ALL chunks from {len(all_entity_document_ids)} entity-matched documents")

        query_embedding = self.generate_embedding(query)
        # Search more chunks since we're looking across more documents
        search_limit = min(len(all_entity_document_ids) * 10, 100)

        filtered_results = self.milvus_client.search_with_filter(
            query_embedding,
            filter_expr=doc_filter,
            top_k=search_limit
        )

        # 7. Collect semantic results from all entity-matched documents
        document_expansion_chunks = []
        seen_ids = set([chunk["id"] for chunk in top_entity_chunks])  # Don't duplicate the top 2 entity chunks

        for hits in filtered_results:
            for hit in hits:
                if hit.id not in seen_ids:
                    document_expansion_chunks.append({
                        "id": hit.id,
                        "distance": hit.distance,
                        "document_id": hit.document_id,
                        "page_number": hit.page_number,
                        "text": hit.text,
                        "person_names": json.loads(hit.person_names),
                        "location_names": json.loads(hit.location_names),
                        "organization_names": json.loads(hit.organization_names),
                        "date_entities": json.loads(hit.date_entities),
                        "other_entities": json.loads(hit.other_entities),
                        "source": "scenario_2_document"
                    })
                    seen_ids.add(hit.id)

        # Sort by distance and take top N
        document_expansion_chunks.sort(key=lambda x: x["distance"])
        document_expansion_chunks = document_expansion_chunks[:document_chunks]

        # 8. Combine: 2 entity chunks + 2 document chunks
        final_chunks = top_entity_chunks + document_expansion_chunks

        logger.info(f"Scenario 2: Returning {len(final_chunks)} chunks "
                   f"({len(top_entity_chunks)} entity + {len(document_expansion_chunks)} document)")

        return final_chunks

    def retrieve_hybrid(self, query: str) -> Dict[str, Any]:
        """
        Hybrid Retrieval: Run both scenarios in parallel and merge results

        Scenario 1 (Direct Semantic): 5 chunks
        - Semantic search on ALL documents → top 3
        - Extract document_ids
        - Semantic search within those documents → top 5

        Scenario 2 (Entity-filtered): 4 chunks (2 entity + 2 document)
        - Extract entities from query
        - Find documents with those entities
        - Get 2 chunks that ACTUALLY contain the entities
        - Get 2 more chunks from same documents via semantic search

        Final: Combine and deduplicate → Max 9 unique chunks
        """
        logger.info(f"=== Hybrid Retrieval Started ===")

        # Run Scenario 1 (Direct Semantic)
        scenario_1_chunks = self.retrieve_scenario_1(query, top_k=5)
        logger.info(f"Scenario 1 returned {len(scenario_1_chunks)} chunks")

        # Run Scenario 2 (Entity-filtered) - 2 entity chunks + 2 document chunks = 4 total
        scenario_2_chunks = self.retrieve_scenario_2(query, entity_chunks=2, document_chunks=2)
        logger.info(f"Scenario 2 returned {len(scenario_2_chunks)} chunks")

        # Combine and deduplicate
        seen_ids = set()
        combined_chunks = []

        # Add Scenario 1 chunks first (Direct Semantic)
        for chunk in scenario_1_chunks:
            if chunk["id"] not in seen_ids:
                seen_ids.add(chunk["id"])
                combined_chunks.append(chunk)

        # Add Scenario 2 chunks (Entity-filtered)
        for chunk in scenario_2_chunks:
            if chunk["id"] not in seen_ids:
                seen_ids.add(chunk["id"])
                chunk["source"] = "scenario_2"
                combined_chunks.append(chunk)

        # Sort by distance (semantic similarity)
        combined_chunks.sort(key=lambda x: x["distance"])

        logger.info(f"=== Hybrid Retrieval Complete: {len(combined_chunks)} unique chunks (max 9) ===")

        return {
            "query": query,
            "total_results": len(combined_chunks),
            "scenario_1_count": len(scenario_1_chunks),
            "scenario_2_count": len(scenario_2_chunks),
            "unique_chunks": len(combined_chunks),
            "chunks": combined_chunks
        }

    def retrieve_with_document_expansion(self, query: str, min_chunks: int = 3, max_chunks: int = 10) -> Dict[str, Any]:
        """
        Enhanced retrieval that expands to get more chunks from the same documents:
        1. Direct semantic search (top 3)
        2. Extract entities from query
        3. If entities found: Get ALL chunks from documents containing those entities
        4. Combine and return
        """
        logger.info(f"Processing query with document expansion: {query}")

        # 1. Direct semantic search
        semantic_chunks = self.semantic_search(query, top_k=3)
        logger.info(f"Found {len(semantic_chunks)} chunks from semantic search")

        # 2. Extract entities from query
        query_entities = self.entity_extractor.extract_entities(query)
        person_names = json.loads(query_entities["person_names"])
        location_names = json.loads(query_entities["location_names"])
        organization_names = json.loads(query_entities["organization_names"])
        date_entities = json.loads(query_entities["date_entities"])
        file_numbers = json.loads(query_entities["file_numbers"])
        other_entities = json.loads(query_entities["other_entities"])

        has_entities = bool(person_names or location_names or organization_names or date_entities or file_numbers or other_entities)

        logger.info(f"Extracted entities - persons={person_names}, locations={location_names}, "
                   f"orgs={organization_names}, dates={date_entities}, files={file_numbers}, others={other_entities}")
        logger.info(f"Entities found: {has_entities}")

        if not has_entities:
            # No entities, just return semantic results
            logger.info("No entities found, returning semantic search results only")
            return {
                "query": query,
                "total_results": len(semantic_chunks),
                "semantic_count": len(semantic_chunks),
                "entity_count": 0,
                "document_expansion": False,
                "chunks": semantic_chunks
            }

        # 3. Get entity-matched chunks to find relevant document_ids
        entity_matched_chunks = self.entity_based_search(query, top_k=50)  # Get more candidates
        logger.info(f"Found {len(entity_matched_chunks)} entity-matched chunks")

        # 4. Extract unique document_ids that contain entities
        entity_document_ids = list(set([chunk["document_id"] for chunk in entity_matched_chunks]))
        logger.info(f"Found entities in {len(entity_document_ids)} documents: {entity_document_ids[:5]}...")

        # 5. Get ALL chunks from those specific documents
        document_chunks = []
        if entity_document_ids:
            # Build filter expression for Milvus
            doc_filter = " or ".join([f'document_id == "{doc_id}"' for doc_id in entity_document_ids])
            logger.info(f"Fetching all chunks from entity-matched documents")

            # Search with document filter
            # Increase top_k significantly to get more chunks per document
            # Formula: num_docs * chunks_per_doc = 18 * 5 = 90
            query_embedding = self.generate_embedding(query)
            chunks_per_doc = 5  # Get at least 5 chunks from each document
            search_limit = min(len(entity_document_ids) * chunks_per_doc, 100)  # Cap at 100

            logger.info(f"Requesting {search_limit} chunks across {len(entity_document_ids)} documents")

            filtered_results = self.milvus_client.search_with_filter(
                query_embedding,
                filter_expr=doc_filter,
                top_k=search_limit
            )

            for hits in filtered_results:
                for hit in hits:
                    document_chunks.append({
                        "id": hit.id,
                        "distance": hit.distance,
                        "document_id": hit.document_id,
                        "page_number": hit.page_number,
                        "text": hit.text,
                        "person_names": json.loads(hit.person_names),
                        "location_names": json.loads(hit.location_names),
                        "organization_names": json.loads(hit.organization_names),
                        "date_entities": json.loads(hit.date_entities),
                        "other_entities": json.loads(hit.other_entities),
                        "source": "document_expansion"
                    })

            logger.info(f"Retrieved {len(document_chunks)} chunks from entity-matched documents")

        # 6. Combine and deduplicate with per-document diversity
        seen_ids = set()
        combined_chunks = []
        chunks_per_document = {}

        # Add semantic search results first
        for chunk in semantic_chunks:
            if chunk["id"] not in seen_ids:
                seen_ids.add(chunk["id"])
                chunk["source"] = "semantic_search"
                combined_chunks.append(chunk)
                doc_id = chunk["document_id"]
                chunks_per_document[doc_id] = chunks_per_document.get(doc_id, 0) + 1

        # Add document expansion results with diversity
        # Ensure we get multiple chunks from each document
        for chunk in document_chunks:
            if chunk["id"] not in seen_ids:
                doc_id = chunk["document_id"]
                current_count = chunks_per_document.get(doc_id, 0)

                # Allow up to 3 chunks per document to ensure diversity
                if current_count < 3:
                    seen_ids.add(chunk["id"])
                    combined_chunks.append(chunk)
                    chunks_per_document[doc_id] = current_count + 1

        # Sort by distance (semantic similarity)
        combined_chunks.sort(key=lambda x: x["distance"])

        # Apply max limit
        final_chunks = combined_chunks[:max_chunks]

        logger.info(f"Returning {len(final_chunks)} chunks after document expansion and deduplication")
        logger.info(f"Chunks per document: {chunks_per_document}")

        return {
            "query": query,
            "total_results": len(final_chunks),
            "semantic_count": len(semantic_chunks),
            "entity_count": len(entity_matched_chunks),
            "document_expansion": True,
            "matched_documents": entity_document_ids,
            "chunks": final_chunks
        }
