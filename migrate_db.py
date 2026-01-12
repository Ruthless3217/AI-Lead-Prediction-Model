import sqlite3

# Connect to the database
conn = sqlite3.connect('leads.db')
cursor = conn.cursor()

print('Adding missing columns to leads table...')

# Add missing columns to leads table
try:
    cursor.execute('ALTER TABLE leads ADD COLUMN run_id INTEGER')
    print('✓ Added run_id column')
except sqlite3.OperationalError as e:
    print(f'  run_id: {e}')

try:
    cursor.execute('ALTER TABLE leads ADD COLUMN priority TEXT')
    print('✓ Added priority column')
except sqlite3.OperationalError as e:
    print(f'  priority: {e}')

try:
    cursor.execute('ALTER TABLE leads ADD COLUMN raw_data TEXT')
    print('✓ Added raw_data column')
except sqlite3.OperationalError as e:
    print(f'  raw_data: {e}')

conn.commit()
conn.close()

print('\n✓ Database migration complete!')
print('\nVerifying columns...')

# Verify
conn = sqlite3.connect('leads.db')
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(leads)')
print('\nLeads table columns:')
for row in cursor.fetchall():
    print(f'  • {row[1]} ({row[2]})')
conn.close()
