# CSRD Dashboard - Quick Start Guide

## 🚀 Running the Interactive Dashboard

The CSRD CO₂ Emissions Dashboard provides comprehensive visualization and audit capabilities for CSRD-compliant CO₂ reporting.

### Prerequisites
- Python 3.8+
- Virtual environment with dependencies installed
- `csrd_co2e_report_with_conversions.csv` generated from the pipeline

### Quick Start (Windows PowerShell)

```powershell
# Navigate to project directory
cd "c:\Users\ameri\Nextcloud\Amerigo\privat\hackton_celonis_ac\Data VESTIGAS Case"

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run the dashboard
streamlit run csrd_dashboard.py
```

The dashboard will open in your default browser at `http://localhost:8501`

### Features

#### 📊 Key Performance Indicators (Top Section)
- **Grand Total CO₂e**: Total emissions (Material + Transport)
- **Material Share %**: Percentage of material emissions
- **Success Rate**: % of items successfully calculated
- **CO₂e Intensity**: kg CO₂e per kg material

#### 📈 Visualizations

1. **Emissions by Module Type** (Donut Chart)
   - Material CO₂e (A1-A3) in blue
   - Transport CO₂e (A4) in green
   - Shows exact proportions and percentages

2. **Top 10 Material Emitters** (Horizontal Bar Chart)
   - Identifies highest CO₂e contributing materials
   - Sorted by material emissions (A1-A3)

3. **Calculation Status Distribution** (Pie Chart)
   - Success (green) vs Error (red) statuses
   - Shows breakdown of calculation results

4. **Emissions by Supplier** (Stacked Bar Chart)
   - Material emissions (blue) and Transport (green) per supplier
   - Sorted by total emissions

#### 📋 Audit Table
- Complete data table with all records
- **Filters**:
  - By Calculation Status
  - By Supplier
- **Download**: Export filtered data as CSV
- Fully sortable and scrollable

### Color Scheme
- **Blue** (#1e3c72): Material emissions (A1-A3), Quantities
- **Green** (#00b894): Transport emissions (A4), Success indicators
- **Red** (#d63031): Error/Failed statuses
- **Gray**: Neutral information

### Tips & Tricks

1. **Filtering**: Use multi-select filters to drill down to specific suppliers or status
2. **Exporting**: Download filtered audit data for further analysis
3. **Hover Details**: Hover over any chart to see detailed values
4. **Mobile Friendly**: Responsive design works on tablets and phones

### Troubleshooting

**"File not found" error:**
- Ensure `csrd_co2e_report_with_conversions.csv` exists in the working directory
- Run the pipeline first: `python csrd_reporting_pipeline.py`

**Dashboard won't start:**
- Verify Streamlit is installed: `pip list | grep streamlit`
- Check Python version: `python --version` (should be 3.8+)
- Try: `pip install --upgrade streamlit plotly`

**Port already in use:**
- Use custom port: `streamlit run csrd_dashboard.py --server.port 8502`

### Advanced Options

```powershell
# Run on specific port
streamlit run csrd_dashboard.py --server.port 8502

# Disable caching
streamlit run csrd_dashboard.py --client.caching=false

# Run headless (no browser)
streamlit run csrd_dashboard.py --server.headless true
```

### Dashboard Structure

```
┌─────────────────────────────────────────┐
│  CSRD CO₂ Emissions Dashboard           │
├─────────────────────────────────────────┤
│  [KPI 1] [KPI 2] [KPI 3] [KPI 4]       │
├─────────────────────────────────────────┤
│  [Module Chart]  [Status Chart]         │
├─────────────────────────────────────────┤
│  [Top 10 Emitters - Full Width]         │
├─────────────────────────────────────────┤
│  [Supplier Emissions - Full Width]      │
├─────────────────────────────────────────┤
│  📋 Audit Table                         │
│  [Filter 1: Status] [Filter 2: Supplier]│
│  [Data Table with Download Button]      │
├─────────────────────────────────────────┤
│  Summary Statistics                     │
└─────────────────────────────────────────┘
```

### Data Flow

```
csrd_co2e_report_with_conversions.csv
    ↓
[Load & Cache]
    ↓
[Calculate KPIs]
    ↓
[Render Dashboard]
    ↓
[User Interactions: Filters, Charts, Downloads]
```

---

**Need help?** Check the console output for error details or review the data file format.

**Status**: ✅ Production Ready | Last Updated: October 23, 2025
