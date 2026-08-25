import pytest
from unittest.mock import Mock, patch
from anonymization.pipelines import AnonymizationPipeline
from anonymization.models.types import (
    Document,
    PipelineConfig,
    ModelBackend,
    AnonymizationStrategy,
    AnonymizationConfig,
)


class TestAnonymizationPipeline:
    def setup_method(self):
        self.config = PipelineConfig(
            model_backend=ModelBackend.HF_TRANSFORMERS,
            model_name="dslim/bert-base-NER",
            anonymization=AnonymizationConfig(strategy=AnonymizationStrategy.MASK),
        )

    @patch("anonymization.pipelines.langgraph_pipeline.HFTransformersNER")
    def test_pipeline_initialization(self, mock_hf_ner):
        pipeline = AnonymizationPipeline(self.config)
        assert pipeline.config == self.config
        assert pipeline.graph is not None

    @patch("anonymization.pipelines.langgraph_pipeline.HFTransformersNER")
    def test_pipeline_run_empty_documents(self, mock_hf_ner):
        pipeline = AnonymizationPipeline(self.config)
        with pytest.raises(RuntimeError, match="No documents to process"):
            pipeline.run([])

    @patch("anonymization.pipelines.langgraph_pipeline.HFTransformersNER")
    def test_pipeline_run_with_documents(self, mock_hf_ner_class):
        mock_ner = Mock()
        mock_hf_ner_class.return_value = mock_ner

        def mock_process(doc):
            doc.entities = [
                type("Entity", (), {
                    "text": "John",
                    "label": type("Label", (), {"value": "PERSON"})(),
                    "start": 0,
                    "end": 4,
                    "score": 0.9,
                    "model_backend": ModelBackend.HF_TRANSFORMERS,
                })()
            ]
            return doc

        mock_ner.process_document.side_effect = mock_process

        pipeline = AnonymizationPipeline(self.config)
        docs = [Document(id="test-1", text="John Smith")]
        results = pipeline.run(docs)

        assert len(results) == 1
        assert results[0].document.id == "test-1"
        assert results[0].entities_found == 1
        assert results[0].backend_used == ModelBackend.HF_TRANSFORMERS

    @patch("anonymization.pipelines.langgraph_pipeline.HFTransformersNER")
    def test_pipeline_with_spacy_backend(self, mock_hf_ner):
        spacy_config = PipelineConfig(
            model_backend=ModelBackend.SPACY,
            spacy_model="en_core_web_trf",
        )

        with patch("anonymization.pipelines.langgraph_pipeline.SpacyNER") as mock_spacy_ner:
            mock_ner = Mock()
            mock_spacy_ner.return_value = mock_ner

            def mock_process(doc):
                doc.entities = []
                return doc

            mock_ner.process_document.side_effect = mock_process

            pipeline = AnonymizationPipeline(spacy_config)
            docs = [Document(id="test-1", text="Test")]
            results = pipeline.run(docs)

            assert len(results) == 1
            mock_spacy_ner.assert_called_once()

    def test_pipeline_config_override(self):
        pipeline = AnonymizationPipeline(self.config)
        override_config = PipelineConfig(
            model_backend=ModelBackend.SPACY,
            spacy_model="en_core_web_sm",
        )

        with patch("anonymization.pipelines.langgraph_pipeline.SpacyNER") as mock_spacy_ner:
            mock_ner = Mock()
            mock_spacy_ner.return_value = mock_ner
            mock_ner.process_document = lambda d: d

            docs = [Document(id="test-1", text="Test")]
            results = pipeline.run(docs, config=override_config)

            assert len(results) == 1