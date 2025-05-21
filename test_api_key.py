#!/usr/bin/env python
"""
Simple test script to verify that the Google API key is working correctly.
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("ERROR: GOOGLE_API_KEY not found in environment.")
    exit(1)

print(f"API Key found: {api_key[:5]}...{api_key[-5:]}")

# Configure genai with the API key
genai.configure(api_key=api_key)

# List available models to verify API key works
try:
    models = genai.list_models()
    print("\nAvailable models:")
    for model in models:
        print(f"- {model.name}")
    
    # Try a simple generation to verify the API key works
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    response = model.generate_content("Hello, world!")
    print("\nGeneration test:")
    print(f"Prompt: 'Hello, world!'")
    print(f"Response: '{response.text}'")
    
    print("\nAPI key is working correctly!")
except Exception as e:
    print(f"\nERROR: Failed to use the API key: {e}")
    exit(1)
