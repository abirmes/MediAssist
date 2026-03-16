from groq import Groq
from config import get_settings

settings = get_settings()


def get_groq_client():
    return Groq(api_key=settings.GROQ_API_KEY)


def generate_medical_question(conversation_history: list,
                               question_number: int) -> str:
    """Génère une question médicale contextuelle via Groq."""
    client = get_groq_client()

    system_prompt = """You are a medical assistant helping to assess a patient's symptoms.
Ask targeted medical questions in French to better understand the patient's condition.
Questions should be about: duration, intensity (1-10), fever, location, associated symptoms.
Be empathetic and clear. Ask ONE question at a time.
IMPORTANT: Always add this disclaimer at the end of your responses:
'⚠️ Je ne suis pas un médecin. Consultez un professionnel de santé.'"""

    messages = [{"role": "system", "content": system_prompt}]

    if conversation_history:
        messages.extend(conversation_history)

    if question_number == 1:
        messages.append({
            "role": "user",
            "content": "Start by asking about the main symptom and its duration."
        })
    else:
        messages.append({
            "role": "user",
            "content": f"Ask question {question_number} based on previous answers."
        })

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=300
    )
    return response.choices[0].message.content


def generate_explanation(orientation: str, symptoms: list,
                          severity_score: float) -> str:
    """Génère une explication en langage naturel via Groq."""
    client = get_groq_client()

    orientation_labels = {
        "urgences":     "appel immédiat au 15 / SAMU ou rendez-vous aux urgences",
        "medecin":      "consultation médicale dans les 24-48 heures",
        "surveillance": "surveillance à domicile avec auto-soins"
    }

    prompt = f"""Patient symptoms: {', '.join(symptoms)}
Severity score: {severity_score}/100
Recommended orientation: {orientation_labels.get(orientation, orientation)}

Write a clear, empathetic explanation in French (3-4 sentences) explaining:
1. Why this orientation is recommended
2. What the patient should do concretely
3. Warning signs to watch for

Always end with: '⚠️ Cette orientation est indicative et ne remplace pas un avis médical.'"""

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=400
    )
    return response.choices[0].message.content