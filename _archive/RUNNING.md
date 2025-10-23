# Running the CSRD CO₂ Reporting Pipeline (Windows PowerShell)

## Prerequisites
- Python 3.8+ installed
- Install dependencies (recommended in a virtual environment):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Set OpenAI API Key (optional but recommended)
```powershell
# PowerShell
$env:OPENAI_API_KEY = 'sk-your-openai-key-here'
```

## Run pipeline
```powershell
# Run full pipeline (demo mode if no API key set)
.\.venv\Scripts\python.exe csrd_reporting_pipeline.py

# Analyze results
.\.venv\Scripts\python.exe analyze_results.py
```

## Output
- `csrd_co2e_report.csv` - final report (semicolon-delimited)
- `csrd_co2e_report.csv` contains calculation status and values for audit

## Notes
- Ökobaudat CSV must be semicolon-delimited and encoded in `latin-1`.
- If OpenAI key is set, the pipeline will use real embeddings; otherwise it runs in demo mode with mock embeddings.
