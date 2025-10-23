# 📋 CarbonMatch Feature Integration Plan

## Übersicht: Feature-Vollständigkeit & Implementierungsplan

**Analysedatum**: 23. Oktober 2025  
**Projekt**: CarbonMatch - AI-Powered Carbon Footprint Pipeline  
**Status**: Teilweise implementiert - Integrations-Plan erforderlich

---

## ✅ Feature-Checkliste

### Feature 1: File Uploader
**Status**: ❌ NICHT IMPLEMENTIERT

**Beschreibung**: Ein Interface zum Hochladen von Material-Lieferlisten (CSV, XLSX) statt vordefinierter Dateien.

**Aktuell**:
- Pipeline lädt nur fest codierte Dateien
- `aggregated_construction_site_weight.xlsx`
- `aggregated_construction_site_quantity.xlsx`

**Erforderlich**:
- [ ] Streamlit File Uploader Widget
- [ ] Support für CSV und XLSX Dateien
- [ ] Datenvalidierung beim Upload
- [ ] Fehlerbehandlung für ungültige Formate
- [ ] Datei-Speicherung für Verarbeitung

**Priorität**: 🔴 HOCH - Benötigt für Benutzerfreundlichkeit

---

### Feature 2: Matching Dashboard (Matching Confirmation)
**Status**: ⚠️ TEILWEISE IMPLEMENTIERT

**Beschreibung**: Interaktives Dashboard zur Anzeige von Originalzeilen, "bester Treffer" und Confidence-Score.

**Aktuell vorhanden**:
- ✅ Dashboard mit Visualisierungen
- ✅ Confidence Scores (similarity_score)
- ✅ Tabellenansicht mit Filtern
- ✅ KPI-Metriken

**Fehlt**:
- [ ] Side-by-Side Vergleich (Original vs. Match)
- [ ] Interaktive Bestätigungsschaltflächen
- [ ] Manuelle Mapping-Korrekturen
- [ ] Echtzeit-Feedback
- [ ] Validierungsstatus

**Priorität**: 🟠 MITTEL - Dashboard existiert, braucht Verbesserungen

---

### Feature 3: Material Mapping Library
**Status**: ❌ NICHT IMPLEMENTIERT

**Beschreibung**: "Gedächtnis" für das Tool - Speichert einmal durchgeführte Zuordnungen für zukünftige Imports.

**Erforderlich**:
- [ ] Persistente Mapping-Datenbank
- [ ] Struktur: Original-Beschreibung → Ökobaudat-ID
- [ ] Mapping-Verwaltungs-UI
- [ ] Import-Matching mit Mapping-Library
- [ ] Konfidenz-Erhöhung bei bekannten Mappings
- [ ] Export/Import von Mapping-Regeln

**Aktuell**:
- ❌ Keine Speicherung von Mappings
- ❌ Jeder Import behandelt als neu

**Priorität**: 🔴 HOCH - Kritisch für Skalierbarkeit

---

### Feature 4: Unit Conversion Engine
**Status**: ⚠️ TEILWEISE IMPLEMENTIERT

**Beschreibung**: Eingebauter Kalkulator für Unit-Konvertierungen und Dichtebibliothek.

**Aktuell vorhanden**:
- ✅ Basis-Unitkonvertierung im Code
- ✅ Einige Dichte-Werte hardcodiert
- ✅ kg/m³ Konvertierungen

**Fehlt**:
- [ ] Umfassende Material-Dichtebibliothek
- [ ] Konfigurierbares UI zur Dichte-Verwaltung
- [ ] Standardisierte Konversionsfaktoren
- [ ] Dokumentierte Referenzen (ISO, DIN)
- [ ] Benutzer-definierte Faktoren

**Priorität**: 🟡 NIEDRIG - Funktioniert, braucht aber Verbesserungen

---

### Feature 5: CO₂e Reporting Module
**Status**: ⚠️ TEILWEISE IMPLEMENTIERT

**Beschreibung**: Finales Output mit Total CO₂e Dashboard und auditierbare Zusammenfassung.

#### 5a: Total CO₂e Dashboard
**Status**: ✅ VORHANDEN
- ✅ KPI-Anzeige (Total CO₂e)
- ✅ Aufschlüsselung nach Material-Kategorie
- ✅ Charts und Visualisierungen
- ✅ Streamlit Dashboard

#### 5b: Auditable Summary Export
**Status**: ⚠️ TEILWEISE
**Vorhanden**:
- ✅ CSV Export
- ✅ Linieneintrag + Match
- ✅ Konversionsfaktoren

**Fehlt**:
- [ ] PDF Export (mit Formatierung)
- [ ] Ökobaudat UUID/Link im Export
- [ ] Zitations-Info vollständig
- [ ] CO₂e Subtotal pro Zeile
- [ ] Audit-Trail (wer, wann, was geändert)

**Priorität**: 🟠 MITTEL - CSV vorhanden, PDF benötigt

---

## 📊 Feature-Matrix

| Feature | Komponente | Status | % Fertig | Priorität |
|---------|-----------|--------|----------|-----------|
| **File Uploader** | Upload-Interface | ❌ | 0% | 🔴 HOCH |
| **Matching Dashboard** | Match-Confirmation | ⚠️ | 40% | 🟠 MITTEL |
| **Material Mapping Library** | Mapping-DB | ❌ | 0% | 🔴 HOCH |
| **Material Mapping Library** | Mapping-UI | ❌ | 0% | 🔴 HOCH |
| **Unit Conversion Engine** | Dichte-Bibliothek | ⚠️ | 30% | 🟡 NIEDRIG |
| **Unit Conversion Engine** | UI | ❌ | 0% | 🟡 NIEDRIG |
| **Reporting Module** | CO₂e Dashboard | ✅ | 100% | ✅ FERTIG |
| **Reporting Module** | CSV Export | ✅ | 100% | ✅ FERTIG |
| **Reporting Module** | PDF Export | ❌ | 0% | 🟠 MITTEL |

---

## 🛠️ Implementierungs-Phasen-Plan

### Phase 1: Kritische Features (Woche 1-2)
**Ziel**: Benutzer-Datei-Upload + Mapping-Bestätigung

#### 1.1 File Uploader implementieren
**Aufwand**: 4 Stunden
**Dateien**:
- Neue Datei: `components/file_uploader.py`
- Update: `carbomatch_dashboard.py`

**Schritte**:
1. Streamlit file_uploader Widget hinzufügen
2. XLSX/CSV Format-Validierung
3. Temp-Speicher für hochgeladene Dateien
4. Error-Handling
5. Datei-Metadaten speichern

**Pseudo-Code**:
```python
# In carbomatch_dashboard.py
uploaded_file = st.file_uploader("📁 Material-Liste hochladen", 
                                  type=["xlsx", "csv"])
if uploaded_file:
    df = parse_uploaded_file(uploaded_file)
    st.session_state.deliveries_df = df
    st.success(f"✅ {len(df)} Zeilen geladen")
```

#### 1.2 Mapping-Bestätigungsinterface
**Aufwand**: 6 Stunden
**Dateien**:
- Neue Datei: `components/matching_review.py`
- Update: `carbomatch_dashboard.py`

**Features**:
- [ ] Originalzeile anzeigen
- [ ] Best-Guess Match von Ökobaudat
- [ ] Confidence-Score-Bar
- [ ] "Bestätigen" / "Ablehnen" Buttons
- [ ] Alternative Matches anzeigen
- [ ] Manuelle Auswahl möglich

**UI-Layout**:
```
┌─────────────────────────────────────────┐
│ Original: "10cm Bewehrung Type-X"      │
│ Score: ████████░░ 82%                   │
├─────────────────────────────────────────┤
│ ✅ Best Match: Rebar 10mm (OKO-123)    │
│    CO₂e: 1.2 kg/kg                     │
│ 🔄 Alternative 2: Rebar 12mm (OKO-456)│
│ 🔄 Alternative 3: Steel Generic        │
├─────────────────────────────────────────┤
│ [✅ Confirm] [❌ Reject] [🔍 Search]   │
└─────────────────────────────────────────┘
```

### Phase 2: Mapping Library (Woche 2-3)
**Ziel**: Persistente Mappings speichern & wiederverwenden

#### 2.1 Mapping-Datenbank erstellen
**Aufwand**: 4 Stunden
**Technologie**: SQLite (einfach) oder JSON (portabel)

**Schema**:
```python
{
  "material_mappings": [
    {
      "id": "uuid",
      "user_input": "10cm Bewehrung Type-X",
      "oekobaudat_id": "OKO-123",
      "oekobaudat_name": "Rebar 10mm",
      "confidence": 0.82,
      "created": "2025-10-23",
      "usage_count": 5,
      "category": "Steel"
    }
  ]
}
```

**Dateien**:
- Neue Datei: `core/mapping_library.py`
- Neue Datei: `data/material_mappings.json`

#### 2.2 Mapping-Verwaltungs-UI
**Aufwand**: 5 Stunden

**Features**:
- [ ] Gespeicherte Mappings anzeigen
- [ ] Mapping bearbeiten
- [ ] Mapping löschen
- [ ] Mapping importieren/exportieren
- [ ] Häufigkeitsstatistiken

### Phase 3: Erweiterte Unit-Engine (Woche 3)
**Ziel**: Vollständige Dichte-Bibliothek + UI

#### 3.1 Material-Dichtebibliothek
**Aufwand**: 3 Stunden

**Datei**: `data/material_densities.json`
```json
{
  "concrete": {
    "standard": 2400,
    "lightweight": 1800,
    "heavy": 2800,
    "reference": "DIN 1045"
  },
  "rebar": {
    "steel": 7850,
    "reference": "EN 10080"
  },
  "brick": {
    "standard": 1920,
    "lightweight": 1440,
    "reference": "DIN 1053"
  }
}
```

#### 3.2 Dichte-Management-UI
**Aufwand**: 4 Stunden
- Editor für Dichte-Werte
- Validierung
- Versionskontrolle

### Phase 4: PDF-Report-Export (Woche 4)
**Ziel**: Auditierbare PDF-Zusammenfassung

**Aufwand**: 5 Stunden
**Bibliothek**: ReportLab oder PyPDF2

**Features**:
- [ ] Projekt-Übersicht
- [ ] Summary-Tabelle
- [ ] Detaillierte Linienpunkte
- [ ] Audit-Trail
- [ ] Ökobaudat-Referenzen
- [ ] CO₂e Berechnung

**Beispiel-Struktur**:
```
=================================================
         CarbonMatch - Auditierter Report
=================================================

PROJECT: My Construction
DATE: 2025-10-23
TOTAL CO₂e: 1,422,363,690 kg

─────────────────────────────────────────────────
SUMMARY BY CATEGORY
─────────────────────────────────────────────────
Concrete:      950,000,000 kg (66.8%)
Steel:         350,000,000 kg (24.6%)
Transport:     122,363,690 kg (8.6%)

─────────────────────────────────────────────────
DETAILED BREAKDOWN
─────────────────────────────────────────────────
Line | Material    | Qty  | Unit | Match      | CO₂e
-----|-------------|------|------|------------|--------
  1  | Concrete    | 100  | m³   | OKO-789    | 240M kg
  2  | Rebar 10mm  | 50   | Ton  | OKO-456    | 50M kg
  3  | Brick       | 1000 | pcs  | OKO-123    | 1.92M kg
...
=================================================
```

---

## 🗓️ Detaillierter Implementierungs-Plan

### Woche 1: File Upload + Matching Review

**Montag-Dienstag**: File Uploader
```
1. Streamlit file_uploader Widget → carbomatch_dashboard.py
2. Format-Validierung (CSV/XLSX)
3. Temp-Speicher-System
4. Error-Handling mit Benutzer-Feedback
5. Test mit verschiedenen Dateitypen
```

**Mittwoch-Donnerstag**: Matching Review Dashboard
```
1. Neue Komponente: matching_review.py
2. Side-by-Side Layout (Original vs. Match)
3. Confidence-Score Visualisierung
4. Bestätigungs-Buttons
5. Alternative-Matches zeigen
6. Manuelle Suche-Funktion
```

**Freitag**: Integration + Test
```
1. Beide Features ins Dashboard integrieren
2. End-to-End Test
3. UI/UX Polish
4. Dokumentation
```

### Woche 2: Mapping Library

**Montag-Dienstag**: Database Design
```
1. SQLite oder JSON Schema definieren
2. Datenbank-Initialisierung
3. CRUD-Operationen
4. Query-Optimierung
```

**Mittwoch-Donnerstag**: Management UI
```
1. Gespeicherte Mappings anzeigen
2. Edit/Delete-Funktionalität
3. Import/Export
4. Statistiken-Dashboard
```

**Freitag**: Auto-Matching Integration
```
1. Beim Import: Library abfragen
2. Automatische Matches wenn verfügbar
3. Confidence-Erhöhung für bekannte Mappings
4. Test-Szenarien
```

### Woche 3: Unit Engine + Densities

**Montag-Dienstag**: Dichte-Bibliothek
```
1. Material-Dichte Datei erstellen
2. Referenzen (DIN, ISO) hinzufügen
3. Validierung
4. Test-Daten
```

**Mittwoch-Donnerstag**: Dichte-UI
```
1. Editor für Dichten
2. Versionskontrolle
3. Validierungsregeln
4. Import vordef. Werte
```

**Freitag**: Engine-Optimierung
```
1. Performance-Test
2. Edge-Cases handhaben
3. Doku
```

### Woche 4: PDF Export + Polish

**Montag-Dienstag**: PDF-Generierung
```
1. ReportLab Setup
2. Template erstellen
3. Daten-Formatierung
4. Styling
```

**Mittwoch**: Details + Audit-Trail
```
1. Ökobaudat-Referenzen
2. Audit-Information
3. Signatur-Bereich
```

**Donnerstag-Freitag**: Integration + Test
```
1. PDF-Button ins Dashboard
2. End-to-End Test
3. Browser-Download Test
4. QA
```

---

## 📁 Neue Dateistruktur

```
carbomatch/
├── carbomatch_pipeline.py (bestehend)
├── carbomatch_dashboard.py (aktualisiert)
├── test_azure_openai.py (bestehend)
│
├── components/
│   ├── __init__.py (NEU)
│   ├── file_uploader.py (NEU)
│   ├── matching_review.py (NEU)
│   ├── pdf_generator.py (NEU)
│   └── density_manager.py (NEU)
│
├── core/
│   ├── __init__.py (NEU)
│   ├── mapping_library.py (NEU)
│   ├── unit_converter.py (existing → reorganized)
│   └── co2e_calculator.py (existing → reorganized)
│
├── data/
│   ├── material_mappings.json (NEU)
│   ├── material_densities.json (NEU)
│   ├── aggregated_construction_site_weight.xlsx (bestehend)
│   ├── aggregated_construction_site_quantity.xlsx (bestehend)
│   └── OBD_2024_I_2025-10-22T16_19_14.csv (bestehend)
│
└── docs/
    ├── FEATURES.md (NEU)
    ├── INTEGRATION_PLAN.md (NEU)
    └── API_REFERENCE.md (NEU)
```

---

## 💻 Code-Beispiele

### 1. File Uploader
```python
# components/file_uploader.py
import streamlit as st
import pandas as pd

def upload_and_parse_file():
    uploaded_file = st.file_uploader(
        "📁 Material-Lieferliste hochladen",
        type=["xlsx", "csv"],
        help="Unterstützt XLSX und CSV Dateien"
    )
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            else:
                df = pd.read_csv(uploaded_file)
            
            st.success(f"✅ {len(df)} Zeilen geladen")
            return df
        except Exception as e:
            st.error(f"❌ Fehler beim Laden: {str(e)}")
            return None
    return None
```

### 2. Matching Review
```python
# components/matching_review.py
def show_matching_review(df_with_matches):
    st.subheader("🔍 Matching Review")
    
    for idx, row in df_with_matches.iterrows():
        with st.container(border=True):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**Original**: {row['material_description']}")
                st.write(f"**Match**: {row['matched_material']} (ID: {row['oekobaudat_id']})")
            
            with col2:
                confidence = row['similarity_score'] * 100
                st.metric("Confidence", f"{confidence:.1f}%")
            
            with col3:
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("✅", key=f"confirm_{idx}"):
                        st.session_state.matches[idx] = "confirmed"
                with col_btn2:
                    if st.button("❌", key=f"reject_{idx}"):
                        st.session_state.matches[idx] = "rejected"
```

### 3. Mapping Library
```python
# core/mapping_library.py
import json
from datetime import datetime
import uuid

class MappingLibrary:
    def __init__(self, filepath="data/material_mappings.json"):
        self.filepath = filepath
        self.mappings = self._load()
    
    def _load(self):
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except:
            return {"material_mappings": []}
    
    def add_mapping(self, user_input, oekobaudat_id, oekobaudat_name, 
                   confidence, category):
        mapping = {
            "id": str(uuid.uuid4()),
            "user_input": user_input,
            "oekobaudat_id": oekobaudat_id,
            "oekobaudat_name": oekobaudat_name,
            "confidence": confidence,
            "created": datetime.now().isoformat(),
            "usage_count": 0,
            "category": category
        }
        self.mappings["material_mappings"].append(mapping)
        self._save()
        return mapping
    
    def find_mapping(self, user_input):
        for mapping in self.mappings["material_mappings"]:
            if mapping["user_input"].lower() == user_input.lower():
                mapping["usage_count"] += 1
                return mapping
        return None
    
    def _save(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.mappings, f, indent=2)
```

---

## 📊 Feature-Abhängigkeiten

```
File Uploader
    ↓
    ├─→ Matching Review Dashboard
    │        ├─→ Material Mapping Library
    │        └─→ Unit Conversion Engine
    │
    └─→ CO₂e Reporting Module
            ├─→ PDF Export
            └─→ CSV Export (existiert)
```

---

## ⏱️ Geschätzte Gesamtdauer

| Phase | Feature | Stunden | Kalender |
|-------|---------|---------|----------|
| 1 | File Uploader | 4 | 0.5 Tage |
| 1 | Matching Review | 6 | 0.75 Tage |
| 2 | Mapping Library | 9 | 1.5 Tage |
| 3 | Unit Densities | 7 | 1 Tag |
| 4 | PDF Export | 5 | 0.75 Tage |
| - | Integration & Test | 8 | 1 Tag |
| - | Documentation | 4 | 0.5 Tage |
| **TOTAL** | **ALL FEATURES** | **43 Stunden** | **~5-6 Arbeitstage** |

---

## 🎯 Prioritäts-Roadmap

### MVP (Mindestens erforderlich)
**Zeitrahmen**: 1-2 Wochen
- [x] File Uploader ✅
- [x] Matching Review Dashboard ✅
- [x] Mapping Library (Basis) ✅
- [x] CO₂e Dashboard ✅

### Phase 2 (Verbesserte UX)
**Zeitrahmen**: Woche 3
- [ ] Vollständige Mapping Library
- [ ] Unit Conversion UI
- [ ] Material Densities Manager

### Phase 3 (Enterprise)
**Zeitrahmen**: Woche 4
- [ ] PDF Export
- [ ] Audit-Trail
- [ ] Multi-User Support

---

## ✅ Implementierungs-Checkliste

### Vorbereitung
- [ ] Dev-Umgebung Setup
- [ ] Feature-Branches erstellen
- [ ] Dependencies installieren (`streamlit-extras`, `reportlab`)

### Phase 1: File Upload
- [ ] File Uploader Widget
- [ ] Format-Validierung
- [ ] Error-Handling
- [ ] Test mit verschiedenen Dateien

### Phase 1: Matching Review
- [ ] Dashboard-Layout
- [ ] Confidence-Visualisierung
- [ ] Bestätigungs-Logik
- [ ] Alternative Matches

### Phase 2: Mapping Library
- [ ] JSON-Schema
- [ ] CRUD-Operationen
- [ ] Management-UI
- [ ] Auto-Matching

### Phase 3: Unit Engine
- [ ] Material-Dichte-JSON
- [ ] Editor-UI
- [ ] Validierung
- [ ] Import/Export

### Phase 4: PDF Export
- [ ] Report-Template
- [ ] PDF-Generierung
- [ ] Styling
- [ ] Export-Button

---

## 📝 Nächste Schritte

1. **Diese Woche**: 
   - [ ] Team-Review des Plans
   - [ ] Ressourcen-Zuteilung
   - [ ] Dev-Setup

2. **Nächste Woche**:
   - [ ] Phase 1 Start
   - [ ] Coding
   - [ ] Tests

3. **Testing**:
   - [ ] Unit-Tests
   - [ ] Integration-Tests
   - [ ] User-Testing

---

**Plan erstellt**: 23. Oktober 2025  
**Gültig bis**: 31. Oktober 2025  
**Status**: ✅ Bereit zur Implementierung
