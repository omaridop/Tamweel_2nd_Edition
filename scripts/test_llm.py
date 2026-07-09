import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from app.pipeline.llm import get_client
from app.pipeline.config import settings

def test_chat():
    print('Testing Chat Completions...')
    client = get_client()
    try:
        res = client.chat.completions.create(
            model=settings.CHAT_MODEL,
            messages=[{'role': 'user', 'content': 'Hello, say PASS if you receive this.'}],
            max_tokens=10
        )
        if res.choices[0].message.content:
            print('Chat: PASS')
        else:
            print('Chat: FAIL (Empty response)')
    except Exception as e:
        print(f'Chat: FAIL ({e})')

def test_embed():
    print('Testing Embeddings...')
    client = get_client()
    try:
        res = client.embeddings.create(
            model=settings.EMBED_MODEL,
            input='Hello',
            encoding_format='float',
            dimensions=settings.EMBED_DIM
        )
        if res.data and len(res.data) > 0:
            print('Embeddings: PASS')
        else:
            print('Embeddings: FAIL (Empty response)')
    except Exception as e:
        print(f'Embeddings: FAIL ({e})')

if __name__ == '__main__':
    test_chat()
    test_embed()
