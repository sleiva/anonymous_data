#!/usr/bin/env python
"""Benchmark script for comparing NER models for anonymization."""

import json
import time
import statistics
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from pathlib import Path

from anonymization import (
    AnonymizationPipeline,
    PipelineConfig,
    Document,
    ModelBackend,
    AnonymizationStrategy,
    AnonymizationConfig,
    HFTransformersNER,
    SpacyNER,
)
from anonymization.utils import load_documents_from_dir_any


@dataclass
class BenchmarkResult:
    model_name: str
    backend: str
    doc_id: str
    doc_length: int
    entities_found: int
    entity_types: Dict[str, int]
    processing_time_ms: float
    anonymized_length: int
    sample_entities: List[Dict[str, Any]]


class OllamaNER:
    """Ollama-based NER using LangChain for structured extraction."""

    def __init__(self, model_name: str = "qwen3.8:27b-mlx", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self._llm = None
        self._chain = None
        self._setup()

    def _setup(self):
        from langchain_ollama import ChatOllama
        from langchain_core.prompts import ChatPromptTemplate
        import re
        import json

        self._llm = ChatOllama(
            model=self.model_name,
            base_url=self.base_url,
            temperature=0,
            # Don't use format="json" - let the model return raw text and we parse it
            num_predict=4096,
        )

        system_prompt = """You are an expert Named Entity Recognition (NER) system specialized in identifying Personally Identifiable Information (PII) in multilingual documents (Spanish, Italian, German, English).

Your task: Extract ALL PII entities from the given text and return them as a JSON array.

ENTITY TYPES (use exactly these labels):
- PERSON: Full person names (first + last), e.g., "Juan Pérez", "María García"
- ORG: Organizations, companies, institutions, e.g., "Google", "Microsoft España", "SANTANDER DIGITAL ASSETS"
- LOC: Locations, cities, countries, addresses, e.g., "Madrid", "Barcelona", "Palo Alto", "Italia"
- DATE: Dates, date ranges, temporal expressions, e.g., "15/03/1985", "Febrero 2022", "Mar 24 – Jul 24", "Ene 2020 – Dic 2020"
- EMAIL: Email addresses, e.g., "juan@empresa.es", "maria.garcia@google.com"
- PHONE: Phone numbers, e.g., "+34 91 123 45 67", "+1-555-123-4567"
- ADDRESS: Full street addresses, e.g., "123 Main Street, New York"
- ID_NUMBER: National ID numbers (DNI, NIE, SSN), e.g., "12345678Z", "X1234567L"
- CREDIT_CARD: Credit card numbers
- IBAN: Bank account numbers (IBAN), e.g., "ES9121000418450200051332"
- IP_ADDRESS: IP addresses
- URL: URLs
- CUSTOM: Any other entity not fitting above categories

RULES:
1. Return ONLY a valid JSON array - no explanations, no markdown, no extra text
2. Each entity object must have: "text" (exact substring), "label" (from list above), "start" (character index), "end" (character index), "score" (confidence 0.0-1.0)
3. For multi-word entities, include the COMPLETE phrase as one entity (e.g., "Juan Pérez" not separate "Juan" and "Pérez")
4. For date ranges, include the full range as one DATE entity
5. Character indices must match the original text exactly
6. Score should reflect confidence: 0.9+ for clear entities, 0.7-0.9 for probable, 0.5-0.7 for uncertain
7. If no entities found, return empty array []

Example output format:
[
  {{"text": "Juan Pérez", "label": "PERSON", "start": 0, "end": 10, "score": 0.99}},
  {{"text": "Madrid", "label": "LOC", "start": 18, "end": 24, "score": 1.0}},
  {{"text": "juan@empresa.es", "label": "EMAIL", "start": 38, "end": 53, "score": 1.0}}
]"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Text: {text}\n\nReturn ONLY the JSON array:")
        ])

        self._chain = prompt | self._llm

    def predict(self, text: str) -> List[Dict]:
        try:
            # Truncate very long texts to avoid context limits and timeouts
            max_chars = 1500  # Much smaller for faster processing with 27B model
            if len(text) > max_chars:
                text = text[:max_chars] + "... [truncated]"

            result = self._chain.invoke({"text": text})
            content = result.content if hasattr(result, 'content') else str(result)

            # Parse JSON from response - handle various formats
            entities = self._parse_json_response(content)

            # Validate and clean results
            validated = []
            for e in entities:
                if isinstance(e, dict) and "text" in e and "label" in e:
                    validated.append({
                        "text": str(e.get("text", "")),
                        "label": str(e.get("label", "CUSTOM")).upper(),
                        "start": int(e.get("start", 0)),
                        "end": int(e.get("end", 0)),
                        "score": float(e.get("score", 0.5)),
                    })
            return validated
        except Exception as e:
            print(f"Ollama error: {e}")
            return []

    def _parse_json_response(self, content: str) -> List[Dict]:
        """Extract and parse JSON array from model response."""
        import re
        import json

        if not content:
            return []

        content = content.strip()

        # Try to extract from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', content, re.DOTALL)
        if json_match:
            content = json_match.group(1)

        # Try to find bare JSON array
        if not (content.startswith('[') and content.endswith(']')):
            match = re.search(r'(\[.*\])', content, re.DOTALL)
            if match:
                content = match.group(1)

        # Parse JSON
        try:
            parsed = json.loads(content)
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass

        return []

    def process_document(self, doc: Document) -> Document:
        entities_data = self.predict(doc.text)
        entities = []
        for e in entities_data:
            entities.append(type('Entity', (), {
                'text': e.get('text', ''),
                'label': type('Label', (), {'value': e.get('label', 'CUSTOM')})(),
                'start': e.get('start', 0),
                'end': e.get('end', 0),
                'score': e.get('score', 0.5),
                'model_backend': ModelBackend.HF_TRANSFORMERS,
            })())
        doc.entities = entities
        return doc


def run_benchmark(
    docs: List[Document],
    models_config: List[Dict],
    output_file: str = "benchmark_results.json"
) -> List[BenchmarkResult]:
    """Run benchmark across all models and documents."""
    results = []

    for model_config in models_config:
        model_name = model_config["name"]
        backend = model_config["backend"]

        print(f"\n{'='*60}")
        print(f"Benchmarking: {model_name} ({backend})")
        print(f"{'='*60}")

        if backend == "ollama":
            ner = OllamaNER(model_config.get("model", "qwen3:8b"))
            pipeline = None
        elif backend == "hf_transformers":
            config = PipelineConfig(
                model_backend=ModelBackend.HF_TRANSFORMERS,
                model_name=model_config["model"],
                confidence_threshold=model_config.get("threshold", 0.5),
                anonymization=AnonymizationConfig(strategy=AnonymizationStrategy.REPLACE),
            )
            pipeline = AnonymizationPipeline(config)
            ner = None
        elif backend == "spacy":
            config = PipelineConfig(
                model_backend=ModelBackend.SPACY,
                spacy_model=model_config["model"],
                confidence_threshold=model_config.get("threshold", 0.5),
                anonymization=AnonymizationConfig(strategy=AnonymizationStrategy.REPLACE),
            )
            pipeline = AnonymizationPipeline(config)
            ner = None
        else:
            continue

        for doc in docs:
            print(f"  Processing: {doc.id} ({len(doc.text)} chars)...")

            start_time = time.perf_counter()

            try:
                if pipeline:
                    result = pipeline.run([doc])[0]
                    entities = result.document.entities
                    anonymized = result.document.anonymized_text or ""
                else:
                    ner.process_document(doc)
                    entities = doc.entities
                    anonymized = doc.anonymized_text or ""

                elapsed_ms = (time.perf_counter() - start_time) * 1000

                entity_types = {}
                sample_entities = []
                for i, e in enumerate(entities[:10]):
                    label = e.label.value if hasattr(e.label, 'value') else str(e.label)
                    entity_types[label] = entity_types.get(label, 0) + 1
                    sample_entities.append({
                        "text": e.text,
                        "label": label,
                        "score": round(e.score, 3),
                    })

                for e in entities[10:]:
                    label = e.label.value if hasattr(e.label, 'value') else str(e.label)
                    entity_types[label] = entity_types.get(label, 0) + 1

                benchmark_result = BenchmarkResult(
                    model_name=model_name,
                    backend=backend,
                    doc_id=doc.id,
                    doc_length=len(doc.text),
                    entities_found=len(entities),
                    entity_types=entity_types,
                    processing_time_ms=round(elapsed_ms, 2),
                    anonymized_length=len(anonymized),
                    sample_entities=sample_entities,
                )
                results.append(benchmark_result)

                print(f"    Entities: {len(entities)}, Time: {elapsed_ms:.0f}ms, Types: {entity_types}")

            except Exception as e:
                print(f"    ERROR: {e}")
                results.append(BenchmarkResult(
                    model_name=model_name,
                    backend=backend,
                    doc_id=doc.id,
                    doc_length=len(doc.text),
                    entities_found=0,
                    entity_types={},
                    processing_time_ms=0,
                    anonymized_length=0,
                    sample_entities=[],
                ))

    save_results(results, output_file)
    return results


def save_results(results: List[BenchmarkResult], output_file: str):
    """Save benchmark results to JSON and CSV."""
    data = [asdict(r) for r in results]

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    import csv
    csv_file = output_file.replace('.json', '.csv')
    if data:
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            for row in data:
                row_copy = row.copy()
                row_copy['entity_types'] = json.dumps(row_copy['entity_types'])
                row_copy['sample_entities'] = json.dumps(row_copy['sample_entities'])
                writer.writerow(row_copy)

    print(f"\nResults saved to {output_file} and {csv_file}")


def generate_report(results: List[BenchmarkResult], output_file: str = "benchmark_report.md"):
    """Generate markdown report from benchmark results."""
    lines = [
        "# NER Model Benchmark Report",
        f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Summary by Model",
        "",
        "| Model | Backend | Avg Entities | Avg Time (ms) | Total Entities |",
        "|-------|---------|--------------|---------------|----------------|",
    ]

    by_model = {}
    for r in results:
        key = f"{r.model_name} ({r.backend})"
        if key not in by_model:
            by_model[key] = []
        by_model[key].append(r)

    for model, res in by_model.items():
        avg_entities = statistics.mean(r.entities_found for r in res)
        avg_time = statistics.mean(r.processing_time_ms for r in res)
        total = sum(r.entities_found for r in res)
        lines.append(f"| {model} | {res[0].backend} | {avg_entities:.1f} | {avg_time:.0f} | {total} |")

    lines.extend(["", "## Detailed Results by Document", ""])

    for r in results:
        lines.extend([
            f"### {r.doc_id} ({r.model_name})",
            f"- **Backend:** {r.backend}",
            f"- **Doc Length:** {r.doc_length} chars",
            f"- **Entities Found:** {r.entities_found}",
            f"- **Processing Time:** {r.processing_time_ms:.0f}ms",
            f"- **Entity Types:** {r.entity_types}",
            f"- **Sample Entities:**",
        ])
        for e in r.sample_entities[:5]:
            lines.append(f"  - `{e['text']}` ({e['label']}: {e['score']})")
        lines.append("")

    with open(output_file, 'w') as f:
        f.write('\n'.join(lines))

    print(f"Report saved to {output_file}")


def main():
    print("Loading documents...")
    docs = load_documents_from_dir_any("data/cv")
    print(f"Loaded {len(docs)} documents")

    models_config = [
        {"name": "mrm8488 BERT Spanish", "backend": "hf_transformers", "model": "mrm8488/bert-spanish-cased-finetuned-ner", "threshold": 0.5},
        {"name": "BETO NER", "backend": "hf_transformers", "model": "dccuchile/bert-base-spanish-wwm-cased-finetuned-ner", "threshold": 0.5},
        {"name": "BERTin NER", "backend": "hf_transformers", "model": "dccuchile/bertin-roberta-base-spanish-finetuned-ner", "threshold": 0.5},
        {"name": "BERT English (baseline)", "backend": "hf_transformers", "model": "dslim/bert-base-NER", "threshold": 0.7},
        {"name": "SpaCy Transformer", "backend": "spacy", "model": "en_core_web_trf", "threshold": 0.5},
        {"name": "Ollama Qwen3 27B", "backend": "ollama", "model": "qwen3.8:27b-mlx"},
    ]

    results = run_benchmark(docs, models_config, "output/benchmark_results.json")
    generate_report(results, "output/benchmark_report.md")

    print("\n" + "="*60)
    print("BENCHMARK COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()