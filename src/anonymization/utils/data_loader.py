from collections.abc import Iterator
from pathlib import Path

import pandas as pd
import anydoc

from anonymization.models.types import Document


def load_documents_from_csv(
    file_path: str | Path,
    text_column: str = "text",
    id_column: str | None = None,
    metadata_columns: list[str] | None = None,
) -> list[Document]:
    """Load documents from CSV file."""
    df = pd.read_csv(file_path)
    
    if text_column not in df.columns:
        raise ValueError(f"Column '{text_column}' not found in CSV")
    
    documents = []
    for idx, row in df.iterrows():
        doc_id = str(row[id_column]) if id_column and id_column in df.columns else f"csv-{idx}"
        metadata = {}
        if metadata_columns:
            for col in metadata_columns:
                if col in df.columns:
                    metadata[col] = row[col]
        
        documents.append(Document(
            id=doc_id,
            text=str(row[text_column]),
            metadata=metadata,
        ))
    
    return documents


def load_documents_from_json(
    file_path: str | Path,
    text_field: str = "text",
    id_field: str | None = None,
) -> list[Document]:
    """Load documents from JSON/JSONL file."""
    if str(file_path).endswith(".jsonl"):
        df = pd.read_json(file_path, lines=True)
    else:
        df = pd.read_json(file_path)
    
    return load_documents_from_csv(
        file_path,  # reuse logic
        text_column=text_field,
        id_column=id_field,
    )


def load_documents_from_text(
    file_path: str | Path,
    encoding: str = "utf-8",
) -> list[Document]:
    """Load documents from plain text file (one document per line)."""
    with open(file_path, encoding=encoding) as f:
        lines = [line.strip() for line in f if line.strip()]
    
    return [Document(id=f"text-{i}", text=line) for i, line in enumerate(lines)]


def load_documents_from_dir(
    dir_path: str | Path,
    pattern: str = "*.txt",
    encoding: str = "utf-8",
) -> list[Document]:
    """Load documents from directory of text files."""
    path = Path(dir_path)
    documents = []
    
    for file_path in path.glob(pattern):
        with open(file_path, encoding=encoding) as f:
            text = f.read().strip()
        if text:
            documents.append(Document(id=file_path.stem, text=text))
    
    return documents


def load_documents_from_pdf(
    file_path: str | Path,
) -> list[Document]:
    """Load document from PDF file using anydoc."""
    markdown = anydoc.to_markdown(str(file_path))
    return [Document(id=Path(file_path).stem, text=markdown)]


def load_documents_from_docx(
    file_path: str | Path,
) -> list[Document]:
    """Load document from DOCX file using anydoc."""
    markdown = anydoc.to_markdown(str(file_path))
    return [Document(id=Path(file_path).stem, text=markdown)]


def load_documents_from_any(
    file_path: str | Path,
) -> list[Document]:
    """Load document from any supported file format (PDF, DOCX, PPTX, XLSX, etc.) using anydoc."""
    markdown = anydoc.to_markdown(str(file_path))
    return [Document(id=Path(file_path).stem, text=markdown)]


def load_documents_from_dir_any(
    dir_path: str | Path,
    pattern: str = "*",
) -> list[Document]:
    """Load documents from directory of any supported file formats using anydoc."""
    path = Path(dir_path)
    documents = []
    
    for file_path in path.glob(pattern):
        if file_path.is_file():
            try:
                markdown = anydoc.to_markdown(str(file_path))
                if markdown.strip():
                    documents.append(Document(id=file_path.stem, text=markdown))
            except anydoc.ConvertError as e:
                print(f"Warning: Could not convert {file_path}: {e}")
    
    return documents


def stream_documents(
    file_path: str | Path,
    text_column: str = "text",
    id_column: str | None = None,
    chunk_size: int = 1000,
) -> Iterator[list[Document]]:
    """Stream documents from large CSV/JSON files in chunks."""
    if str(file_path).endswith(".csv"):
        reader = pd.read_csv(file_path, chunksize=chunk_size)
    else:
        reader = pd.read_json(file_path, lines=True, chunksize=chunk_size)
    
    for chunk_df in reader:
        docs = []
        for idx, row in chunk_df.iterrows():
            doc_id = str(row[id_column]) if id_column and id_column in chunk_df.columns else f"stream-{idx}"
            docs.append(Document(id=doc_id, text=str(row[text_column])))
        yield docs


def save_results(results: list, output_path: str | Path, format: str = "json"):
    """Save processing results to file."""
    import json

    from anonymization.models.types import ProcessingResult
    
    data = []
    for r in results:
        if isinstance(r, ProcessingResult):
            data.append({
                "id": r.document.id,
                "original_text": r.document.text,
                "anonymized_text": r.document.anonymized_text,
                "entities_found": r.entities_found,
                "processing_time_ms": r.processing_time_ms,
                "backend": r.backend_used.value,
                "entities": [
                    {
                        "text": e.text,
                        "type": e.label.value,
                        "start": e.start,
                        "end": e.end,
                        "score": e.score,
                    }
                    for e in r.document.entities
                ],
            })
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if format == "json":
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    elif format == "csv":
        pd.DataFrame(data).to_csv(output_path, index=False)
    elif format == "jsonl":
        with open(output_path, "w") as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")