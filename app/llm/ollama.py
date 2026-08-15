import os
import requests

OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://host.docker.internal:11434')
MODEL_NAME = os.getenv('OLLAMA_MODEL', 'qwen3:4b-instruct')

def generate_answer(prompt: str) -> str:
    response = requests.post(f'{OLLAMA_URL}/api/generate', json={'model': MODEL_NAME, 'prompt': prompt, 'stream': False, 'think': False, 'options': {'num_predict': 256, 'temperature': 0.0}}, timeout=180)
    response.raise_for_status()
    data = response.json()
    return data['response'].strip()
