import glob
import json
import os
import re

files = glob.glob(r'C:\Users\dlohn\.gemini\antigravity-ide\brain\*\.system_generated\logs\transcript.jsonl')
print(f"Total transcripts found: {len(files)}")

sessions_found = []

for filepath in files:
    parts = filepath.split(os.sep)
    # find brain index
    try:
        b_idx = parts.index('brain')
        sess_id = parts[b_idx + 1]
    except Exception:
        sess_id = "unknown"
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if '"USER_INPUT"' in line or '"USER_EXPLICIT"' in line:
                try:
                    data = json.loads(line)
                    content = data.get('content', '')
                    m = re.search(r'<USER_REQUEST>(.*?)</USER_REQUEST>', content, re.DOTALL)
                    req = m.group(1).strip() if m else ''
                    date = data.get('created_at', '')
                    if req:
                        sessions_found.append({
                            'session_id': sess_id,
                            'date': date,
                            'prompt': req,
                            'file': filepath
                        })
                except Exception:
                    pass

print(f"Total user requests extracted: {len(sessions_found)}")

# Sort by date
sessions_found.sort(key=lambda x: x['date'], reverse=True)

# Print recent user requests and filter for keywords
print("\n=== RECENT USER PROMPTS ===")
for item in sessions_found[:40]:
    p_lower = item['prompt'].lower()
    print(f"Session: {item['session_id']} | Date: {item['date']}")
    print(f"Prompt: {item['prompt'][:250]}\n" + "-"*50)
