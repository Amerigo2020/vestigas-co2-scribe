import pandas as pd

print("=== EXAMINING WEIGHT DELIVERY FILE ===")
try:
    df_weight = pd.read_excel('aggregated_construction_site_weight.xlsx')
    print("Weight file columns:", df_weight.columns.tolist())
    print("\nFirst 3 rows:")
    print(df_weight.head(3))
    print(f"\nShape: {df_weight.shape}")
except Exception as e:
    print(f"Error reading weight file: {e}")

print("\n=== EXAMINING QUANTITY DELIVERY FILE ===")
try:
    df_quantity = pd.read_excel('aggregated_construction_site_quantity.xlsx')
    print("Quantity file columns:", df_quantity.columns.tolist())
    print("\nFirst 3 rows:")
    print(df_quantity.head(3))
    print(f"\nShape: {df_quantity.shape}")
except Exception as e:
    print(f"Error reading quantity file: {e}")

print("\n=== EXAMINING OEKOBAUDAT FILE ===")
try:
    df_oeko = pd.read_csv('OBD_2024_I_2025-10-22T16_19_14.csv', delimiter=';', encoding='utf-8-sig')
    print("Oekobaudat file columns:", df_oeko.columns.tolist())
    print("\nFirst 3 rows:")
    print(df_oeko.head(3))
    print(f"\nShape: {df_oeko.shape}")
    print(f"\nUnique Modul values: {df_oeko['Modul'].unique() if 'Modul' in df_oeko.columns else 'No Modul column'}")
except Exception as e:
    print(f"Error reading Oekobaudat file: {e}")
