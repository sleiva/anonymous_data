import json
from pathlib import Path
from typing import Dict, Any, List

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

from ..models.types import Document, Entity, EntityType, ModelBackend


class OllamaNER:
    """Ollama-based NER using LangChain with configurable model parameters."""

    def __init__(
        self,
        model_name: str = "ornith:latest",
        base_url: str = "http://localhost:11434",
        config_path: str = "ollama.json",
        timeout: int = 30,
    ):
        self.model_name = model_name
        self.base_url = base_url
        self.config_path = Path(config_path)
        self.timeout = timeout
        self._llm = None
        self._chain = None
        self._config = self._load_config()
        self._model_params = self._get_model_params()
        self._setup()

    def _load_config(self) -> Dict[str, Any]:
        if self.config_path.exists():
            with open(self.config_path) as f:
                return json.load(f)
        return {}

    def _get_model_params(self) -> Dict[str, Any]:
        models = self._config.get("models", {})
        if self.model_name in models:
            return models[self.model_name].get("parameters", {})
        return self._config.get("recommended_ner_params", {}).get(self.model_name, {})

    def _setup(self):
        params = self._model_params
        system_prompt = self._config.get("global_settings", {}).get("system_prompt", "")
        human_template = self._config.get("global_settings", {}).get(
            "human_template", "Text: {text}\n\nReturn ONLY the JSON array:"
        )

        self._llm = ChatOllama(
            model=self.model_name,
            base_url=self.base_url,
            temperature=params.get("temperature", 0.6),
            top_p=params.get("top_p", 0.95),
            top_k=params.get("top_k", 20),
            repeat_penalty=params.get("repeat_penalty", 1.0),
            min_p=params.get("min_p", 0.0),
            num_predict=params.get("num_predict", 1024),
            timeout=self.timeout,
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_template),
        ])

        self._chain = prompt | self._llm

    def _map_label(self, label: str) -> EntityType:
        label_mapping = self._config.get("label_mapping", {})
        return EntityType(label_mapping.get(label.upper(), label.upper()))

    def _parse_json_response(self, content: str) -> List[Dict]:
        import re
        import json

        if not content:
            return []

        content = content.strip()

        json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', content, re.DOTALL)
        if json_match:
            content = json_match.group(1)

        if not (content.startswith('[') and content.endswith(']')):
            match = re.search(r'(\[.*\])', content, re.DOTALL)
            if match:
                content = match.group(1)

        try:
            parsed = json.loads(content)
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass
        return []

    def predict(self, text: str) -> List[Dict]:
        import re

        try:
            max_chars = self._config.get("global_settings", {}).get("max_chars_per_request", 3000)
            if len(text) > max_chars:
                text = text[:max_chars] + "... [truncated]"

            result = self._chain.invoke({"text": text})
            content = result.content if hasattr(result, 'content') else str(result)

            entities = []
            parsed = self._parse_json_response(content)

            for e in parsed:
                if isinstance(e, dict) and "text" in e and "label" in e:
                    entities.append({
                        "text": str(e.get("text", "")),
                        "label": self._map_label(e.get("label", "CUSTOM")),
                        "start": int(e.get("start", 0)),
                        "end": int(e.get("end", 0)),
                        "score": float(e.get("score", 0.5)),
                    })
            return entities
        except Exception as e:
            print(f"Ollama error: {e}")
            return []

    def process_document(self, doc: Document) -> Document:
        entities_data = self.predict(doc.text)
        entities = []
        for e in entities_data:
            entities.append(type('Entity', (), {
                'text': e.get('text', ''),
                'label': e.get('label'),
                'start': e.get('start', 0),
                'end': e.get('end', 0),
                'score': e.get('score', 0.5),
                'model_backend': ModelBackend.HF_TRANSFORMERS,
            })())
        doc.entities = entities
        return doc


def get_available_models(config_path: str = "ollama.json") -> Dict[str, Dict]:
    """Get available models from config."""
    config_path = Path(config_path)
    if not config_path.exists():
        return {}
    with open(config_path) as f:
        config = json.load(f)
    return config.get("models", {})


def get_recommended_params(model_name: str, config_path: str = "ollama.json") -> Dict:
    """Get recommended parameters for a model."""
    config_path = Path(config_path)
    if not config_path.exists():
        return {}
    with open(config_path) as f:
        config = json.load(f)
    return config.get("recommended_ner_params", {}).get(model_name, {})