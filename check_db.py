import sqlite3

conn = sqlite3.connect('leads.db')
cursor = conn.cursor()

print('=== Leads Table Columns ===')
cursor.execute('PRAGMA table_info(leads)')
for row in cursor.fetchall():
    print(f'  {row[1]} ({row[2]})')

print('\n=== Prediction Runs Table Columns ===')
cursor.execute('PRAGMA table_info(prediction_runs)')
for row in cursor.fetchall():
    print(f'  {row[1]} ({row[2]})')

conn.close()
