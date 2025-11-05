import spacy
from typing import Dict, List
import logging
import json
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EntityExtractor:
    # Generic legal/business terms to exclude from entity extraction
    EXCLUDED_ENTITIES = {
        "buyer", "seller", "purchaser", "vendor", "lessor", "lessee",
        "landlord", "tenant", "borrower", "lender", "party", "parties",
        "assignor", "assignee", "grantor", "grantee", "owner", "operator",
        "manager", "agent", "representative", "client", "customer",
        "llc", "inc", "corp", "ltd", "lp", "company", "corporation",
        "entity", "individual", "person", "organization"
    }

    def __init__(self, model_name: str = "en_core_web_lg"):
        """Initialize spaCy NLP model"""
        try:
            self.nlp = spacy.load(model_name)
            logger.info(f"Loaded spaCy model: {model_name}")
        except OSError:
            logger.error(f"Model {model_name} not found. Please download it using: python -m spacy download {model_name}")
            raise

    def extract_entities(self, text: str) -> Dict[str, str]:
        """
        Extract named entities from text and return as lists of strings stored as JSON strings.
        All entities are normalized to lowercase for case-insensitive matching.

        Entity types:
        - PERSON: People, including fictional
        - GPE: Geopolitical entities (countries, cities, states)
        - LOC: Non-GPE locations (mountain ranges, bodies of water)
        - ORG: Companies, agencies, institutions
        - DATE: Absolute or relative dates or periods
        - FILE_NUMBER: Custom extraction for file/case numbers (e.g., 1002-361178-RTT)
        """
        # First, extract custom file numbers using regex (before spaCy processing)
        file_numbers = self._extract_file_numbers(text)

        doc = self.nlp(text)

        # Initialize entity lists
        person_names = []
        location_names = []
        organization_names = []
        date_entities = []
        other_entities = []

        # Extract entities FIRST, then normalize to lowercase
        for ent in doc.ents:
            entity_text_original = ent.text.strip()
            entity_text = entity_text_original.lower()  # Convert to lowercase AFTER extraction

            # Skip generic legal/business terms
            if entity_text in self.EXCLUDED_ENTITIES:
                continue

            # Skip single-word generic terms that are too short (less than 3 chars)
            if len(entity_text) < 3:
                continue

            if ent.label_ == "PERSON":
                person_names.append(entity_text)
            elif ent.label_ in ["GPE", "LOC"]:
                location_names.append(entity_text)
            elif ent.label_ == "ORG":
                organization_names.append(entity_text)
            elif ent.label_ == "DATE":
                date_entities.append(entity_text)
            else:
                # Other entity types like MONEY, PERCENT, etc.
                other_entities.append(f"{ent.label_}:{entity_text}")

        # Remove duplicates while preserving order
        person_names = list(dict.fromkeys(person_names))
        location_names = list(dict.fromkeys(location_names))
        organization_names = list(dict.fromkeys(organization_names))
        date_entities = list(dict.fromkeys(date_entities))
        other_entities = list(dict.fromkeys(other_entities))

        # Convert lists to JSON strings for storage
        return {
            "person_names": json.dumps(person_names),
            "location_names": json.dumps(location_names),
            "organization_names": json.dumps(organization_names),
            "date_entities": json.dumps(date_entities),
            "file_numbers": json.dumps(file_numbers),
            "other_entities": json.dumps(other_entities)
        }

    def _extract_file_numbers(self, text: str) -> List[str]:
        """
        Extract file/case numbers using regex patterns.

        Common patterns:
        - 1002-361178-RTT (Republic Title format)
        - NCS-1150719-ATL (First American format)
        - Similar numeric-dash patterns

        Returns:
            List of normalized file numbers (lowercase)
        """
        file_numbers = []

        # Pattern: 3-4 digits, dash, 5-7 digits, dash, 2-4 uppercase letters
        # Examples: 1002-361178-RTT, NCS-1150719-ATL
        pattern = r'\b[A-Z0-9]{3,4}-\d{5,7}-[A-Z]{2,4}\b'

        matches = re.findall(pattern, text)

        # Normalize to lowercase and remove duplicates
        file_numbers = list(dict.fromkeys([m.lower() for m in matches]))

        return file_numbers

    @staticmethod
    def parse_entities(entity_json: str) -> List[str]:
        """Parse JSON string back to list"""
        try:
            return json.loads(entity_json)
        except:
            return []
