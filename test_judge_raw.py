from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import json
import re

llm = ChatOllama(model='deepseek-v4-pro:cloud', base_url='http://localhost:11434', temperature=0.1, num_predict=2048)

system = '''You are an expert evaluator for Named Entity Recognition (NER) systems.

Your task: Compare TWO NER model outputs on the SAME input text and determine which is better.

OUTPUT FORMAT: Return ONLY valid JSON:
{{
  "winner": "A" | "B" | "TIE",
  "reasoning": "Detailed explanation of why...",
  "scores": {{
    "model_a": {{"precision": 0.85, "recall": 0.90, "grouping": 0.95, "typing": 0.88, "anonymization": 0.92, "overall": 0.89}},
    "model_b": {{"precision": 0.75, "recall": 0.80, "grouping": 0.70, "typing": 0.82, "anonymization": 0.85, "overall": 0.77}}
  }},
  "notes": "Key observations..."
}}'''

prompt = ChatPromptTemplate.from_messages([
    ('system', system),
    ('human', 'Model A: 10 entities (Juan Perez PERSON, Madrid LOC). Model B: 5 entities (Madrid LOC).')
])

chain = prompt | llm
result = chain.invoke({})
print('Raw result:')
print(result.content)
print('---')

# Try to parse
content = result.content.strip()
json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
if json_match:
    print('Found in markdown:')
    print(json_match.group(1))
elif '{' in content and '}' in content:
    match = re.search(r'(\{.*\})', content, re.DOTALL)
    if match:
        print('Found bare JSON:')
        print(match.group(1))
        try:
            parsed = json.loads(match.group(1))
            print('Parsed successfully!')
            print(json.dumps(parsed, indent=2))
        except json.JSONDecodeError as e:
            print('JSON decode error:', e)