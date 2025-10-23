#!/usr/bin/env python3
"""
Azure OpenAI Integration Test
==============================

Demonstrates how to use Azure OpenAI for embeddings and chat completions.
This script shows the code patterns used in the CSRD pipeline.

Usage:
    python test_azure_openai.py

Requirements:
    - Set OPENAI_API_KEY environment variable before running
    - openai Python package installed
"""

import os
import sys
from openai import AzureOpenAI

# Fix Unicode encoding on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
AZURE_ENDPOINT = "https://aoai-hackathon.openai.azure.com/"
AZURE_API_VERSION = "2024-12-01-preview"
EMBEDDING_MODEL = "text-embedding-ada-002"
CHAT_MODEL = "o4-mini"

# Get API key from environment
api_key = os.environ.get("OPENAI_API_KEY", "")

if not api_key:
    print("⚠️  WARNING: OPENAI_API_KEY environment variable not set")
    print("Please run:")
    print('  $env:OPENAI_API_KEY="your-key-here"')
    exit(1)

print("=" * 70)
print("🔵 Azure OpenAI Integration Test")
print("=" * 70)
print(f"✅ API Key loaded: {api_key[:20]}...{api_key[-10:]}")
print(f"☁️  Endpoint: {AZURE_ENDPOINT}")
print(f"🔧 API Version: {AZURE_API_VERSION}")

try:
    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        api_version=AZURE_API_VERSION,
        azure_endpoint=AZURE_ENDPOINT,
        api_key=api_key,
    )
    print("✅ Azure OpenAI client initialized successfully\n")

    # Test 1: Embeddings
    print("-" * 70)
    print("TEST 1: Text Embeddings")
    print("-" * 70)
    
    test_phrases = [
        "Betonstahl B 500 B 10mm",
        "Transportbeton C30/37",
        "Stahlarmierung Stützen"
    ]
    
    print(f"Generating embeddings for {len(test_phrases)} phrases...\n")
    
    response = client.embeddings.create(
        input=test_phrases,
        model=EMBEDDING_MODEL
    )
    
    for item in response.data:
        embedding = item.embedding
        length = len(embedding)
        print(f"  data[{item.index}] ({test_phrases[item.index]})")
        print(f"    Length: {length} dimensions")
        print(f"    Values: [{embedding[0]:.4f}, {embedding[1]:.4f}, ..., {embedding[length-2]:.4f}, {embedding[length-1]:.4f}]")
    
    print(f"\n  Tokens used:")
    print(f"    Prompt tokens: {response.usage.prompt_tokens}")
    print(f"    Total tokens: {response.usage.total_tokens}")

    # Test 2: Chat Completion
    print("\n" + "-" * 70)
    print("TEST 2: Chat Completion")
    print("-" * 70)
    
    print("\nUser Query: 'Explain what GWP (Global Warming Potential) means in construction materials'")
    print("\nGenerating response...\n")
    
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant specializing in CSRD sustainability reporting and construction materials.",
            },
            {
                "role": "user",
                "content": "Explain what GWP (Global Warming Potential) means in construction materials",
            }
        ],
        max_completion_tokens=500,
        model=CHAT_MODEL
    )
    
    print("Assistant Response:")
    print(response.choices[0].message.content)
    print(f"\nTokens used:")
    print(f"  Prompt tokens: {response.usage.prompt_tokens}")
    print(f"  Completion tokens: {response.usage.completion_tokens}")
    print(f"  Total tokens: {response.usage.total_tokens}")

    # Test 3: Batch Embeddings (CSRD Pipeline Pattern)
    print("\n" + "-" * 70)
    print("TEST 3: Batch Embeddings (CSRD Pipeline Pattern)")
    print("-" * 70)
    
    construction_materials = [
        "Stahlbeton, Ortbeton",
        "Baustahlgewebematte",
        "Transportbeton, Ready Mix Beton",
        "Stahl, Baustahl",
        "Dämmstoffe, Wärmedämmung"
    ]
    
    print(f"\nGenerating embeddings for {len(construction_materials)} construction materials...\n")
    
    response = client.embeddings.create(
        input=construction_materials,
        model=EMBEDDING_MODEL
    )
    
    embeddings = [item.embedding for item in response.data]
    
    print(f"✅ Generated {len(embeddings)} embeddings")
    for i, (material, embedding) in enumerate(zip(construction_materials, embeddings)):
        print(f"  [{i+1}] {material}: {len(embedding)} dimensions")
    
    # Simple similarity example
    print("\n  Similarity Analysis:")
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    
    similarity_matrix = cosine_similarity(embeddings)
    
    for i in range(len(construction_materials)):
        most_similar_idx = np.argsort(similarity_matrix[i])[-2]  # Second highest (first is itself)
        similarity_score = similarity_matrix[i][most_similar_idx]
        print(f"    '{construction_materials[i]}'")
        print(f"      Most similar to: '{construction_materials[most_similar_idx]}'")
        print(f"      Similarity score: {similarity_score:.3f}")

    print("\n" + "=" * 70)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print("\nThe CSRD pipeline uses this same Azure OpenAI integration to:")
    print("  1. Generate embeddings for 2,363 Ökobaudat materials")
    print("  2. Generate embeddings for 456 delivery items")
    print("  3. Match delivery items to Ökobaudat using cosine similarity")
    print("  4. Calculate CO₂e using the matched material GWP factors")

except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {e}")
    print("\nPossible solutions:")
    print("  1. Verify OPENAI_API_KEY is set correctly")
    print("  2. Check Azure endpoint is accessible")
    print("  3. Ensure API key is valid and not expired")
    print("  4. Verify 'text-embedding-ada-002' model is deployed in Azure OpenAI")
    exit(1)
