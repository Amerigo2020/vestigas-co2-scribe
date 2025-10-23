#!/usr/bin/env python3
"""
CarbonMatch - CO₂ Emissions Dashboard
=====================================

Interactive Streamlit dashboard for visualizing carbon footprint compliance,
audit trails, and performance metrics with comprehensive filtering and drill-down.

Run with: streamlit run carbomatch_dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="CarbonMatch - CO₂ Emissions Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .metric-value {
        font-size: 2.5em;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 0.9em;
        opacity: 0.9;
    }
    .success-card {
        background: linear-gradient(135deg, #00b894 0%, #00a868 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .dashboard-title {
        text-align: center;
        color: #1e3c72;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)


@st.cache_data
def load_data(filepath="carbomatch_report.csv"):
    """Load and cache the CarbonMatch report data"""
    try:
        df = pd.read_csv(filepath, sep=';', encoding='utf-8-sig')
        # Ensure numeric columns
        numeric_cols = ['Menge', 'similarity_score', 'calculated_co2e_a1_a3', 
                       'calculated_co2e_a4', 'total_co2e']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None


def calculate_kpis(df):
    """Calculate key performance indicators"""
    if df is None or len(df) == 0:
        return {}
    
    total_co2e = df['total_co2e'].sum()
    material_co2e = df['calculated_co2e_a1_a3'].sum()
    transport_co2e = df['calculated_co2e_a4'].sum()
    
    # Calculate success rate - check for 'Success' in calculation_status
    successful = df[df['calculation_status'].str.contains('Success', na=False)]
    success_rate = (len(successful) / len(df) * 100) if len(df) > 0 else 0
    
    # Material percentage
    material_pct = (material_co2e / total_co2e * 100) if total_co2e > 0 else 0
    
    return {
        'total_co2e': total_co2e,
        'material_co2e': material_co2e,
        'transport_co2e': transport_co2e,
        'success_rate': success_rate,
        'material_pct': material_pct,
        'total_items': len(df),
        'successful_items': len(successful),
        'failed_items': len(df) - len(successful)
    }


def create_supplier_category_chart(df):
    """Create pie chart for supplier emissions - group small ones as 'Others'"""
    supplier_emissions = df.groupby('Lieferant')['calculated_co2e_a1_a3'].sum().sort_values(ascending=False)
    total_emissions = supplier_emissions.sum()
    
    # Calculate percentages
    supplier_pcts = (supplier_emissions / total_emissions * 100)
    
    # Split into major (>1%) and minor (<1%)
    major_suppliers = supplier_pcts[supplier_pcts >= 1.0]
    minor_suppliers = supplier_pcts[supplier_pcts < 1.0]
    
    # Build chart data
    labels = list(major_suppliers.index)
    values = [supplier_emissions[s] for s in labels]
    colors_palette = px.colors.qualitative.Set3
    
    # Add "Others" if there are minor suppliers
    others_count = len(minor_suppliers)
    if others_count > 0:
        labels.append(f"Others ({others_count} supplier{'s' if others_count > 1 else ''})")
        values.append(minor_suppliers.sum() * total_emissions / 100)
    
    # Ensure enough colors
    colors = [colors_palette[i % len(colors_palette)] for i in range(len(labels))]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors),
        textinfo='label+percent',
        textposition='inside',
        hovertemplate='<b>%{label}</b><br>CO₂e: %{value:,.0f} kg<br>Share: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title="Material Emissions by Supplier (A1-A3, <1% grouped as Others)",
        height=400,
        showlegend=True,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    return fig, others_count, len(major_suppliers)


def create_top_emitters_chart(df, top_n=10):
    """Create horizontal bar chart for top material emitters"""
    top_items = df.nlargest(top_n, 'calculated_co2e_a1_a3')[
        ['Artikel', 'calculated_co2e_a1_a3', 'Lieferant']
    ].copy()
    
    # Truncate artikel names for display
    top_items['Artikel_short'] = top_items['Artikel'].str[:40]
    
    fig = go.Figure(data=[go.Bar(
        y=top_items['Artikel_short'],
        x=top_items['calculated_co2e_a1_a3'],
        orientation='h',
        marker=dict(color='#1e3c72'),
        text=top_items['calculated_co2e_a1_a3'].apply(lambda x: f'{x:,.0f} kg'),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>CO₂e: %{x:,.0f} kg<extra></extra>'
    )])
    
    fig.update_layout(
        title=f"Top {top_n} Material Emitters (A1-A3)",
        xaxis_title="CO₂e (kg)",
        yaxis_title="Material Item",
        height=400,
        showlegend=False,
        margin=dict(l=200, r=50, t=50, b=50)
    )
    
    fig.update_xaxes(tickformat=',')
    
    return fig


def create_supplier_emissions_chart(df):
    """Create stacked bar chart for emissions by supplier"""
    supplier_data = df.groupby('Lieferant').agg({
        'calculated_co2e_a1_a3': 'sum',
        'calculated_co2e_a4': 'sum'
    }).reset_index()
    
    supplier_data['total'] = supplier_data['calculated_co2e_a1_a3'] + supplier_data['calculated_co2e_a4']
    supplier_data = supplier_data.sort_values('total', ascending=True)  # Ascending for horizontal stacking
    
    fig = go.Figure()
    
    # Add Material CO₂e (blue)
    fig.add_trace(go.Bar(
        y=supplier_data['Lieferant'],
        x=supplier_data['calculated_co2e_a1_a3'],
        name='Material CO₂e (A1-A3)',
        marker=dict(color='#1e3c72'),
        orientation='h',
        hovertemplate='<b>%{y}</b><br>Material: %{x:,.0f} kg<extra></extra>'
    ))
    
    # Add Transport CO₂e (green)
    fig.add_trace(go.Bar(
        y=supplier_data['Lieferant'],
        x=supplier_data['calculated_co2e_a4'],
        name='Transport CO₂e (A4)',
        marker=dict(color='#00b894'),
        orientation='h',
        hovertemplate='<b>%{y}</b><br>Transport: %{x:,.0f} kg<extra></extra>'
    ))
    
    fig.update_layout(
        title="Emissions by Supplier (Stacked)",
        barmode='stack',
        xaxis_title="CO₂e (kg)",
        yaxis_title="Supplier",
        height=400 + max(0, (len(supplier_data) - 8) * 20),
        showlegend=True,
        hovermode='y unified',
        margin=dict(l=250, r=50, t=50, b=50)
    )
    
    fig.update_xaxes(tickformat=',')
    
    return fig


def create_status_distribution_chart(df):
    """Create pie chart for calculation status distribution"""
    status_counts = df['calculation_status'].value_counts().reset_index()
    status_counts.columns = ['status', 'count']
    
    # Define colors: Success in green, errors in red
    colors = []
    for status in status_counts['status']:
        if 'Success' in status:
            colors.append('#00b894')
        elif 'Error' in status:
            colors.append('#d63031')
        else:
            colors.append('#fdcb6e')
    
    fig = go.Figure(data=[go.Pie(
        labels=status_counts['status'],
        values=status_counts['count'],
        marker=dict(colors=colors),
        textinfo='label+percent+value',
        textposition='inside',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title="Calculation Status Distribution (Audit)",
        height=400,
        showlegend=True,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    return fig


def main():
    """Main dashboard application"""
    
    # Title and header with Professional Logo
    st.markdown("""
    <div style='display: flex; align-items: center; margin-bottom: 30px; gap: 20px;'>
        <!-- CarbonMatch Team Logo SVG -->
        <svg width="120" height="120" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
            <!-- Leaf -->
            <g id="leaf">
                <ellipse cx="50" cy="60" rx="18" ry="35" fill="none" stroke="#2ecc71" stroke-width="3" transform="rotate(-35 50 60)"/>
                <path d="M 50 30 Q 55 45 50 65" fill="none" stroke="#2ecc71" stroke-width="2"/>
            </g>
            <!-- Puzzle piece 1 -->
            <g id="puzzle1" transform="translate(80, 40)">
                <rect x="0" y="0" width="35" height="35" fill="none" stroke="#3498db" stroke-width="2.5" rx="3"/>
                <circle cx="35" cy="17" r="6" fill="none" stroke="#3498db" stroke-width="2.5"/>
            </g>
            <!-- Puzzle piece 2 -->
            <g id="puzzle2" transform="translate(80, 75)">
                <rect x="0" y="0" width="35" height="35" fill="none" stroke="#3498db" stroke-width="2.5" rx="3"/>
                <circle cx="0" cy="17" r="6" fill="none" stroke="#3498db" stroke-width="2.5"/>
            </g>
            <!-- Puzzle piece 3 -->
            <g id="puzzle3" transform="translate(115, 57)">
                <rect x="0" y="0" width="35" height="35" fill="none" stroke="#3498db" stroke-width="2.5" rx="3"/>
                <circle cx="17" cy="35" r="6" fill="none" stroke="#3498db" stroke-width="2.5"/>
            </g>
            <!-- Connection lines -->
            <line x1="115" y1="75" x2="130" y2="92" stroke="#95a5a6" stroke-width="1.5" stroke-dasharray="3,3"/>
            <line x1="115" y1="55" x2="130" y2="70" stroke="#95a5a6" stroke-width="1.5" stroke-dasharray="3,3"/>
        </svg>
        
        <div>
            <h1 style='margin: 0; color: #1e3c72; font-size: 2.5em; font-weight: 700;'>CarbonMatch</h1>
            <p style='margin: 5px 0 0 0; color: #27ae60; font-size: 1.1em; font-weight: 600;'>TEAM</p>
            <p style='margin: 8px 0 0 0; color: #666; font-size: 0.95em;'>CO₂ Emissions Dashboard & CSRD Compliance</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<p style='text-align: center; color: #666; font-size: 0.9em;'>Comprehensive audit and visualization of CSRD-compliant CO₂ reporting | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>", unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    if df is None or len(df) == 0:
        st.error("❌ Unable to load data. Please ensure carbomatch_report.csv exists in the working directory.")
        return
    
    # Calculate KPIs
    kpis = calculate_kpis(df)
    
    # ============== KPI SECTION (TOP METRICS) ==============
    st.markdown("### 🎯 KEY METRICS - Overview")
    
    # Calculate intensity
    intensity = kpis['total_co2e'] / (df['Menge'].sum()) if df['Menge'].sum() > 0 else 0
    
    # Create 2x2 grid with styled metrics
    col1, col2 = st.columns(2)
    
    with col1:
        col1a, col1b = st.columns(2)
        with col1a:
            st.metric(
                "📊 TOTAL CO₂e",
                f"{kpis['total_co2e']/1e6:.2f}M kg",
                delta="Material Footprint"
            )
        with col1b:
            st.metric(
                "✅ Success Rate",
                f"{kpis['success_rate']:.1f}%",
                delta=f"{kpis['successful_items']}/{kpis['total_items']} items"
            )
    
    with col2:
        col2a, col2b = st.columns(2)
        with col2a:
            st.metric(
                "🏭 Material CO₂e (A1-A3)",
                f"{kpis['material_co2e']/1e6:.2f}M kg",
                delta=f"{kpis['material_pct']:.1f}% of total"
            )
        with col2b:
            st.metric(
                "⚙️ Intensity",
                f"{intensity:.2f} kg CO₂e/kg",
                delta="per kg of material"
            )
    
    st.divider()
    
    # ============== TOP EMITTERS SECTION (SECTION 2) ==============
    st.markdown("### 📊 Top Material Emitters (A1-A3)")
    
    st.plotly_chart(
        create_top_emitters_chart(df, top_n=15),
        use_container_width=True
    )
    
    st.divider()
    
    # ============== AUDIT TABLE SECTION (SECTION 3) ==============
    st.markdown("### 📋 Audit Data Table")
    
    # Filters
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        selected_status = st.multiselect(
            "Filter by Calculation Status:",
            options=df['calculation_status'].unique(),
            default=None
        )
    
    with col_filter2:
        selected_suppliers = st.multiselect(
            "Filter by Supplier:",
            options=sorted(df['Lieferant'].unique()),
            default=None
        )
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_status:
        filtered_df = filtered_df[filtered_df['calculation_status'].isin(selected_status)]
    
    if selected_suppliers:
        filtered_df = filtered_df[filtered_df['Lieferant'].isin(selected_suppliers)]
    
    # Display filtered data
    st.write(f"**Showing {len(filtered_df)} of {len(df)} records**")
    
    # Select columns for display
    display_columns = [
        'Lieferant', 'Artikel-Nummer', 'Artikel', 'Menge', 'Einheit',
        'matched_material', 'similarity_score', 'matched_oeko_unit',
        'calculated_co2e_a1_a3', 'calculated_co2e_a4', 'total_co2e',
        'calculation_status'
    ]
    
    # Only include columns that exist
    display_columns = [col for col in display_columns if col in filtered_df.columns]
    
    # Format numeric columns for display
    display_df = filtered_df[display_columns].copy()
    
    numeric_display = ['similarity_score', 'calculated_co2e_a1_a3', 'calculated_co2e_a4', 'total_co2e']
    for col in numeric_display:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: f'{x:,.2f}' if pd.notna(x) else 'N/A')
    
    # Display as interactive table
    st.dataframe(
        display_df,
        width='stretch',
        height=400
    )
    
    # Download button
    csv = filtered_df[display_columns].to_csv(sep=';', index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 Download Filtered Data (CSV)",
        data=csv,
        file_name=f"csrd_audit_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
    
    st.divider()
    
    # ============== VISUALIZATIONS SECTION (SECTION 4 - MOVED DOWN) ==============
    st.markdown("### 📈 Detailed Analysis - Materials & Suppliers")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        chart_fig, others_count, major_count = create_supplier_category_chart(df)
        st.plotly_chart(chart_fig, use_container_width=True)
        
        # Show analysis info
        st.info(f"📊 **Analysis:** {major_count} suppliers >1% | {others_count} suppliers <1% → Others")
    
    with col_right:
        st.plotly_chart(
            create_status_distribution_chart(df),
            use_container_width=True
        )
    
    st.divider()
    
    # ============== SUMMARY SECTION ==============
    st.markdown("### 📌 Summary - Key Figures")
    
    st.markdown("""
    **📊 What is CO₂e Intensity?**
    
    Intensity = Total CO₂e ÷ Total Material Weight
    
    It shows how much carbon is emitted per kilogram of material received.
    
    **Example:** If intensity = 929 kg CO₂e/kg, it means:
    - For every 1 kg of delivered material, we emit ~929 kg of CO₂e during production (A1-A3)
    - This high value is because the materials are production-intensive (steel, concrete, etc.)
    - Lower intensity = more sustainable material choice
    """)
    
    summary_col1, summary_col2, summary_col3 = st.columns(3)
    
    with summary_col1:
        st.write("**🏭 Material Emissions (A1-A3):**")
        st.write(f"- Total: {kpis['material_co2e']/1e6:.2f}M kg CO₂e")
        st.write(f"- Percentage: {kpis['material_pct']:.1f}% of total")
        st.write(f"- Per Item: {kpis['material_co2e']/kpis['total_items']:,.0f} kg CO₂e/item")
    
    with summary_col2:
        st.write("**✅ Processing Status:**")
        st.write(f"- Successful: {kpis['successful_items']} ({kpis['success_rate']:.1f}%)")
        st.write(f"- Failed: {kpis['failed_items']}")
        st.write(f"- Total Items: {kpis['total_items']}")
    
    with summary_col3:
        st.write("**📊 Material Weight & Intensity:**")
        total_weight = df['Menge'].sum()
        st.write(f"- Total Weight: {total_weight:,.0f} kg")
        st.write(f"- **Intensity: {intensity:.2f} kg CO₂e/kg**")
        st.write(f"  (Carbon per kg material)")
    
    st.markdown("---")
    st.markdown("<p style='text-align: center; font-size: 0.8em; color: #999;'>CarbonMatch Dashboard | CSRD Compliance Reporting | Data Audit Trail</p>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
