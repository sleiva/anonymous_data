# NER Model Benchmark Report
**Generated:** 2026-08-25 13:45:08

## Summary by Model

| Model | Backend | Avg Entities | Avg Time (ms) | Total Entities |
|-------|---------|--------------|---------------|----------------|
| mrm8488 BERT Spanish (hf_transformers) | hf_transformers | 230.3 | 682 | 691 |
| BETO NER (hf_transformers) | hf_transformers | 378.0 | 423 | 1134 |
| BERTin NER (hf_transformers) | hf_transformers | 384.0 | 582 | 1152 |
| BERT English (baseline) (hf_transformers) | hf_transformers | 115.7 | 447 | 347 |
| SpaCy Transformer (spacy) | spacy | 75.3 | 741 | 226 |
| Ollama Qwen3 27B (ollama) | ollama | 0.3 | 69921 | 1 |

## Detailed Results by Document

### CV ITALIANO - R.E. (mrm8488 BERT Spanish)
- **Backend:** hf_transformers
- **Doc Length:** 7125 chars
- **Entities Found:** 242
- **Processing Time:** 1841ms
- **Entity Types:** {'CUSTOM': 116, 'LOC': 50, 'ORG': 72, 'PERSON': 4}
- **Sample Entities:**
  - `Auto` (CUSTOM: 0.961)
  - `Deloc` (CUSTOM: 0.8)
  - `##zazio` (CUSTOM: 0.558)
  - `##du` (CUSTOM: 0.578)
  - `##ve` (CUSTOM: 0.567)

### CV I.S. - FINANZAS (mrm8488 BERT Spanish)
- **Backend:** hf_transformers
- **Doc Length:** 4978 chars
- **Entities Found:** 155
- **Processing Time:** 80ms
- **Entity Types:** {'CUSTOM': 129, 'ORG': 23, 'LOC': 3}
- **Sample Entities:**
  - `PRO` (CUSTOM: 0.87)
  - `AL` (CUSTOM: 0.501)
  - `##GECO SAU` (ORG: 0.765)
  - `YODEYMA` (CUSTOM: 0.526)
  - `##U` (ORG: 0.551)

### CV - J.L.  PERFIL ALEMAN (mrm8488 BERT Spanish)
- **Backend:** hf_transformers
- **Doc Length:** 6687 chars
- **Entities Found:** 294
- **Processing Time:** 125ms
- **Entity Types:** {'CUSTOM': 199, 'ORG': 87, 'PERSON': 6, 'LOC': 2}
- **Sample Entities:**
  - `Erfa` (CUSTOM: 0.656)
  - `Management` (CUSTOM: 0.642)
  - `Un` (CUSTOM: 0.973)
  - `Mit` (CUSTOM: 0.966)
  - `. Experte` (CUSTOM: 0.966)

### CV ITALIANO - R.E. (BETO NER)
- **Backend:** hf_transformers
- **Doc Length:** 7125 chars
- **Entities Found:** 405
- **Processing Time:** 1033ms
- **Entity Types:** {'CUSTOM': 277, 'ORG': 80, 'LOC': 44, 'PERSON': 4}
- **Sample Entities:**
  - `PROFI` (CUSTOM: 0.7)
  - `* * con solida esperienza in * *` (CUSTOM: 0.866)
  - `Auto` (CUSTOM: 0.705)
  - `, elettrodomestica settore del bianco, * * * * elettromeccanica - plastica, alimentare, tessile e beni di consumo * *. In grado di condurre` (CUSTOM: 0.968)
  - `Operations` (CUSTOM: 0.637)

### CV I.S. - FINANZAS (BETO NER)
- **Backend:** hf_transformers
- **Doc Length:** 4978 chars
- **Entities Found:** 288
- **Processing Time:** 88ms
- **Entity Types:** {'CUSTOM': 241, 'ORG': 44, 'LOC': 3}
- **Sample Entities:**
  - `| o o o o o o o o o o o | FORTALEZAS PROFESIONALES flow, reporting. personas y tareas. EXPERIENCIA PROFESIONAL ( E` (CUSTOM: 0.937)
  - `). AISLAMIENTOS SUAVAL reestructuración financiera.` (CUSTOM: 0.961)
  - `ALGECO` (ORG: 0.889)
  - `fusion.` (CUSTOM: 0.928)
  - `YODEYMA` (ORG: 0.734)

### CV - J.L.  PERFIL ALEMAN (BETO NER)
- **Backend:** hf_transformers
- **Doc Length:** 6687 chars
- **Entities Found:** 441
- **Processing Time:** 148ms
- **Entity Types:** {'CUSTOM': 326, 'ORG': 104, 'PERSON': 3, 'LOC': 8}
- **Sample Entities:**
  - `P R O F I L Mehr als 25 Jahre Erfahrung im` (CUSTOM: 0.924)
  - `Management` (CUSTOM: 0.611)
  - `und der von` (CUSTOM: 0.995)
  - `##men und, vom Mittelstand bis zum Konzern. Experte` (CUSTOM: 0.869)
  - `,` (CUSTOM: 0.996)

### CV ITALIANO - R.E. (BERTin NER)
- **Backend:** hf_transformers
- **Doc Length:** 7125 chars
- **Entities Found:** 369
- **Processing Time:** 1503ms
- **Entity Types:** {'CUSTOM': 296, 'LOC': 21, 'ORG': 52}
- **Sample Entities:**
  - ` ##` (CUSTOM: 0.974)
  - ` PROFILO` (CUSTOM: 0.759)
  - `

` (CUSTOM: 0.895)
  - `***Operations` (CUSTOM: 0.709)
  - ` Director` (CUSTOM: 0.845)

### CV I.S. - FINANZAS (BERTin NER)
- **Backend:** hf_transformers
- **Doc Length:** 4978 chars
- **Entities Found:** 253
- **Processing Time:** 75ms
- **Entity Types:** {'CUSTOM': 202, 'ORG': 48, 'LOC': 3}
- **Sample Entities:**
  - ` |o o o o o o o o o o o|FORTALEZAS PROFESIONALES flow, reporting. personas y tareas. EXPERIENCIA PROFESIONAL (Ekon). AISLAMIENTOS SUAV` (CUSTOM: 0.877)
  - ` reestructuración financiera.` (CUSTOM: 0.989)
  - ` ALGECO` (ORG: 0.893)
  - ` SAU` (ORG: 0.625)
  - ` fusion.` (CUSTOM: 0.748)

### CV - J.L.  PERFIL ALEMAN (BERTin NER)
- **Backend:** hf_transformers
- **Doc Length:** 6687 chars
- **Entities Found:** 530
- **Processing Time:** 167ms
- **Entity Types:** {'CUSTOM': 475, 'ORG': 45, 'LOC': 9, 'PERSON': 1}
- **Sample Entities:**
  - `

Mehr als 25 Jahre` (CUSTOM: 0.761)
  - ` Erfahrung` (CUSTOM: 0.629)
  - ` im` (CUSTOM: 0.523)
  - ` Management` (CUSTOM: 0.551)
  - ` und der` (CUSTOM: 0.925)

### CV ITALIANO - R.E. (BERT English (baseline))
- **Backend:** hf_transformers
- **Doc Length:** 7125 chars
- **Entities Found:** 104
- **Processing Time:** 1091ms
- **Entity Types:** {'ORG': 80, 'LOC': 15, 'PERSON': 4, 'CUSTOM': 5}
- **Sample Entities:**
  - `Deloc` (ORG: 0.924)
  - `P & L` (ORG: 0.892)
  - `Lea` (ORG: 0.742)
  - `Operations and Manufacturing` (ORG: 0.807)
  - `dell` (ORG: 0.764)

### CV I.S. - FINANZAS (BERT English (baseline))
- **Backend:** hf_transformers
- **Doc Length:** 4978 chars
- **Entities Found:** 110
- **Processing Time:** 110ms
- **Entity Types:** {'ORG': 103, 'LOC': 4, 'PERSON': 3}
- **Sample Entities:**
  - `##Z` (ORG: 0.833)
  - `E` (ORG: 0.767)
  - `##P` (ORG: 0.957)
  - `##IENCIA` (ORG: 0.794)
  - `AISLAM` (ORG: 0.851)

### CV - J.L.  PERFIL ALEMAN (BERT English (baseline))
- **Backend:** hf_transformers
- **Doc Length:** 6687 chars
- **Entities Found:** 133
- **Processing Time:** 139ms
- **Entity Types:** {'ORG': 129, 'LOC': 4}
- **Sample Entities:**
  - `##ternehmen` (ORG: 0.852)
  - `Mittelstand` (ORG: 0.8)
  - `Organisationen` (ORG: 0.774)
  - `Einheite` (ORG: 0.769)
  - `Branch` (ORG: 0.76)

### CV ITALIANO - R.E. (SpaCy Transformer)
- **Backend:** spacy
- **Doc Length:** 7125 chars
- **Entities Found:** 105
- **Processing Time:** 1633ms
- **Entity Types:** {'ORG': 35, 'LOC': 14, 'DATE': 25, 'CUSTOM': 30, 'PERSON': 1}
- **Sample Entities:**
  - `Operations` (ORG: 1.0)
  - `Gestione delle` (ORG: 1.0)
  - `Acquisti/Negoziazione Risorse Umane` (ORG: 1.0)
  - `Palo Alto` (LOC: 1.0)
  - `USA` (LOC: 1.0)

### CV I.S. - FINANZAS (SpaCy Transformer)
- **Backend:** spacy
- **Doc Length:** 4978 chars
- **Entities Found:** 70
- **Processing Time:** 254ms
- **Entity Types:** {'ORG': 38, 'PERSON': 6, 'DATE': 15, 'LOC': 2, 'CUSTOM': 9}
- **Sample Entities:**
  - `EXPERIENCIA PROFESIONAL` (ORG: 1.0)
  - `Ekon` (ORG: 1.0)
  - `ALGECO SAU` (PERSON: 1.0)
  - `YODEYMA SLU ALGECO SAU PERI SAU|Tesorería` (PERSON: 1.0)
  - `ERP` (ORG: 1.0)

### CV - J.L.  PERFIL ALEMAN (SpaCy Transformer)
- **Backend:** spacy
- **Doc Length:** 6687 chars
- **Entities Found:** 51
- **Processing Time:** 337ms
- **Entity Types:** {'DATE': 8, 'ORG': 32, 'CUSTOM': 7, 'LOC': 3, 'PERSON': 1}
- **Sample Entities:**
  - `25 Jahre` (DATE: 1.0)
  - `TGA` (ORG: 1.0)
  - `Handwerk` (ORG: 1.0)
  - `Photovoltaik` (ORG: 1.0)
  - `im Innen- und Außendienst` (ORG: 1.0)

### CV ITALIANO - R.E. (Ollama Qwen3 27B)
- **Backend:** ollama
- **Doc Length:** 7125 chars
- **Entities Found:** 0
- **Processing Time:** 74229ms
- **Entity Types:** {}
- **Sample Entities:**

### CV I.S. - FINANZAS (Ollama Qwen3 27B)
- **Backend:** ollama
- **Doc Length:** 4978 chars
- **Entities Found:** 0
- **Processing Time:** 76813ms
- **Entity Types:** {}
- **Sample Entities:**

### CV - J.L.  PERFIL ALEMAN (Ollama Qwen3 27B)
- **Backend:** ollama
- **Doc Length:** 6687 chars
- **Entities Found:** 1
- **Processing Time:** 58722ms
- **Entity Types:** {'DATE': 1}
- **Sample Entities:**
  - `11/2023 – heute` (DATE: 0.95)
