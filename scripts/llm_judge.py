#!/usr/bin/env python
"""
LLM-as-Judge for NER/Anonymization Evaluation
Uses powerful Ollama cloud models to evaluate and compare NER model outputs.
"""

import json
import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from pathlib import Path

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate


@dataclass
class JudgeEvaluation:
    """Evaluation result from LLM judge."""
    model_a: str
    model_b: str
    winner: str  # "A", "B", "TIE"
    reasoning: str
    scores: Dict[str, Dict[str, float]]  # model -> {precision, recall, f1, overall}
    notes: str


class LLMJudge:
    """LLM-as-Judge for comparing NER model outputs."""

    def __init__(
        self,
        judge_model: str = "deepseek-v4-pro:cloud",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.1,
    ):
        self.judge_model = judge_model
        self.base_url = base_url
        self.temperature = temperature
        self._llm = None
        self._setup()

    def _setup(self):
        """Initialize the LLM and prompt templates."""
        self._llm = ChatOllama(
            model=self.judge_model,
            base_url=self.base_url,
            temperature=self.temperature,
            num_predict=4096,
        )

# System prompt for evaluation - all curly braces doubled to escape
        self.system_prompt = (
            "You are an expert evaluator for Named Entity Recognition (NER) systems, "
            "specialized in PII (Personally Identifiable Information) detection and anonymization.\n\n"
            "Your task: Compare TWO NER model outputs on the SAME input text and determine which is better.\n\n"
            "EVALUATION CRITERIA (weighted):\n"
            "1. Precision (30%): Are detected entities actually PII? Few false positives.\n"
            "2. Recall (30%): Are all PII entities found? Few false negatives.\n"
            "3. Entity Grouping (20%): Multi-word entities correctly grouped "
            "(e.g., Juan Perez as ONE PERSON, not two).\n"
            "4. Entity Typing (15%): Correct labels (PERSON, ORG, LOC, DATE, EMAIL, etc.)\n"
            "5. Anonymization Quality (5%): If anonymized, does it preserve readability while hiding PII?\n\n"
            "SCORING: Rate each model 0.0-1.0 on each criterion, then compute weighted overall.\n\n"
            "OUTPUT FORMAT: Return ONLY valid JSON:\n"
            "{{\n"
            "  \"winner\": \"A\" | \"B\" | \"TIE\",\n"
            "  \"reasoning\": \"Detailed explanation of why...\",\n"
            "  \"scores\": {{\n"
            "    \"model_a\": {{\"precision\": 0.85, \"recall\": 0.90, \"grouping\": 0.95, "
            "\"typing\": 0.88, \"anonymization\": 0.92, \"overall\": 0.89}},\n"
            "    \"model_b\": {{\"precision\": 0.75, \"recall\": 0.80, \"grouping\": 0.70, "
            "\"typing\": 0.82, \"anonymization\": 0.85, \"overall\": 0.77}}\n"
            "  }},\n"
            "  \"notes\": \"Key observations...\"\n"
            "}}"
        )

        self.eval_prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human",
                "Compare these two NER model outputs on the same text:\n\n"
                "**INPUT TEXT:**\n{input_text}\n\n"
                "**MODEL A ({model_a_name}) OUTPUT:**\n"
                "Entities found: {model_a_count}\n"
                "{model_a_entities}\n\n"
                "**MODEL B ({model_b_name}) OUTPUT:**\n"
                "Entities found: {model_b_count}\n"
                "{model_b_entities}\n\n"
                "**ANONYMIZED TEXT A:**\n{anon_a}\n\n"
                "**ANONYMIZED TEXT B:**\n{anon_b}\n\n"
                "Evaluate and return ONLY the JSON format specified.")
        ])

        self.chain = self.eval_prompt | self._llm

    def evaluate_pair(
        self,
        input_text: str,
        model_a_name: str,
        model_a_entities: List[Dict],
        model_a_anon: str,
        model_b_name: str,
        model_b_entities: List[Dict],
        model_b_anon: str,
    ) -> JudgeEvaluation:
        """Compare two model outputs."""

        # Format entities for display
        def format_entities(entities):
            if not entities:
                return "  (none)"
            lines = []
            for e in entities[:20]:  # Limit to top 20
                label = e.get('label', e.get('type', 'UNKNOWN'))
                text = e.get('text', '')
                score = e.get('score', e.get('confidence', 0))
                start = e.get('start', '?')
                end = e.get('end', '?')
                lines.append(f"  - '{text}' ({label}: {score:.2f}) [{start}:{end}]")
            if len(entities) > 20:
                lines.append(f"  ... and {len(entities) - 20} more")
            return "\n".join(lines)

        try:
            result = self.chain.invoke({
                "input_text": input_text[:3000] + ("... [truncated]" if len(input_text) > 3000 else ""),
                "model_a_name": model_a_name,
                "model_a_count": len(model_a_entities),
                "model_a_entities": format_entities(model_a_entities),
                "model_b_name": model_b_name,
                "model_b_count": len(model_b_entities),
                "model_b_entities": format_entities(model_b_entities),
                "anon_a": model_a_anon[:500] + ("... [truncated]" if len(model_a_anon) > 500 else ""),
                "anon_b": model_b_anon[:500] + ("... [truncated]" if len(model_b_anon) > 500 else ""),
            })

            content = result.content if hasattr(result, 'content') else str(result)

            # Debug: print raw content
            print(f"      [DEBUG] Raw response length: {len(content)}")
            if len(content) < 500:
                print(f"      [DEBUG] Raw: {content[:500]}")
            else:
                print(f"      [DEBUG] Raw start: {content[:200]}...")
                print(f"      [DEBUG] Raw end: {content[-200:]}")

            # Parse JSON response
            parsed = self._parse_json(content)
            print(f"      [DEBUG] Parsed: {parsed}")

            return JudgeEvaluation(
                model_a=model_a_name,
                model_b=model_b_name,
                winner=parsed.get("winner", "TIE"),
                reasoning=parsed.get("reasoning", ""),
                scores=parsed.get("scores", {}),
                notes=parsed.get("notes", ""),
            )

        except Exception as e:
            return JudgeEvaluation(
                model_a=model_a_name,
                model_b=model_b_name,
                winner="ERROR",
                reasoning=f"Judge error: {e}",
                scores={},
                notes=str(e),
            )

    def _parse_json(self, content: str) -> Dict:
        """Extract and parse JSON from response."""
        import re
        import json

        if not content:
            return {}

        content = content.strip()

        # Try markdown code block
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            content = json_match.group(1)
        elif not content.startswith('{'):
            # Try to find JSON object
            match = re.search(r'(\{.*\})', content, re.DOTALL)
            if match:
                content = match.group(1)

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {}

    def evaluate_all_pairs(
        self,
        input_text: str,
        model_outputs: Dict[str, Dict],  # model_name -> {entities, anonymized}
    ) -> List[JudgeEvaluation]:
        """Evaluate all pairwise combinations."""
        models = list(model_outputs.keys())
        evaluations = []

        for i in range(len(models)):
            for j in range(i + 1, len(models)):
                model_a = models[i]
                model_b = models[j]

                print(f"  Judging: {model_a} vs {model_b}...")

                eval_result = self.evaluate_pair(
                    input_text=input_text,
                    model_a_name=model_a,
                    model_a_entities=model_outputs[model_a].get("entities", []),
                    model_a_anon=model_outputs[model_a].get("anonymized", ""),
                    model_b_name=model_b,
                    model_b_entities=model_outputs[model_b].get("entities", []),
                    model_b_anon=model_outputs[model_b].get("anonymized", ""),
                )
                evaluations.append(eval_result)

        return evaluations


def run_llm_judge(
    benchmark_results_file: str = "output/benchmark_results.json",
    judge_model: str = "deepseek-v4-pro:cloud",
    output_file: str = "output/llm_judge_evaluation.json",
) -> List[JudgeEvaluation]:
    """Run LLM judge on benchmark results."""

    # Load benchmark results
    with open(benchmark_results_file) as f:
        benchmark_data = json.load(f)

    # Group by document
    by_doc = {}
    for entry in benchmark_data:
        doc_id = entry["doc_id"]
        if doc_id not in by_doc:
            by_doc[doc_id] = {}
        by_doc[doc_id][entry["model_name"]] = {
            "entities": entry.get("sample_entities", []),
            "anonymized": entry.get("anonymized_text", ""),
        }

    # Load original texts
    from anonymization.utils import load_documents_from_dir_any
    docs = load_documents_from_dir_any("data/cv")
    doc_texts = {d.id: d.text for d in docs}

    # Initialize judge
    judge = LLMJudge(judge_model=judge_model)

    all_evaluations = []

    for doc_id, model_outputs in by_doc.items():
        if len(model_outputs) < 2:
            continue

        input_text = doc_texts.get(doc_id, "")
        if not input_text:
            continue

        print(f"\n{'='*60}")
        print(f"Evaluating document: {doc_id}")
        print(f"{'='*60}")

        evaluations = judge.evaluate_all_pairs(input_text, model_outputs)
        all_evaluations.extend(evaluations)

        # Print summary
        for e in evaluations:
            print(f"  {e.model_a} vs {e.model_b} -> Winner: {e.winner}")
            if e.scores:
                for m, s in e.scores.items():
                    if s:
                        print(f"    {m}: overall={s.get('overall', 0):.2f}")
                    else:
                        print(f"    {m}: overall=0.00 (no scores)")

    # Save results
    with open(output_file, 'w') as f:
        json.dump([asdict(e) for e in all_evaluations], f, indent=2, ensure_ascii=False)

    # Generate summary report
    generate_judge_report(all_evaluations, output_file.replace('.json', '_report.md'))

    return all_evaluations


def generate_judge_report(evaluations: List[JudgeEvaluation], output_file: str):
    """Generate markdown report from judge evaluations."""
    lines = [
        "# LLM-as-Judge Evaluation Report",
        f"**Judge Model:** {evaluations[0].model_a if evaluations else 'N/A'} (configured separately)",
        f"**Total Comparisons:** {len(evaluations)}",
        "",
        "## Pairwise Results",
        "",
        "| Model A | Model B | Winner | Model A Overall | Model B Overall |",
        "|---------|---------|--------|-----------------|-----------------|",
    ]

    # Win counts
    win_counts = {}
    for e in evaluations:
        if e.winner == "A":
            win_counts[e.model_a] = win_counts.get(e.model_a, 0) + 1
        elif e.winner == "B":
            win_counts[e.model_b] = win_counts.get(e.model_b, 0) + 1

        scores_a = e.scores.get(e.model_a, {})
        scores_b = e.scores.get(e.model_b, {})
        lines.append(f"| {e.model_a} | {e.model_b} | {e.winner} | "
                     f"{scores_a.get('overall', 0):.2f} | {scores_b.get('overall', 0):.2f} |")

    lines.extend(["", "## Win Counts", ""])
    for model, wins in sorted(win_counts.items(), key=lambda x: -x[1]):
        lines.append(f"- **{model}**: {wins} wins")

    lines.extend(["", "## Detailed Evaluations", ""])
    for e in evaluations:
        lines.extend([
            f"### {e.model_a} vs {e.model_b}",
            f"**Winner:** {e.winner}",
            f"**Reasoning:** {e.reasoning}",
            f"**Notes:** {e.notes}",
            "",
        ])

    with open(output_file, 'w') as f:
        f.write('\n'.join(lines))

    print(f"Judge report saved to {output_file}")


def main():
    import sys

    judge_model = sys.argv[1] if len(sys.argv) > 1 else "deepseek-v4-pro:cloud"

    print(f"Initializing LLM Judge with model: {judge_model}")
    print("Running evaluation on benchmark results...")

    run_llm_judge(judge_model=judge_model)


if __name__ == "__main__":
    main()