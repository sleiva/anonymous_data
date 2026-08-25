import typer
from rich.console import Console
from rich.table import Table
from loguru import logger

from anonymization import (
    AnonymizationPipeline,
    PipelineConfig,
    Document,
    ModelBackend,
    AnonymizationStrategy,
    EntityType,
    AnonymizationConfig,
)

app = typer.Typer(help="BERT-based Data Anonymization Experiments")
console = Console()


@app.command()
def run(
    text: str = typer.Argument(..., help="Text to anonymize"),
    backend: ModelBackend = typer.Option(ModelBackend.HF_TRANSFORMERS, help="Model backend"),
    model: str = typer.Option("dslim/bert-base-NER", help="HF model name or SpaCy model"),
    strategy: AnonymizationStrategy = typer.Option(AnonymizationStrategy.MASK, help="Anonymization strategy"),
    threshold: float = typer.Option(0.7, help="Confidence threshold"),
    device: str = typer.Option("auto", help="Device (auto, cpu, cuda, mps)"),
):
    """Run anonymization on a single text"""
    config = PipelineConfig(
        model_backend=backend,
        model_name=model,
        confidence_threshold=threshold,
        device=device,
        anonymization=AnonymizationConfig(strategy=strategy),
    )

    pipeline = AnonymizationPipeline(config)
    doc = Document(id="cli-input", text=text)

    console.print(f"[bold]Processing with {backend.value}...[/bold]")
    results = pipeline.run([doc])

    for result in results:
        console.print(f"\n[green]Original:[/green] {result.document.text}")
        console.print(f"[green]Anonymized:[/green] {result.document.anonymized_text}")
        console.print(f"[green]Entities found:[/green] {result.entities_found}")
        console.print(f"[green]Backend:[/green] {result.backend_used.value}")
        console.print(f"[green]Time:[/green] {result.processing_time_ms:.2f}ms")

        if result.document.entities:
            table = Table(title="Detected Entities")
            table.add_column("Text")
            table.add_column("Type")
            table.add_column("Start")
            table.add_column("End")
            table.add_column("Score")

            for ent in result.document.entities:
                table.add_row(ent.text, ent.label.value, str(ent.start), str(ent.end), f"{ent.score:.3f}")

            console.print(table)


@app.command()
def batch(
    input_file: str = typer.Argument(..., help="Input file (CSV/JSON)"),
    text_column: str = typer.Option("text", help="Column containing text"),
    output_file: str = typer.Option("anonymized_output.json", help="Output file"),
    backend: ModelBackend = typer.Option(ModelBackend.HF_TRANSFORMERS, help="Model backend"),
    model: str = typer.Option("dslim/bert-base-NER", help="Model name"),
    strategy: AnonymizationStrategy = typer.Option(AnonymizationStrategy.MASK, help="Strategy"),
):
    """Run batch anonymization on a file"""
    import pandas as pd

    df = pd.read_csv(input_file) if input_file.endswith(".csv") else pd.read_json(input_file)
    texts = df[text_column].astype(str).tolist()

    config = PipelineConfig(
        model_backend=backend,
        model_name=model,
        anonymization=AnonymizationConfig(strategy=strategy),
    )

    pipeline = AnonymizationPipeline(config)
    docs = [Document(id=f"doc-{i}", text=t) for i, t in enumerate(texts)]

    console.print(f"[bold]Processing {len(docs)} documents...[/bold]")
    results = pipeline.run(docs)

    output_data = [
        {
            "id": r.document.id,
            "original": r.document.text,
            "anonymized": r.document.anonymized_text,
            "entities": [
                {"text": e.text, "type": e.label.value, "start": e.start, "end": e.end, "score": e.score}
                for e in r.document.entities
            ],
        }
        for r in results
    ]

    pd.DataFrame(output_data).to_json(output_file, orient="records", indent=2)
    console.print(f"[green]Saved to {output_file}[/green]")


@app.command()
def compare(
    text: str = typer.Argument(..., help="Text to compare"),
    hf_model: str = typer.Option("dslim/bert-base-NER", help="HF model"),
    spacy_model: str = typer.Option("en_core_web_trf", help="SpaCy model"),
    threshold: float = typer.Option(0.7, help="Threshold"),
):
    """Compare HF Transformers vs SpaCy on same text"""
    from anonymization import HFTransformersNER, SpacyNER

    hf_config = PipelineConfig(model_backend=ModelBackend.HF_TRANSFORMERS, model_name=hf_model, confidence_threshold=threshold)
    spacy_config = PipelineConfig(model_backend=ModelBackend.SPACY, spacy_model=spacy_model, confidence_threshold=threshold)

    hf_ner = HFTransformersNER(hf_config)
    spacy_ner = SpacyNER(spacy_config)

    doc_hf = Document(id="compare", text=text)
    doc_spacy = Document(id="compare", text=text)

    hf_ner.process_document(doc_hf)
    spacy_ner.process_document(doc_spacy)

    table = Table(title="Backend Comparison")
    table.add_column("Backend")
    table.add_column("Entities")
    table.add_column("Details")

    hf_entities = ", ".join(f"{e.text}({e.label.value}:{e.score:.2f})" for e in doc_hf.entities)
    spacy_entities = ", ".join(f"{e.text}({e.label.value})" for e in doc_spacy.entities)

    table.add_row("HF Transformers", str(len(doc_hf.entities)), hf_entities or "None")
    table.add_row("SpaCy", str(len(doc_spacy.entities)), spacy_entities or "None")

    console.print(table)


@app.command()
def process_docs(
    input_dir: str = typer.Argument(..., help="Input directory with documents"),
    output_file: str = typer.Option("anonymized_docs.json", help="Output file"),
    pattern: str = typer.Option("*", help="File pattern (e.g., *.pdf, *.docx)"),
    backend: ModelBackend = typer.Option(ModelBackend.SPACY, help="Model backend (SPACY recommended for docs)"),
    model: str = typer.Option("en_core_web_trf", help="Model name"),
    strategy: AnonymizationStrategy = typer.Option(AnonymizationStrategy.REPLACE, help="Anonymization strategy"),
):
    """Process documents from directory (PDF, DOCX, PPTX, XLSX, etc.) using anydoc"""
    from anonymization.utils import load_documents_from_dir_any
    
    console.print(f"[bold]Loading documents from {input_dir}...[/bold]")
    docs = load_documents_from_dir_any(input_dir, pattern)
    
    if not docs:
        console.print("[yellow]No documents found[/yellow]")
        return
    
    console.print(f"[green]Loaded {len(docs)} documents[/green]")
    
    config = PipelineConfig(
        model_backend=backend,
        spacy_model=model if backend == ModelBackend.SPACY else "en_core_web_trf",
        model_name=model if backend == ModelBackend.HF_TRANSFORMERS else "dslim/bert-base-NER",
        anonymization=AnonymizationConfig(strategy=strategy),
    )
    
    pipeline = AnonymizationPipeline(config)
    
    console.print(f"[bold]Processing {len(docs)} documents with {backend.value}...[/bold]")
    results = pipeline.run(docs)
    
    output_data = [
        {
            "id": r.document.id,
            "original": r.document.text,
            "anonymized": r.document.anonymized_text,
            "entities": [
                {"text": e.text, "type": e.label.value, "start": e.start, "end": e.end, "score": e.score}
                for e in r.document.entities
            ],
        }
        for r in results
    ]
    
    import pandas as pd
    pd.DataFrame(output_data).to_json(output_file, orient="records", indent=2)
    console.print(f"[green]Saved to {output_file}[/green]")


if __name__ == "__main__":
    app()