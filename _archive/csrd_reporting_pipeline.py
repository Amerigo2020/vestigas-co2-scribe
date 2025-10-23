#!/usr/bin/env python3
"""
CSRD CO₂ Reporting Pipeline for VESTIGAS
==========================================

A complete end-to-end pipeline for:
1. Material delivery data ingestion (Weight & Quantity files)
2. Ökobaudat environmental database matching via AI embeddings
3. CO₂e calculation (A1-A3 modules)
4. Transport simulation
5. Final CSRD-compliant reporting

Author: VESTIGAS Hackathon Team
Date: October 23, 2025
"""

import pandas as pd
import numpy as np
import os
from typing import Tuple, Dict, List, Optional
import logging
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# AI/ML Libraries
try:
    from openai import AzureOpenAI
    from sklearn.metrics.pairwise import cosine_similarity
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI or sklearn not available. Install with: pip install openai scikit-learn")

# Configuration - Azure OpenAI
AZURE_ENDPOINT = "https://aoai-hackathon.openai.azure.com/"
AZURE_API_VERSION = "2024-12-01-preview"
AZURE_EMBEDDING_MODEL = "text-embedding-ada-002"
AZURE_CHAT_MODEL = "o4-mini"
SUBSCRIPTION_KEY = os.environ.get("OPENAI_API_KEY", "")  # Get from environment variable

OUTPUT_FILE = "csrd_co2e_report_with_conversions.csv"

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CSRDReportingPipeline:
    """Main pipeline class for CSRD CO₂ reporting"""
    
    def __init__(self, api_key: str = ""):
        """Initialize the pipeline with Azure OpenAI API key"""
        self.api_key = api_key or SUBSCRIPTION_KEY
        self.client = None
        self.deliveries_df = None
        self.oeko_df = None
        self.matched_df = None
        self.embedding_cache = {}
        
        # Initialize Azure OpenAI client robustly
        if OPENAI_AVAILABLE and self.api_key:
            try:
                self.client = AzureOpenAI(
                    api_version=AZURE_API_VERSION,
                    azure_endpoint=AZURE_ENDPOINT,
                    api_key=self.api_key
                )
                logger.info("✅ Azure OpenAI client initialized successfully")
            except Exception as e:
                logger.warning(f"Azure OpenAI initialization failed: {e}. Will use mock embeddings for demo.")
                self.client = None
        else:
            if not self.api_key:
                logger.warning("⚠️  No API key found (set OPENAI_API_KEY env var) - using mock embeddings for demo")
            else:
                logger.warning("⚠️  OpenAI library not available - using mock embeddings for demo")
    
    def load_and_clean_data(self, 
                           weight_path: str = "aggregated_construction_site_weight.xlsx",
                           quantity_path: str = "aggregated_construction_site_quantity.xlsx", 
                           oekobaudat_path: str = "OBD_2024_I_2025-10-22T16_19_14.csv") -> None:
        """
        Step 1: Load and clean all input data files
        
        Args:
            weight_path: Path to weight delivery data
            quantity_path: Path to quantity delivery data  
            oekobaudat_path: Path to Ökobaudat database
        """
        logger.info("=== STEP 1: DATA INGESTION AND CLEANING ===")
        
        # Load delivery files
        try:
            df_weight = pd.read_excel(weight_path)
            df_quantity = pd.read_excel(quantity_path)
            
            # Combine both delivery files
            self.deliveries_df = pd.concat([df_weight, df_quantity], ignore_index=True)
            logger.info(f"Loaded delivery data: {len(df_weight)} weight + {len(df_quantity)} quantity = {len(self.deliveries_df)} total records")
            
        except Exception as e:
            logger.error(f"Error loading delivery files: {e}")
            raise
        
        # Load and clean Ökobaudat database
        try:
            # Use latin-1 encoding based on our testing
            oeko_raw = pd.read_csv(oekobaudat_path, delimiter=';', encoding='latin-1', low_memory=False)
            
            # Filter for A1-A3 modules only
            self.oeko_df = oeko_raw[oeko_raw['Modul'] == 'A1-A3'].copy()
            logger.info(f"Loaded Ökobaudat data: {len(oeko_raw)} total records, {len(self.oeko_df)} A1-A3 records")
            
            # Clean numeric columns - replace comma with dot and convert to float
            numeric_columns = ['GWPtotal (A2)', 'Rohdichte (kg/m3)', 'Schuettdichte (kg/m3)']
            
            for col in numeric_columns:
                if col in self.oeko_df.columns:
                    self.oeko_df[col] = (self.oeko_df[col]
                                       .astype(str)
                                       .str.replace(',', '.', regex=False)
                                       .replace(['nan', 'None', ''], np.nan))
                    self.oeko_df[col] = pd.to_numeric(self.oeko_df[col], errors='coerce')
            
            # Handle missing values for critical columns
            self.oeko_df['Name (de)'] = self.oeko_df['Name (de)'].fillna('MISSING')
            self.oeko_df['GWPtotal (A2)'] = self.oeko_df['GWPtotal (A2)'].fillna('MISSING')
            
            logger.info("Data cleaning completed successfully")
            
        except Exception as e:
            logger.error(f"Error loading Ökobaudat file: {e}")
            raise
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Step 2a: Generate vector embedding for given text using Azure OpenAI
        
        Args:
            text: Input text to embed
            
        Returns:
            Vector embedding as list of floats, or None if error
        """
        if not text or pd.isna(text):
            return None
            
        # Check cache first
        if text in self.embedding_cache:
            return self.embedding_cache[text]
        
        try:
            # Use Azure OpenAI client if available
            if self.client:
                response = self.client.embeddings.create(
                    model=AZURE_EMBEDDING_MODEL,
                    input=str(text).strip()
                )
                embedding = response.data[0].embedding
                self.embedding_cache[text] = embedding
                return embedding

            # Mock embedding for demo/testing when API not available or fails
            np.random.seed(abs(hash(str(text))) % (2**32))
            mock_embedding = np.random.normal(0, 1, 1536).tolist()  # ada-002 has 1536 dimensions
            self.embedding_cache[text] = mock_embedding
            return mock_embedding

        except Exception as e:
            logger.error(f"Error generating embedding for '{text}': {e}")
            return None
    
    def generate_embeddings_and_match(self) -> None:
        """
        Step 2: Generate embeddings and perform semantic matching
        """
        logger.info("=== STEP 2: EMBEDDING GENERATION AND MATCHING ===")
        
        # Generate embeddings for unique Ökobaudat entries
        logger.info("Generating embeddings for Ökobaudat database...")
        unique_oeko_materials = self.oeko_df['Name (de)'].unique()
        
        oeko_embeddings = []
        oeko_texts = []
        
        for i, material in enumerate(unique_oeko_materials):
            if i % 100 == 0:
                logger.info(f"Processing Ökobaudat embedding {i+1}/{len(unique_oeko_materials)}")
                
            embedding = self.get_embedding(material)
            if embedding:
                oeko_embeddings.append(embedding)
                oeko_texts.append(material)
        
        oeko_embeddings = np.array(oeko_embeddings)
        logger.info(f"Generated {len(oeko_embeddings)} Ökobaudat embeddings")
        
        # Generate embeddings for delivery items and find matches
        logger.info("Matching delivery items to Ökobaudat database...")
        matches = []
        
        # Ensure Artikel and Menge columns exist and are strings/numbers
        self.deliveries_df['Artikel'] = self.deliveries_df['Artikel'].astype(str)
        # Normalize Menge to numeric
        def parse_menge(x):
            try:
                if pd.isna(x):
                    return 0.0
                s = str(x).replace(',', '.').strip()
                return float(s)
            except Exception:
                return 0.0
        self.deliveries_df['Menge'] = self.deliveries_df['Menge'].apply(parse_menge)

        for i, artikel in enumerate(self.deliveries_df['Artikel']):
            if i % 50 == 0:
                logger.info(f"Processing delivery item {i+1}/{len(self.deliveries_df)}")
            
            delivery_embedding = self.get_embedding(artikel)
            
            if delivery_embedding is not None and len(oeko_embeddings) > 0:
                # Calculate cosine similarity
                similarities = cosine_similarity([delivery_embedding], oeko_embeddings)[0]
                best_match_idx = np.argmax(similarities)
                best_match_similarity = similarities[best_match_idx]
                best_match_material = oeko_texts[best_match_idx]
                
                # Get the corresponding Ökobaudat row
                matched_oeko_row = self.oeko_df[self.oeko_df['Name (de)'] == best_match_material].iloc[0]
                
                matches.append({
                    'delivery_index': i,
                    'matched_material': best_match_material,
                    'similarity_score': best_match_similarity,
                    'matched_uuid': matched_oeko_row['UUID'],
                    'matched_gwp': matched_oeko_row['GWPtotal (A2)'],
                    'matched_oeko_unit': matched_oeko_row['Bezugseinheit'],
                    'matched_rohdichte': matched_oeko_row['Rohdichte (kg/m3)'],
                    'matched_category': matched_oeko_row.get('Kategorie (original)', 'Unknown')
                })
            else:
                # No match found
                matches.append({
                    'delivery_index': i,
                    'matched_material': 'NO_MATCH',
                    'similarity_score': 0.0,
                    'matched_uuid': 'NO_MATCH',
                    'matched_gwp': 'MISSING',
                    'matched_oeko_unit': 'Unknown',
                    'matched_rohdichte': np.nan,
                    'matched_category': 'Unknown'
                })
        
        # Create matched dataframe
        matches_df = pd.DataFrame(matches)
        self.matched_df = pd.concat([
            self.deliveries_df.reset_index(drop=True),
            matches_df.drop('delivery_index', axis=1)
        ], axis=1)
        
        logger.info(f"Matching completed. Average similarity score: {matches_df['similarity_score'].mean():.3f}")
    
    def convert_unsupported_units(self, row: pd.Series) -> Tuple[float, str, str]:
        """
        Convert unsupported units to supported kg or m3 using material-specific factors
        
        Args:
            row: DataFrame row with delivery and matched data
            
        Returns:
            Tuple of (converted_quantity, converted_unit, conversion_status)
        """
        try:
            menge = float(row.get('Menge', 0) if not pd.isna(row.get('Menge', None)) else 0.0)
            unit = str(row.get('matched_oeko_unit', '')).strip()
            artikel = str(row.get('Artikel', '')).lower()
            matched_material = str(row.get('matched_material', '')).lower()
            rohdichte = row.get('matched_rohdichte', np.nan)
            
            # Normalize unit
            unit_norm = unit.lower().replace('^', '').replace('\u00b3', '3').replace('³', '3').strip()
            
            # Already supported units - no conversion needed
            if unit_norm in ['kg', 'm3']:
                return menge, unit_norm, "No conversion needed"
            
            # Unit conversion logic based on material type and unit
            if unit_norm in ['qm', 'm2']:
                # Area-based conversion to volume (m3) then to mass (kg)
                # Use material-specific thickness assumptions
                thickness_m = 0.01  # Default 1cm thickness
                
                # Material-specific thickness assumptions
                if any(x in artikel for x in ['beton', 'concrete', 'estrich']):
                    thickness_m = 0.15  # 15cm for concrete slabs
                elif any(x in artikel for x in ['dach', 'roof', 'membrane', 'folie']):
                    thickness_m = 0.005  # 5mm for membranes/roofing
                elif any(x in artikel for x in ['wand', 'wall', 'mauer']):
                    thickness_m = 0.20  # 20cm for walls
                elif any(x in artikel for x in ['dämmung', 'insulation', 'isolierung']):
                    thickness_m = 0.10  # 10cm for insulation
                elif any(x in artikel for x in ['blech', 'sheet', 'platte']):
                    thickness_m = 0.002  # 2mm for metal sheets
                
                volume_m3 = menge * thickness_m
                
                # Convert to kg if density available
                if not pd.isna(rohdichte) and rohdichte > 0:
                    mass_kg = volume_m3 * float(rohdichte)
                    return mass_kg, 'kg', f"Converted: {menge} m² × {thickness_m}m × {rohdichte} kg/m³ = {mass_kg:.2f} kg"
                else:
                    return volume_m3, 'm3', f"Converted: {menge} m² × {thickness_m}m = {volume_m3:.3f} m³"
            
            elif unit_norm in ['pcs.', 'pcs', 'stk', 'st', 'stück']:
                # Piece-based conversion to mass (kg)
                # Use material-specific weight per piece
                weight_per_piece_kg = 1.0  # Default 1kg per piece
                
                # Material-specific weight assumptions
                if any(x in artikel for x in ['schraube', 'screw', 'bolt', 'mutter']):
                    weight_per_piece_kg = 0.01  # 10g for small fasteners
                elif any(x in artikel for x in ['nagel', 'nail']):
                    weight_per_piece_kg = 0.005  # 5g for nails
                elif any(x in artikel for x in ['ziegel', 'brick', 'stein']):
                    weight_per_piece_kg = 2.5  # 2.5kg for bricks
                elif any(x in artikel for x in ['balken', 'beam', 'träger']):
                    weight_per_piece_kg = 50.0  # 50kg for beams
                elif any(x in artikel for x in ['platte', 'panel', 'board']):
                    weight_per_piece_kg = 25.0  # 25kg for panels
                elif any(x in artikel for x in ['rohr', 'pipe', 'tube']):
                    weight_per_piece_kg = 10.0  # 10kg for pipes
                elif any(x in artikel for x in ['fenster', 'window', 'tür', 'door']):
                    weight_per_piece_kg = 30.0  # 30kg for windows/doors
                elif any(x in artikel for x in ['dachziegel', 'tile']):
                    weight_per_piece_kg = 3.0  # 3kg for roof tiles
                
                # Check if matched material gives us better weight estimate
                if any(x in matched_material for x in ['stahl', 'steel', 'eisen']):
                    weight_per_piece_kg *= 7.85  # Steel density factor
                elif any(x in matched_material for x in ['holz', 'wood', 'timber']):
                    weight_per_piece_kg *= 0.6   # Wood density factor
                elif any(x in matched_material for x in ['aluminium', 'aluminum']):
                    weight_per_piece_kg *= 2.7   # Aluminum density factor
                
                mass_kg = menge * weight_per_piece_kg
                return mass_kg, 'kg', f"Converted: {menge} pcs × {weight_per_piece_kg:.3f} kg/pc = {mass_kg:.2f} kg"
            
            elif unit_norm == 'm':
                # Linear meter conversion to mass (kg)
                # Use material-specific weight per meter
                weight_per_meter_kg = 1.0  # Default 1kg per meter
                
                # Material-specific linear weight assumptions
                if any(x in artikel for x in ['stahl', 'steel', 'eisen', 'bewehrung', 'betonstahl']):
                    # Steel reinforcement - estimate from diameter
                    if '8' in artikel:
                        weight_per_meter_kg = 0.395  # 8mm rebar
                    elif '10' in artikel:
                        weight_per_meter_kg = 0.617  # 10mm rebar
                    elif '12' in artikel:
                        weight_per_meter_kg = 0.888  # 12mm rebar
                    elif '14' in artikel:
                        weight_per_meter_kg = 1.208  # 14mm rebar
                    elif '16' in artikel:
                        weight_per_meter_kg = 1.578  # 16mm rebar
                    elif '20' in artikel:
                        weight_per_meter_kg = 2.466  # 20mm rebar
                    elif '25' in artikel:
                        weight_per_meter_kg = 3.853  # 25mm rebar
                    else:
                        weight_per_meter_kg = 1.5  # Default for steel
                
                elif any(x in artikel for x in ['rohr', 'pipe', 'tube']):
                    weight_per_meter_kg = 5.0  # 5kg/m for pipes
                elif any(x in artikel for x in ['kabel', 'cable', 'leitung']):
                    weight_per_meter_kg = 0.5  # 0.5kg/m for cables
                elif any(x in artikel for x in ['holz', 'wood', 'balken']):
                    weight_per_meter_kg = 15.0  # 15kg/m for wooden beams
                elif any(x in artikel for x in ['profil', 'profile']):
                    weight_per_meter_kg = 8.0  # 8kg/m for profiles
                
                mass_kg = menge * weight_per_meter_kg
                return mass_kg, 'kg', f"Converted: {menge} m × {weight_per_meter_kg:.3f} kg/m = {mass_kg:.2f} kg"
            
            else:
                # Unknown unit - return original
                return menge, unit_norm, f"Unknown unit '{unit}' - no conversion available"
                
        except Exception as e:
            return 0.0, unit, f"Conversion error: {str(e)}"

    def calculate_material_co2e(self, row: pd.Series) -> Tuple[float, str]:
        """
        Step 3: Calculate material CO₂e for a single row with unit conversion
        
        Args:
            row: DataFrame row with matched data
            
        Returns:
            Tuple of (co2e_value, calculation_status)
        """
        try:
            # Handle missing GWP first
            gwp = row['matched_gwp']
            if gwp == 'MISSING' or pd.isna(gwp):
                return 0.0, "Error: GWP missing"

            try:
                gwp = float(str(gwp).replace(',', '.'))
            except Exception:
                return 0.0, "Error: Invalid GWP value"

            # Try unit conversion for unsupported units
            converted_menge, converted_unit, conversion_status = self.convert_unsupported_units(row)
            
            if converted_menge <= 0:
                return 0.0, f"Error: Invalid quantity after conversion"
            
            rohdichte = row.get('matched_rohdichte', np.nan)

            # Calculate CO2e based on converted unit
            if converted_unit == 'kg':
                # Direct calculation: Converted Menge (kg) * GWP
                co2e = converted_menge * gwp
                if "Converted:" in conversion_status:
                    status = f"Success: {conversion_status}"
                else:
                    status = "Success: kg unit"

            elif converted_unit == 'm3':
                # For m3 units, we can calculate directly
                co2e = converted_menge * gwp
                if "Converted:" in conversion_status:
                    status = f"Success: {conversion_status}"
                else:
                    status = "Success: m³ unit"

            else:
                # Still unsupported after conversion attempt
                return 0.0, f"Error: Unit '{converted_unit}' not supported - {conversion_status}"
            
            return max(0.0, co2e), status
            
        except Exception as e:
            return 0.0, f"Error: Calculation failed - {str(e)}"
    
    def calculate_all_co2e(self) -> None:
        """
        Step 3: Calculate CO₂e for all materials
        """
        logger.info("=== STEP 3: CO₂E CALCULATION (MATERIAL A1-A3) ===")
        
        if self.matched_df is None:
            raise ValueError("No matched data available. Run generate_embeddings_and_match() first.")
        
        # Apply CO₂e calculation to all rows
        co2e_results = self.matched_df.apply(self.calculate_material_co2e, axis=1, result_type='expand')
        
        self.matched_df['calculated_co2e_a1_a3'] = co2e_results[0]
        self.matched_df['calculation_status'] = co2e_results[1]
        
        # Calculate summary statistics
        total_co2e = self.matched_df['calculated_co2e_a1_a3'].sum()
        total_weight = self.matched_df['Menge'].sum()
        successful_calcs = len(self.matched_df[self.matched_df['calculation_status'].str.contains('Success', na=False)])
        
        logger.info(f"CO₂e calculation completed:")
        logger.info(f"  Total CO₂e (A1-A3): {total_co2e:,.2f} kg CO₂e")
        logger.info(f"  Total material weight: {total_weight:,.2f} kg")
        logger.info(f"  CO₂e intensity: {total_co2e/total_weight:.4f} kg CO₂e/kg material")
        logger.info(f"  Successful calculations: {successful_calcs}/{len(self.matched_df)} ({successful_calcs/len(self.matched_df)*100:.1f}%)")
    
    def simulate_transport_co2e(self) -> None:
        """
        Step 4: Simulate transport CO₂e (A4 module)
        """
        logger.info("=== STEP 4: TRANSPORT CO₂E SIMULATION ===")
        
        # Simple transport simulation
        # Assumption: Average transport distance 100km, truck emission factor 0.8 kg CO₂e/tkm
        avg_distance_km = 100
        truck_emission_factor = 0.0008  # kg CO₂e per kg per km
        
        self.matched_df['transport_distance_km'] = avg_distance_km
        self.matched_df['calculated_co2e_a4'] = (
            self.matched_df['Menge'] * avg_distance_km * truck_emission_factor
        )
        
        total_transport_co2e = self.matched_df['calculated_co2e_a4'].sum()
        logger.info(f"Transport CO₂e simulation completed:")
        logger.info(f"  Total transport CO₂e (A4): {total_transport_co2e:,.2f} kg CO₂e")
        logger.info(f"  Average distance assumed: {avg_distance_km} km")
    
    def generate_final_report(self) -> None:
        """
        Step 5: Generate final CSRD-compliant report
        """
        logger.info("=== STEP 5: FINAL REPORT GENERATION ===")
        
        # Calculate total CO₂e
        self.matched_df['total_co2e'] = (
            self.matched_df['calculated_co2e_a1_a3'] + 
            self.matched_df['calculated_co2e_a4']
        )
        
        # Select columns for final report
        report_columns = [
            'Lieferant',
            'Artikel-Nummer', 
            'Artikel',
            'Menge',
            'Einheit',
            'matched_material',
            'matched_category',
            'similarity_score',
            'matched_oeko_unit',
            'calculated_co2e_a1_a3',
            'calculated_co2e_a4',
            'total_co2e',
            'calculation_status'
        ]
        
        final_df = self.matched_df[report_columns].copy()
        
        # Round numeric columns
        numeric_cols = ['similarity_score', 'calculated_co2e_a1_a3', 'calculated_co2e_a4', 'total_co2e']
        for col in numeric_cols:
            final_df[col] = final_df[col].round(4)
        
        # Generate summary statistics
        print("\n" + "="*80)
        print("CSRD CO₂ REPORTING - EXECUTIVE SUMMARY")
        print("="*80)
        
        total_materials = len(final_df)
        total_weight = final_df['Menge'].sum()
        total_material_co2e = final_df['calculated_co2e_a1_a3'].sum()
        total_transport_co2e = final_df['calculated_co2e_a4'].sum()
        grand_total_co2e = final_df['total_co2e'].sum()
        
        print(f"📊 PROJECT TOTALS:")
        print(f"   • Total materials processed: {total_materials:,} items")
        print(f"   • Total material weight: {total_weight:,.2f} kg")
        print(f"   • Material CO₂e (A1-A3): {total_material_co2e:,.2f} kg CO₂e")
        print(f"   • Transport CO₂e (A4): {total_transport_co2e:,.2f} kg CO₂e")
        print(f"   • GRAND TOTAL CO₂e: {grand_total_co2e:,.2f} kg CO₂e")
        
        print(f"\n🎯 KEY PERFORMANCE INDICATORS:")
        print(f"   • CO₂e intensity: {grand_total_co2e/total_weight:.4f} kg CO₂e/kg material")
        print(f"   • Material vs Transport ratio: {total_material_co2e/total_transport_co2e:.1f}:1")
        
        # Top CO₂e contributors
        print(f"\n🔝 TOP 5 CO₂e CONTRIBUTORS:")
        top_contributors = final_df.nlargest(5, 'total_co2e')
        for i, (_, row) in enumerate(top_contributors.iterrows(), 1):
            print(f"   {i}. {row['Artikel'][:50]}... - {row['total_co2e']:,.2f} kg CO₂e")
        
        # Export to CSV
        final_df.to_csv(OUTPUT_FILE, sep=';', index=False, encoding='utf-8-sig')
        logger.info(f"Final report exported to {OUTPUT_FILE}")
        
        print(f"\n📄 Report exported to: {OUTPUT_FILE}")
        print("="*80)


def main():
    """Main execution function"""
    print("🌱 VESTIGAS CSRD CO₂ REPORTING PIPELINE")
    print("=" * 50)
    print(f"📅 Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 OpenAI Available: {OPENAI_AVAILABLE}")
    print(f"☁️  Azure Endpoint: {AZURE_ENDPOINT}")
    
    try:
        # Initialize pipeline with Azure OpenAI
        pipeline = CSRDReportingPipeline(api_key=SUBSCRIPTION_KEY)
        
        # Execute the full pipeline
        pipeline.load_and_clean_data()
        pipeline.generate_embeddings_and_match()  
        pipeline.calculate_all_co2e()
        pipeline.simulate_transport_co2e()
        pipeline.generate_final_report()
        
        print("\n✅ PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise


if __name__ == "__main__":
    main()
