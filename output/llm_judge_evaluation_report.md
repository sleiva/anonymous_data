# LLM-as-Judge Evaluation Report
**Judge Model:** mrm8488 BERT Spanish (configured separately)
**Total Comparisons:** 45

## Pairwise Results

| Model A | Model B | Winner | Model A Overall | Model B Overall |
|---------|---------|--------|-----------------|-----------------|
| mrm8488 BERT Spanish | BETO NER | TIE | 0.00 | 0.00 |
| mrm8488 BERT Spanish | BERTin NER | TIE | 0.00 | 0.00 |
| mrm8488 BERT Spanish | BERT English (baseline) | B | 0.00 | 0.00 |
| mrm8488 BERT Spanish | SpaCy Transformer | B | 0.00 | 0.00 |
| mrm8488 BERT Spanish | Ollama Qwen3 27B | B | 0.00 | 0.00 |
| BETO NER | BERTin NER | TIE | 0.00 | 0.00 |
| BETO NER | BERT English (baseline) | B | 0.00 | 0.00 |
| BETO NER | SpaCy Transformer | B | 0.00 | 0.00 |
| BETO NER | Ollama Qwen3 27B | B | 0.00 | 0.00 |
| BERTin NER | BERT English (baseline) | B | 0.00 | 0.00 |
| BERTin NER | SpaCy Transformer | B | 0.00 | 0.00 |
| BERTin NER | Ollama Qwen3 27B | B | 0.00 | 0.00 |
| BERT English (baseline) | SpaCy Transformer | B | 0.00 | 0.00 |
| BERT English (baseline) | Ollama Qwen3 27B | A | 0.00 | 0.00 |
| SpaCy Transformer | Ollama Qwen3 27B | A | 0.00 | 0.00 |
| mrm8488 BERT Spanish | BETO NER | A | 0.00 | 0.00 |
| mrm8488 BERT Spanish | BERTin NER | TIE | 0.00 | 0.00 |
| mrm8488 BERT Spanish | BERT English (baseline) | A | 0.00 | 0.00 |
| mrm8488 BERT Spanish | SpaCy Transformer | B | 0.00 | 0.00 |
| mrm8488 BERT Spanish | Ollama Qwen3 27B | A | 0.00 | 0.00 |
| BETO NER | BERTin NER | TIE | 0.00 | 0.00 |
| BETO NER | BERT English (baseline) | A | 0.00 | 0.00 |
| BETO NER | SpaCy Transformer | B | 0.00 | 0.00 |
| BETO NER | Ollama Qwen3 27B | A | 0.00 | 0.00 |
| BERTin NER | BERT English (baseline) | TIE | 0.00 | 0.00 |
| BERTin NER | SpaCy Transformer | B | 0.00 | 0.00 |
| BERTin NER | Ollama Qwen3 27B | A | 0.00 | 0.00 |
| BERT English (baseline) | SpaCy Transformer | B | 0.00 | 0.00 |
| BERT English (baseline) | Ollama Qwen3 27B | A | 0.00 | 0.00 |
| SpaCy Transformer | Ollama Qwen3 27B | A | 0.00 | 0.00 |
| mrm8488 BERT Spanish | BETO NER | A | 0.00 | 0.00 |
| mrm8488 BERT Spanish | BERTin NER | TIE | 0.00 | 0.00 |
| mrm8488 BERT Spanish | BERT English (baseline) | B | 0.00 | 0.00 |
| mrm8488 BERT Spanish | SpaCy Transformer | B | 0.00 | 0.00 |
| mrm8488 BERT Spanish | Ollama Qwen3 27B | B | 0.00 | 0.00 |
| BETO NER | BERTin NER | TIE | 0.00 | 0.00 |
| BETO NER | BERT English (baseline) | B | 0.00 | 0.00 |
| BETO NER | SpaCy Transformer | B | 0.00 | 0.00 |
| BETO NER | Ollama Qwen3 27B | B | 0.00 | 0.00 |
| BERTin NER | BERT English (baseline) | B | 0.00 | 0.00 |
| BERTin NER | SpaCy Transformer | B | 0.00 | 0.00 |
| BERTin NER | Ollama Qwen3 27B | B | 0.00 | 0.00 |
| BERT English (baseline) | SpaCy Transformer | B | 0.00 | 0.00 |
| BERT English (baseline) | Ollama Qwen3 27B | B | 0.00 | 0.00 |
| SpaCy Transformer | Ollama Qwen3 27B | B | 0.00 | 0.00 |

## Win Counts

- **SpaCy Transformer**: 14 wins
- **BERT English (baseline)**: 8 wins
- **Ollama Qwen3 27B**: 8 wins
- **mrm8488 BERT Spanish**: 4 wins
- **BETO NER**: 2 wins
- **BERTin NER**: 1 wins

## Detailed Evaluations

### mrm8488 BERT Spanish vs BETO NER
**Winner:** TIE
**Reasoning:** Both models completely fail to identify any actual PII entities from the input text. The true entities include organizations (e.g., Sightglass Vision Inc, CooperVision, EssilorLuxottica, IMPRIMA SPA, TP Reflex Group), locations (e.g., Palo Alto, USA, Como, Varese, Italy, Poland, Turkey), and dates (e.g., Febbraio 2022 – Ad oggi). Neither model detects any of these. Instead, both outputs consist of token fragments and false positives, likely due to applying Spanish-language models to Italian text. Model A produces fragments like 'Auto', 'Deloc', '##zazio', and incorrectly labels 'Rio' as LOC. Model B produces long nonsensical spans and fragments like 'PROFI', '##ENZE' as ORG, and 'Auto'. No correct entity grouping or typing is present. Anonymized texts are empty, so anonymization quality cannot be assessed and is scored zero. Overall, both models are equally ineffective for this task.
**Notes:** Both models are Spanish BERT variants applied to Italian text, causing severe tokenization and entity recognition failures. No true PII entities were detected; all outputs are false positives or meaningless fragments. Anonymized texts were not provided, so anonymization quality is zero.

### mrm8488 BERT Spanish vs BERTin NER
**Winner:** TIE
**Reasoning:** Both models failed to identify any actual PII entities from the input text. Model A produced subword fragments (e.g., 'Auto', 'Deloc', '##zazio') with incorrect labels, while Model B produced large, irrelevant text spans labeled as CUSTOM. Neither model detected company names, locations, dates, or other PII. No anonymized text was provided, so anonymization quality cannot be assessed.
**Notes:** Both outputs are severely flawed: Model A splits words into subword tokens and mislabels them; Model B captures long, non-PII text spans as CUSTOM entities. Neither model identified any correct entity (ORG, LOC, DATE, etc.). Anonymized texts were empty, so anonymization quality was set to 0.0 for both.

### mrm8488 BERT Spanish vs BERT English (baseline)
**Winner:** B
**Reasoning:** Model A is completely unusable: it outputs subword fragments (e.g., '##zazio', '##du', '##ve') due to tokenization mismatch, with no real PII entities detected, resulting in zero precision and recall. Model B at least identifies some true entities such as 'Palo Alto' (LOC), 'USA' (LOC), and 'CooperVision' (ORG), but it misses most organizations, locations, and all dates, and includes false positives like 'Deloc', 'Lea', 'dell', and 'Feb'. Therefore Model B is better, though both are poor.
**Notes:** No anonymized text was produced by either model, so anonymization score is 0. Model A appears to be a Spanish model applied to Italian text, causing severe tokenization issues. Model B has some correct entity types but low recall and many false positives.

### mrm8488 BERT Spanish vs SpaCy Transformer
**Winner:** B
**Reasoning:** Model A produces only subword fragments (e.g., 'Auto', 'Deloc', '##zazio', 'Rio') that are not valid named entities, resulting in zero precision, recall, and grouping. Model B, while imperfect, correctly identifies several entities such as 'Palo Alto' (LOC), 'USA' (LOC), 'Febbraio 2022' (DATE), 'CooperVision' (ORG), and 'Dicembre 2018' (DATE). However, Model B also has false positives (e.g., 'Gestione delle' as ORG, 'Acquisti/Negoziazione Risorse Umane' as ORG) and misses many actual PII entities (e.g., 'Sightglass Vision Inc', 'EssilorLuxottica', 'IMPRIMA SPA', 'Como', 'Varese', 'Italy', 'Poland', 'Turkey', 'Luglio 2016'). Overall, Model B is clearly better than Model A.
**Notes:** Model A is unusable for NER due to subword tokenization artifacts. Model B shows some capability but suffers from low recall and several false positives, especially treating generic phrases as organizations. No anonymized text was provided for either model, so anonymization quality could not be assessed.

### mrm8488 BERT Spanish vs Ollama Qwen3 27B
**Winner:** B
**Reasoning:** Model A outputs subword fragments from a Spanish BERT tokenizer (e.g., '##zazio', '##du', '##ve') that do not correspond to any actual PII entities. It has 10 false positives and zero true positives, resulting in precision 0.0 and recall 0.0. Model B outputs no entities, so it has zero false positives (perfect precision) but also zero true positives (recall 0.0). Given the equal weighting of precision and recall, Model B's avoidance of false positives gives it a slight overall advantage, though both models fail to detect any PII. Anonymization is absent in both outputs.
**Notes:** Model A's output is unusable due to tokenization artifacts and incorrect entity labels. Model B likely failed due to language mismatch or inability to detect entities in the Italian text. Neither model produced anonymized text, so anonymization quality is zero for both.

### BETO NER vs BERTin NER
**Winner:** TIE
**Reasoning:** Both models completely fail to detect any PII entities. They output random text fragments, punctuation, and formatting artifacts as CUSTOM entities with low confidence. No actual PII such as names, organizations, locations, dates, or contact information is identified. The anonymized texts are empty, so anonymization quality cannot be evaluated. Therefore, both models have zero precision, recall, grouping, typing, and anonymization performance.
**Notes:** Both models are not suitable for PII detection on this Italian CV. BETO is a Spanish model and BERTin is not fine-tuned for NER. The input contains markdown formatting that confuses the models, leading to nonsensical entity spans. No real PII is detected, and no anonymization is performed.

### BETO NER vs BERT English (baseline)
**Winner:** B
**Reasoning:** Model A fails completely: it detects no actual PII entities, instead returning long, meaningless CUSTOM spans and one incorrect ORG fragment ('##ENZE'). Its precision, recall, grouping, and typing are all effectively zero. Model B, while still poor, correctly identifies at least three real entities: 'Palo Alto' (LOC), 'USA' (LOC), and 'CooperVision' (ORG). However, Model B also produces many false positives (e.g., 'Deloc', 'P & L', 'Lea', 'Operations and Manufacturing', 'dell', 'Feb') and misses most actual PII such as 'SIGHTGLASSVISION INC', 'IMPRIMA SPA', 'Como', 'Varese', 'EssilorLuxottica', and all dates. Neither model provides anonymized text, so anonymization quality is zero for both. Overall, Model B is better because it at least identifies some true entities, but both are far from acceptable.
**Notes:** Model A output is essentially noise with no real PII. Model B has some correct entities but suffers from high false positive rate and low recall. No anonymized text was provided for either model.

### BETO NER vs SpaCy Transformer
**Winner:** B
**Reasoning:** Model B (SpaCy Transformer) significantly outperforms Model A (BETO NER) on this Italian CV text. Model A produces only fragmented, meaningless entities (e.g., 'PROFI', '##ENZE', random text spans) with no valid PII detection, resulting in near-zero precision and recall. Model B correctly identifies several real PII entities such as locations (Palo Alto, USA), dates (Febbraio 2022, Dicembre 2018), and an organization (CooperVision), though it also includes some false positives (e.g., 'Operations', 'Gestione delle' as ORG) and misses many other organizations and locations. Overall, Model B demonstrates better precision, recall, grouping, and typing, making it the clear winner.
**Notes:** Model A fails to detect any meaningful PII, outputting only subword fragments and random text spans. Model B identifies some correct entities but has notable false positives and low recall, missing many organizations (SIGHTGLASSVISION INC, IMPRIMA SPA, TP REFLEX GROUP, EssilorLuxottica) and locations (Como, Varese, Italy, Poland, Turkey). Anonymization quality could not be assessed as no anonymized text was provided.

### BETO NER vs Ollama Qwen3 27B
**Winner:** B
**Reasoning:** Model A produces 10 entities, all of which are false positives or tokenization artifacts (e.g., 'PROFI', 'Auto', '##ENZE', long spans of non-PII text). It fails to identify any actual PII such as organizations, locations, or dates. Model B detects no entities, which means it also misses all PII, but it does not introduce false positives. In a PII detection context, false positives can lead to harmful over-redaction, so Model B's empty output is marginally less problematic. Both models have zero recall and no anonymization, but Model B's precision is vacuously perfect, giving it a slight overall edge.
**Notes:** Both models are inadequate for PII detection on this text. Model A hallucinates irrelevant fragments, while Model B fails to detect any entities. The input contains clear PII (organizations like Sightglass Vision Inc, Imprima Spa, TP Reflex Group; locations like Palo Alto, Como, Varese; and dates), but neither model identifies them. Model B is chosen only because it avoids false positives.

### BERTin NER vs BERT English (baseline)
**Winner:** B
**Reasoning:** Model A produces only arbitrary text chunks labeled as CUSTOM, with no meaningful PII entities detected. It fails completely on precision, recall, grouping, and typing. Model B, while still poor, at least identifies some real entities such as 'USA' (LOC), 'Palo Alto' (LOC), and 'CooperVision' (ORG). However, Model B also has many false positives (e.g., 'Deloc', 'P&L', 'Lea', 'Feb') and misses most actual PII (organizations, locations, dates). Overall, Model B is clearly better than Model A, but both are far from acceptable for PII detection.
**Notes:** Model A output is unusable: all entities are CUSTOM and consist of random text fragments. Model B has some correct entities but suffers from truncation ('Deloc', 'Lea'), false positives ('P&L', 'Operations and Manufacturing', 'dell', 'Feb'), and low recall (misses Sightglass Vision Inc, EssilorLuxottica, IMPRIMA SPA, Como, TP REFLEX GROUP, Varese, Italy, Poland, Turkey, dates, etc.). Anonymized texts are empty for both models, so anonymization quality is scored 0.

### BERTin NER vs SpaCy Transformer
**Winner:** B
**Reasoning:** Model A outputs meaningless text fragments labeled as CUSTOM, with no actual PII entities detected, resulting in zero precision, recall, grouping, typing, and anonymization quality. Model B identifies several correct entities (e.g., Palo Alto, USA, Febbraio 2022, CooperVision, Dicembre 2018) with correct types and grouping, but it also produces false positives (e.g., 'Operations', 'Gestione delle', 'Acquisti/Negoziazione Risorse Umane', 'Logistica & Supply Chain Centralizzata') and misses many PII entities present in the text (e.g., SIGHTGLASSVISION INC, EssilorLuxottica, IMPRIMA SPA, TP REFLEX GROUP, Como, Varese, Italia, Polonia, Turchia, Germania, Luglio 2016, second Dicembre 2018). Anonymized texts were not provided, so anonymization quality is scored 0 for both.
**Notes:** Model A is completely ineffective for PII detection. Model B shows some capability but suffers from low recall and several false positives, indicating it is not reliable for comprehensive PII anonymization.

### BERTin NER vs Ollama Qwen3 27B
**Winner:** B
**Reasoning:** Model A produces 10 false positive entities, all labeled CUSTOM, which are arbitrary text spans and do not correspond to any actual PII (names, organizations, locations, dates, etc.). This results in zero precision and zero recall, and would lead to incorrect redaction if anonymization were applied. Model B produces no entities, so it has no false positives (perfect precision) but also zero recall, leaving all PII unredacted. While both models fail to detect any PII, Model B is less harmful because it does not introduce incorrect annotations. Therefore, Model B is slightly better overall.
**Notes:** Model A's output is nonsensical, detecting random text chunks as CUSTOM entities. Model B detects nothing, which is at least clean but useless for PII anonymization. Neither model identifies any actual PII such as company names, locations, or dates present in the resume.

### BERT English (baseline) vs SpaCy Transformer
**Winner:** B
**Reasoning:** Model B demonstrates significantly better precision and recall compared to Model A. Model A produces many false positives (e.g., 'Deloc', 'P&L', 'Lea', 'Feb' as ORG) and misses nearly all real organizations and dates. Model B correctly identifies key locations (Palo Alto, USA), dates (Febbraio 2022, Dicembre 2018), and one organization (CooperVision), with fewer false positives. While both models have low recall, Model B's entity typing and grouping are more accurate, making it the superior output.
**Notes:** Anonymized texts were not provided, so anonymization quality was scored neutrally at 0.5 for both models. Model A suffers from severe fragmentation and misclassification, while Model B still misses many entities (e.g., SIGHTGLASSVISION INC, IMPRIMA SPA, Como, Varese) but shows better handling of dates and locations.

### BERT English (baseline) vs Ollama Qwen3 27B
**Winner:** A
**Reasoning:** Model A identifies at least some true PII entities (Palo Alto, USA, CooperVision) despite many false positives from truncated words and non-PII terms. Model B identifies no entities at all, resulting in zero recall and no anonymization capability. Although Model B has no false positives, its complete failure to detect any PII makes it worse for the task of PII anonymization. Therefore Model A is better, but both models perform poorly.
**Notes:** Model A found 3 true positives out of 10 detections, with 7 false positives (e.g., 'Deloc', 'P&L', 'Lea', 'Feb'). Model B found no entities, so precision is set to 0 due to no true positives. Neither model produced anonymized text, so anonymization quality is 0 for both.

### SpaCy Transformer vs Ollama Qwen3 27B
**Winner:** A
**Reasoning:** Model A detects at least some PII entities (locations, dates, organizations) despite several false positives and many missed entities. Model B detects zero entities, providing no anonymization value. While Model A's precision and recall are low, it is clearly more useful than Model B, which fails completely.
**Notes:** Model A correctly identifies Palo Alto, USA, CooperVision, and several dates, but mislabels job titles and department names as ORG and misses many true entities (e.g., IMPRIMA SPA, Como, TP REFLEX GROUP, Varese, Luglio 2016, Italia, Polonia, Turchia, Germania). Model B returns no entities, so it cannot anonymize any PII. Anonymized texts are empty for both models.

### mrm8488 BERT Spanish vs BETO NER
**Winner:** A
**Reasoning:** Model A correctly identifies 'ALGECO SAU' as a single ORG entity, which is a key company name. It also detects 'YODEYMA' and 'ICO' as entities, though with incorrect types (CUSTOM instead of ORG). However, it produces several subword false positives like 'PRO', 'AL', '##U', 'SA', and 'Sistemas'. Model B, on the other hand, generates massive false positive spans that include large chunks of unrelated text, splits 'ALGECO' and 'SAU' into separate tokens, and also misclassifies 'ICO'. Both models miss many true entities, but Model A's errors are less catastrophic and its grouping of 'ALGECO SAU' is superior.
**Notes:** No anonymized text was provided, so anonymization scores are neutral (0.5). Model A's main advantage is correct grouping of 'ALGECO SAU' and fewer large false positive spans. Both models suffer from low recall and typing errors, especially misclassifying organizations as CUSTOM.

### mrm8488 BERT Spanish vs BERTin NER
**Winner:** TIE
**Reasoning:** 
**Notes:** 

### mrm8488 BERT Spanish vs BERT English (baseline)
**Winner:** A
**Reasoning:** Both models perform poorly due to subword tokenization and miss most PII entities in the text. However, Model A captures slightly more complete and meaningful entities such as 'ALGECO SAU' and 'YODEYMA', while Model B outputs many meaningless fragments like '##Z', 'E', '##P', and '##IENCIA'. Model A has marginally better precision and grouping, though both have very low recall and no anonymization was provided.
**Notes:** Both outputs are severely degraded by subword tokenization. Model A identifies 'ALGECO SAU' and 'YODEYMA' as more complete spans, while Model B fragments 'YODEYMA SLU' into 'Y' and '##ODEYMA SL'. Neither model provides anonymized text, so anonymization quality is zero for both.

### mrm8488 BERT Spanish vs SpaCy Transformer
**Winner:** B
**Reasoning:** Model B, despite errors, identifies several real entities including date ranges and some organization names (Ekon, ALGECO SAU, SANTANDER DIGITAL ASSETS). Model A is severely degraded by subword tokenization, producing fragments like 'PRO', 'AL', '##U', and 'SA', with almost no usable entities. Model B has better precision, recall, grouping, and typing, though both fail to provide anonymized text.
**Notes:** Model A's output is dominated by BERT subword artifacts, making it nearly useless. Model B correctly detects three date ranges and some organizations, but mislabels ALGECO SAU as PERSON and merges multiple companies into one entity. No anonymized text was provided by either model, so anonymization quality is scored as 0.

### mrm8488 BERT Spanish vs Ollama Qwen3 27B
**Winner:** A
**Reasoning:** Model A at least identified some entities, including 'ALGECO SAU' as ORG and 'YODEYMA' (though mislabeled as CUSTOM), while Model B found no entities at all. Although Model A has many false positives and poor grouping due to subword tokenization, its recall is non-zero, making it marginally better than Model B's complete failure to detect any PII.
**Notes:** Model A's output is heavily fragmented due to subword tokenization (e.g., '##GECO SAU', '##U'), leading to low precision and grouping. It also mislabels many entities as CUSTOM instead of ORG. Model B produced no output, resulting in zero recall. Neither model provided anonymized text, so anonymization quality is scored as 0 for both.

### BETO NER vs BERTin NER
**Winner:** TIE
**Reasoning:** 
**Notes:** 

### BETO NER vs BERT English (baseline)
**Winner:** A
**Reasoning:** Model A at least identifies some real organization entities (ALGECO, YODEYMA, ICO) despite poor grouping and many false-positive CUSTOM spans. Model B is severely degraded by using an English tokenizer on Spanish text, producing subword fragments like '##Z', '##P', and '##IENCIA' that are not meaningful PII entities. Both models have very low recall and poor precision, but Model A is less unusable.
**Notes:** No anonymized text was provided for either model, so anonymization quality is scored 0.0. Model A's CUSTOM entities often span long non-PII text, and it splits multi-word organizations (e.g., ALGECO SAU into ALGECO, ##GECO, SAU). Model B's output is dominated by subword fragments from an English tokenizer applied to Spanish, making it nearly useless for NER.

### BETO NER vs SpaCy Transformer
**Winner:** B
**Reasoning:** Model B correctly identifies several key entities such as dates and some organization names (Ekon, SANTANDER DIGITAL ASSETS) despite type errors and grouping issues. Model A produces mostly long CUSTOM spans that are not PII, misses nearly all actual entities, and fragments organization names into subword tokens. Model B has higher precision and recall, though both fail to anonymize.
**Notes:** Model A's CUSTOM entities are long text fragments, not PII; it splits ALGECO into ALGECO and ##GECO, and misses all dates. Model B detects some dates and orgs but mislabels companies as PERSON and groups multiple companies into one entity. Neither model provided anonymized text, so anonymization quality is zero.

### BETO NER vs Ollama Qwen3 27B
**Winner:** A
**Reasoning:** Model A at least attempted to identify some entities, including a few company names (ALGECO, YODEYMA) even though they are fragmented and surrounded by many false positives. Model B found no entities at all, resulting in zero recall. Both models perform poorly, but Model A has a marginal advantage in recall and grouping, despite very low precision and incorrect typing.
**Notes:** Model A produces many false positives as large CUSTOM chunks and fragments company names (e.g., ALGECO, ##GECO, SAU). Model B fails to detect any PII. Neither model is suitable for anonymization; anonymized texts are empty.

### BERTin NER vs BERT English (baseline)
**Winner:** TIE
**Reasoning:** 
**Notes:** 

### BERTin NER vs SpaCy Transformer
**Winner:** B
**Reasoning:** Model B has higher precision and recall, and slightly better grouping and typing. Model A produces many false positives (CUSTOM entities that are not PII) and splits company names into fragments, while Model B correctly identifies some complete company names and date ranges, though it also has grouping errors and false positives. Both models have low recall, but Model B finds more true PII entities.
**Notes:** Anonymized texts were not provided, so anonymization quality could not be assessed; both models were given a neutral score of 0.5. Model A has severe grouping issues (e.g., 'ALGECO', 'SAU', 'SA', 'U' as separate entities) and many false positives labeled CUSTOM. Model B incorrectly labels 'ALGECO SAU' as PERSON and merges multiple company names into one entity, but it correctly identifies several date ranges and the company 'Ekon'. Both models miss many PII entities present in the text, resulting in low recall.

### BERTin NER vs Ollama Qwen3 27B
**Winner:** A
**Reasoning:** Model A at least identifies some organization entities (ALGECO, YODEYMA, etc.) from the resume, despite many false positives and poor grouping. Model B detects no entities at all, resulting in zero recall and no anonymization. While Model A's precision and grouping are weak, it provides partial value, making it the better output.
**Notes:** Model A mislabels non-PII spans as CUSTOM, splits multi-word company names (e.g., ALGECO SAU into ALGECO, SA, U), and misses many organizations. Model B fails completely by returning no entities.

### BERT English (baseline) vs SpaCy Transformer
**Winner:** B
**Reasoning:** Model B (SpaCy Transformer) produces more meaningful entities compared to Model A (BERT English baseline), which outputs subword fragments like '##Z' and 'E' that are not valid entities. Model B correctly identifies some organizations (Ekon) and dates, though it has errors in entity typing and grouping. Model A has extremely low precision and recall, failing to capture most PII and generating many false positives. Overall, Model B is better despite its own inaccuracies.
**Notes:** Model A is a BERT English model applied to Spanish text, resulting in subword tokenization and meaningless entities. Model B identifies some correct entities but mislabels organizations as persons and groups multiple entities incorrectly. Neither model performs anonymization, so anonymization scores are 0.0.

### BERT English (baseline) vs Ollama Qwen3 27B
**Winner:** A
**Reasoning:** Model A at least identifies some true organization entities such as 'ALGECO SA', 'ICO', and 'YODEYMA SL', despite severe subword tokenization artifacts from using an English BERT model on Spanish text. Model B returns no entities at all, resulting in zero recall and no anonymization. Although Model A has low precision and poor grouping, it is the only output with any correct detections, making it the better of the two.
**Notes:** Model A suffers from subword tokenization (e.g., '##Z', '##P', '##IENCIA') causing many false positives and fragmented entities. Model B produced no entities, so recall is zero. Neither model provided anonymized text.

### SpaCy Transformer vs Ollama Qwen3 27B
**Winner:** A
**Reasoning:** Model A detected 10 entities, including some correct dates and organization names, but suffered from false positives (e.g., 'EXPERIENCIA PROFESIONAL', 'ERP', 'Axapta') and incorrect typing/grouping (e.g., 'ALGECO SAU' as PERSON, 'YODEYMA SLU ALGECO SAU PERI SAU|Tesorería' as a single PERSON). Model B detected no entities at all, resulting in zero recall and no useful output. Although Model A's precision and typing are imperfect, it at least identified some true PII, making it clearly better than Model B.
**Notes:** Model A found some correct dates and organizations but mislabeled several entities and grouped unrelated tokens together. Model B produced no entities, so recall is zero. Neither model provided anonymized text, so anonymization quality is scored 0 for both.

### mrm8488 BERT Spanish vs BETO NER
**Winner:** A
**Reasoning:** Both models perform poorly because the input text contains no explicit PII entities (no names, emails, phone numbers, etc.) in the visible portion. Therefore, all detected entities are false positives. Model A at least identifies individual words or subwords (e.g., 'Management', 'Operation', 'Service') and attempts one ORG label, while Model B groups large, nonsensical spans including punctuation and partial phrases (e.g., 'P R O F I L Mehr als 25 Jahre Erfahrung im', ',', '##men und, vom Mittelstand bis zum Konzern. Experte'). Model A's output is less chaotic and slightly more structured, making it the better of the two despite both being incorrect.
**Notes:** No anonymized text was provided, so anonymization quality is scored 0 for both. Recall is set to 1.0 because there are no true PII entities in the visible input, so no false negatives occurred. The main differentiator is grouping and precision: Model A produces smaller, word-like false positives, while Model B produces large, punctuation-inclusive false spans.

### mrm8488 BERT Spanish vs BERTin NER
**Winner:** TIE
**Reasoning:** Both models completely fail to detect any PII entities. Model A outputs fragments of common German words (e.g., 'Erfa', 'Un', 'Prozes') and one incorrect ORG label ('Organ'), while Model B outputs arbitrary text spans including newlines and punctuation (e.g., '\n\nMehr als 25 Jahre', ' und\n\n'). Neither model identifies actual PII such as the location 'Viernheim' (truncated as 'Viernhei...') or any person/organization names. Both produce only false positives, no correct grouping, no correct typing, and no anonymization. Therefore, they are equally ineffective.
**Notes:** Both outputs are nonsensical and not usable for PII detection. The input text contains minimal PII (possibly a location), but neither model captures it. Anonymized texts are empty, indicating no anonymization was performed.

### mrm8488 BERT Spanish vs BERT English (baseline)
**Winner:** B
**Reasoning:** Both models perform poorly because they are applied to German text using Spanish and English language models, respectively, and the input contains no explicit PII entities. The correct output should be empty. Model A produces highly fragmented and meaningless entities (e.g., 'Erfa', 'Un', 'Mit', '. Experte', 'Prozes', 'Organ', 'Einhe') with inconsistent labels (CUSTOM and ORG). Model B, while still incorrect, at least identifies some complete German words (e.g., 'Mittelstand', 'Organisationen', 'TGA', 'Handwerk', 'Photovoltaik', 'Montage') and uses a consistent ORG label. Thus, Model B is slightly better in grouping and typing, though both have zero precision and recall.
**Notes:** The input text is a German CV with no explicit PII (no names, emails, etc.). Both models incorrectly detect non-PII words as entities. Model A's output is more fragmented and uses non-standard labels. Model B's output is less fragmented and uses a consistent label, but still false positives. Anonymization is not performed, so that criterion is neutral.

### mrm8488 BERT Spanish vs SpaCy Transformer
**Winner:** B
**Reasoning:** Model A produces only fragmented, non-PII tokens with generic CUSTOM labels and one incorrect ORG label, resulting in zero true positives and no useful entity detection. Model B at least identifies some date entities (e.g., '11/2023') and groups a multi-word phrase, but it mislabels industry sectors as ORG and misses several dates and the location. Overall, Model B is less incorrect and partially useful, while Model A is essentially noise.
**Notes:** Model A's output consists of truncated word fragments and irrelevant tokens, with no valid PII entities. Model B correctly identifies one date and groups a phrase, but misclassifies eight industry terms as ORG and misses other dates and the location 'Viernheim'. Neither model provides anonymized text, so anonymization quality is zero for both.

### mrm8488 BERT Spanish vs Ollama Qwen3 27B
**Winner:** B
**Reasoning:** Model B correctly identified a date entity ('11/2023 – heute') with high precision and correct typing, while Model A produced 10 false positives (e.g., 'Management', 'Operation', 'Prozes') and no true PII entities, likely because it is a Spanish model applied to German text. Model B's recall is low (missed other dates like '06/23 – 10/223' and '2022 – heute'), but it is still far better than Model A's zero recall. Neither model provided anonymized text, so anonymization quality is scored 0 for both.
**Notes:** Model A is a Spanish NER model misapplied to German text, resulting in many false positives and incorrect labels (CUSTOM). Model B correctly identifies one date but misses other dates and possibly a location. Anonymization was not performed by either model.

### BETO NER vs BERTin NER
**Winner:** TIE
**Reasoning:** Both models completely fail to identify any PII entities. The input text contains no personal identifiers (names, emails, phone numbers, etc.), yet both models output 10 false positive entities, all labeled as CUSTOM with nonsensical spans (including punctuation and partial words). Neither model demonstrates any precision, recall, correct grouping, or typing. Anonymization is absent in both. Therefore, they are equally poor and there is no meaningful difference.
**Notes:** Both models hallucinate entities on a text with no PII. Model A includes punctuation and fragmented phrases; Model B splits words and includes whitespace. Neither output is useful for PII detection or anonymization.

### BETO NER vs BERT English (baseline)
**Winner:** B
**Reasoning:** Model B, despite using an English BERT on German text, produces more coherent entity spans (mostly industry terms) compared to Model A, which outputs random text fragments and punctuation as entities. Model A's output is essentially unusable, with no meaningful PII detection. Model B at least identifies some organization-like terms, though they are not true PII. Both models fail to detect actual PII such as dates or locations, resulting in zero recall for both. Overall, Model B is marginally better due to higher precision, grouping, and typing scores.
**Notes:** Both models are severely underperforming due to language mismatch (Spanish BETO and English BERT applied to German text). Model A detects arbitrary spans including punctuation, while Model B detects fragmented words and generic industry terms. Neither model identifies true PII like dates (e.g., 11/2023) or locations (e.g., Viernheim). Anonymization outputs are empty, so anonymization quality is scored as 0.

### BETO NER vs SpaCy Transformer
**Winner:** B
**Reasoning:** Model B, while still poor, at least identifies some temporal expressions (dates) and groups multi-word phrases correctly, whereas Model A produces nonsensical entities including punctuation and random text fragments, with no meaningful typing. Model A's output is essentially noise, while Model B has some limited value despite mislabeling many industry terms as organizations.
**Notes:** Anonymized texts were not provided, so anonymization quality could not be assessed; both models were given a neutral score of 0.5. Model A detects only CUSTOM entities, many of which are punctuation or arbitrary text spans, resulting in zero precision and recall. Model B correctly identifies some dates (e.g., '11/2023') and groups multi-word expressions, but mislabels industry terms as ORG and misses other dates and locations, leading to low precision and recall.

### BETO NER vs Ollama Qwen3 27B
**Winner:** B
**Reasoning:** Model B correctly identified a date entity ('11/2023 – heute') with the appropriate DATE label, demonstrating at least some precision and correct typing. Model A produced 10 arbitrary text spans labeled as CUSTOM, none of which correspond to actual PII, resulting in zero precision and recall. Model A's grouping is also poor, as it splits text into meaningless fragments. Since no anonymized text was provided, anonymization quality cannot be assessed and is scored as 0 for both.
**Notes:** Model A's output is entirely false positives with no meaningful entity grouping or typing. Model B found one correct date but missed other dates present in the text (e.g., '06/23 – 10/223', '2022 – heute'), leading to low recall. Anonymization was not performed by either model, so that criterion is not applicable.

### BERTin NER vs BERT English (baseline)
**Winner:** B
**Reasoning:** Both models perform poorly on PII detection, as neither identifies actual PII entities (e.g., names, emails, dates, locations) from the resume text. Model A outputs arbitrary text fragments labeled as CUSTOM with no meaningful entity boundaries or types, while Model B at least labels some entities as ORG (though they are industry terms, not PII) and has slightly better grouping (though subword tokens like '##ternehmen' indicate tokenization issues). Model B's use of a standard entity type and more coherent spans makes it marginally less bad, but both fail to detect any true PII.
**Notes:** Both models are unsuitable for PII detection on this text. Model A's entities are nonsensical spans with a generic CUSTOM label, while Model B misclassifies industry terms as ORG. Neither detects dates (e.g., '11/2023') or location ('Viernhei...') that appear in the text. Anonymization is absent in both outputs.

### BERTin NER vs SpaCy Transformer
**Winner:** B
**Reasoning:** Model B performs slightly better because it identifies at least one true PII entity (the date '11/2023') and uses standard entity types (DATE, ORG), even though most of its ORG labels are incorrect. Model A produces meaningless word fragments with a custom label, failing to detect any PII. Both models are poor for this text, which contains few explicit PII entities, but Model B is less bad.
**Notes:** Model A fragments words and labels everything as CUSTOM, making it useless for PII detection. Model B correctly identifies one date but mislabels industry terms (e.g., 'TGA', 'Handwerk', 'Photovoltaik') as ORG and misses other dates like '06/23' and '2022'. Neither model provides anonymized text, so anonymization quality is zero for both.

### BERTin NER vs Ollama Qwen3 27B
**Winner:** B
**Reasoning:** Model A detected 10 entities, but all are non-PII text fragments (e.g., 'Mehr als 25 Jahre', 'Erfahrung', 'im', 'Management') labeled as CUSTOM, resulting in zero precision and recall. Model B detected one correct DATE entity ('11/2023 – heute') with high confidence, which is a valid PII type. Although Model B missed other dates and possibly a location, it at least produced a meaningful, correctly typed entity, making it clearly better than Model A's entirely false positives.
**Notes:** Model A's output is entirely false positives with fragmented word spans and meaningless CUSTOM labels. Model B correctly identifies one date but misses other dates (e.g., '06/23 – 10/223', '2022 – heute') and possibly a location ('Viernhei...'). No anonymized text was provided by either model, so anonymization quality is scored as 0 for both.

### BERT English (baseline) vs SpaCy Transformer
**Winner:** B
**Reasoning:** Model B is clearly better because it correctly identifies date entities (e.g., '11/2023') and maintains proper entity grouping without subword token artifacts. Model A produces subword tokens like '##ternehmen' and '##te Elektrotechnik', which are not valid entities, and it misses all date expressions. Both models have low precision due to labeling industry terms as ORG, but Model B at least has correct grouping and some correct typing.
**Notes:** No anonymized text was provided for either model, so anonymization quality is scored 0. Model A suffers from severe subword tokenization and false positives, while Model B has better grouping but still misclassifies industry terms as organizations. The input text contains few true PII entities; the main PII-like elements are dates and a truncated location, which Model B partially captures.

### BERT English (baseline) vs Ollama Qwen3 27B
**Winner:** B
**Reasoning:** Model B correctly identifies a date range ('11/2023 – heute') with high precision and correct typing, while Model A produces subword tokens and mislabels generic terms as organizations, resulting in zero precision and recall. Model B's output is far more accurate despite missing some entities.
**Notes:** Model A is a BERT English baseline applied to German text, leading to subword tokenization and false positives. Model B correctly identifies one date but misses other dates and a location. Anonymization was not provided by either model, so anonymization scores are set to 0.

### SpaCy Transformer vs Ollama Qwen3 27B
**Winner:** B
**Reasoning:** Model B correctly identifies one DATE entity ('11/2023 – heute') with exact span and correct type, achieving perfect precision and grouping for that entity. Model A produces many false positives, labeling industry sectors (TGA, Handwerk, Photovoltaik, etc.) as ORG and misclassifying '25 Jahre' as DATE, resulting in zero correct detections. Although Model B has low recall (misses two other dates), its output is far more reliable than Model A's noisy predictions.
**Notes:** Anonymized texts were not provided, so anonymization quality is set to neutral (0.5) for both. Model A's false positives severely hurt precision and typing. Model B's only weakness is low recall, missing two other DATE entities in the text.
