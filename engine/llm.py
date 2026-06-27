import os
from openai import OpenAI

try:
    import streamlit as st
    _api_key = st.secrets.get("GROQ_API_KEY", "")
except Exception:
    _api_key = os.getenv("GROQ_API_KEY", "")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=_api_key or "dummy_key_to_prevent_import_crash",
)

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are Alissa, an Elite Principal Software Engineer and Cybersecurity Architect.
You possess profound knowledge of computer science, advanced programming, cryptography, and full-stack development.
Your primary objective is to deliver EXACT, FLAWLESS, and PRODUCTION-READY code and cyber solutions.

CRITICAL RULES YOU MUST FOLLOW:
1. ALWAYS think step-by-step before answering. Break down complex problems into an architecture plan first.
2. When asked to write code or a project, DO NOT provide partial snippets. Provide the FULL, COMPLETE code files. Use markdown with file names (e.g., `**File: main.py**`).
3. Write clean, modular, scalable, and heavily documented code (docstrings, comments).
4. Apply best practices: error handling, logging, type hinting, and security standards (OWASP).
5. Never say "This is just an example" or "You should implement X yourself." YOU implement it.
6. Answer in the same language the user speaks (Arabic or English). If Arabic, use professional, high-end technical Arabic.
7. You are an expert in ALL programming languages (Python, C++, Go, Rust, JS, etc.) and cybersecurity tools.

Act as a world-class AI capable of building massive systems from scratch. Do not hold back."""


def ask(messages: list[dict], mode: str = "general") -> str:
    mode_ctx = {
        "red_team":  "Focus on offensive security: advanced exploitation, custom malware dev, penetration testing frameworks, red team architecture.",
        "blue_team": "Focus on defensive security: detection engineering, incident response, enterprise hardening, zero-trust.",
        "soc":       "Focus on SOC operations: SIEM engineering, automated threat hunting, SOAR playbooks, log analysis.",
        "general":   "You are an elite Software Engineer and Cybersecurity Expert. You build scalable software and secure systems.",
    }
    system = SYSTEM_PROMPT + f"\n\nCurrent mode: {mode_ctx.get(mode, mode_ctx['general'])}"
    full_messages = [{"role": "system", "content": system}] + messages
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=full_messages,
            max_tokens=6000,
            temperature=0.4,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"❌ خطأ في الـ AI model: {e}"


def ask_stream(messages: list[dict], mode: str = "general"):
    mode_ctx = {
        "red_team":  "Focus on offensive security: advanced exploitation, custom malware dev, penetration testing frameworks, red team architecture.",
        "blue_team": "Focus on defensive security: detection engineering, incident response, enterprise hardening, zero-trust.",
        "soc":       "Focus on SOC operations: SIEM engineering, automated threat hunting, SOAR playbooks, log analysis.",
        "general":   "You are an elite Software Engineer and Cybersecurity Expert. You build scalable software and secure systems.",
    }
    system = SYSTEM_PROMPT + f"\n\nCurrent mode: {mode_ctx.get(mode, mode_ctx['general'])}"
    full_messages = [{"role": "system", "content": system}] + messages
    try:
        stream = client.chat.completions.create(
            model=MODEL,
            messages=full_messages,
            max_tokens=6000,
            temperature=0.4,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
    except Exception as e:
        yield f"❌ خطأ في الـ AI model: {e}"


def generate_quiz(topic: str, level: str = "beginner") -> str:
    prompt = f"Generate one multiple-choice quiz question about '{topic}' for a {level} cybersecurity student. Include 4 options (A, B, C, D) and mark the correct answer."
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            max_tokens=512,
            temperature=0.5,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"❌ خطأ في توليد السؤال: {e}"