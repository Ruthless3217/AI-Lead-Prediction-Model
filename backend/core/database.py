import sqlite3
import json
from datetime import datetime
import os


# Point to backend/data/leads.db
DB_NAME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "leads.db")

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Create Prediction Runs Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS prediction_runs (
            run_id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_leads INTEGER,
            high_priority_count INTEGER,
            medium_priority_count INTEGER,
            low_priority_count INTEGER,
            accuracy REAL,
            f1_score REAL,
            pr_auc REAL,
            precision_at_k REAL,
            recall_at_k REAL,
            has_actual_data INTEGER DEFAULT 0
        )
    ''')
    
    # Simple migration: Add columns if they don't exist
    try:
        c.execute('ALTER TABLE prediction_runs ADD COLUMN f1_score REAL')
        c.execute('ALTER TABLE prediction_runs ADD COLUMN pr_auc REAL')
        c.execute('ALTER TABLE prediction_runs ADD COLUMN precision_at_k REAL')
        c.execute('ALTER TABLE prediction_runs ADD COLUMN recall_at_k REAL')
    except:
        # Columns likely exist
        pass

    # ... leads and notifications tables ... 
    
    # Create Leads Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            lead_id TEXT,
            source TEXT,
            time_on_site INTEGER,
            pages_visited INTEGER,
            email_opened INTEGER,
            meeting_booked INTEGER,
            converted INTEGER,
            prediction_score REAL,
            priority TEXT,
            raw_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (run_id) REFERENCES prediction_runs (run_id)
        )
    ''')
    
    # Create Notifications Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL, 
            message TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# ... save_lead, get_recent_leads ...

def save_lead(lead_data, prediction_score=None, run_id=None, priority=None):
    conn = get_db_connection()
    c = conn.cursor()
    # ... (same as before) ...
    try:
        # Store complete lead data as JSON for easy retrieval
        raw_data_json = json.dumps(lead_data)
        
        c.execute('''
            INSERT INTO leads (run_id, lead_id, source, time_on_site, pages_visited, email_opened, meeting_booked, converted, prediction_score, priority, raw_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            run_id,
            str(lead_data.get('LeadID', '')),
            lead_data.get('Source', ''),
            lead_data.get('TimeOnSite', 0),
            lead_data.get('PagesVisited', 0),
            lead_data.get('EmailOpened', 0),
            lead_data.get('MeetingBooked', 0),
            lead_data.get('Converted', 0),
            prediction_score,
            priority,
            raw_data_json
        ))
        conn.commit()
        lead_db_id = c.lastrowid
    except Exception as e:
        print(f"DB Error: {e}")
        lead_db_id = None
        
    conn.close()
    return lead_db_id

def get_recent_leads(limit=50):
    conn = get_db_connection()
    leads = conn.execute('SELECT * FROM leads ORDER BY created_at DESC LIMIT ?', (limit,)).fetchall()
    conn.close()
    return [dict(ix) for ix in leads]

def save_prediction_run(filename, total_leads, high_count, medium_count, low_count, accuracy=None, has_actual_data=False, metrics=None):
    """Save a prediction run to the database and return the run_id"""
    conn = get_db_connection()
    c = conn.cursor()
    
    if metrics is None: metrics = {}
    
    try:
        c.execute('''
            INSERT INTO prediction_runs (
                filename, total_leads, high_priority_count, medium_priority_count, low_priority_count, 
                accuracy, f1_score, pr_auc, precision_at_k, recall_at_k, has_actual_data
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            filename, total_leads, high_count, medium_count, low_count, 
            accuracy, 
            metrics.get('f1_score'), metrics.get('pr_auc'), 
            metrics.get('precision_at_k'), metrics.get('recall_at_k'),
            1 if has_actual_data else 0
        ))
        conn.commit()
        run_id = c.lastrowid
    except Exception as e:
        print(f"DB Error saving prediction run: {e}")
        run_id = None
    
    conn.close()
    return run_id

def get_prediction_history():
    """Get all prediction runs ordered by most recent first"""
    conn = get_db_connection()
    runs = conn.execute('''
        SELECT run_id, filename, timestamp, total_leads, 
               high_priority_count, medium_priority_count, low_priority_count, 
               accuracy, f1_score, pr_auc, precision_at_k, recall_at_k, has_actual_data
        FROM prediction_runs 
        ORDER BY timestamp DESC
    ''').fetchall()
    conn.close()
    return [dict(run) for run in runs]



def save_leads_batch(leads_data_list):
    """Save multiple leads in a single transaction for performance"""
    
    if not leads_data_list:
        return
        
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        # Chunking for stability (SQLite can perform poorly with massive single transactions)
        BATCH_SIZE = 5000
        total_items = len(leads_data_list)
        
        for i in range(0, total_items, BATCH_SIZE):
            chunk = leads_data_list[i:i + BATCH_SIZE]
            data_to_insert = []
            
            for item in chunk:
                lead_data = item.get('lead_data', {})
                prediction_score = item.get('prediction_score')
                run_id = item.get('run_id')
                priority = item.get('priority')
                
                # Fast JSON dump
                raw_data_json = json.dumps(lead_data, separators=(',', ':')) # compact json
                
                data_to_insert.append((
                    run_id,
                    str(lead_data.get('LeadID', '')),
                    lead_data.get('Source', ''),
                    lead_data.get('TimeOnSite', 0),
                    lead_data.get('PagesVisited', 0),
                    lead_data.get('EmailOpened', 0),
                    lead_data.get('MeetingBooked', 0),
                    lead_data.get('Converted', 0),
                    prediction_score,
                    priority,
                    raw_data_json
                ))
            
            c.executemany('''
                INSERT INTO leads (run_id, lead_id, source, time_on_site, pages_visited, email_opened, meeting_booked, converted, prediction_score, priority, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', data_to_insert)
            conn.commit() # Commit each chunk
    except Exception as e:
        print(f"DB Batch Error: {e}")
    finally:
        conn.close()

def get_leads_by_run(run_id):
    """Get all leads from a specific prediction run"""
    conn = get_db_connection()
    leads = conn.execute('''
        SELECT * FROM leads 
        WHERE run_id = ? 
        ORDER BY prediction_score DESC
    ''', (run_id,)).fetchall()
    conn.close()
    
    # Parse raw_data JSON back to dict
    result = []
    for lead in leads:
        lead_dict = dict(lead)
        if lead_dict.get('raw_data'):
            try:
                lead_dict['raw_data'] = json.loads(lead_dict['raw_data'])
            except:
                pass
        result.append(lead_dict)
    
    return result

# --- Search & Notifications ---

def search_leads(query):
    """Search leads by ID, source, or raw data content"""
    conn = get_db_connection()
    search_term = f"%{query}%"
    try:
        leads = conn.execute('''
            SELECT * FROM leads 
            WHERE lead_id LIKE ? 
            OR source LIKE ? 
            OR raw_data LIKE ?
            ORDER BY created_at DESC 
            LIMIT 50
        ''', (search_term, search_term, search_term)).fetchall()
        
        # Parse results
        result = []
        for lead in leads:
            lead_dict = dict(lead)
            if lead_dict.get('raw_data'):
                try:
                    lead_dict['raw_data'] = json.loads(lead_dict['raw_data'])
                except:
                    pass
            result.append(lead_dict)
        return result
    finally:
        conn.close()

def create_notification(noti_type, message):
    """Create a new notification"""
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO notifications (type, message) VALUES (?, ?)', (noti_type, message))
        conn.commit()
        return True
    except Exception as e:
        print(f"Notification Error: {e}")
        return False
    finally:
        conn.close()

def get_notifications(limit=10, unread_only=False):
    """Get notifications"""
    conn = get_db_connection()
    try:
        query = 'SELECT * FROM notifications'
        if unread_only:
            query += ' WHERE is_read = 0'
        query += ' ORDER BY created_at DESC LIMIT ?'
        
        notis = conn.execute(query, (limit,)).fetchall()
        return [dict(n) for n in notis]
    finally:
        conn.close()

def mark_notification_read(noti_id):
    """Mark a notification as read"""
    conn = get_db_connection()
    try:
        conn.execute('UPDATE notifications SET is_read = 1 WHERE id = ?', (noti_id,))
        conn.commit()
        return True
    finally:
        conn.close()

# Initialize on module load
if not os.path.exists(DB_NAME):
    init_db()
else:
    # Ensure table exists even if file exists
    init_db()
