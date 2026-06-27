import os
from openai import OpenAI

try:
    import streamlit as st
    _api_key = st.secrets.get("GROQ_API_KEY", "")
except Exception:
    _api_key = os.getenv("GROQ_API_KEY", "")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=_api_key,
)

MODEL = "llama-3.3-70b-versatile"

INTENTS = {
    "red_team":  ["exploit", "payload", "reverse shell", "privilege escalation", "CVE", "metasploit", "SQLi", "XSS", "SSRF", "RCE", "buffer overflow", "هجوم", "اختراق", "ثغرة"],
    "blue_team": ["firewall", "IDS", "IPS", "hardening", "patch", "defense", "incident response", "SIEM", "حماية", "دفاع", "تحديث"],
    "soc":       ["log", "alert", "SIEM", "threat hunting", "SOC", "monitoring", "triage", "investigation", "لوج", "مراقبة", "تحليل"],
    "general":   [],
}


def _keyword_classify(text: str) -> str | None:
    text_lower = text.lower()
    scores = {k: 0 for k in INTENTS}
    for intent, keywords in INTENTS.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                scores[intent] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else None


def classify_intent(user_message: str) -> dict:
    keyword_result = _keyword_classify(user_message)
    if keyword_result:
        return {"intent": keyword_result, "method": "keyword"}

    prompt = f"""Classify this cybersecurity question into exactly one category.
Categories: red_team, blue_team, soc, general
Question: "{user_message}"
Reply with only the category name, nothing else."""

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0.0,
        )
        raw = resp.choices[0].message.content.strip().lower()
        intent = raw if raw in INTENTS else "general"
        return {"intent": intent, "method": "llm"}
    except Exception:
        return {"intent": "general", "method": "fallback"}


def extract_topic(user_message: str) -> str:
    prompt = f'Extract the main cybersecurity topic from this message in 2-4 words max: "{user_message}". Reply with only the topic.'
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20,
            temperature=0.0,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return "Cybersecurity"