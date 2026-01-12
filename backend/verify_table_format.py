
import sys
import os
import pandas as pd

# Add project root to path (one level up from backend)
project_root = os.path.dirname(os.getcwd())
if os.path.basename(os.getcwd()) == 'backend':
    sys.path.append(project_root)
else:
    sys.path.append(os.getcwd())

# Mock necessary imports
class MockRequest:
    def __init__(self):
        self.message = "top 5 leads"
        self.context = ""
        self.filename = None

# Test Data
data = {
    'LeadID': ['L101', 'L102', 'L103'],
    'prediction_score': [0.95, 0.85, 0.75],
    'explanation': ['High time on site', 'Referral source', 'Opened email'],
    'TimeOnSite': [100, 50, 30],
    'PagesVisited': [5, 3, 1],
    'Source': ['LinkedIn', 'Google', 'Email'],
    'MeetingBooked': [1, 0, 0],
    'EmailOpened': [1, 1, 1]
}
df = pd.DataFrame(data)

def test_top_leads_logic(df_target):
    print("\n--- Testing Top Leads Logic ---")
    n_leads = 3
    
    # Logic copied/adapted from chat.py to verify string formatting without running full server
    df_top = df_target.sort_values(by='prediction_score', ascending=False).head(n_leads)
    
    response_lines = [f"Here are the top {n_leads} leads to focus on:\n"]
    response_lines.append("| Rank | Lead ID | Score | Key Insights |")
    response_lines.append("|---|---|---|---|")
    
    idx = 1
    for _, lead in df_top.iterrows():
        lead_id = lead.get('LeadID')
        score_val = lead.get('prediction_score', 0)
        score_pct = int(score_val * 100)
        
        reasons = []
        expl = lead.get('explanation')
        if expl: reasons.append(expl)
        
        reason_str = ", ".join(reasons[:2])
        response_lines.append(f"| {idx} | **{lead_id}** | {score_pct}% | {reason_str} |")
        idx += 1
        
    print("\n".join(response_lines))


