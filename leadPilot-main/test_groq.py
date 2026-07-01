#!/usr/bin/env python
"""Test Groq API connectivity"""
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

print(f"Testing Groq API Key: {GROQ_API_KEY[:10]}...")
print(f"Using Model: {GROQ_MODEL}")

try:
    client = Groq(api_key=GROQ_API_KEY)
    print("✓ Groq client initialized successfully")
    
    # Test with a simple message
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": "ping"}],
        max_tokens=10
    )
    print("✓ Groq API test successful!")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
