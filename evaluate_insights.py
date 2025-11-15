"""
LLM Evaluation Framework
"""
import sqlite3
import json

class InsightEvaluator:
    def __init__(self, db_name='contractors.db'):
        self.db_name = db_name
    
    def evaluate_insight(self, insight_text, contractor_data):
        scores = {}
        scores['specificity'] = self.score_specificity(insight_text, contractor_data)
        scores['actionability'] = self.score_actionability(insight_text)
        scores['relevance'] = self.score_relevance(insight_text)
        scores['clarity'] = self.score_clarity(insight_text)
        scores['length'] = self.score_length(insight_text)
        scores['overall'] = sum(scores.values()) / len(scores)
        return scores
    
    def score_specificity(self, insight, contractor_data):
        score = 0
        if contractor_data.get('rating') and str(contractor_data['rating']) in insight:
            score += 3
        if contractor_data.get('name'):
            name_parts = contractor_data['name'].split()
            if any(part in insight for part in name_parts):
                score += 2
        return min(score, 10)
    
    def score_actionability(self, insight):
        action_keywords = ['approach', 'mention', 'highlight', 'discuss', 'opportunity', 'recommend']
        keyword_count = sum(1 for keyword in action_keywords if keyword.lower() in insight.lower())
        return min(keyword_count * 3, 10)
    
    def score_relevance(self, insight):
        score = 5
        relevant_keywords = ['roofing', 'material', 'product', 'quality', 'service']
        matches = sum(1 for keyword in relevant_keywords if keyword in insight.lower())
        return min(score + matches, 10)
    
    def score_clarity(self, insight):
        score = 10
        sentences = [s for s in insight.split('.') if s.strip()]
        if sentences:
            avg_words = sum(len(s.split()) for s in sentences) / len(sentences)
            if avg_words > 30:
                score -= 3
        return max(score, 0)
    
    def score_length(self, insight):
        sentences = len([s for s in insight.split('.') if s.strip()])
        word_count = len(insight.split())
        if 2 <= sentences <= 4 and 50 <= word_count <= 120:
            return 10
        elif 1 <= sentences <= 5 and 30 <= word_count <= 150:
            return 7
        return 4
    
    def generate_report(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.id, c.name, c.rating, i.insight_text
            FROM contractors c
            JOIN insights i ON c.id = i.contractor_id
        ''')
        
        results = []
        
        for row in cursor.fetchall():
            contractor_data = {'id': row[0], 'name': row[1], 'rating': row[2]}
            scores = self.evaluate_insight(row[3], contractor_data)
            results.append({
                'contractor_name': row[1],
                'insight': row[3],
                'scores': scores
            })
        
        conn.close()
        
        if not results:
            print("\n✗ No insights found!")
            return
        
        print("\n" + "="*80)
        print("INSIGHT EVALUATION REPORT")
        print("="*80)
        
        all_scores = {'specificity': [], 'actionability': [], 'relevance': [], 'clarity': [], 'length': [], 'overall': []}
        for result in results:
            for key, value in result['scores'].items():
                all_scores[key].append(value)
        
        print("\nAVERAGE SCORES:")
        for metric, scores in all_scores.items():
            avg = sum(scores) / len(scores) if scores else 0
            print(f"{metric.capitalize():20s}: {avg:.2f}/10")
        
        with open('evaluation_report.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print("\n✓ Report saved to evaluation_report.json")

if __name__ == "__main__":
    evaluator = InsightEvaluator()
    evaluator.generate_report()