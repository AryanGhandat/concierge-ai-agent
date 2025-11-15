import os, json, re
import pandas as pd
from datetime import datetime, timedelta
from dateutil import parser as date_parser

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
USE_OPENAI = OPENAI_API_KEY is not None
if USE_OPENAI:
    try:
        import openai
        openai.api_key = OPENAI_API_KEY
    except Exception:
        USE_OPENAI = False

def generate_sample_emails(path='emails.csv'):
    rows = [
        {
            'id': 1,
            'from': 'manager@example.com',
            'subject': 'Please prepare Q3 report',
            'date': '2025-11-01',
            'body': "Hi Aryan, Can you prepare the Q3 sales report by next Friday? Also include the new region's metrics. Let's sync on Monday. Thanks!"
        },
        {
            'id': 2,
            'from': 'hr@example.com',
            'subject': 'Complete mandatory training',
            'date': '2025-11-02',
            'body': 'Dear team, Please complete the mandatory security training before Nov 20. Certificates will be uploaded to the portal.'
        },
        {
            'id': 3,
            'from': 'friend@example.com',
            'subject': 'Weekend plans',
            'date': '2025-11-03',
            'body': "Hey! Want to go hiking this Saturday?"
        }
    ]
    pd.DataFrame(rows).to_csv(path, index=False)
    print('Saved sample emails to', path)

def make_prompt_for_email(email_row):
    prompt = (
        "You are a concise assistant that: 1) Summarizes the email in one sentence;"
        " 2) Extracts action items as JSON array with fields: task, priority (Low/Medium/High), due (YYYY-MM-DD or null)."
        " Provide only valid JSON for the 'tasks' field.\n\nEmail:\n" +
        f"Subject: {email_row['subject']}\nBody: {email_row['body']}\n\n"
    )
    return prompt

def process_email_with_openai(email_row, max_tokens=300):
    prompt = make_prompt_for_email(email_row)
    try:
        resp = openai.ChatCompletion.create(
            model='gpt-4o-mini',
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=max_tokens,
            temperature=0.0,
        )
        text = resp['choices'][0]['message']['content'].strip()
        return text
    except Exception as e:
        print('OpenAI API error:', e)
        return None

def rule_based_extract(email_row):
    text = (str(email_row.get('subject','')) + ' ' + str(email_row.get('body',''))).lower()
    tasks = []
    if 'report' in text:
        due = None
        if 'next friday' in text:
            due_date = datetime.today() + timedelta((4 - datetime.today().weekday()) % 7)
            due = due_date.strftime('%Y-%m-%d')
        tasks.append({'task': 'Prepare report', 'priority': 'High', 'due': due})
    if 'training' in text:
        m = re.search(r'(by|before) (\w+ \d{1,2})', text)
        due = None
        if m:
            try:
                due = str(date_parser.parse(m.group(2), fuzzy=True).date())
            except Exception:
                due = m.group(2)
        tasks.append({'task': 'Complete mandatory training', 'priority': 'High', 'due': due})
    return {
        'summary': text[:200] + ('...' if len(text)>200 else ''),
        'tasks': tasks
    }

def run_agent(input_csv='emails.csv', output_csv='email_agent_output.csv'):
    if not os.path.exists(input_csv):
        generate_sample_emails(input_csv)
    emails = pd.read_csv(input_csv)
    results = []
    for _, row in emails.iterrows():
        if USE_OPENAI:
            out = process_email_with_openai(row)
            if out is None:
                parsed = rule_based_extract(row)
                results.append({'id': row['id'], 'summary': parsed['summary'], 'tasks': parsed['tasks']})
            else:
                jmatch = re.search(r"\{.*\}|\[.*\]", out, re.DOTALL)
                if jmatch:
                    try:
                        parsed_json = json.loads(jmatch.group(0))
                        if isinstance(parsed_json, list):
                            tasks = parsed_json
                            summary = out.split('\n')[0]
                        elif isinstance(parsed_json, dict) and 'tasks' in parsed_json:
                            tasks = parsed_json['tasks']
                            summary = parsed_json.get('summary', out.split('\n')[0])
                        else:
                            tasks = []
                            summary = out
                    except Exception:
                        tasks = []
                        summary = out
                else:
                    parsed = rule_based_extract(row)
                    summary = parsed['summary']
                    tasks = parsed['tasks']
                results.append({'id': row['id'], 'summary': summary, 'tasks': tasks})
        else:
            parsed = rule_based_extract(row)
            results.append({'id': row['id'], 'summary': parsed['summary'], 'tasks': parsed['tasks']})
    out_df = pd.DataFrame([{'id': r['id'], 'summary': r['summary'], 'tasks': json.dumps(r['tasks'])} for r in results])
    out_df.to_csv(output_csv, index=False)
    print('Saved', output_csv)

if __name__ == '__main__':
    run_agent()
