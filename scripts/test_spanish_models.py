#!/usr/bin/env python
"""Test Spanish NER models for anonymization."""

from anonymization import (
    HFTransformersNER,
    PipelineConfig,
    Document,
    ModelBackend,
    AnonymizationPipeline,
    AnonymizationStrategy,
    AnonymizationConfig,
)

SPANISH_NER_MODELS = [
    ("mrm8488/bert-spanish-cased-finetuned-ner", "BERT Spanish (mrm8488)"),
    ("dccuchile/bert-base-spanish-wwm-cased-finetuned-ner", "BETO (dccuchile)"),
    ("dccuchile/bertin-roberta-base-spanish-finetuned-ner", "BERTin (dccuchile)"),
    ("dslim/bert-base-NER", "BERT English (baseline)"),
]

TEST_TEXTS = [
    "Juan Pérez vive en Madrid y trabaja en Google.",
    "María García, directora de Microsoft España, nació en Barcelona el 15/03/1985.",
    "El DNI 12345678Z pertenece a Pedro López de Santander.",
    "Contacto: ana.martin@empresa.es, teléfono +34 91 234 56 78.",
    "Factura para Apple Inc. por 50.000€, IBAN: ES9121000418450200051332.",
]


def test_model(model_name: str, display_name: str):
    print(f"\n{'='*60}")
    print(f"Testing: {display_name}")
    print(f"Model: {model_name}")
    print(f"{'='*60}")

    config = PipelineConfig(
        model_backend=ModelBackend.HF_TRANSFORMERS,
        model_name=model_name,
        confidence_threshold=0.5,
    )

    try:
        ner = HFTransformersNER(config)

        for text in TEST_TEXTS:
            doc = Document(id="test", text=text)
            ner.process_document(doc)

            entities_str = ", ".join(
                f"{e.text}({e.label.value}:{e.score:.2f})" for e in doc.entities
            )
            print(f"  Input:  {text}")
            print(f"  Entities: {entities_str or 'None'}")

    except Exception as e:
        print(f"  ERROR: {e}")


def test_pipeline_anonymization():
    print(f"\n{'='*60}")
    print("Testing full anonymization pipeline with Spanish models")
    print(f"{'='*60}")

    text = "Juan Pérez (juan@empresa.es) vive en Madrid, DNI: 12345678Z."

    for model_name, display_name in SPANISH_NER_MODELS[:3]:  # Only Spanish models
        print(f"\n--- {display_name} ---")

        config = PipelineConfig(
            model_backend=ModelBackend.HF_TRANSFORMERS,
            model_name=model_name,
            anonymization=AnonymizationConfig(strategy=AnonymizationStrategy.REPLACE),
        )

        try:
            pipeline = AnonymizationPipeline(config)
            doc = Document(id="test", text=text)
            result = pipeline.run([doc])[0]

            print(f"  Original:     {result.document.text}")
            print(f"  Anonymized:   {result.document.anonymized_text}")
            print(f"  Entities:     {result.entities_found}")

        except Exception as e:
            print(f"  ERROR: {e}")


if __name__ == "__main__":
    for model_name, display_name in SPANISH_NER_MODELS:
        test_model(model_name, display_name)

    test_pipeline_anonymization()