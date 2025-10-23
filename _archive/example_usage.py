#!/usr/bin/env python3
"""
Example Usage Script for CSRD CO₂ Reporting Pipeline
===================================================

This script demonstrates how to use the CSRD reporting pipeline
with your own OpenAI API key for production use.

Usage:
    python example_usage.py
"""

import os
from csrd_reporting_pipeline import CSRDReportingPipeline

def main():
    """Example of how to use the pipeline with a real API key"""
    
    print("🌱 VESTIGAS CSRD CO₂ REPORTING - EXAMPLE USAGE")
    print("=" * 55)
    
    # Option 1: Set API key as environment variable
    api_key = os.getenv('OPENAI_API_KEY')
    
    # Option 2: Set API key directly (NOT recommended for production)
    # api_key = "sk-your-actual-openai-api-key-here"
    
    if not api_key:
        print("⚠️  WARNING: No OpenAI API key found!")
        print("   Set environment variable: set OPENAI_API_KEY=your-key")
        print("   Or modify this script to include your API key")
        print("   Running in DEMO MODE with mock embeddings...")
        api_key = "VESTIGAS_API_KEY"  # Will trigger demo mode
    else:
        print(f"✅ OpenAI API key found: {api_key[:8]}...")
    
    # Initialize the pipeline
    pipeline = CSRDReportingPipeline(api_key=api_key)
    
    # Execute the complete workflow
    try:
        print("\n🚀 Starting pipeline execution...")
        
        # Step 1: Load and clean data
        pipeline.load_and_clean_data()
        
        # Step 2: Generate embeddings and match materials
        pipeline.generate_embeddings_and_match()
        
        # Step 3: Calculate material CO₂e
        pipeline.calculate_all_co2e()
        
        # Step 4: Simulate transport CO₂e
        pipeline.simulate_transport_co2e()
        
        # Step 5: Generate final report
        pipeline.generate_final_report()
        
        print("\n✅ Pipeline completed successfully!")
        print("📄 Check 'csrd_co2e_report.csv' for results")
        
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        raise

def set_api_key_instructions():
    """Print instructions for setting up OpenAI API key"""
    print("\n" + "="*60)
    print("📋 OPENAI API KEY SETUP INSTRUCTIONS")
    print("="*60)
    print("\n🔑 To use real AI embeddings (recommended for production):")
    print("\n1. Get an OpenAI API key from: https://platform.openai.com/api-keys")
    print("\n2. Set as environment variable:")
    print("   Windows (PowerShell): $env:OPENAI_API_KEY='your-key-here'")
    print("   Windows (CMD):        set OPENAI_API_KEY=your-key-here")
    print("   Linux/Mac:            export OPENAI_API_KEY='your-key-here'")
    print("\n3. Or modify this script to include your key directly")
    print("\n💡 The pipeline works in demo mode without an API key,")
    print("   but real embeddings provide much better matching accuracy!")
    print("="*60)

if __name__ == "__main__":
    # Show API key setup instructions
    set_api_key_instructions()
    
    # Run the main pipeline
    main()
