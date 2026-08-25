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

    def __init__(self, model_name: str = "qwen3:8b", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self._llm = None
        self._chain = None
        self._setup()

    def _setup(self):
        from langchain_ollama import ChatOllama
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import JsonOutputParser

        self._llm = ChatOllama(
            model=self.model_name,
            base_url=self.base_url,
            temperature=0,
            format="json",
        )

        prompt = ChatPromptTemplate.from_template("""
Extract all personally identifiable information (PII) entities from the text.
Return a JSON array of objects with: text, label, start, end, score.
Labels: PERSON, ORG, LOC, DATE, EMAIL, PHONE, ADDRESS, ID_NUMBER, CREDIT_CARD, IBAN, IP_ADDRESS, URL, CUSTOM.

Text: {text}

Return ONLY the JSON array, no extra text.
""")

        self._chain = prompt | self._llm | JsonOutputParser()

    def predict(self, text: str) -> List[Dict]:
        try:
            result = self._chain.invoke({"text": text})
            if isinstance(result, list):
                return result
            return []
        except Exception as e:
            print(f"Ollama error: {e}")
            return []

    def process_document(self, doc: Document) -> Document:
        entities_data = self.predict(doc.text)
        entities = []
        for e in entities_data:
            if isinstance(e, dict) and "text" in e:
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
        {"name": "Ollama Qwen3 8B", "backend": "ollama", "model": "qwen3:8b"},
    ]

    results = run_benchmark(docs, models_config, "output/benchmark_results.json")
    generate_report(results, "output/benchmark_report.md")

    print("\n" + "="*60)
    print("BENCHMARK COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()