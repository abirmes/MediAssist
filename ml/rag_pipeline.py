import os
import pandas as pd
from groq import Groq
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


DATA_PATH = 'ml/data/raw/'
CHROMA_PATH = 'ml/data/processed/chroma_db'

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_MODEL = 'llama-3.3-70b-versatile'
COLLECTION = 'mediassist_medical'

_vectorstore = None
_embeddings = None


def get_vectorstore():
    global _vectorstore, _embeddings

    if _vectorstore is not None:
        return _vectorstore

    _embeddings = HuggingFaceEmbeddings(
        model_name='sentence-transformers/all-MiniLM-L6-v2',
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

    if os.path.exists(CHROMA_PATH):
        _vectorstore = Chroma(
            collection_name=COLLECTION,
            embedding_function=_embeddings,
            persist_directory=CHROMA_PATH
        )
    else:
        docs = load_documents()

        _vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=_embeddings,
            collection_name=COLLECTION,
            persist_directory=CHROMA_PATH
        )

    return _vectorstore


def load_documents():
    docs = []

    try:
        df = pd.read_csv(f'{DATA_PATH}symptom_Description.csv')
        df.columns = [c.strip() for c in df.columns]

        for _, row in df.iterrows():
            disease = str(row.iloc[0]).strip()
            desc = str(row.iloc[1]).strip()

            docs.append(Document(
                page_content=f"{disease}: {desc}",
                metadata={'disease': disease, 'type': 'description'}
            ))
    except Exception:
        pass

    try:
        df = pd.read_csv(f'{DATA_PATH}symptom_precaution.csv')
        df.columns = [c.strip() for c in df.columns]

        for _, row in df.iterrows():
            disease = str(row.iloc[0]).strip()
            precs = [
                str(row.iloc[i]).strip()
                for i in range(1, min(5, len(row)))
                if str(row.iloc[i]).strip() not in ['', 'nan']
            ]

            if precs:
                docs.append(Document(
                    page_content = f"{disease} precautions: {', '.join(precs)}",
                    metadata     = {
                        'disease':     disease,
                        'type':        'precaution',
                        'precautions': ', '.join(precs)  # ← liste → string
                    }
                ))
    except Exception:
        pass

    return docs


def generate_rag_response(symptoms, orientation, severity_score):
    vectorstore = get_vectorstore()

    query = ' '.join(symptoms)
    docs = vectorstore.similarity_search(query, k=5)

    context = []
    diseases = []
    precautions = []

    for doc in docs:
        context.append(f"- {doc.page_content}")
        diseases.append(doc.metadata.get('disease'))

        if doc.metadata.get('type') == 'precaution':
            precs = doc.metadata.get('precautions', '')
            if precs:
                precautions.extend(precs.split(', ')) 

    context = '\n'.join(context)

    labels = {
        'urgences': 'URGENCES',
        'medecin': 'MEDECIN',
        'surveillance': 'SURVEILLANCE'
    }

    prompt = f"""
Assistant médical.

Symptômes: {', '.join(symptoms)}
Gravité: {severity_score}/100
Orientation: {labels.get(orientation, orientation)}

{context}

Réponse courte en français:
- expliquer l’orientation
- donner précautions
- signes d’alerte

Finir par: Cette orientation ne remplace pas un médecin.
"""

    client = Groq(api_key=GROQ_API_KEY)

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0.3,
        max_tokens=500
    )

    return {
        'explanation': response.choices[0].message.content,
        'retrieved_docs': len(docs),
        'context_diseases': list(set(diseases))[:3],
        'precautions': precautions[:3]
    }


def benchmark(symptoms, orientation, severity_score):
    client = Groq(api_key=GROQ_API_KEY)

    no_rag = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{
            'role': 'user',
            'content': f"Symptoms: {', '.join(symptoms)}. Severity: {severity_score}. Orientation: {orientation}. Short advice in French."
        }],
        temperature=0.3,
        max_tokens=300
    )

    with_rag = generate_rag_response(symptoms, orientation, severity_score)

    print('\nWITHOUT RAG:\n', no_rag.choices[0].message.content)
    print('\nWITH RAG:\n', with_rag['explanation'])


if __name__ == '__main__':
    get_vectorstore()

    tests = [
        (['chest pain', 'sweating', 'shortness of breath'], 'urgences', 85),
        (['high fever', 'cough', 'fatigue'], 'medecin', 65),
        (['runny nose', 'sneezing'], 'surveillance', 30),
    ]

    for s, o, sc in tests:
        result = generate_rag_response(s, o, sc)
        print('\n', result['explanation'])

    benchmark(
        ['chest pain', 'sweating', 'shortness of breath'],
        'urgences',
        85
    )