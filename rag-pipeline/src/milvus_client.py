from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MilvusClient:
    def __init__(self, host: str = "localhost", port: str = "19530"):
        self.host = host
        self.port = port
        self.collection_name = "document_chunks"
        self.collection = None

    def connect(self):
        """Connect to Milvus server"""
        try:
            connections.connect("default", host=self.host, port=self.port)
            logger.info(f"Connected to Milvus at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            raise

    def create_collection(self, embedding_dim: int = 384):
        """Create collection with schema for document chunks"""
        if utility.has_collection(self.collection_name):
            logger.info(f"Collection {self.collection_name} already exists")
            self.collection = Collection(self.collection_name)
            return

        # Define schema
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="document_id", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="file_hash", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="page_number", dtype=DataType.INT64),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=embedding_dim),
            # Entity lists stored as JSON strings
            FieldSchema(name="person_names", dtype=DataType.VARCHAR, max_length=5000),
            FieldSchema(name="location_names", dtype=DataType.VARCHAR, max_length=5000),
            FieldSchema(name="organization_names", dtype=DataType.VARCHAR, max_length=5000),
            FieldSchema(name="date_entities", dtype=DataType.VARCHAR, max_length=5000),
            FieldSchema(name="other_entities", dtype=DataType.VARCHAR, max_length=5000),
        ]

        schema = CollectionSchema(fields=fields, description="Document chunks with embeddings and entities")
        self.collection = Collection(name=self.collection_name, schema=schema)

        # Create index for vector search
        index_params = {
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }
        self.collection.create_index(field_name="embedding", index_params=index_params)
        logger.info(f"Created collection {self.collection_name}")

    def document_exists(self, document_id: str = None, file_hash: str = None) -> bool:
        """Check if document already exists by document_id or file_hash"""
        if not self.collection:
            raise Exception("Collection not initialized")

        try:
            self.collection.load()

            if file_hash:
                expr = f'file_hash == "{file_hash}"'
            elif document_id:
                expr = f'document_id == "{document_id}"'
            else:
                return False

            results = self.collection.query(expr=expr, output_fields=["document_id"], limit=1)
            return len(results) > 0
        except Exception as e:
            logger.warning(f"Error checking document existence: {e}")
            return False

    def insert_chunks(self, chunks: List[Dict[str, Any]]):
        """Insert document chunks into Milvus"""
        if not self.collection:
            raise Exception("Collection not initialized")

        # Prepare data for insertion
        data = [
            [chunk["document_id"] for chunk in chunks],
            [chunk["file_hash"] for chunk in chunks],
            [chunk["page_number"] for chunk in chunks],
            [chunk["text"] for chunk in chunks],
            [chunk["embedding"] for chunk in chunks],
            [chunk["person_names"] for chunk in chunks],
            [chunk["location_names"] for chunk in chunks],
            [chunk["organization_names"] for chunk in chunks],
            [chunk["date_entities"] for chunk in chunks],
            [chunk["other_entities"] for chunk in chunks],
        ]

        self.collection.insert(data)
        self.collection.flush()
        logger.info(f"Inserted {len(chunks)} chunks into Milvus")

    def load_collection(self):
        """Load collection into memory for search"""
        if self.collection:
            self.collection.load()
            logger.info(f"Loaded collection {self.collection_name}")

    def search(self, query_embedding: List[float], top_k: int = 5):
        """Search for similar chunks"""
        if not self.collection:
            raise Exception("Collection not initialized")

        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            output_fields=["document_id", "page_number", "text", "person_names",
                          "location_names", "organization_names", "date_entities", "other_entities"]
        )
        return results

    def search_with_filter(self, query_embedding: List[float], filter_expr: str, top_k: int = 5):
        """Search for similar chunks with metadata filter"""
        if not self.collection:
            raise Exception("Collection not initialized")

        self.collection.load()

        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            expr=filter_expr,
            limit=top_k,
            output_fields=["document_id", "page_number", "text", "person_names",
                          "location_names", "organization_names", "date_entities", "other_entities"]
        )
        return results
