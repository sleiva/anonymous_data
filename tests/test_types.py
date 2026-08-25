import pytest
from anonymization.models.types import (
    Entity,
    EntityType,
    AnonymizationStrategy,
    ModelBackend,
    AnonymizationConfig,
    PipelineConfig,
    Document,
    ProcessingResult,
)


class TestEntity:
    def test_entity_creation(self):
        entity = Entity(
            text="John Smith",
            label=EntityType.PERSON,
            start=0,
            end=10,
            score=0.95,
            model_backend=ModelBackend.HF_TRANSFORMERS,
        )
        assert entity.text == "John Smith"
        assert entity.label == EntityType.PERSON
        assert entity.score == 0.95

    def test_entity_score_validation(self):
        with pytest.raises(ValueError):
            Entity(
                text="test",
                label=EntityType.PERSON,
                start=0,
                end=4,
                score=1.5,
                model_backend=ModelBackend.HF_TRANSFORMERS,
            )

        with pytest.raises(ValueError):
            Entity(
                text="test",
                label=EntityType.PERSON,
                start=0,
                end=4,
                score=-0.1,
                model_backend=ModelBackend.HF_TRANSFORMERS,
            )


class TestAnonymizationConfig:
    def test_default_config(self):
        config = AnonymizationConfig()
        assert config.strategy == AnonymizationStrategy.MASK
        assert config.mask_char == "*"
        assert config.preserve_length is True

    def test_custom_config(self):
        config = AnonymizationConfig(
            strategy=AnonymizationStrategy.REPLACE,
            mask_char="#",
            preserve_length=False,
            custom_replacements={EntityType.EMAIL: "[EMAIL]"},
        )
        assert config.strategy == AnonymizationStrategy.REPLACE
        assert config.mask_char == "#"
        assert config.preserve_length is False


class TestPipelineConfig:
    def test_default_config(self):
        config = PipelineConfig()
        assert config.model_backend == ModelBackend.HF_TRANSFORMERS
        assert config.model_name == "dslim/bert-base-NER"
        assert config.confidence_threshold == 0.7
        assert config.device == "auto"

    def test_spacy_config(self):
        config = PipelineConfig(
            model_backend=ModelBackend.SPACY,
            spacy_model="en_core_web_trf",
        )
        assert config.model_backend == ModelBackend.SPACY
        assert config.spacy_model == "en_core_web_trf"


class TestDocument:
    def test_document_creation(self):
        doc = Document(id="test-1", text="Hello world")
        assert doc.id == "test-1"
        assert doc.text == "Hello world"
        assert doc.entities == []
        assert doc.anonymized_text is None

    def test_document_with_entities(self):
        entity = Entity(
            text="John",
            label=EntityType.PERSON,
            start=0,
            end=4,
            score=0.9,
            model_backend=ModelBackend.HF_TRANSFORMERS,
        )
        doc = Document(id="test-1", text="John Smith", entities=[entity])
        assert len(doc.entities) == 1
        assert doc.entities[0].text == "John"