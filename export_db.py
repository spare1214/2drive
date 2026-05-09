import sqlite3
import json

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Lista tutte le tabelle
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

data = {}

for table in tables:
    table_name = table[0]
    if table_name.startswith('sqlite_'):
        continue
    
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    # Nomi colonne
    col_names = [description[0] for description in cursor.description]
    
    # Converti in lista di dizionari
    table_data = []
    for row in rows:
        row_dict = {}
        for i, col in enumerate(col_names):
            row_dict[col] = row[i]
        table_data.append(row_dict)
    
    data[table_name] = table_data
    print(f"✅ Esportata tabella {table_name}: {len(table_data)} righe")

# Salva in file JSON
with open('database_export.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, default=str, ensure_ascii=False)

print(f"\n📁 Dati esportati in database_export.json")
conn.close()
