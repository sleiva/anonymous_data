import hashlib

from loguru import logger

from ..models.types import AnonymizationConfig, AnonymizationStrategy, Document, Entity, EntityType


class Anonymizer:
    def __init__(self, config: AnonymizationConfig):
        self.config = config
        self._replacement_counters: dict[EntityType, int] = {}

    def _get_mask(self, length: int) -> str:
        if self.config.preserve_length:
            return self.config.mask_char * length
        return self.config.mask_char * 8

    def _get_replacement(self, entity: Entity) -> str:
        if entity.label in self.config.custom_replacements:
            return self.config.custom_replacements[entity.label]

        counter = self._replacement_counters.get(entity.label, 0) + 1
        self._replacement_counters[entity.label] = counter
        return f"[{entity.label.value}_{counter}]"

    def _get_hash(self, text: str) -> str:
        salt = self.config.hash_salt or ""
        return hashlib.sha256(f"{salt}{text}".encode()).hexdigest()[:12]

    def anonymize(self, doc: Document) -> Document:
        if not doc.entities:
            logger.warning(f"Document {doc.id} has no entities to anonymize")
            doc.anonymized_text = doc.text
            return doc

        sorted_entities = sorted(doc.entities, key=lambda e: e.start, reverse=True)
        text = doc.text

        for entity in sorted_entities:
            start, end = entity.start, entity.end
            original = text[start:end]

            if self.config.strategy == AnonymizationStrategy.MASK:
                replacement = self._get_mask(len(original))
            elif self.config.strategy == AnonymizationStrategy.REPLACE:
                replacement = self._get_replacement(entity)
            elif self.config.strategy == AnonymizationStrategy.HASH:
                replacement = self._get_hash(original)
            elif self.config.strategy == AnonymizationStrategy.REDACT:
                replacement = f"[REDACTED_{entity.label.value}]"
            elif self.config.strategy == AnonymizationStrategy.PSEUDONYMIZE:
                replacement = self._get_replacement(entity)
            else:
                replacement = self._get_mask(len(original))

            text = text[:start] + replacement + text[end:]

        doc.anonymized_text = text
        return doc

    def anonymize_batch(self, docs: list[Document]) -> list[Document]:
        return [self.anonymize(doc) for doc in docs]


def create_anonymizer(config: AnonymizationConfig | None = None) -> Anonymizer:
    return Anonymizer(config or AnonymizationConfig())