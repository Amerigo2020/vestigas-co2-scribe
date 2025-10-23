import pandas as pd

# Load the report with conversions
df = pd.read_csv('csrd_co2e_report_with_conversions.csv', sep=';', encoding='utf-8-sig')

print('🎯 UNIT CONVERSION SUCCESS ANALYSIS')
print('=' * 50)
print(f'Total items: {len(df)}')

successful = df[df['calculation_status'].str.contains('Success', na=False)]
print(f'Successful calculations: {len(successful)} ({len(successful)/len(df)*100:.1f}%)')

print('\n📊 CALCULATION STATUS BREAKDOWN:')
status_counts = df['calculation_status'].value_counts()
for status, count in status_counts.items():
    print(f'  {count:3d} ({count/len(df)*100:.1f}%) - {status[:100]}')

print('\n🔧 CONVERSION EXAMPLES:')
converted = df[df['calculation_status'].str.contains('Converted:', na=False)]
print(f'Items with unit conversions: {len(converted)}')

for i, (_, row) in enumerate(converted.head(8).iterrows()):
    artikel = str(row['Artikel'])[:50]
    status = str(row['calculation_status'])[:120]
    co2e = row['calculated_co2e_a1_a3']
    
    print(f'\n{i+1}. {artikel}...')
    print(f'   Status: {status}...')
    print(f'   CO₂e: {co2e:,.0f} kg')

print(f'\n📈 IMPACT OF CONVERSIONS:')
print(f'Before conversions (from previous runs): ~40% success rate')
print(f'After conversions: {len(successful)/len(df)*100:.1f}% success rate')
print(f'Improvement: +{len(successful)/len(df)*100 - 40:.1f} percentage points')
