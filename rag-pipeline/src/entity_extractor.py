import spacy
from typing import Dict, List
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EntityExtractor:
    def __init__(self, model_name: str = "en_core_web_md"):
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
        """
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
            "other_entities": json.dumps(other_entities)
        }

    @staticmethod
    def parse_entities(entity_json: str) -> List[str]:
        """Parse JSON string back to list"""
        try:
            return json.loads(entity_json)
        except:
            return []
