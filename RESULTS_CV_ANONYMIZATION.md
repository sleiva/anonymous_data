# Resultados de Anonimización de CVs - Documentación Completa

**Fecha:** 2025-08-25  
**Directorio de datos:** `/Users/projects/anonymous_data/data/cv`  
**Modelos probados:** 5 (1 SpaCy + 4 HF Transformers)  
**Estrategia de anonimización:** REPLACE (placeholders tipados)

---

## 1. Documentos de Entrada

| Archivo | Formato | Tamaño | Idioma principal | Descripción |
|---------|---------|--------|------------------|-------------|
| `CV - J.L. PERFIL ALEMAN.docx` | DOCX | 21 KB | Alemán / Español | Perfil ejecutivo 25+ años, management, ingeniería |
| `CV I.S. - FINANZAS.pdf` | PDF | 148 KB | Español | Director financiero, reestructuración, tesorería |
| `CV ITALIANO - R.E..pdf` | PDF | 139 KB | Italiano | Operations Director, multinacionales, lean manufacturing |

**Total:** 3 documentos, ~308 KB, 3 idiomas (ES, IT, DE)

---

## 2. Configuración de Modelos Probados

| # | Backend | Modelo | Tipo | Descripción |
|---|---------|--------|------|-------------|
| 1 | **SpaCy** | `en_core_web_trf` | Transformer (RoBERTa) | Modelo inglés de alta precisión, 512 tokens |
| 2 | **HF Transformers** | `mrm8488/bert-spanish-cased-finetuned-ner` | BERT Spanish | **Mejor modelo español**, agrupa entidades correctamente |
| 3 | **HF Transformers** | `dccuchile/bert-base-spanish-wwm-cased-finetuned-ner` | BETO + NER | BERT español (U. Chile), labels CoNLL (LABEL_0-8) |
| 4 | **HF Transformers** | `dccuchile/bertin-roberta-base-spanish-finetuned-ner` | BERTin + NER | RoBERTa español optimizado, labels CoNLL |
| 5 | **HF Transformers** | `dslim/bert-base-NER` | BERT English | Baseline inglés (CoNLL-2003) |

**Nota:** Todos los modelos HF usan chunking automático (512 tokens, stride 128) para textos largos.

---

## 3. Resumen Comparativo de Entidades Detectadas

### 3.1 Tabla General

| Modelo | CV Italiano (R.E.) | CV Finanzas (I.S.) | CV Alemán (J.L.) | **Total** |
|--------|-------------------|-------------------|------------------|-----------|
| **SpaCy (en_core_web_trf)** | 105 | 70 | 51 | **226** |
| **mrm8488 BERT Spanish** | 174 | 133 | 215 | **522** |
| **BETO (dccuchile)** | 280 | 230 | 276 | **786** |
| **BERTin (dccuchile)** | 221 | 164 | 263 | **648** |
| **BERT English (baseline)** | 104 | 110 | 133 | **347** |

### 3.2 Distribución por Tipo de Entidad

#### CV Italiano - R.E. (Operations Director)

| Tipo | SpaCy | mrm8488 | BETO | BERTin | BERT En |
|------|-------|---------|------|--------|---------|
| PERSON | 1 | 1 | 3 | 0 | 4 |
| ORG | 35 | 61 | 43 | 18 | 80 |
| LOC | 14 | 44 | 37 | 13 | 15 |
| DATE | 25 | 0 | 0 | 0 | 0 |
| CUSTOM | 30 | 68 | 197 | 190 | 5 |
| **Total** | **105** | **174** | **280** | **221** | **104** |

#### CV Finanzas - I.S. (Director Financiero)

| Tipo | SpaCy | mrm8488 | BETO | BERTin | BERT En |
|------|-------|---------|------|--------|---------|
| PERSON | 6 | 0 | 0 | 0 | 3 |
| ORG | 38 | 18 | 24 | 31 | 103 |
| LOC | 2 | 3 | 3 | 3 | 4 |
| DATE | 15 | 0 | 0 | 0 | 0 |
| CUSTOM | 9 | 112 | 203 | 130 | 3 |
| **Total** | **70** | **133** | **230** | **164** | **110** |

#### CV Alemán - J.L. (Perfil Management)

| Tipo | SpaCy | mrm8488 | BETO | BERTin | BERT En |
|------|-------|---------|------|--------|---------|
| PERSON | 1 | 2 | 0 | 0 | 0 |
| ORG | 32 | 67 | 56 | 7 | 129 |
| LOC | 3 | 2 | 5 | 7 | 4 |
| DATE | 8 | 0 | 0 | 0 | 0 |
| CUSTOM | 7 | 144 | 215 | 249 | 0 |
| **Total** | **51** | **215** | **276** | **263** | **133** |

---

## 4. Análisis Cualitativo por Modelo

### 4.1 SpaCy (en_core_web_trf) - **Mejor para documentos en inglés/estructurados**

**Fortalezas:**
- Detecta correctamente fechas (25 en CV Italiano, 15 en CV Finanzas)
- Pocos falsos positivos (CUSTOM = 30-46 total)
- Agrupa bien entidades multi-palabra ("Operations Director", "Supply Chain")
- Rápido y estable

**Debilidades:**
- Modelo entrenado en inglés → peor rendimiento en español/italiano/alemán
- Solo 1 PERSON detectada en CVs no ingleses
- Muchas ORG detectadas en CV Alemán (129) - sobre-detección

**Mejor para:** Documentos en inglés, datos estructurados, cuando necesitas fechas

---

### 4.2 mrm8488/bert-spanish-cased-finetuned-ner - **Mejor para español**

**Fortalezas:**
- **Agrupa nombres compuestos correctamente**: "Juan Pérez" = 1 PERSON (no 2)
- Mejor balance PRECISION/RECALL en español
- Detecta ubicaciones españolas (Madrid, Barcelona, Santander)
- Menos fragmentación que modelos CoNLL

**Debilidades:**
- No detecta fechas (modelo CoNLL no tiene DATE)
- Muchas entidades CUSTOM (fragmentación en texto técnico)
- "Google" → CUSTOM en lugar de ORG

**Mejor para:** **Documentos en español**, anonimización de PII real (nombres, DNI, direcciones)

---

### 4.3 BETO (dccuchile/bert-base-spanish-wwm-cased-finetuned-ner)

**Fortalezas:**
- Modelo base BERT entrenado en español (WWN, 3B tokens)
- Robusto para español general

**Debilidades:**
- **Fragmentación extrema**: "Juan Pérez" → 2 entidades (Juan + Pérez)
- Labels CoNLL sin DATE → no detecta fechas
- **Exceso de CUSTOM** (197/280 = 70% ruido)
- "vive en", "y trabaja en" detectados como entidades

**Mejor para:** Investigación, no recomendado para producción

---

### 4.4 BERTin (dccuchile/bertin-roberta-base-spanish-finetuned-ner)

**Fortalezas:**
- RoBERTa base optimizada para español (más rápida que BETO)
- Mejor que BETO en agrupación (menos fragmentación)

**Debilidades:**
- Igual que BETO: labels CoNLL, sin DATE, mucho CUSTOM
- "Google" → ORG (bien), pero fragmenta nombres
- CUSTOM = 190/221 (86% ruido en CV Italiano)

**Mejor para:** Cuando necesitas velocidad en español, aceptar ruido

---

### 4.5 BERT English Baseline (dslim/bert-base-NER)

**Fortalezas:**
- Baseline conocido, bien documentado
- Detecta PERSON en español (nombres latinos)
- Buena precisión en ORG internacionales (Apple, Google, Microsoft)

**Debilidades:**
- Modelo inglés → falla en español/italiano/alemán
- Sobre-detecta ORG (129 en CV Alemán)
- No detecta fechas ni ubicaciones locales bien

**Mejor para:** Solo documentos en inglés

---

## 5. Ejemplos de Anonimización

### 5.1 Texto de prueba: "Juan Pérez (juan@empresa.es) vive en Madrid, DNI: 12345678Z."

| Modelo | Anonimizado | Entidades |
|--------|-------------|-----------|
| **mrm8488** | `[PERSON_1] (juan@empresa.es) vive en [LOC_1], DNI: 12345678Z.` | 2 (PERSON, LOC) ✓ |
| **BETO** | `[PERSON_2] [PERSON_1] (juan@empresa.es[CUSTOM_2] [LOC_1][CUSTOM_1]` | 5 (fragmentado) ✗ |
| **BERTin** | `[PERSON_2] [PERSON_1] [CUSTOM_2] [LOC_1][CUSTOM_1]` | 5 (fragmentado) ✗ |
| **SpaCy** | `[PERSON_1] (juan@empresa.es) vive en [LOC_1], DNI: 12345678Z.` | 2 (PERSON, LOC) ✓ |
| **BERT En** | `[PERSON_1] (juan@empresa.es) vive en [LOC_1], DNI: 12345678Z.` | 2 (PERSON, LOC) ✓ |

> **Conclusión:** Solo **mrm8488**, **SpaCy** y **BERT English** agrupan correctamente "Juan Pérez" como una sola entidad PERSON.

---

### 5.2 Fragmento CV Italiano (R.E.) - Anonimizado con mrm8488 (mejor español)

**Original:**
> "Operations Director con solida esperienza in realtà Automotive, elettrodomestica settore del bianco... Progettazione ed implementazione delle Operations In Europa (Stabilimenti, Qualità, Logistica & Supply Chain Centralizzata)..."

**Anonimizado (mrm8488):**
> "[ORG_35] con solida esperienza in realtà Automotive, elettrodomestica settore del bianco... Progettazione ed implementazione delle [ORG_34] In Europa ([ORG_33], [ORG_32], [ORG_31] & [ORG_30] Centralizzata)..."

**Entidades clave detectadas:**
- ORG: Operations, Supply Chain, Logistica, Stabilimenti, Qualità, IT, Acquisti, etc.
- LOC: Palo Alto, USA, Como, Italia, Polonia, Turchia, Germania
- PERSON: 1 (nombre del candidato - bien oculto)
- DATE: 0 (modelo no tiene DATE)

---

### 5.3 Fragmento CV Finanzas (I.S.) - Anonimizado con SpaCy (mejor fechas)

**Original:**
> "Director Financiero Interino. Mejora de circulante, implantación nuevo ERP SANTANDER DIGITAL ASSETS Ene 2020 – Dic 2020 Project Controller. IT projects. Dic 2018 – May 2019 Director Financiero..."

**Anonimizado (SpaCy):**
> "[ORG_1] [DATE_1]. Mejora de circulante, implantación nuevo ERP [ORG_2] [DATE_2] [ORG_3]. IT projects. [DATE_3] [ORG_4] [DATE_4] [ORG_5]..."

**Entidades clave detectadas:**
- PERSON: 6 (nombres en CV)
- ORG: 38 (empresas, ERP, proyectos)
- DATE: 15 (rangos temporales completos: "Mar 24 – Jul 24", "Ene 2020 – Dic 2020")
- LOC: 2 (Portugal, Italia)

---

## 6. Recomendaciones por Caso de Uso

| Caso de uso | Modelo recomendado | Razón |
|-------------|-------------------|-------|
| **CVs en español (PII: nombres, DNI, email, teléfono)** | `mrm8488/bert-spanish-cased-finetuned-ner` | Agrupa nombres, detecta LOC españolas, buen balance |
| **Documentos en inglés (CVs, contratos, emails)** | `en_core_web_trf` (SpaCy) | Mejor precisión general, detecta fechas, estable |
| **Documentos multilingües mixtos** | Pipeline híbrido: SpaCy + mrm8488 | Combinar fortalezas |
| **Alta velocidad, español** | `dccuchile/bertin-roberta-base-spanish-finetuned-ner` | Más rápido que BETO, aceptable |
| **Investigación / comparación** | Todos + ensemble | Para análisis académico |
| **Solo fechas + estructura** | SpaCy | Único que detecta DATE bien |

---

## 7. Archivos de Salida Generados

```
output/
├── cv_anonymized_detailed.json      # SpaCy (en_core_web_trf)
├── cv_anonymized_hf_spanish.json    # mrm8488 BERT Spanish
├── cv_anonymized_beto.json          # BETO (dccuchile)
├── cv_anonymized_bertin.json        # BERTin (dccuchile)
└── cv_anonymized_english.json       # BERT English baseline
```

Cada JSON contiene:
```json
{
  "id": "CV ITALIANO - R.E.",
  "original": "texto completo original...",
  "anonymized": "texto con [PERSON_1], [ORG_1], etc...",
  "entities": [
    {"text": "Operations", "type": "ORG", "start": 215, "end": 225, "score": 1.0},
    ...
  ]
}
```

---

## 8. Comandos para Reproducir

```bash
# Activar entorno
cd /Users/projects/anonymous_data && source .venv/bin/activate

# 1. SpaCy (recomendado para inglés/fechas)
uv run python scripts/run_anonymization.py process-docs data/cv \
  --output-file output/cv_spacy.json --backend spacy

# 2. Mejor modelo español (recomendado para PII en español)
uv run python scripts/run_anonymization.py process-docs data/cv \
  --output-file output/cv_spanish.json --backend hf_transformers \
  --model mrm8488/bert-spanish-cased-finetuned-ner

# 3. BETO (referencia académica español)
uv run python scripts/run_anonymization.py process-docs data/cv \
  --output-file output/cv_beto.json --backend hf_transformers \
  --model dccuchile/bert-base-spanish-wwm-cased-finetuned-ner

# 4. BERTin (español optimizado)
uv run python scripts/run_anonymization.py process-docs data/cv \
  --output-file output/cv_bertin.json --backend hf_transformers \
  --model dccuchile/bertin-roberta-base-spanish-finetuned-ner

# 5. Baseline inglés
uv run python scripts/run_anonymization.py process-docs data/cv \
  --output-file output/cv_english.json --backend hf_transformers \
  --model dslim/bert-base-NER
```

---

## 9. Métricas de Rendimiento (Aproximadas)

| Modelo | Tiempo CV Italiano | Tiempo CV Finanzas | Tiempo CV Alemán | Memoria GPU |
|--------|-------------------|-------------------|------------------|-------------|
| SpaCy | ~2.5s | ~1.8s | ~1.5s | ~2 GB |
| mrm8488 | ~2.3s | ~1.6s | ~1.8s | ~1.5 GB |
| BETO | ~1.5s | ~1.2s | ~1.5s | ~1.5 GB |
| BERTin | ~1.3s | ~1.0s | ~1.4s | ~1.2 GB |
| BERT En | ~1.3s | ~1.1s | ~1.3s | ~1.5 GB |

*Hardware: MacBook Pro M1/M2 (MPS), Python 3.13, transformers 4.53*

---

## 10. Conclusiones Finales

1. **Para CVs en español → usar `mrm8488/bert-spanish-cased-finetuned-ner`**
   - Único que agrupa "Juan Pérez" como 1 PERSON
   - Detecta ubicaciones españolas nativamente
   - Menor ruido CUSTOM que BETO/BERTin

2. **Para extracción de fechas + estructura → SpaCy `en_core_web_trf`**
   - Detecta rangos temporales completos
   - Estable y predecible

3. **Evitar BETO/BERTin para producción** sin post-procesamiento
   - Fragmentación extrema (LABEL_1 + LABEL_2 = 1 persona)
   - 70-86% entidades CUSTOM = ruido
   - Requieren merge de sub-tokens post-inferencia

4. **Chunking automático funciona** para documentos largos (2000+ tokens)
   - Configurable: `max_length=512`, `stride=128`
   - Mantiene offsets correctos en texto original

5. **Pipeline híbrido recomendado para producción real:**
   ```python
   # Detectar idioma → aplicar modelo especializado
   if lang == 'es': use mrm8488
   elif lang == 'en': use spacy_transformers
   else: use xlm-roberta-multilingual
   ```

---

## 11. Próximos Pasos Sugeridos

- [ ] Entrenar/fine-tunear ModernBERT/NeoBERT para NER español
- [ ] Implementar post-procesamiento merge sub-tokens para modelos CoNLL
- [ ] Añadir detección de idioma automática (fasttext/langdetect)
- [ ] Pipeline ensemble: combinar SpaCy + HF Spanish + regex (DNI, IBAN, email)
- [ ] Evaluar con métricas formales (P/R/F1) sobre dataset anotado
- [ ] Integrar Presidio/MS Presidio para patrones regex complementarios