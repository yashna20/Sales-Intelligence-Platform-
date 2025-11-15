"""
Database Setup and ETL Pipeline
"""
import sqlite3
import json
from datetime import datetime
import re

class ContractorDatabase:
    def __init__(self, db_name='contractors.db'):
        self.db_name = db_name
        self.create_tables()
    
    def create_tables(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contractors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                rating REAL,
                address TEXT,
                phone TEXT,
                website TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, address)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS certifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contractor_id INTEGER,
                certification_name TEXT,
                FOREIGN KEY (contractor_id) REFERENCES contractors(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contractor_id INTEGER,
                service_name TEXT,
                FOREIGN KEY (contractor_id) REFERENCES contractors(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contractor_id INTEGER,
                insight_text TEXT,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (contractor_id) REFERENCES contractors(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✓ Database tables created")
    
    def insert_contractor(self, contractor_data):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO contractors 
                (name, rating, address, phone, website, description, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                contractor_data.get('name'),
                self.clean_rating(contractor_data.get('rating')),
                contractor_data.get('address'),
                self.clean_phone(contractor_data.get('phone')),
                contractor_data.get('website'),
                contractor_data.get('description'),
                datetime.now()
            ))
            
            contractor_id = cursor.lastrowid
            
            for cert in contractor_data.get('certifications', []):
                if cert:
                    cursor.execute('''
                        INSERT INTO certifications (contractor_id, certification_name)
                        VALUES (?, ?)
                    ''', (contractor_id, cert))
            
            for service in contractor_data.get('services', []):
                if service:
                    cursor.execute('''
                        INSERT INTO services (contractor_id, service_name)
                        VALUES (?, ?)
                    ''', (contractor_id, service))
            
            conn.commit()
            return contractor_id
            
        except Exception as e:
            print(f"Error inserting contractor: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def clean_rating(self, rating):
        try:
            if rating:
                return float(str(rating).replace('★', '').strip())
        except:
            pass
        return 0.0
    
    def clean_phone(self, phone):
        if not phone:
            return None
        digits = re.sub(r'\D', '', str(phone))
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        return phone

def etl_process():
    print("\nStarting ETL Process...")
    
    try:
        with open('contractors_raw.json', 'r') as f:
            raw_data = json.load(f)
        print(f"✓ Loaded {len(raw_data)} raw records")
    except FileNotFoundError:
        print("✗ Error: contractors_raw.json not found!")
        return
    
    db = ContractorDatabase()
    success_count = 0
    
    for contractor in raw_data:
        if contractor.get('name'):
            contractor_id = db.insert_contractor(contractor)
            if contractor_id:
                success_count += 1
    
    print(f"✓ ETL completed: {success_count}/{len(raw_data)} contractors loaded")

if __name__ == "__main__":
    etl_process()