import pandas as pd

print("=== TRYING DIFFERENT ENCODINGS FOR OEKOBAUDAT FILE ===")
encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-16']

for encoding in encodings:
    try:
        df_oeko = pd.read_csv('OBD_2024_I_2025-10-22T16_19_14.csv', delimiter=';', encoding=encoding)
        print(f"\n✓ SUCCESS with encoding: {encoding}")
        print("Oekobaudat file columns:", df_oeko.columns.tolist())
        print(f"Shape: {df_oeko.shape}")
        if 'Modul' in df_oeko.columns:
            print(f"Unique Modul values: {df_oeko['Modul'].unique()}")
        print("\nFirst 2 rows:")
        print(df_oeko.head(2))
        break
    except Exception as e:
        print(f"✗ Failed with encoding {encoding}: {e}")
