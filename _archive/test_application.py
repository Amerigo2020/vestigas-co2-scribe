#!/usr/bin/env python3
"""
CarbonMatch - Application Test Script
======================================

Tests the CarbonMatch pipeline with real data:
- Input: aggregated_construction_site_combined.xlsx
- Input: oekobaudat.csv
- Output: carbomatch_report.csv

Usage:
    python test_application.py
"""

import os
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from carbomatch_pipeline import CarbonMatchPipeline

def print_header(text):
    """Print formatted header"""
    print(f"\n{'=' * 70}")
    print(f"  {text}")
    print(f"{'=' * 70}\n")

def print_section(text):
    """Print section header"""
    print(f"\n> {text}")
    print("-" * 70)

def test_pipeline():
    """Main test function"""
    
    print_header("TEST: CarbonMatch Pipeline Test")
    
    # Check if files exist
    print_section("1️⃣  Checking Input Files")
    
    input_files = {
        "aggregated_construction_site_combined.xlsx": "Delivery data",
        "oekobaudat.csv": "Ökobaudat database"
    }
    
    all_exist = True
    for filename, description in input_files.items():
        filepath = project_root / filename
        exists = filepath.exists()
        status = "[OK]" if exists else "[FAIL]"
        size = f"{filepath.stat().st_size / 1024:.1f} KB" if exists else "N/A"
        print(f"{status} {filename:50s} ({description:20s}) {size}")
        if not exists:
            all_exist = False
    
    if not all_exist:
        print("\n[ERROR] Not all input files found!")
        return False
    
    print("\n[OK] All input files found!")
    
    # Initialize pipeline
    print_section("2️⃣  Initializing Pipeline")
    
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if api_key:
        print("[OK] Azure OpenAI API key found in environment")
    else:
        print("[WARN] No Azure OpenAI API key - will use mock embeddings for demo")
    
    pipeline = CarbonMatchPipeline(api_key=api_key)
    print("[OK] Pipeline initialized successfully")
    
    # Load data
    print_section("3️⃣  Loading Data")
    
    try:
        pipeline.load_and_clean_data(
            weight_path="aggregated_construction_site_combined.xlsx",
            oekobaudat_path="oekobaudat.csv"
        )
        print(f"[OK] Deliveries loaded: {len(pipeline.deliveries_df)} records")
        print(f"[OK] Okobaudat loaded: {len(pipeline.oeko_df)} records (A1-A3 module)")
        
        # Show sample data
        print("\n[DATA] Sample Delivery Data:")
        print(pipeline.deliveries_df.head(3).to_string())
        
        print("\n[DATA] Sample Okobaudat Data:")
        print(pipeline.oeko_df.head(3)[['Name (de)', 'GWPtotal (A2)', 'Rohdichte (kg/m3)']].to_string())
        
    except Exception as e:
        print(f"[ERROR] Error loading data: {e}")
        return False
    
    # Process materials - Step 2: Embeddings & Matching
    print_section("4️⃣  Processing Materials (Step 2-3)")
    
    try:
        print("[PROC] Generating embeddings and matching materials...")
        pipeline.generate_embeddings_and_match()
        print(f"[OK] Matching complete!")
        print(f"   - Matched: {len(pipeline.matched_df)} records")
        print(f"   - Avg similarity: {pipeline.matched_df['similarity_score'].mean():.3f}")
        
        # Step 3: Calculate CO2e
        print("\n[PROC] Calculating CO2e values...")
        pipeline.calculate_all_co2e()
        print(f"[OK] CO2e calculation complete!")
        
        # Step 4: Transport simulation
        print("\n[PROC] Simulating transport CO2e...")
        pipeline.simulate_transport_co2e()
        print(f"[OK] Transport simulation complete!")
        
    except Exception as e:
        print(f"[ERROR] Error processing materials: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Show results
    print_section("5️⃣  Results Summary")
    
    if pipeline.matched_df is not None:
        print("\n[STATS] Statistics:")
        print(f"   Total records: {len(pipeline.matched_df)}")
        
        print("\n[CO2E] CO2e Statistics (kg CO2e):")
        if 'calculated_co2e_a1_a3' in pipeline.matched_df.columns:
            material_co2e = pipeline.matched_df['calculated_co2e_a1_a3'].sum()
            transport_co2e = pipeline.matched_df['calculated_co2e_a4'].sum()
            total_co2e = material_co2e + transport_co2e
            avg_material_co2e = pipeline.matched_df['calculated_co2e_a1_a3'].mean()
            
            print(f"   Material CO2e (A1-A3): {material_co2e:,.1f} kg CO2e")
            print(f"   Transport CO2e (A4): {transport_co2e:,.1f} kg CO2e")
            print(f"   TOTAL: {total_co2e:,.1f} kg CO2e")
            print(f"   Average: {avg_material_co2e:,.1f} kg CO2e per record")
        
        # Show sample results
        print("\n[TOP5] Top 5 CO2e Contributors:")
        display_cols = ['Artikel', 'matched_material', 'similarity_score', 'calculated_co2e_a1_a3']
        available_cols = [col for col in display_cols if col in pipeline.matched_df.columns]
        
        top_5 = pipeline.matched_df.nlargest(5, 'calculated_co2e_a1_a3')
        print(top_5[available_cols].to_string())
    
    # Export report
    print_section("6️⃣  Generating Report")
    
    try:
        pipeline.generate_final_report()
        output_file = project_root / "carbomatch_report.csv"
        
        if output_file.exists():
            size = output_file.stat().st_size / 1024
            print(f"[OK] Report generated: {output_file.name} ({size:.1f} KB)")
            print(f"   Path: {output_file}")
            
            # Show sample
            report_df = pd.read_csv(output_file, sep=';')
            print(f"\n[DATA] Report preview (first 3 rows, selected columns):")
            display_cols = ['Artikel', 'matched_material', 'calculated_co2e_a1_a3', 'calculated_co2e_a4', 'total_co2e']
            available_cols = [col for col in display_cols if col in report_df.columns]
            print(report_df.head(3)[available_cols].to_string())
        else:
            print(f"[ERROR] Report file not found!")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error generating report: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Final summary
    print_header("SUCCESS: TEST COMPLETED SUCCESSFULLY")
    
    print("[SUMMARY] Summary:")
    print(f"   [OK] Pipeline initialized and running")
    print(f"   [OK] Data loaded successfully")
    print(f"   [OK] Materials matched with Okobaudat database")
    print(f"   [OK] CO2e calculations completed")
    print(f"   [OK] Report generated")
    
    print("\n[NEXT] Next Steps:")
    print("   1. Review carbomatch_report.csv")
    print("   2. Launch dashboard: streamlit run carbomatch_dashboard.py")
    print("   3. Check README.md for detailed documentation")
    
    return True

if __name__ == "__main__":
    try:
        success = test_pipeline()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[WARN] Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
