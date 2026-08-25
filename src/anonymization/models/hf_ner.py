import torch
from loguru import logger
from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline

from ..models.types import Document, Entity, EntityType, ModelBackend, PipelineConfig


CONLL_LABEL_MAP = {
    "LABEL_0": EntityType.CUSTOM,   # O
    "LABEL_1": EntityType.PERSON,   # B-PER
    "LABEL_2": EntityType.PERSON,   # I-PER
    "LABEL_3": EntityType.ORGANIZATION,   # B-ORG
    "LABEL_4": EntityType.ORGANIZATION,   # I-ORG
    "LABEL_5": EntityType.LOCATION,   # B-LOC
    "LABEL_6": EntityType.LOCATION,   # I-LOC
    "LABEL_7": EntityType.CUSTOM,   # B-MISC
    "LABEL_8": EntityType.CUSTOM,   # I-MISC
}

DEFAULT_MAX_LENGTH = 512
DEFAULT_STRIDE = 128


class HFTransformersNER:
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.device = self._resolve_device()
        self.tokenizer = None
        self.model = None
        self.ner_pipeline = None
        self._label_map = {
            "PER": EntityType.PERSON,
            "PERSON": EntityType.PERSON,
            "ORG": EntityType.ORGANIZATION,
            "LOC": EntityType.LOCATION,
            "GPE": EntityType.LOCATION,
            "DATE": EntityType.DATE,
            "MISC": EntityType.CUSTOM,
        }
        self._use_conll_mapping = False
        self._max_length = getattr(config, "max_length", None) or DEFAULT_MAX_LENGTH
        self._stride = getattr(config, "stride", None) or DEFAULT_STRIDE
        self._load_model()

    def _resolve_device(self) -> str:
        if self.config.device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            if torch.backends.mps.is_available():
                return "mps"
            return "cpu"
        return self.config.device

    def _load_model(self) -> None:
        logger.info(f"Loading HF model: {self.config.model_name} on {self.device}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(
            self.config.model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
        ).to(self.device)

        model_max_length = getattr(self.model.config, "max_position_embeddings", None)
        if model_max_length:
            self._max_length = min(self._max_length, model_max_length)

        self.ner_pipeline = pipeline(
            "ner",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0 if self.device == "cuda" else -1,
            aggregation_strategy="simple",
            batch_size=self.config.batch_size,
        )

        self._detect_label_scheme()

    def _detect_label_scheme(self) -> None:
        if hasattr(self.model.config, "id2label"):
            labels = list(self.model.config.id2label.values())
            if labels and labels[0].startswith("LABEL_"):
                self._use_conll_mapping = True
                logger.info("Detected CoNLL label scheme (LABEL_0, LABEL_1, ...)")

    def _map_label(self, label: str) -> EntityType:
        label_upper = label.upper()

        if self._use_conll_mapping and label_upper in CONLL_LABEL_MAP:
            return CONLL_LABEL_MAP[label_upper]

        for key, entity_type in self._label_map.items():
            if key in label_upper:
                return entity_type
        return EntityType.CUSTOM

    def _chunk_text(self, text: str) -> list[tuple[str, int]]:
        """Split text into overlapping chunks that fit model max length."""
        if not self.tokenizer:
            return [(text, 0)]

        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        if len(tokens) <= self._max_length:
            return [(text, 0)]

        chunks = []
        for i in range(0, len(tokens), self._max_length - self._stride):
            chunk_tokens = tokens[i:i + self._max_length]
            chunk_text = self.tokenizer.decode(chunk_tokens, skip_special_tokens=True)
            chunks.append((chunk_text, i))
            if i + self._max_length >= len(tokens):
                break

        return chunks

    def predict(self, text: str) -> list[Entity]:
        if not self.ner_pipeline:
            raise RuntimeError("Model not loaded")

        chunks = self._chunk_text(text)
        all_entities = []
        char_offset = 0

        for chunk_text, token_offset in chunks:
            try:
                results = self.ner_pipeline(chunk_text)
            except Exception as e:
                logger.warning(f"Failed to process chunk: {e}")
                continue

            for r in results:
                if r["score"] < self.config.confidence_threshold:
                    continue

                entity_type = self._map_label(r["entity_group"])
                start = r["start"] + char_offset
                end = r["end"] + char_offset

                all_entities.append(
                    Entity(
                        text=r["word"],
                        label=entity_type,
                        start=start,
                        end=end,
                        score=r["score"],
                        model_backend=ModelBackend.HF_TRANSFORMERS,
                    )
                )

            char_offset += len(chunk_text)

        return all_entities

    def predict_batch(self, texts: list[str]) -> list[list[Entity]]:
        return [self.predict(text) for text in texts]

    def process_document(self, doc: Document) -> Document:
        entities = self.predict(doc.text)
        doc.entities = entities
        return doc