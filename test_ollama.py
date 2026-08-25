from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import re

llm = ChatOllama(model='qwen3.8:27b-mlx', base_url='http://localhost:11434', temperature=0, format='json', num_predict=2048)

system_prompt = '''You are an expert NER system. Extract PII entities from text. Return ONLY a JSON array with objects: text, label, start, end, score.
Labels: PERSON, ORG, LOC, DATE, EMAIL, PHONE, ADDRESS, ID_NUMBER, CREDIT_CARD, IBAN, IP_ADDRESS, URL, CUSTOM.
Rules: Return ONLY valid JSON array. No markdown, no explanations.
Example: [{{"text": "Juan Pérez", "label": "PERSON", "start": 0, "end": 10, "score": 0.99}}]'''

prompt = ChatPromptTemplate.from_messages([
    ('system', system_prompt),
    ('human', 'Text: {text}\n\nReturn ONLY the JSON array:')
])

chain = prompt | llm

text = 'Juan Pérez vive en Madrid y trabaja en Google. Email: juan@empresa.es'
result = chain.invoke({'text': text})
print('Raw content:')
print(result.content)
print('---')

# Try to extract JSON
json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', result.content, re.DOTALL)
if json_match:
    print('Found JSON in markdown:')
    print(json_match.group(1))
else:
    print('No markdown JSON found')
    # Try bare JSON
    if '[' in result.content and ']' in result.content:
        match = re.search(r'(\[.*\])', result.content, re.DOTALL)
        if match:
            print('Found bare JSON:')
            print(match.group(1))