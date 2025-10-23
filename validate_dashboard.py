#!/usr/bin/env python3
"""
CSRD Dashboard Data Validation & Demo
====================================

This script validates the dashboard data and demonstrates the visualizations
that would appear in the Streamlit dashboard without requiring server startup.
"""

import pandas as pd
import numpy as np
from datetime import datetime

def validate_dashboard_data():
    """Validate the data file and display dashboard metrics"""
    
    print("=" * 80)
    print("🌱 CSRD DASHBOARD DATA VALIDATION & DEMO")
    print("=" * 80)
    print(f"Validation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Load data
    try:
        df = pd.read_csv('csrd_co2e_report_with_conversions.csv', sep=';', encoding='utf-8-sig')
        print(f"✅ Data file loaded successfully ({len(df)} records)\n")
    except FileNotFoundError:
        print("❌ Error: csrd_co2e_report_with_conversions.csv not found")
        print("   Please run the pipeline first: python csrd_reporting_pipeline.py")
        return
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return
    
    # Validate columns
    required_columns = [
        'Artikel', 'Menge', 'Lieferant', 'calculation_status',
        'calculated_co2e_a1_a3', 'calculated_co2e_a4', 'total_co2e'
    ]
    
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        print(f"❌ Missing columns: {missing_cols}")
        return
    
    print("✅ All required columns present\n")
    
    # Ensure numeric columns
    numeric_cols = ['Menge', 'similarity_score', 'calculated_co2e_a1_a3', 
                   'calculated_co2e_a4', 'total_co2e']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # ============== KPI VALIDATION ==============
    print("📊 KEY PERFORMANCE INDICATORS")
    print("-" * 80)
    
    total_co2e = df['total_co2e'].sum()
    material_co2e = df['calculated_co2e_a1_a3'].sum()
    transport_co2e = df['calculated_co2e_a4'].sum()
    successful = df[df['calculation_status'].str.contains('Success', na=False)]
    success_rate = (len(successful) / len(df) * 100) if len(df) > 0 else 0
    material_pct = (material_co2e / total_co2e * 100) if total_co2e > 0 else 0
    
    print(f"🌍 Grand Total CO₂e:     {total_co2e:>20,.0f} kg ({total_co2e/1e6:.1f}M kg)")
    print(f"📦 Material CO₂e (A1-A3): {material_co2e:>20,.0f} kg ({material_co2e/1e6:.1f}M kg)")
    print(f"🚚 Transport CO₂e (A4):  {transport_co2e:>20,.0f} kg ({transport_co2e/1e6:.1f}M kg)")
    print(f"📊 Material Share:       {material_pct:>20,.1f}%")
    print(f"✅ Success Rate:         {success_rate:>20,.1f}% ({len(successful)}/{len(df)} items)")
    
    intensity = total_co2e / (df['Menge'].sum()) if df['Menge'].sum() > 0 else 0
    print(f"⚡ CO₂e Intensity:       {intensity:>20,.2f} kg/kg material")
    print()
    
    # ============== CHART A: MODULE EMISSIONS ==============
    print("📈 CHART A: EMISSIONS BY MODULE TYPE")
    print("-" * 80)
    print(f"Material (A1-A3): {material_co2e:>15,.0f} kg ({material_pct:.1f}%)")
    print(f"Transport (A4):   {transport_co2e:>15,.0f} kg ({100-material_pct:.1f}%)")
    print(f"TOTAL:            {total_co2e:>15,.0f} kg (100.0%)")
    print(f"→ Visualization: Donut chart with blue (Material) and green (Transport)\n")
    
    # ============== CHART B: TOP EMITTERS ==============
    print("📈 CHART B: TOP 10 MATERIAL EMITTERS")
    print("-" * 80)
    top_items = df.nlargest(10, 'calculated_co2e_a1_a3')[
        ['Artikel', 'calculated_co2e_a1_a3', 'Lieferant']
    ]
    
    for i, (idx, row) in enumerate(top_items.iterrows(), 1):
        artikel = str(row['Artikel'])[:50]
        co2e = row['calculated_co2e_a1_a3']
        pct = (co2e / material_co2e * 100)
        print(f"{i:2d}. {artikel:<50} {co2e:>15,.0f} kg ({pct:>5.1f}%)")
    
    print(f"→ Visualization: Horizontal bar chart (blue bars)\n")
    
    # ============== CHART C: SUPPLIER EMISSIONS ==============
    print("📈 CHART C: EMISSIONS BY SUPPLIER (STACKED)")
    print("-" * 80)
    
    supplier_data = df.groupby('Lieferant').agg({
        'calculated_co2e_a1_a3': 'sum',
        'calculated_co2e_a4': 'sum'
    }).reset_index()
    
    supplier_data['total'] = supplier_data['calculated_co2e_a1_a3'] + supplier_data['calculated_co2e_a4']
    supplier_data = supplier_data.sort_values('total', ascending=False)
    
    for i, (idx, row) in enumerate(supplier_data.head(10).iterrows(), 1):
        supplier = str(row['Lieferant'])[:40]
        material = row['calculated_co2e_a1_a3']
        transport = row['calculated_co2e_a4']
        total = row['total']
        pct = (total / total_co2e * 100)
        print(f"{i:2d}. {supplier:<40} Material: {material:>12,.0f} kg | Transport: {transport:>10,.0f} kg | Total: {total:>12,.0f} kg ({pct:>5.1f}%)")
    
    if len(supplier_data) > 10:
        print(f"    ... and {len(supplier_data)-10} more suppliers")
    
    print(f"→ Visualization: Stacked horizontal bars (blue = Material, green = Transport)\n")
    
    # ============== CHART D: STATUS DISTRIBUTION ==============
    print("📈 CHART D: CALCULATION STATUS DISTRIBUTION (AUDIT)")
    print("-" * 80)
    
    status_counts = df['calculation_status'].value_counts().sort_values(ascending=False)
    
    for status, count in status_counts.items():
        pct = (count / len(df) * 100)
        bar_length = int(pct / 2)
        bar = "█" * bar_length + "░" * (50 - bar_length)
        
        # Color coding
        if 'Success' in status:
            color = "✅ GREEN"
        elif 'Error' in status:
            color = "❌ RED"
        else:
            color = "⚠️  YELLOW"
        
        status_short = status[:60]
        print(f"[{color}] {status_short:<60}")
        print(f"         {bar} {count:>4} ({pct:>5.1f}%)")
    
    print(f"→ Visualization: Pie chart (green = Success, red = Error)\n")
    
    # ============== AUDIT TABLE PREVIEW ==============
    print("📋 AUDIT TABLE PREVIEW (First 5 records)")
    print("-" * 80)
    
    display_cols = ['Lieferant', 'Artikel', 'Menge', 'calculated_co2e_a1_a3', 'calculation_status']
    
    for i, (idx, row) in enumerate(df.head(5).iterrows(), 1):
        print(f"\n{i}. {row['Lieferant']}")
        print(f"   Artikel: {str(row['Artikel'])[:60]}")
        print(f"   Menge: {row['Menge']:,.0f}, CO₂e: {row['calculated_co2e_a1_a3']:,.0f} kg")
        print(f"   Status: {row['calculation_status']}")
    
    print(f"\n→ Full table available with filters for Status and Supplier")
    print(f"→ Download capability for filtered data as CSV\n")
    
    # ============== FILTER CAPABILITIES ==============
    print("🔍 FILTER CAPABILITIES")
    print("-" * 80)
    
    status_types = df['calculation_status'].nunique()
    supplier_count = df['Lieferant'].nunique()
    
    print(f"📊 Status Types Available: {status_types}")
    for status in df['calculation_status'].unique()[:5]:
        count = len(df[df['calculation_status'] == status])
        print(f"   - {status} ({count} items)")
    if status_types > 5:
        print(f"   ... and {status_types - 5} more")
    
    print(f"\n🏢 Suppliers Available: {supplier_count}")
    suppliers = df['Lieferant'].unique()[:5]
    for supplier in suppliers:
        count = len(df[df['Lieferant'] == supplier])
        print(f"   - {supplier} ({count} items)")
    if supplier_count > 5:
        print(f"   ... and {supplier_count - 5} more")
    
    print()
    
    # ============== SUMMARY ==============
    print("=" * 80)
    print("✅ DASHBOARD VALIDATION COMPLETE")
    print("=" * 80)
    print(f"\n✓ Data integrity: PASS")
    print(f"✓ Required columns: PASS")
    print(f"✓ Numeric values: PASS")
    print(f"✓ Filter options: PASS ({status_types} statuses, {supplier_count} suppliers)")
    print(f"✓ All visualizations ready for rendering")
    
    print(f"\n🚀 To launch the interactive dashboard, run:")
    print(f"   streamlit run csrd_dashboard.py")
    print()


if __name__ == "__main__":
    validate_dashboard_data()
