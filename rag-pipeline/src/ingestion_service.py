from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import logging
import hashlib
import os
from .milvus_client import MilvusClient
from .document_loader import DocumentLoader
from .entity_extractor import EntityExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(
        self,
        milvus_host: str = "localhost",
        milvus_port: str = "19530",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """Initialize ingestion service with all components"""
        # Initialize embedding model
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()

        # Initialize Milvus client
        self.milvus_client = MilvusClient(host=milvus_host, port=milvus_port)
        self.milvus_client.connect()
        self.milvus_client.create_collection(embedding_dim=self.embedding_dim)

        # Initialize entity extractor
        self.entity_extractor = EntityExtractor()

        # Initialize document loader
        self.document_loader = DocumentLoader()

    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts"""
        embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def process_pages(self, pages: List[Dict[str, Any]], file_hash: str) -> List[Dict[str, Any]]:
        """Process pages: extract entities and generate embeddings"""
        processed_chunks = []

        logger.info(f"Processing {len(pages)} pages...")

        # Extract entities for each page
        for page in pages:
            entities = self.entity_extractor.extract_entities(page["text"])
            page.update(entities)

        # Generate embeddings in batch
        texts = [page["text"] for page in pages]
        embeddings = self.generate_embeddings(texts)

        # Combine everything
        for page, embedding in zip(pages, embeddings):
            processed_chunks.append({
                "document_id": page["document_id"],
                "file_hash": file_hash,
                "page_number": page["page_number"],
                "text": page["text"],
                "embedding": embedding,
                "person_names": page["person_names"],
                "location_names": page["location_names"],
                "organization_names": page["organization_names"],
                "date_entities": page["date_entities"],
                "other_entities": page["other_entities"]
            })

        logger.info(f"Processed {len(processed_chunks)} chunks")
        return processed_chunks

    def ingest_document(self, file_path: str) -> Dict[str, Any]:
        """Ingest a single document"""
        logger.info(f"Ingesting document: {file_path}")

        # Calculate file hash
        file_hash = self.calculate_file_hash(file_path)
        document_id = os.path.basename(file_path)

        # Check if document already exists
        if self.milvus_client.document_exists(file_hash=file_hash):
            logger.info(f"Document already exists (hash: {file_hash}), skipping: {file_path}")
            return {"status": "skipped", "reason": "already_exists", "file": file_path}

        # Load document pages
        pages = self.document_loader.load_document(file_path)

        if not pages:
            logger.warning(f"No pages found in document: {file_path}")
            return {"status": "skipped", "reason": "no_pages", "file": file_path}

        # Process pages
        chunks = self.process_pages(pages, file_hash)

        # Insert into Milvus
        self.milvus_client.insert_chunks(chunks)
        self.milvus_client.load_collection()

        logger.info(f"Successfully ingested {len(chunks)} chunks from {file_path}")
        return {"status": "success", "chunks": len(chunks), "file": file_path}

    def ingest_directory(self, directory_path: str, file_name: str = None) -> Dict[str, Any]:
        """Ingest all documents from a directory or specific file"""
        logger.info(f"Ingesting from directory: {directory_path}")

        results = {
            "ingested": [],
            "skipped": [],
            "failed": []
        }

        # Get list of files to process
        supported_extensions = {'.pdf', '.md', '.markdown', '.txt'}
        files_to_process = []

        if file_name:
            # Process specific file
            file_path = os.path.join(directory_path, file_name)
            if os.path.exists(file_path):
                files_to_process.append(file_path)
            else:
                logger.error(f"File not found: {file_path}")
                results["failed"].append({"file": file_name, "reason": "not_found"})
                return results
        else:
            # Process all files in directory
            for root, _, files in os.walk(directory_path):
                for file in files:
                    if os.path.splitext(file)[1].lower() in supported_extensions:
                        files_to_process.append(os.path.join(root, file))

        logger.info(f"Found {len(files_to_process)} files to process")

        # Process each file
        for file_path in files_to_process:
            try:
                result = self.ingest_document(file_path)
                if result["status"] == "success":
                    results["ingested"].append(result)
                elif result["status"] == "skipped":
                    results["skipped"].append(result)
            except Exception as e:
                logger.error(f"Failed to ingest {file_path}: {e}")
                results["failed"].append({"file": file_path, "reason": str(e)})

        logger.info(f"Ingestion complete. Ingested: {len(results['ingested'])}, "
                   f"Skipped: {len(results['skipped'])}, Failed: {len(results['failed'])}")
        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get ingestion statistics"""
        if self.milvus_client.collection:
            num_entities = self.milvus_client.collection.num_entities
            return {
                "total_chunks": num_entities,
                "embedding_dimension": self.embedding_dim,
                "collection_name": self.milvus_client.collection_name
            }
        return {}
