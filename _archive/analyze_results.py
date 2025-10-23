#!/usr/bin/env python3
"""
CSRD Report Analysis Utilities
=============================

This script provides analysis and visualization tools for the generated
CSRD CO₂ reporting output.

Usage:
    python analyze_results.py
"""

import pandas as pd
import numpy as np
from datetime import datetime

def load_report(filename="csrd_co2e_report.csv"):
    """Load and return the CSRD report"""
    try:
        df = pd.read_csv(filename, sep=';', encoding='utf-8-sig')
        print(f"✅ Loaded report: {len(df)} records from {filename}")
        return df
    except FileNotFoundError:
        print(f"❌ Report file '{filename}' not found. Run the pipeline first!")
        return None
    except Exception as e:
        print(f"❌ Error loading report: {e}")
        return None

def analyze_calculation_status(df):
    """Analyze the success/failure rates of calculations"""
    print("\n" + "="*60)
    print("📊 CALCULATION STATUS ANALYSIS")
    print("="*60)
    
    status_counts = df['calculation_status'].value_counts()
    total = len(df)
    
    print(f"\n📈 Success/Error Breakdown:")
    for status, count in status_counts.items():
        percentage = (count / total) * 100
        print(f"   • {status}: {count:,} ({percentage:.1f}%)")
    
    # Successful calculations only
    successful = df[df['calculation_status'].str.contains('Success', na=False)]
    if len(successful) > 0:
        print(f"\n✅ Successful Calculations: {len(successful)}/{total} ({len(successful)/total*100:.1f}%)")
        print(f"   • Total CO₂e from successful: {successful['total_co2e'].sum():,.2f} kg CO₂e")
        print(f"   • Average CO₂e per item: {successful['total_co2e'].mean():,.2f} kg CO₂e")

def analyze_suppliers(df):
    """Analyze CO₂e by supplier"""
    print("\n" + "="*60)
    print("🏢 SUPPLIER ANALYSIS")
    print("="*60)
    
    supplier_summary = df.groupby('Lieferant').agg({
        'Menge': 'sum',
        'total_co2e': 'sum',
        'Artikel': 'count'
    }).round(2)
    
    supplier_summary.columns = ['Total_Weight_kg', 'Total_CO2e_kg', 'Item_Count']
    supplier_summary['CO2e_Intensity'] = (supplier_summary['Total_CO2e_kg'] / 
                                         supplier_summary['Total_Weight_kg']).round(4)
    
    # Sort by total CO₂e
    supplier_summary = supplier_summary.sort_values('Total_CO2e_kg', ascending=False)
    
    print(f"\n📋 Top Suppliers by CO₂e Impact:")
    for i, (supplier, row) in enumerate(supplier_summary.head(5).iterrows(), 1):
        print(f"   {i}. {supplier}")
        print(f"      • Items: {row['Item_Count']} | Weight: {row['Total_Weight_kg']:,.0f} kg")
        print(f"      • CO₂e: {row['Total_CO2e_kg']:,.0f} kg | Intensity: {row['CO2e_Intensity']:.4f} kg CO₂e/kg")

def analyze_materials(df):
    """Analyze CO₂e by material categories"""
    print("\n" + "="*60)
    print("🔬 MATERIAL CATEGORY ANALYSIS")
    print("="*60)
    
    # Group by matched category
    category_summary = df.groupby('matched_category').agg({
        'total_co2e': ['sum', 'count', 'mean'],
        'similarity_score': 'mean'
    }).round(2)
    
    category_summary.columns = ['Total_CO2e', 'Item_Count', 'Avg_CO2e_per_Item', 'Avg_Similarity']
    category_summary = category_summary.sort_values('Total_CO2e', ascending=False)
    
    print(f"\n📋 Top Material Categories by CO₂e:")
    for i, (category, row) in enumerate(category_summary.head(5).iterrows(), 1):
        category_short = category[:50] + "..." if len(category) > 50 else category
        print(f"   {i}. {category_short}")
        print(f"      • Total CO₂e: {row['Total_CO2e']:,.0f} kg | Items: {row['Item_Count']}")
        print(f"      • Avg per item: {row['Avg_CO2e_per_Item']:,.0f} kg | Match quality: {row['Avg_Similarity']:.3f}")

def analyze_units(df):
    """Analyze unit distribution and success rates"""
    print("\n" + "="*60)
    print("📏 UNIT ANALYSIS")
    print("="*60)
    
    unit_analysis = df.groupby(['matched_oeko_unit', 'calculation_status']).size().unstack(fill_value=0)
    
    print(f"\n📊 Unit Distribution and Success Rates:")
    for unit in unit_analysis.index:
        total = unit_analysis.loc[unit].sum()
        successful = unit_analysis.loc[unit].get('Success: kg unit', 0) + \
                    unit_analysis.loc[unit].get('Success: m³ unit', 0)
        success_rate = (successful / total * 100) if total > 0 else 0
        
        print(f"   • {unit}: {total} items ({success_rate:.1f}% success)")

def generate_executive_summary(df):
    """Generate a comprehensive executive summary"""
    print("\n" + "="*80)
    print("📋 EXECUTIVE SUMMARY - DETAILED ANALYSIS")
    print("="*80)
    
    total_items = len(df)
    total_weight = df['Menge'].sum()
    total_material_co2e = df['calculated_co2e_a1_a3'].sum()
    total_transport_co2e = df['calculated_co2e_a4'].sum()
    total_co2e = df['total_co2e'].sum()
    
    successful_calcs = len(df[df['calculation_status'].str.contains('Success', na=False)])
    avg_similarity = df['similarity_score'].mean()
    
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Dataset Overview:")
    print(f"   • Total materials: {total_items:,} items")
    print(f"   • Total weight: {total_weight:,.2f} kg")
    print(f"   • Successful calculations: {successful_calcs:,} ({successful_calcs/total_items*100:.1f}%)")
    print(f"   • Average matching similarity: {avg_similarity:.3f}")
    
    print(f"\n🌍 Carbon Footprint Summary:")
    print(f"   • Material CO₂e (A1-A3): {total_material_co2e:,.2f} kg CO₂e")
    print(f"   • Transport CO₂e (A4): {total_transport_co2e:,.2f} kg CO₂e")
    print(f"   • TOTAL PROJECT CO₂e: {total_co2e:,.2f} kg CO₂e")
    
    print(f"\n📈 Key Performance Indicators:")
    co2e_intensity = total_co2e / total_weight if total_weight > 0 else 0
    print(f"   • Overall CO₂e intensity: {co2e_intensity:.4f} kg CO₂e/kg material")
    
    material_transport_ratio = total_material_co2e / total_transport_co2e if total_transport_co2e > 0 else 0
    print(f"   • Material:Transport ratio: {material_transport_ratio:.1f}:1")
    
    # Equivalent conversions
    co2e_tons = total_co2e / 1000
    print(f"\n🔄 Equivalent Measures:")
    print(f"   • Total CO₂e: {co2e_tons:,.2f} tonnes")
    print(f"   • Per kg material: {co2e_intensity:.4f} kg CO₂e/kg")

def main():
    """Main analysis function"""
    print("🔍 CSRD REPORT ANALYSIS TOOL")
    print("=" * 40)
    
    # Load the report
    df = load_report()
    if df is None:
        return
    
    # Run all analyses
    analyze_calculation_status(df)
    analyze_suppliers(df)
    analyze_materials(df)
    analyze_units(df)
    generate_executive_summary(df)
    
    print(f"\n✅ Analysis completed!")
    print(f"📄 Analyzed {len(df)} records from CSRD report")

if __name__ == "__main__":
    main()
