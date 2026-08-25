import pytest
from anonymization.models.types import (
    Document,
    Entity,
    EntityType,
    AnonymizationConfig,
    AnonymizationStrategy,
    ModelBackend,
)
from anonymization.utils.anonymizer import Anonymizer, create_anonymizer


class TestAnonymizer:
    def setup_method(self):
        self.doc = Document(
            id="test-1",
            text="John Smith lives at 123 Main St. Email: john@example.com",
            entities=[
                Entity(text="John Smith", label=EntityType.PERSON, start=0, end=10, score=0.95, model_backend=ModelBackend.HF_TRANSFORMERS),
                Entity(text="123 Main St", label=EntityType.ADDRESS, start=18, end=29, score=0.9, model_backend=ModelBackend.HF_TRANSFORMERS),
                Entity(text="john@example.com", label=EntityType.EMAIL, start=38, end=54, score=0.99, model_backend=ModelBackend.HF_TRANSFORMERS),
            ],
        )

    def test_mask_strategy(self):
        config = AnonymizationConfig(strategy=AnonymizationStrategy.MASK, preserve_length=True)
        anonymizer = Anonymizer(config)
        result = anonymizer.anonymize(self.doc)

        assert result.anonymized_text is not None
        assert "John Smith" not in result.anonymized_text
        assert "123 Main St" not in result.anonymized_text
        assert "john@example.com" not in result.anonymized_text
        assert "*" in result.anonymized_text

    def test_mask_strategy_preserve_length_false(self):
        config = AnonymizationConfig(strategy=AnonymizationStrategy.MASK, preserve_length=False)
        anonymizer = Anonymizer(config)
        result = anonymizer.anonymize(self.doc)

        assert "********" in result.anonymized_text

    def test_replace_strategy(self):
        config = AnonymizationConfig(strategy=AnonymizationStrategy.REPLACE)
        anonymizer = Anonymizer(config)
        result = anonymizer.anonymize(self.doc)

        assert "[PERSON_1]" in result.anonymized_text
        assert "[ADDRESS_1]" in result.anonymized_text
        assert "[EMAIL_1]" in result.anonymized_text

    def test_hash_strategy(self):
        config = AnonymizationConfig(strategy=AnonymizationStrategy.HASH, hash_salt="test-salt")
        anonymizer = Anonymizer(config)
        result = anonymizer.anonymize(self.doc)

        assert result.anonymized_text is not None
        assert "John Smith" not in result.anonymized_text

    def test_redact_strategy(self):
        config = AnonymizationConfig(strategy=AnonymizationStrategy.REDACT)
        anonymizer = Anonymizer(config)
        result = anonymizer.anonymize(self.doc)

        assert "[REDACTED_PERSON]" in result.anonymized_text
        assert "[REDACTED_ADDRESS]" in result.anonymized_text
        assert "[REDACTED_EMAIL]" in result.anonymized_text

    def test_pseudonymize_strategy(self):
        config = AnonymizationConfig(strategy=AnonymizationStrategy.PSEUDONYMIZE)
        anonymizer = Anonymizer(config)
        result = anonymizer.anonymize(self.doc)

        assert "[PERSON_1]" in result.anonymized_text

    def test_custom_replacements(self):
        config = AnonymizationConfig(
            strategy=AnonymizationStrategy.REPLACE,
            custom_replacements={EntityType.EMAIL: "[CONTACT]", EntityType.PERSON: "[NAME]"},
        )
        anonymizer = Anonymizer(config)
        result = anonymizer.anonymize(self.doc)

        assert "[CONTACT]" in result.anonymized_text
        assert "[NAME]" in result.anonymized_text

    def test_empty_entities(self):
        doc = Document(id="test-2", text="No entities here", entities=[])
        config = AnonymizationConfig()
        anonymizer = Anonymizer(config)
        result = anonymizer.anonymize(doc)

        assert result.anonymized_text == "No entities here"

    def test_batch_anonymize(self):
        config = AnonymizationConfig(strategy=AnonymizationStrategy.MASK)
        anonymizer = Anonymizer(config)
        docs = [self.doc, self.doc]
        results = anonymizer.anonymize_batch(docs)

        assert len(results) == 2
        assert all(r.anonymized_text is not None for r in results)

    def test_create_anonymizer_factory(self):
        anonymizer = create_anonymizer()
        assert isinstance(anonymizer, Anonymizer)

        config = AnonymizationConfig(strategy=AnonymizationStrategy.HASH)
        anonymizer = create_anonymizer(config)
        assert anonymizer.config.strategy == AnonymizationStrategy.HASH