# CarbonMatch - AI-Powered Carbon Footprint Pipeline
## 🌱 Enterprise Solution for CSRD-Compliant Carbon Reporting

### Overview
**CarbonMatch** is a complete, automated pipeline for **CSRD-compliant CO₂ reporting** in the construction industry. Using advanced AI embeddings, it matches material delivery descriptions to environmental database entries, calculates carbon footprints, and generates audit-ready reports.

---

## 🎯 Key Features

### ✅ **Core Capabilities**
- **Azure OpenAI Integration**: Uses Azure OpenAI embeddings for semantic matching (text-embedding-ada-002)
- **Comprehensive CO₂e Calculation**: Handles A1-A3 (material) and A4 (transport) modules  
- **Multi-Unit Support**: Processes kg, m³, and other standard construction units
- **Robust Error Handling**: Flags unsupported units and missing data with detailed status tracking
- **CSRD-Compliant Output**: Generates audit-ready reports with semicolon separators

### 📊 **Input Data Processing**
- **Delivery Data**: Processes both weight (`aggregated_construction_site_weight.xlsx`) and quantity (`aggregated_construction_site_quantity.xlsx`) files
- **Environmental Database**: Integrates with Ökobaudat CSV (A1-A3 modules only)
- **Data Cleaning**: Automatically handles German decimal notation (comma → dot conversion)

### 🔬 **Technical Architecture**
- **Embedding Generation**: Azure OpenAI `text-embedding-ada-002` for semantic similarity (1536 dimensions)
- **Similarity Matching**: Cosine similarity using scikit-learn
- **Unit Conversion**: Handles density-based calculations for m³ materials
- **Modular Design**: Clean, maintainable class-based architecture
- **Cloud Integration**: Enterprise-grade Azure infrastructure for reliability

---

## 🚀 Quick Start

### Prerequisites
```bash
pip install pandas numpy openai scikit-learn openpyxl streamlit plotly
```

### Azure OpenAI Configuration

Set your Azure OpenAI API key (required for real embeddings):
```powershell
$env:OPENAI_API_KEY="your-azure-openai-api-key"
```

See [AZURE_OPENAI_SETUP.md](./AZURE_OPENAI_SETUP.md) for detailed configuration options.

### Basic Usage
```python
from carbomatch_pipeline import CarbonMatchPipeline
import os

# API key is read from OPENAI_API_KEY environment variable
pipeline = CarbonMatchPipeline()

# Run the complete pipeline
pipeline.load_and_clean_data()
pipeline.generate_embeddings_and_match()  # Uses Azure OpenAI
pipeline.calculate_all_co2e()
pipeline.simulate_transport_co2e()
pipeline.generate_final_report()
```

### Command Line Execution
```bash
python carbomatch_pipeline.py
```

### Testing the Application

Run the comprehensive test script with real data:

```powershell
# Activate virtual environment (if needed)
.\.venv\Scripts\Activate.ps1

# Run the test script
python test_application.py
```

**Test Script Features:**
- ✅ Verifies input files (aggregated_construction_site_combined.xlsx, oekobaudat.csv)
- ✅ Initializes CarbonMatch pipeline
- ✅ Loads and cleans data (441 delivery items, 2,535 A1-A3 materials)
- ✅ Generates embeddings and matches materials
- ✅ Calculates CO₂e values (A1-A3 and A4 transport)
- ✅ Generates final report (carbomatch_report.csv)

**Expected Output:**
```
Total materials processed: 441 items
Total material weight: 1,291,546.62 kg
Material CO₂e (A1-A3): 167,572,143.47 kg CO₂e
Transport CO₂e (A4): 103,323.73 kg CO₂e
GRAND TOTAL CO₂e: 167,675,467.20 kg CO₂e
CO₂e intensity: 129.8 kg CO₂e/kg material
```

---

## 📁 File Structure

```
Data VESTIGAS Case/
├── carbomatch_pipeline.py           # Main pipeline script
├── carbomatch_dashboard.py          # Interactive Streamlit dashboard
├── test_application.py              # Application test script (NEW)
├── carbomatch_report.csv            # Generated output report
├── aggregated_construction_site_combined.xlsx  # Combined delivery data
├── oekobaudat.csv                   # Ökobaudat database
├── _archive/                        # Deprecated and test scripts
└── README.md                        # This documentation
```

---

## 🔧 Configuration

### Azure OpenAI Setup

The pipeline uses Azure OpenAI for embeddings. Configure your API key:

**Option 1: Environment Variable (Recommended)**
```powershell
$env:OPENAI_API_KEY="your-azure-openai-api-key"
```

**Option 2: Command Line**
```powershell
$env:OPENAI_API_KEY="key-here"; python csrd_reporting_pipeline.py
```

**Option 3: Permanent (Windows)**
1. System Properties → Environment Variables
2. Add `OPENAI_API_KEY` with your key
3. Restart terminal

See [AZURE_OPENAI_SETUP.md](./AZURE_OPENAI_SETUP.md) for complete setup guide.

### Azure Endpoints & Models
```python
AZURE_ENDPOINT = "https://aoai-hackathon.openai.azure.com/"
AZURE_API_VERSION = "2024-12-01-preview"
AZURE_EMBEDDING_MODEL = "text-embedding-ada-002"
AZURE_CHAT_MODEL = "o4-mini"
```

### Customizable Parameters
```python
# Transport simulation parameters
avg_distance_km = 100  # Average transport distance
truck_emission_factor = 0.0008  # kg CO₂e per kg per km

# Output file
OUTPUT_FILE = "csrd_co2e_report_with_conversions.csv"
```

---

## 📈 Pipeline Workflow

### **Step 1: Data Ingestion & Cleaning**
- Load delivery files (Excel format)
- Load Ökobaudat database (CSV, semicolon-delimited)
- Filter for A1-A3 modules only
- Clean numeric columns (comma → dot conversion)
- Handle missing values

### **Step 2: AI Embedding & Matching**
- Generate embeddings for all unique Ökobaudat materials
- Generate embeddings for delivery items
- Calculate cosine similarity scores
- Match each delivery item to best Ökobaudat entry

### **Step 3: CO₂e Calculation (A1-A3)**
- **kg units**: Direct multiplication (Menge × GWP)
- **m³ units**: Volume conversion (Menge ÷ Rohdichte × GWP)
- **Other units**: Flagged as unsupported
- Error handling for missing densities

### **Step 4: Transport Simulation (A4)**
- Applies standard transport assumptions
- Calculates based on weight and distance
- Uses industry-standard emission factors

### **Step 5: Report Generation**
- Combines all calculations
- Generates executive summary
- Exports to CSRD-compliant CSV format

---

## 📊 Output Report Structure

### Final CSV Columns:
- `Lieferant` - Supplier name
- `Artikel-Nummer` - Item number  
- `Artikel` - Item description
- `Menge` - Quantity
- `Einheit` - Unit
- `matched_material` - Matched Ökobaudat material
- `matched_category` - Material category
- `similarity_score` - AI matching confidence (0-1)
- `matched_oeko_unit` - Ökobaudat reference unit
- `calculated_co2e_a1_a3` - Material CO₂e (kg)
- `calculated_co2e_a4` - Transport CO₂e (kg)
- `total_co2e` - Total CO₂e (kg)
- `calculation_status` - Success/error status

### Executive Summary Example:
```
📊 PROJECT TOTALS:
   • Total materials processed: 456 items
   • Total material weight: 2,253,599.62 kg
   • Material CO₂e (A1-A3): 171,285,723.54 kg CO₂e
   • Transport CO₂e (A4): 180,287.97 kg CO₂e
   • GRAND TOTAL CO₂e: 171,466,011.51 kg CO₂e

🎯 KEY PERFORMANCE INDICATORS:
   • CO₂e intensity: 76.0854 kg CO₂e/kg material
   • Material vs Transport ratio: 950.1:1
```

---

## ⚠️ Important Notes

### **Data Requirements**
- **Ökobaudat File**: Must use semicolon (`;`) delimiter
- **Excel Files**: Standard Excel format (.xlsx)
- **Encoding**: Ökobaudat requires `latin-1` encoding

### **API Considerations**
- **OpenAI API**: Required for production use
- **Demo Mode**: Falls back to mock embeddings if API unavailable
- **Rate Limits**: Consider OpenAI rate limits for large datasets

### **Unit Support**
- ✅ **Supported**: `kg`, `m3`
- ❌ **Unsupported**: `qm`, `pcs.`, `Stk` (flagged as errors)
- 🔄 **Extensible**: Easy to add new unit conversions

---

## 🔍 Troubleshooting

### Common Issues:

**1. Encoding Errors**
```
Solution: Verify Ökobaudat file uses semicolon delimiter and latin-1 encoding
```

**2. Missing GWP Values**
```
Solution: Pipeline handles with "MISSING" flag and zero CO₂e calculation
```

**3. OpenAI API Errors**
```
Solution: Check API key validity and rate limits; demo mode available
```

**4. Unit Conversion Failures**
```
Solution: Check for missing density values in Ökobaudat data
```

---

## 🏆 Hackathon Team Deliverables

### ✅ **Completed Requirements**
- [x] End-to-end pipeline implementation
- [x] AI-powered semantic matching
- [x] Multi-format data ingestion
- [x] CSRD-compliant reporting
- [x] Robust error handling
- [x] Executive summary generation
- [x] Audit-ready CSV export

### 🎯 **Performance Metrics**
- **Processing Speed**: ~456 items in ~15 seconds
- **Matching Accuracy**: Average similarity score 0.089
- **Success Rate**: 39.5% successful calculations (others flagged appropriately)
- **Data Coverage**: 2,535 Ökobaudat materials, 456 delivery items

---

## 🚀 Future Enhancements

### **Phase 2 Roadmap**
- [ ] Advanced transport routing optimization
- [ ] Multi-supplier consolidation logic
- [ ] Real-time API integration
- [ ] Dashboard visualization
- [ ] B1-B7, C1-C4, D module support
- [ ] Machine learning accuracy improvements

### **Enterprise Features**
- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] Web interface development
- [ ] Multi-tenant architecture
- [ ] Advanced reporting templates
- [ ] Integration with ERP systems

---

## 📝 License & Attribution

**Developed by**: CarbonMatch Hackathon Team  
**Date**: October 23, 2025  
**License**: MIT  
**Contact**: hackathon@vestigas.com

---

*This solution demonstrates the power of AI in environmental reporting, providing construction companies with the tools needed for accurate, automated CSRD compliance.*
