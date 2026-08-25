from enum import Enum

from pydantic import BaseModel, Field


class EntityType(str, Enum):
    PERSON = "PERSON"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    ADDRESS = "ADDRESS"
    ID_NUMBER = "ID_NUMBER"
    ORGANIZATION = "ORG"
    LOCATION = "LOC"
    DATE = "DATE"
    CREDIT_CARD = "CREDIT_CARD"
    IBAN = "IBAN"
    IP_ADDRESS = "IP_ADDRESS"
    URL = "URL"
    CUSTOM = "CUSTOM"


class AnonymizationStrategy(str, Enum):
    MASK = "mask"
    REPLACE = "replace"
    HASH = "hash"
    REDACT = "redact"
    PSEUDONYMIZE = "pseudonymize"


class ModelBackend(str, Enum):
    HF_TRANSFORMERS = "hf_transformers"
    SPACY = "spacy"


class Entity(BaseModel):
    text: str
    label: EntityType
    start: int
    end: int
    score: float = Field(ge=0.0, le=1.0)
    model_backend: ModelBackend


class AnonymizationConfig(BaseModel):
    strategy: AnonymizationStrategy = AnonymizationStrategy.MASK
    mask_char: str = "*"
    preserve_length: bool = True
    custom_replacements: dict[EntityType, str] = Field(default_factory=dict)
    hash_salt: str | None = None


class PipelineConfig(BaseModel):
    model_backend: ModelBackend = ModelBackend.HF_TRANSFORMERS
    model_name: str = "dslim/bert-base-NER"
    confidence_threshold: float = 0.7
    device: str = "auto"
    batch_size: int = 32
    anonymization: AnonymizationConfig = Field(default_factory=AnonymizationConfig)
    language: str = "en"
    spacy_model: str = "en_core_web_trf"


class Document(BaseModel):
    id: str
    text: str
    metadata: dict = Field(default_factory=dict)
    entities: list[Entity] = Field(default_factory=list)
    anonymized_text: str | None = None


class ProcessingResult(BaseModel):
    document: Document
    processing_time_ms: float
    entities_found: int
    backend_used: ModelBackend