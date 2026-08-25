# BERT-based Data Anonymization Experiments

Experiments for PII detection and anonymization using BERT models with LangGraph pipelines. Supports both Hugging Face Transformers and SpaCy backends.

## Features

- **Dual Backend Support**: HF Transformers + PyTorch and SpaCy transformers
- **LangGraph Pipelines**: Stateful, streaming, and checkpointable anonymization workflows
- **Multiple Strategies**: Mask, Replace, Hash, Redact, Pseudonymize
- **Configurable**: YAML/ENV configuration, custom entity types, confidence thresholds
- **Batch & Streaming**: Process single documents, batches, or stream results
- **Comparison Tools**: Built-in benchmarking between backends and models

## Quick Start

```bash
# Install dependencies (use uv for speed)
pip install uv
uv venv && uv pip install -e ".[dev]"

# Copy config
cp .env.example .env

# Download SpaCy transformer model
uv run python -m spacy download en_core_web_trf

# Run CLI - Single text
uv run python scripts/run_anonymization.py run "John Smith lives at 123 Main St. Email: john@example.com" --backend hf_transformers

# Process documents (PDF, DOCX, PPTX, XLSX) using anydoc
uv run python scripts/run_anonymization.py process-docs data/cv --output-file output/cv_anonymized.json --backend spacy
```

## Project Structure

```
anonymous_data/
├── src/anonymization/
│   ├── models/           # NER model implementations
│   │   ├── types.py      # Pydantic models
│   │   ├── hf_ner.py     # Hugging Face Transformers BERT
│   │   └── spacy_ner.py  # SpaCy transformer pipeline
│   ├── pipelines/        # LangGraph pipelines
│   │   └── langgraph_pipeline.py
│   └── utils/            # Utilities
│       ├── anonymizer.py # Anonymization strategies
│       └── config.py     # Settings management
├── scripts/              # CLI entry points
├── notebooks/            # Jupyter experiments
├── tests/                # Unit tests
├── config/               # Configuration files
└── data/                 # Data directories
```

## Usage Examples

### Python API

```python
from anonymization import (
    AnonymizationPipeline,
    PipelineConfig,
    Document,
    ModelBackend,
    AnonymizationStrategy,
)

# HF Transformers pipeline
config = PipelineConfig(
    model_backend=ModelBackend.HF_TRANSFORMERS,
    model_name="dslim/bert-base-NER",
    confidence_threshold=0.7,
    anonymization=AnonymizationConfig(strategy=AnonymizationStrategy.MASK),
)

pipeline = AnonymizationPipeline(config)
docs = [Document(id="1", text="John Smith (john@email.com) works at Google.")]
results = pipeline.run(docs)

for r in results:
    print(r.document.anonymized_text)
    # Output: ********** (****@*******.***) works at *****.
```

### SpaCy Backend

```python
config = PipelineConfig(
    model_backend=ModelBackend.SPACY,
    spacy_model="en_core_web_trf",
    anonymization=AnonymizationConfig(strategy=AnonymizationStrategy.REPLACE),
)
```

### Streaming Results

```python
for chunk in pipeline.run_stream(docs):
    for node_name, state in chunk.items():
        if node_name == "collect_results":
            for r in state["results"]:
                print(f"Processed: {r.document.id}")
```

### CLI

```bash
# Single text
python scripts/run_anonymization.py "John Doe at john@company.com" --backend hf_transformers

# Batch processing
python scripts/run_anonymization.py batch input.csv --text-column text --output output.json

# Compare backends
python scripts/run_anonymization.py compare "John Smith at Google" --hf-model dslim/bert-base-NER --spacy-model en_core_web_trf
```

## Anonymization Strategies

| Strategy | Description | Example |
|----------|-------------|---------|
| `MASK` | Replace with mask character | `John Smith` → `**********` |
| `REPLACE` | Replace with typed placeholder | `John Smith` → `[PERSON_1]` |
| `HASH` | Replace with salted hash | `John Smith` → `a1b2c3d4e5f6` |
| `REDACT` | Replace with redaction marker | `John Smith` → `[REDACTED_PERSON]` |
| `PSEUDONYMIZE` | Consistent replacement per entity | `John Smith` → `[PERSON_1]` |

## Configuration

Environment variables (`.env`):

```env
HF_TOKEN=your_huggingface_token
DEFAULT_DEVICE=auto
LOG_LEVEL=INFO
DATA_DIR=data
OUTPUT_DIR=output
```

Pipeline config options:

```python
PipelineConfig(
    model_backend=ModelBackend.HF_TRANSFORMERS,  # or SPACY
    model_name="dslim/bert-base-NER",            # HF model
    spacy_model="en_core_web_trf",               # SpaCy model
    confidence_threshold=0.7,
    device="auto",                                # auto, cpu, cuda, mps
    batch_size=32,
    language="en",
    anonymization=AnonymizationConfig(...),
)
```

## Supported Entity Types

- `PERSON` - Person names
- `ORG` - Organizations
- `LOC` / `GPE` - Locations
- `DATE` - Dates
- `EMAIL` - Email addresses
- `PHONE` - Phone numbers
- `ADDRESS` - Physical addresses
- `ID_NUMBER` - ID numbers (DNI, SSN, etc.)
- `CREDIT_CARD` - Credit card numbers
- `IBAN` - Bank account numbers
- `IP_ADDRESS` - IP addresses
- `URL` - URLs
- `CUSTOM` - Other entities

## Models Tested

### HF Transformers (English)
- `dslim/bert-base-NER` (default)
- `dbmdz/bert-large-cased-finetuned-conll03-english`
- `Jean-Baptiste/roberta-large-ner-english`
- `xlm-roberta-large-finetuned-conll03-english` (multilingual)

### HF Transformers (Spanish)
- `mrm8488/bert-spanish-cased-finetuned-ner` - **Best Spanish NER**, groups entities correctly
- `dccuchile/bert-base-spanish-wwm-cased-finetuned-ner` - BETO with NER head (CoNLL labels)
- `dccuchile/bertin-roberta-base-spanish-finetuned-ner` - BERTin with NER head (CoNLL labels)

### New Generation (2024-2025) - Base models, need fine-tuning for NER
- `answerdotai/ModernBERT-base` / `ModernBERT-large` - 8k context, RoPE, 2T tokens
- `neulab/NeoBERT` - Fast long-context (4k), MTEB optimized

### SpaCy
- `en_core_web_sm` - Small CNN
- `en_core_web_md` - Medium CNN + vectors
- `en_core_web_lg` - Large CNN + vectors
- `en_core_web_trf` - Transformer (RoBERTa) - **best accuracy**

## Running Tests

```bash
pytest tests/ -v
```

## Document Processing (PDF, DOCX, PPTX, XLSX)

Using **anydoc** (Firecrawl) for fast document-to-Markdown conversion:

```python
from anonymization.utils import load_documents_from_dir_any, load_documents_from_pdf, load_documents_from_any

# Load all documents from directory (any supported format)
docs = load_documents_from_dir_any("data/cv")

# Or single file
docs = load_documents_from_pdf("document.pdf")
docs = load_documents_from_any("document.docx")

# Then anonymize
pipeline = AnonymizationPipeline(config)
results = pipeline.run(docs)
```

CLI:
```bash
# Process all documents in directory
uv run python scripts/run_anonymization.py process-docs data/cv --output-file output/anonymized.json

# With specific pattern and backend
uv run python scripts/run_anonymization.py process-docs data/cv --pattern "*.pdf" --backend spacy
```

## Extending

### Custom Entity Types

```python
from anonymization.models.types import EntityType

# Add to EntityType enum or use EntityType.CUSTOM with custom_replacements
config = PipelineConfig(
    anonymization=AnonymizationConfig(
        custom_replacements={EntityType.CUSTOM: "[CUSTOM]"}
    )
)
```

### Custom Pipeline Nodes

```python
from anonymization.pipelines import AnonymizationPipeline

class CustomPipeline(AnonymizationPipeline):
    def _build_graph(self):
        # Add custom nodes before/after existing ones
        workflow = super()._build_graph()
        return workflow
```

## License

MIT