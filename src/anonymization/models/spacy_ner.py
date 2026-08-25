import spacy
from loguru import logger

from ..models.types import Document, Entity, EntityType, ModelBackend, PipelineConfig


class SpacyNER:
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.nlp = None
        self._label_map = {
            "PERSON": EntityType.PERSON,
            "ORG": EntityType.ORGANIZATION,
            "GPE": EntityType.LOCATION,
            "LOC": EntityType.LOCATION,
            "DATE": EntityType.DATE,
            "TIME": EntityType.DATE,
            "MONEY": EntityType.CUSTOM,
            "PERCENT": EntityType.CUSTOM,
            "CARDINAL": EntityType.CUSTOM,
            "ORDINAL": EntityType.CUSTOM,
            "NORP": EntityType.ORGANIZATION,
            "FAC": EntityType.LOCATION,
            "PRODUCT": EntityType.CUSTOM,
            "EVENT": EntityType.CUSTOM,
            "WORK_OF_ART": EntityType.CUSTOM,
            "LAW": EntityType.CUSTOM,
            "LANGUAGE": EntityType.CUSTOM,
        }
        self._load_model()

    def _load_model(self) -> None:
        logger.info(f"Loading SpaCy model: {self.config.spacy_model}")
        try:
            self.nlp = spacy.load(self.config.spacy_model)
        except OSError:
            logger.warning(f"Model {self.config.spacy_model} not found. Downloading...")
            spacy.cli.download(self.config.spacy_model)
            self.nlp = spacy.load(self.config.spacy_model)

    def _map_label(self, label: str) -> EntityType:
        return self._label_map.get(label.upper(), EntityType.CUSTOM)

    def predict(self, text: str) -> list[Entity]:
        if not self.nlp:
            raise RuntimeError("Model not loaded")

        doc = self.nlp(text)
        entities = []

        for ent in doc.ents:
            entity_type = self._map_label(ent.label_)
            entities.append(
                Entity(
                    text=ent.text,
                    label=entity_type,
                    start=ent.start_char,
                    end=ent.end_char,
                    score=1.0,
                    model_backend=ModelBackend.SPACY,
                )
            )

        return entities

    def predict_batch(self, texts: list[str]) -> list[list[Entity]]:
        if not self.nlp:
            raise RuntimeError("Model not loaded")

        docs = list(self.nlp.pipe(texts, batch_size=self.config.batch_size))
        batch_entities = []

        for doc in docs:
            entities = []
            for ent in doc.ents:
                entity_type = self._map_label(ent.label_)
                entities.append(
                    Entity(
                        text=ent.text,
                        label=entity_type,
                        start=ent.start_char,
                        end=ent.end_char,
                        score=1.0,
                        model_backend=ModelBackend.SPACY,
                    )
                )
            batch_entities.append(entities)

        return batch_entities

    def process_document(self, doc: Document) -> Document:
        entities = self.predict(doc.text)
        doc.entities = entities
        return doc