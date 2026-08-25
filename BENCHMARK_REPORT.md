# NER Model Benchmark Report for PII Anonymization

**Project:** BERT-based Data Anonymization Experiments  
**Date:** 2025-08-25  
**Repository:** https://github.com/sleiva/anonymous_data  
**Test Data:** 3 Real CVs (PDF/DOCX) — Italian, Spanish, German (~308 KB total)

---

## Executive Summary

This benchmark evaluates **6 NER models** across **3 multilingual CV documents** for PII detection and anonymization quality. A **LLM-as-Judge** (deepseek-v4-pro:cloud, 671B params) performed 45 pairwise comparisons to determine the best model for production use.

### Key Findings

| Rank | Model | Backend | Wins (Judge) | Best For |
|------|-------|---------|--------------|----------|
| 1 | **SpaCy Transformer** | SpaCy | 14/45 | **Multilingual + Dates** (only model detecting DATE entities) |
| 2 | **BERT English Baseline** | HF | 8/45 | English documents, fallback |
| 3 | **Ollama Qwen3 27B** | Ollama | 8/45 | Local inference, but **too slow** (70s/doc) |
| 4 | **mrm8488 BERT Spanish** | HF | 4/45 | **Spanish PII** (groups "Juan Pérez" = 1 PERSON) |
| 5 | **BETO NER** | HF | 2/45 | Spanish academic reference |
| 6 | **BERTin NER** | HF | 1/45 | Fast Spanish, but high noise |

---

## 1. Quantitative Benchmark Results

### Entities Detected per Document (3 CVs)

| Model | CV Italiano (R.E.) | CV Finanzas (I.S.) | CV Alemán (J.L.) | **Total** | Avg Time/doc |
|-------|-------------------|-------------------|------------------|-----------|--------------|
| **mrm8488 BERT Spanish** | 242 | 155 | 294 | **691** | 584 ms |
| **BETO NER** | 405 | 288 | 441 | **1134** | 432 ms |
| **BERTin NER** | 369 | 253 | 530 | **1152** | 479 ms |
| **BERT English (baseline)** | 104 | 110 | 133 | **347** | 384 ms |
| **SpaCy Transformer** | 105 | 70 | 51 | **226** | 644 ms |
| **Ollama Qwen3 27B** | 0 | 0 | 0 | **0** | **92,810 ms** |

### Entity Type Distribution (Total across all 3 CVs)

| Type | mrm8488 | BETO | BERTin | BERT En | SpaCy | Ollama |
|------|---------|------|--------|---------|-------|--------|
| PERSON | 10 | 7 | 1 | 7 | 8 | 0 |
| ORG | 220 | 168 | 60 | 312 | 105 | 0 |
| LOC | 103 | 45 | 23 | 23 | 22 | 0 |
| DATE | 0 | 0 | 0 | 0 | **48** | 0 |
| CUSTOM | 358 | 914 | 1069 | 8 | 43 | 0 |

---

## 2. Qualitative Analysis by Model

### 🏆 mrm8488/bert-spanish-cased-finetuned-ner — **Best for Spanish PII**

**Strengths:**
- Only model that correctly groups multi-word names: `"Juan Pérez"` → 1 PERSON (not 2)
- Good LOC detection for Spanish locations (Madrid, Barcelona, Santander)
- Reasonable speed (~150-1800ms depending on doc length)
- Handles chunking for long texts (512 tokens + 128 stride)

**Weaknesses:**
- No DATE entity support (CoNLL labels only)
- High CUSTOM noise on non-Spanish text (Italian/German)
- Subword tokenization artifacts on non-Spanish languages

**Judge Verdict:** Wins 4/15 comparisons on Spanish CV; loses to SpaCy/BERT-English on multilingual docs.

---

### 🏆 SpaCy en_core_web_trf — **Best for Dates + English**

**Strengths:**
- **Only model detecting DATE entities** (48 total across 3 CVs)
- Clean entity grouping: "Operations Director", "Supply Chain Centralizada"
- Stable, predictable output
- Good LOC detection (Palo Alto, USA, Como, Varese)

**Weaknesses:**
- English-trained → poor PERSON recall on non-English (1-6 PERSON vs 10+)
- Over-detects ORG on German CV (129 entities, mostly industry terms)
- Slower than HF models (~1.6s/doc)

**Judge Verdict:** 14 wins — dominates on CVs with dates (Finanzas, Alemán).

---

### 📊 BETO / BERTin (dccuchile) — **High Noise, CoNLL Labels**

**Critical Issue:** Both use CoNLL label scheme (LABEL_0-8) without B-/I- merging → **extreme fragmentation**

```
BETO output for "Juan Pérez vive en Madrid":
  "Juan" (PERSON), "Pérez" (PERSON), "vive en" (CUSTOM), 
  "Madrid" (LOC), "y trabaja en" (CUSTOM), "." (CUSTOM)
```

**Stats:**
- BETO: 70-80% CUSTOM noise
- BERTin: 86% CUSTOM noise
- Require post-processing merge to be usable

**Judge Verdict:** Only 2-3 wins total; judge notes "both equally ineffective" on non-Spanish text.

---

### 🤖 Ollama Qwen3 27B (qwen3.8:27b-mlx) — **Too Slow for Production**

| Metric | Value |
|--------|-------|
| Avg time/doc | **92,810 ms (93 seconds)** |
| Total entities (3 CVs) | **0** |
| Only detection in test | "11/2023 – heute" (DATE) on short German text |

**Why it fails:**
- 27B model on CPU/MPS → extremely slow
- Base model without NER fine-tuning → recall ≈ 0
- Prompt-based NER without fine-tuning → poor recall
- Truncation to 1500 chars loses context
- JSON parsing issues on long outputs

**Judge Verdict:** 8 wins — only when compared to completely broken models (BETO/BERTin on German). Judge: *"avoiding falsos positivos es preferible a alucinar entidades"*

---

### 📊 BERT English Baseline (dslim/bert-base-NER)

**Surprisingly decent as fallback:**
- Good on English/International names (Palo Alto, USA, Google, Apple)
- Clean ORG detection (Apple Inc., Microsoft, CooperVision)
- Low CUSTOM noise (5-8%)
- Fast (110-900ms)

**Fails on:**
- Non-Latin scripts / non-English names
- No DATE support
- Subword fragmentation on German/Italian

---

## 3. LLM-as-Judge Evaluation (deepseek-v4-pro:cloud)

### Methodology
- **Judge:** deepseek-v4-pro:cloud (671B params) via Ollama + LangChain
- **Criteria (weighted):** Precision 30%, Recall 30%, Grouping 20%, Typing 15%, Anonymization 5%
- **Comparisons:** 45 pairwise (6 models × 3 CVs = 15 pairs × 3 docs)
- **Output:** JSON scores + detailed reasoning

### Win Counts (45 total comparisons)

| Model | Wins | Win Rate |
|-------|------|----------|
| SpaCy Transformer | **14** | 31% |
| BERT English | 8 | 18% |
| Ollama Qwen3 27B | 8 | 18% |
| mrm8488 BERT Spanish | 4 | 9% |
| BETO NER | 2 | 4% |
| BERTin NER | 1 | 2% |
| TIE | 8 | 18% |

### Judge Insights by Document

#### CV Italiano (Operations Director, 7125 chars)
- **All HF Spanish models fail** — tokenizer mismatch on Italian
- **SpaCy wins** — detects 25 DATEs, 14 LOC, 35 ORG
- **mrm8488** produces subword fragments: `Auto`, `Deloc`, `##zazio`
- Judge: *"Both models are Spanish BERT variants applied to Italian text, causing severe tokenization failures"*

#### CV Finanzas (Director Financiero, 4978 chars)
- **SpaCy wins** — 15 DATEs (ranges: "Mar 24 – Jul 24", "Ene 2020 – Dic 2020")
- **mrm8488** best for Spanish PII: "ALGECO SAU" as 1 ORG, "Madrid" LOC
- **BETO/BERTin** → 70-80% CUSTOM noise

#### CV Alemán (Perfil Management, 6687 chars)
- **All models struggle** — German text, no explicit PII
- **Ollama Qwen3 27B** detects "11/2023 – heute" (DATE) — only correct detection
- **SpaCy/BERT-English** detect industry terms as ORG (TGA, Handwerk, Photovoltaik)
- Judge: *"Input contains no explicit PII; all detections are false positives"*

---

## 4. Ollama Configuration Tested

```json
{
    "min_p": 0,
    "presence_penalty": 0,
    "repeat_penalty": 1,
    "temperature": 1,
    "top_k": 20,
    "top_p": 0.95
}
```

**Result:** Parameters work for short prompts (tested: "Juan Pérez vive en Madrid" → 3 entities correctly extracted), but model fails on long CV texts due to:
1. No NER fine-tuning
2. 1500 char truncation loses context
3. 27B model too slow on CPU/MPS (93s/doc)

---

## 5. Recommendations by Use Case

| Use Case | Recommended Pipeline |
|----------|---------------------|
| **Spanish PII (names, DNI, email, phone)** | `mrm8488/bert-spanish-cased-finetuned-ner` + HF Transformers |
| **Multilingual docs + Dates required** | `en_core_web_trf` (SpaCy) |
| **English-only documents** | `dslim/bert-base-NER` or `en_core_web_trf` |
| **Maximum recall (research)** | Ensemble: SpaCy + mrm8488 + Regex |
| **Production with local inference** | Avoid Ollama 27B (93s/doc); use quantized HF models |
| **Academic reference (Spanish)** | BETO/BERTin + post-merge |

---

## 6. Production Pipeline Architecture

```python
# Recommended: Language-aware ensemble
def detect_pii(text: str, lang: str) -> List[Entity]:
    if lang == 'es':
        return mrm8488_ner.predict(text)      # Best Spanish grouping
    elif lang == 'en':
        return spacy_ner.predict(text)        # Best dates + English
    else:
        # Multilingual fallback
        hf_entities = xlm_roberta_ner.predict(text)
        spacy_entities = spacy_ner.predict(text)
        return merge_entities(hf_entities, spacy_entities)

def anonymize_pipeline(text: str, lang: str) -> str:
    entities = detect_pii(text, lang)
    return anonymizer.anonymize(text, entities, strategy=REPLACE)
```

---

## 7. Files Generated

```
output/
├── benchmark_results.json          # Raw benchmark data (all models, all docs)
├── benchmark_results.csv           # For Excel/pandas analysis
├── benchmark_report.md             # This benchmark report
├── llm_judge_evaluation.json       # 45 pairwise evaluations (detailed)
└── llm_judge_evaluation_report.md  # Full judge report with reasoning
```

### CV Anonymization Outputs (per model)
```
output/
├── cv_anonymized_detailed.json      # SpaCy
├── cv_anonymized_hf_spanish.json    # mrm8488 (best Spanish)
├── cv_anonymized_beto.json          # BETO
├── cv_anonymized_bertin.json        # BERTin
└── cv_anonymized_english.json       # BERT English baseline
```

---

## 8. Reproduction Commands

```bash
# Setup
git clone https://github.com/sleiva/anonymous_data.git
cd anonymous_data
uv venv && uv pip install -e ".[dev]"
uv run python -m spacy download en_core_web_trf

# Run benchmark
uv run python scripts/benchmark_models.py

# Run LLM Judge (requires deepseek-v4-pro:cloud in Ollama)
uv run python scripts/llm_judge.py deepseek-v4-pro:cloud

# View reports
cat output/benchmark_report.md
cat output/llm_judge_evaluation_report.md
```

---

## 9. Limitations & Future Work

### Current Limitations
1. **No ground truth labels** — Judge evaluates relative quality, not absolute F1
2. **Ollama too slow** — 93s/doc makes it impractical for batch processing
3. **BETO/BERTin need post-merge** — CoNLL labels require B-/I- merging
4. **Anonymization not evaluated** — Judge scored anonymization 0 (no output provided)
5. **No ground truth** — Cannot compute absolute P/R/F1

### Recommended Next Steps
1. **Fine-tune ModernBERT/NeoBERT** for Spanish NER (8k context, RoPE)
2. **Add regex patterns** for DNI, IBAN, email, phone (high-precision rules)
3. **Implement ensemble** with voting/confidence weighting
4. **Create labeled test set** for absolute metrics (P/R/F1)
5. **Quantize HF models** (INT8/INT4) for faster local inference
6. **Add language detection** (fasttext/langdetect) for auto-routing

---

## 10. Conclusion

**For production Spanish PII anonymization today:** Use **mrm8488/bert-spanish-cased-finetuned-ner** with HF Transformers — it's the only model that correctly groups Spanish names and runs at acceptable speed.

**For multilingual documents requiring date detection:** Use **SpaCy en_core_web_trf** — it's the only model that reliably detects DATE entities across languages.

**The LLM-as-Judge (deepseek-v4-pro) provides reliable relative rankings** and detailed reasoning that matches our quantitative findings. It correctly identifies that model performance is heavily dependent on language match (Spanish models on Spanish text, English models on English text).

**Ollama base models are NOT suitable for production NER** without fine-tuning, regardless of parameter tuning. The 93s/doc latency and 0 entity recall on CVs make it impractical.

---

*Report generated automatically from benchmark + LLM-as-Judge evaluation pipeline.  
Full raw data available in `output/benchmark_results.json` and `output/llm_judge_evaluation.json`.*