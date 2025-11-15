"""
AI Insights Generator - Fixed for Python 3.14 compatibility
"""
import os
from dotenv import load_dotenv
import sqlite3
import requests
import json

load_dotenv()

class InsightsGenerator:
    def __init__(self, db_name='contractors.db'):
        self.db_name = db_name
        
        # Get API key
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file!")
        
        print(f"✓ API Key loaded: {self.api_key[:20]}...")
        
        # Azure OpenAI endpoint
        self.api_url = "https://mvptesting.cognitiveservices.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2025-01-01-preview"
        self.headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key  # Azure uses 'api-key' not 'Authorization'
        }
    
    def generate_insight(self, contractor_data):
        """Generate AI insight using direct API call"""
        
        # Prepare contractor context
        context = f"""
Contractor Name: {contractor_data.get('name', 'Unknown')}
Rating: {contractor_data.get('rating', 'N/A')}/5.0
Address: {contractor_data.get('address', 'N/A')}
Phone: {contractor_data.get('phone', 'N/A')}
Website: {contractor_data.get('website', 'N/A')}
Description: {contractor_data.get('description') or 'No description'}
Certifications: {', '.join(contractor_data.get('certifications', [])) or 'None'}
Services: {', '.join(contractor_data.get('services', [])) or 'None'}
Reviews Count: {contractor_data.get('reviews_count', 'N/A')}
        """
        
        prompt = f"""You are a sales intelligence assistant for roofing distributors.

Based on this contractor information, generate a concise sales insight (2-3 sentences):
1. Key strengths or selling points
2. Potential business opportunities for a roofing materials distributor
3. Suggested talking points for sales engagement

Contractor Information:
{context}

Generate a professional, actionable insight for the sales team:"""
        
        # Prepare API request
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a B2B sales intelligence assistant specializing in the roofing industry."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 200,
            "temperature": 0.7
        }
        
        try:
            # Make API call using requests
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            # Check if request was successful
            if response.status_code == 200:
                data = response.json()
                insight = data['choices'][0]['message']['content'].strip()
                return insight
            else:
                print(f"  ✗ API Error {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"  ✗ Request timeout")
            return None
        except Exception as e:
            print(f"  ✗ Error generating insight: {e}")
            return None
    
    def process_all_contractors(self):
        """Generate insights for all contractors in database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Get contractors without insights
        cursor.execute('''
            SELECT c.id, c.name, c.rating, c.address, c.phone, c.website, c.description
            FROM contractors c
            LEFT JOIN insights i ON c.id = i.contractor_id
            WHERE i.id IS NULL
        ''')
        
        contractors = cursor.fetchall()
        columns = ['id', 'name', 'rating', 'address', 'phone', 'website', 'description']
        
        if len(contractors) == 0:
            print("\n✓ All contractors already have insights!")
            conn.close()
            return
        
        print(f"\n{'='*80}")
        print(f"Generating insights for {len(contractors)} contractors...")
        print(f"{'='*80}\n")
        
        success_count = 0
        failed_count = 0
        
        for idx, contractor_row in enumerate(contractors, 1):
            contractor = dict(zip(columns, contractor_row))
            
            # Get certifications
            cursor.execute('SELECT certification_name FROM certifications WHERE contractor_id = ?', 
                          (contractor['id'],))
            contractor['certifications'] = [row[0] for row in cursor.fetchall()]
            
            # Get services
            cursor.execute('SELECT service_name FROM services WHERE contractor_id = ?', 
                          (contractor['id'],))
            contractor['services'] = [row[0] for row in cursor.fetchall()]
            
            # Set reviews_count to None (column doesn't exist in database)
            contractor['reviews_count'] = None
            
            # Generate insight
            print(f"[{idx}/{len(contractors)}] Processing: {contractor['name'][:50]}...", end=" ")
            
            insight = self.generate_insight(contractor)
            
            if insight:
                # Save insight to database
                cursor.execute('''
                    INSERT INTO insights (contractor_id, insight_text)
                    VALUES (?, ?)
                ''', (contractor['id'], insight))
                conn.commit()
                print(f"✓")
                success_count += 1
            else:
                print(f"✗ Failed")
                failed_count += 1
            
            # Small delay to avoid rate limits
            import time
            time.sleep(0.5)
        
        conn.close()
        
        print(f"\n{'='*80}")
        print(f"COMPLETE!")
        print(f"{'='*80}")
        print(f"✓ Successfully generated: {success_count}")
        print(f"✗ Failed: {failed_count}")
        print(f"Total: {len(contractors)}")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("AI INSIGHTS GENERATOR")
    print("="*80)
    
    try:
        generator = InsightsGenerator()
        generator.process_all_contractors()
        
        print("\n✅ All insights generated successfully!")
        print("\nYou can now run: python3 evaluate_insights.py")
        
    except ValueError as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease create a .env file with your OPENAI_API_KEY")
    except FileNotFoundError:
        print(f"\n✗ Error: contractors.db not found!")
        print("Please run database.py first")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()