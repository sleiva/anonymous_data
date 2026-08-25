from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from loguru import logger
from pydantic import BaseModel, Field

from ..models.hf_ner import HFTransformersNER
from ..models.spacy_ner import SpacyNER
from ..models.types import Document, ModelBackend, PipelineConfig, ProcessingResult
from ..utils.anonymizer import create_anonymizer
from ..utils.config import get_settings


class PipelineState(BaseModel):
    documents: list[Document] = Field(default_factory=list)
    current_doc_index: int = 0
    config: PipelineConfig | None = None
    results: list[ProcessingResult] = Field(default_factory=list)
    error: str | None = None


class AnonymizationPipeline:
    def __init__(self, config: PipelineConfig | None = None):
        self.config = config or PipelineConfig()
        self.settings = get_settings()
        self.hf_ner = None
        self.spacy_ner = None
        self.anonymizer = create_anonymizer(self.config.anonymization)
        self.graph = self._build_graph()

    def _get_ner_model(self, backend: ModelBackend):
        if backend == ModelBackend.HF_TRANSFORMERS:
            if not self.hf_ner:
                self.hf_ner = HFTransformersNER(self.config)
            return self.hf_ner
        if not self.spacy_ner:
            self.spacy_ner = SpacyNER(self.config)
        return self.spacy_ner

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(PipelineState)

        workflow.add_node("validate_input", self._validate_input)
        workflow.add_node("extract_entities", self._extract_entities)
        workflow.add_node("anonymize", self._anonymize)
        workflow.add_node("collect_results", self._collect_results)

        workflow.add_edge(START, "validate_input")
        workflow.add_edge("validate_input", "extract_entities")
        workflow.add_edge("extract_entities", "anonymize")
        workflow.add_edge("anonymize", "collect_results")
        workflow.add_edge("collect_results", END)

        return workflow.compile(checkpointer=MemorySaver())

    def _validate_input(self, state: PipelineState) -> PipelineState:
        if not state.documents:
            state.error = "No documents to process"
            return state

        if not state.config:
            state.config = self.config

        logger.info(f"Validated {len(state.documents)} documents for processing")
        return state

    def _extract_entities(self, state: PipelineState) -> PipelineState:
        if state.error:
            return state

        config = state.config or self.config
        ner_model = self._get_ner_model(config.model_backend)

        for i, doc in enumerate(state.documents):
            state.current_doc_index = i
            try:
                ner_model.process_document(doc)
                logger.debug(f"Doc {doc.id}: found {len(doc.entities)} entities")
            except Exception as e:
                logger.error(f"Error processing doc {doc.id}: {e}")
                state.error = str(e)
                break

        return state

    def _anonymize(self, state: PipelineState) -> PipelineState:
        if state.error:
            return state

        for doc in state.documents:
            try:
                self.anonymizer.anonymize(doc)
            except Exception as e:
                logger.error(f"Error anonymizing doc {doc.id}: {e}")
                state.error = str(e)
                break

        return state

    def _collect_results(self, state: PipelineState) -> PipelineState:
        if state.error:
            return state

        for doc in state.documents:
            result = ProcessingResult(
                document=doc,
                processing_time_ms=0.0,
                entities_found=len(doc.entities),
                backend_used=state.config.model_backend if state.config else self.config.model_backend,
            )
            state.results.append(result)

        logger.info(f"Pipeline completed. Processed {len(state.results)} documents")
        return state

    def run(self, documents: list[Document], config: PipelineConfig | None = None) -> list[ProcessingResult]:
        initial_state = PipelineState(documents=documents, config=config or self.config)
        thread_id = f"run-{id(documents)}"
        final_state = self.graph.invoke(initial_state, config={"configurable": {"thread_id": thread_id}})

        if final_state.get("error"):
            raise RuntimeError(f"Pipeline failed: {final_state['error']}")

        return final_state["results"]

    def run_stream(self, documents: list[Document], config: PipelineConfig | None = None):
        initial_state = PipelineState(documents=documents, config=config or self.config)
        thread_id = f"run-{id(documents)}"
        for chunk in self.graph.stream(initial_state, config={"configurable": {"thread_id": thread_id}}):
            yield chunk