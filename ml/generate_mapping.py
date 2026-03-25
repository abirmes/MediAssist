import pandas as pd
import json
import os
from groq import Groq

train = pd.read_csv('/app/ml/data/raw/trainings.csv', encoding='latin-1')
train.columns = [c.replace('\xa0', ' ').strip() for c in train.columns]
test = pd.read_csv('/app/ml/data/raw/testing.csv', encoding='latin-1')
test.columns = [c.replace('\xa0', ' ').strip() for c in test.columns]
df = pd.concat([train, test], ignore_index=True)
diseases = df['Prognosis'].unique().tolist()
print(f'Maladies a classifier : {len(diseases)}')

client = Groq(api_key=os.getenv('GROQ_API_KEY'))
mapping = {}
batch_size = 50
batches = [diseases[i:i+batch_size] for i in range(0, len(diseases), batch_size)]

for i, batch in enumerate(batches):
    print(f'Batch {i+1}/{len(batches)}...')
    diseases_str = '\n'.join([f'- {d}' for d in batch])

    prompt = (
        "Classify each disease into exactly one category:\n"
        "- urgences: life-threatening, needs immediate ER\n"
        "- medecin: needs doctor in 24-48h\n"
        "- surveillance: mild, manageable at home\n\n"
        "Target: ~25% urgences, ~40% medecin, ~35% surveillance\n"
        "Be decisive. Do NOT put everything in medecin.\n\n"
        f"Diseases:\n{diseases_str}\n\n"
        'Return ONLY valid JSON like: {"Disease Name": "orientation", ...}'
    )

    response = client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0.1,
        max_tokens=2000
    )
    raw = response.choices[0].message.content.strip()
    print(f'  Preview: {raw[:100]}')

    if '```json' in raw:
        raw = raw.split('```json')[1].split('```')[0].strip()
    elif '```' in raw:
        raw = raw.split('```')[1].split('```')[0].strip()

    try:
        batch_result = json.loads(raw)
        if batch_result and isinstance(list(batch_result.values())[0], str):
            mapping.update(batch_result)
            print(f'  OK : {len(batch_result)} maladies')
        else:
            for orient, dlist in batch_result.items():
                if isinstance(dlist, list):
                    for d in dlist:
                        mapping[d.strip()] = orient
    except Exception as e:
        print(f'  Erreur: {e} | Raw: {raw[:200]}')

with open('/app/ml/data/processed/disease_orientation.json', 'w') as f:
    json.dump(mapping, f, indent=2, ensure_ascii=False)

from collections import Counter
print(f'\nTotal mappe : {len(mapping)}')
print(Counter(mapping.values()))