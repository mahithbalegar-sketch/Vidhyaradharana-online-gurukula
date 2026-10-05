from datetime import datetime
import os
import math
import random
import time
import json
import base64
import urllib.request
import urllib.error
import html
import re
import threading
from streamlit.components.v1 import html as components_html
import streamlit as st  

# ============================================================
# API & AUTH CONFIGURATION
# ============================================================
def _secret(name, default=""):
    try:
        return st.secrets[name]
    except Exception:
        return os.environ.get(name, default)

GEMINI_API_KEY = _secret("GEMINI_API_KEY", "AQ.Ab8RN6KbP4LPmwXv1CNobIgz5dSXzIbei5XZvz6BRHwcuZOP_w")
SMTP_SENDER = _secret("SMTP_SENDER")
SMTP_APP_PASSWORD = _secret("SMTP_APP_PASSWORD")
PHONEPE_UPI = _secret("PHONEPE_UPI")
PHONEPE_AMOUNT = "250"
PAYMENTS_LIVE = True
APPROVAL_SALT = _secret("APPROVAL_SALT", "change-me")
ELEVENLABS_API_KEY = _secret("ELEVENLABS_API_KEY", "sk_8fd6e2649efc1f415456b49f1c53e2c0535ca20136316844")
ELEVENLABS_VOICE_ID = "EXAVITQu4vr4xnSDxMaL"
VOICE_NAME = "Sarah (English)"

VOICE_CATALOG = {
    "Sarah (English)": "EXAVITQu4vr4xnSDxMaL",
    "George (English)": "JBFqnCBsd6RMkjVDRZzb",
    "Alice (English)": "Xb7hH8MSUJpSbSDYk0k2",
    "Daniel (English)": "onwK4e9ZLuTAKqWW03F9",
    "Will (English)": "bIHbv24MWmeRgasZH58o",
    "Laura (English)": "FGY2WhTYpPnrIDTdsKH5",
    "Charlie (English)": "IKne3meq5aSn9XLyUdCD",
    "Callum (English)": "N2lVS1w4EtoT3dr4eOWO",
    "River (English)": "SAz9YHcvj6GT2YYXdXww",
    "Liam (English)": "TX3LPaxmHKxFdv7VOQHJ",
    "Matilda (English)": "XrExE9yKIg1WjnnlVkGX",
    "Jessica (English)": "cgSgspJ2msm6clMCkdW9",
    "Eric (English)": "cjVigY5qzO86Huf0OWal",
    "Brian (English)": "nPczCjzI2devNBz1zQrb",
    "Lily (English)": "pFZP5JQG7iQjIQuC4Bku",
}

INDIAN_LANGUAGES = [
    "English (India)",
    "Hindi",
    "Kannada",
    "Telugu",
    "Tamil",
    "Malayalam",
    "Marathi",
    "Gujarati",
    "Bengali",
    "Punjabi",
    "Odia",
    "Assamese",
    "Sanskrit",
    "Urdu",
]

st.set_page_config(
    page_title="विद्याराधना — Vidhyaradhana",
    page_icon="🪔",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(show_spinner=False)
def _prep_html(s):
    return "\n".join(ln.lstrip() for ln in s.strip("\n").splitlines())


def md(s):
    st.markdown(_prep_html(s), unsafe_allow_html=True)


def open_sidebar_button():
    """Shows a menu chip and clicks Streamlit's hidden sidebar toggle."""
    components_html(
        """
        <div style="font-family:Eczar,sans-serif;margin:0 0 8px 0;">
          <button id="vr-open-side" style="
            background:rgba(28,19,13,0.8);color:#f7eedb;border:1px solid rgba(201,147,59,0.45);
            border-radius:999px;padding:12px 18px;font-weight:700;cursor:pointer;
            backdrop-filter:blur(16px);box-shadow:0 8px 20px rgba(0,0,0,0.28);">
            ☰ Open menu
          </button>
          <span style="color:#c4ad99;font-size:12.5px;margin-left:8px;">
            If the left panel is hidden, tap this or the gold ☰ at the top-left.
          </span>
        </div>
        <script>
        function vrToggleSidebar() {
          const docs = [document, window.parent && window.parent.document].filter(Boolean);
          const sels = [
            '[data-testid="stSidebarCollapsedControl"]',
            '[data-testid="collapsedControl"]',
            '[data-testid="stExpandSidebarButton"]',
            'button[kind="header"]',
            '[data-testid="stBaseButton-header"]'
          ];
          for (const doc of docs) {
            for (const s of sels) {
              const el = doc.querySelector(s);
              if (el) { el.click(); return; }
            }
          }
        }
        const btn = document.getElementById("vr-open-side");
        if (btn) btn.addEventListener("click", vrToggleSidebar);
        </script>
        """,
        height=58,
    )


def play_browser_voice(text, lang_code="en-IN"):
    spoken = _speech_text(text)
    if not spoken:
        return
    safe_text = json.dumps(spoken)
    vol = float(st.session_state.get("voice_volume", 0.9))
    spd = float(st.session_state.get("voice_speed", 1.0))
    components_html(
        f"""
        <div style="font-family:Inter,sans-serif;display:flex;align-items:center;gap:8px;margin:8px 0;">
          <button id="vr-play" style="background:#c45b28;color:#fff;border:0;border-radius:999px;padding:8px 18px;font-size:13px;font-weight:700;cursor:pointer;">Play</button>
          <button id="vr-stop" style="background:#2a1c14;color:#f7eedb;border:1px solid #c45b28;border-radius:999px;padding:8px 18px;font-size:13px;font-weight:700;cursor:pointer;">Stop</button>
          <span style="color:#e6d3bb;font-size:13px;">Browser voice</span>
        </div>
        <script>
        const text = {safe_text};
        const p = document.getElementById("vr-play");
        const s = document.getElementById("vr-stop");
        function speakNow() {{
          if (!window.speechSynthesis) return;
          window.speechSynthesis.cancel();
          const msg = new SpeechSynthesisUtterance(text);
          msg.rate = {spd};
          msg.volume = {vol};
          msg.lang = "{lang_code}";
          window.speechSynthesis.speak(msg);
        }}
        if (p) p.onclick = speakNow;
        if (s) s.onclick = function() {{ if (window.speechSynthesis) window.speechSynthesis.cancel(); }};
        </script>
        """,
        height=54,
    )


def speak_browser_fallback(text, lang_code="en-IN"):
    play_browser_voice(text, lang_code)


def _speech_text(text):
    clean = re.sub(r"[#*_`>]+", "", str(text or ""))
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean[:900]


def _elevenlabs_bytes(voice_id, spoken, key):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    payload = {
        "text": spoken,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": float(st.session_state.get("voice_stability", 0.62)),
            "similarity_boost": 0.82,
            "style": 0.12,
            "use_speaker_boost": True,
        },
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "xi-api-key": key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=28) as resp:
            audio_bytes = resp.read()
        return base64.b64encode(audio_bytes).decode("ascii"), None
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="ignore")
        if e.code == 402:
            return None, "402"
        return None, f"Voice HTTP {e.code}: {err[:120]}"
    except Exception as e:
        return None, str(e)


def generate_elevenlabs_speech(text):
    key = (ELEVENLABS_API_KEY or os.environ.get("ELEVENLABS_API_KEY") or "").strip()
    spoken = _speech_text(text)
    if not key or not spoken:
        return None, "Missing voice key or text"
    voice_id = st.session_state.get("voice_id") or ELEVENLABS_VOICE_ID
    audio, err = _elevenlabs_bytes(voice_id, spoken, key)
    if audio:
        return audio, None
    if voice_id != ELEVENLABS_VOICE_ID:
        audio, err2 = _elevenlabs_bytes(ELEVENLABS_VOICE_ID, spoken, key)
        if audio:
            st.session_state.voice_fallback_note = "That voice needs a paid plan. Playing Sarah instead."
            return audio, None
        err = err2 or err
    return None, err or "Voice failed"


def play_named_voice(audio_b64):
    vol = float(st.session_state.get("voice_volume", 0.9))
    spd = float(st.session_state.get("voice_speed", 1.0))
    name = html.escape(str(st.session_state.get("voice_name", VOICE_NAME)))
    components_html(
        f"""
        <div style="font-family:Inter,sans-serif;display:flex;align-items:center;gap:8px;margin:8px 0;">
          <button id="vr-play" style="background:#c45b28;color:#fff;border:0;border-radius:999px;padding:8px 18px;font-size:13px;font-weight:700;cursor:pointer;">Play</button>
          <button id="vr-stop" style="background:#2a1c14;color:#f7eedb;border:1px solid #c45b28;border-radius:999px;padding:8px 18px;font-size:13px;font-weight:700;cursor:pointer;">Stop</button>
          <span style="color:#e6d3bb;font-size:13px;">{name}</span>
        </div>
        <audio id="aman-voice" preload="auto" src="data:audio/mpeg;base64,{audio_b64}"></audio>
        <script>
        const a = document.getElementById("aman-voice");
        if (a) {{ a.volume = {vol}; a.playbackRate = {spd}; }}
        const p = document.getElementById("vr-play");
        const s = document.getElementById("vr-stop");
        if (p) p.onclick = function(){{ if(a){{ a.currentTime = 0; a.play().catch(function(){{}}); }} }};
        if (s) s.onclick = function(){{ if(a){{ a.pause(); a.currentTime = 0; }} }};
        </script>
        """,
        height=54,
    )


# ============================================================
# VEDIC COLORS + IPHONE-STYLE LIQUID GLASS
# ============================================================
md("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rozha+One&family=Yatra+One&family=Cinzel:wght@600;700;800&family=Eczar:wght@500;600;700&family=Inter:wght@500;600;700&display=swap');

:root {
  --bg: #120c08;
  --surface: rgba(40, 26, 18, 0.72);
  --surface2: rgba(50, 32, 22, 0.82);
  --bhojpatra: #f7eedb;
  --muted: #c4ad99;
  --gerua: #c45b28;
  --brass: #d0a24a;
  --line: rgba(201,147,59,0.22);
  --border-carved: rgba(201,147,59,0.28);
  --ios: cubic-bezier(0.32, 0.72, 0, 1);
}

html, body, [class*="css"] {
  font-family: 'Eczar', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
  background-color: var(--bg) !important;
  -webkit-font-smoothing: antialiased;
}

.stApp, .stAppViewContainer, [data-testid="stMain"], [data-testid="stAppViewContainer"]>section,
.main .block-container {
  background:
    radial-gradient(ellipse at 50% -10%, rgba(201,147,59,0.16) 0%, transparent 42%),
    radial-gradient(circle at 50% 0%, #2a1a12 0%, var(--bg) 78%) !important;
  color: var(--bhojpatra) !important;
}

.main .block-container {
  max-width: 980px;
  padding: 1.2rem 1.2rem 5rem !important;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"],
footer, .stDeployButton { display: none !important; }

[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
[data-testid="stExpandSidebarButton"] {
  display: flex !important;
  visibility: visible !important;
  opacity: 1 !important;
  position: fixed !important;
  top: 14px !important;
  left: 14px !important;
  z-index: 100000 !important;
  width: 44px !important;
  height: 44px !important;
  border-radius: 22px !important;
  background: rgba(28,19,13,0.78) !important;
  backdrop-filter: blur(16px) !important;
  -webkit-backdrop-filter: blur(16px) !important;
  border: 1px solid rgba(201,147,59,0.45) !important;
  box-shadow: 0 8px 24px rgba(0,0,0,0.35) !important;
  color: #f7eedb !important;
  transition: transform 0.4s var(--ios), box-shadow 0.4s var(--ios) !important;
}
[data-testid="stSidebarCollapsedControl"]:hover,
[data-testid="collapsedControl"]:hover,
[data-testid="stExpandSidebarButton"]:hover {
  transform: scale(1.08) !important;
  box-shadow: 0 10px 28px rgba(201,147,59,0.28) !important;
}
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="collapsedControl"] svg,
[data-testid="stExpandSidebarButton"] svg {
  fill: #c9933b !important;
  color: #c9933b !important;
}

section[data-testid="stSidebar"] {
  transition: min-width 0.45s var(--ios), max-width 0.45s var(--ios), transform 0.45s var(--ios) !important;
}

h1, h2, h3 {
  font-family: 'Rozha One', 'Cinzel', serif !important;
  color: var(--brass) !important;
  letter-spacing: 0.4px;
  font-weight: 400 !important;
}

p, li, label, .stMarkdown, [data-testid="stMarkdownContainer"],
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p {
  color: #f7eedb !important;
  font-size: 15.5px;
}
.stCaption, small { color: #d8c4ae !important; }

section[data-testid="stSidebar"] {
  background: rgba(12,8,5,0.88) !important;
  border-right: 1px solid var(--line) !important;
  backdrop-filter: blur(22px) saturate(1.2) !important;
  -webkit-backdrop-filter: blur(22px) saturate(1.2) !important;
}
section[data-testid="stSidebar"] * { color: #eedcc8 !important; }
section[data-testid="stSidebar"] .stButton>button {
  background: rgba(40,26,18,0.55) !important;
  border: 1px solid transparent !important;
  color: #eedcc8 !important;
  text-align: left !important;
  border-radius: 16px !important;
  padding: 14px 16px !important;
  font-size: 15.5px !important;
  font-weight: 600 !important;
  margin-bottom: 7px !important;
  min-height: 50px !important;
}
section[data-testid="stSidebar"] .stButton>button:hover {
  background: rgba(54,34,23,0.9) !important;
  color: var(--bhojpatra) !important;
}
section[data-testid="stSidebar"] .stButton>button[kind="primary"] {
  background: linear-gradient(180deg, #d36a34 0%, var(--gerua) 100%) !important;
  color: #fff !important;
}

.stButton>button {
  min-height: 52px !important;
  border-radius: 18px !important;
  background: rgba(40,26,18,0.78) !important;
  color: var(--bhojpatra) !important;
  border: 1px solid var(--border-carved) !important;
  font-weight: 700 !important;
  font-size: 16px !important;
  backdrop-filter: blur(12px) !important;
}
.stButton>button:hover {
  border-color: var(--brass) !important;
  background: rgba(51,32,20,0.92) !important;
}
.stButton>button:active { transform: scale(0.97) !important; }
.stButton>button[kind="primary"] {
  background: linear-gradient(180deg, #d36a34 0%, var(--gerua) 100%) !important;
  color: #fff7ee !important;
  -webkit-text-fill-color: #fff7ee !important;
  border: 0 !important;
}

/* Make every form control readable like an app */
.stTextInput input, .stTextArea textarea, .stNumberInput input,
[data-baseweb="select"] > div, [data-baseweb="input"] input,
.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div {
  background: #2a1c14 !important;
  color: #f7eedb !important;
  border: 1px solid #7a5638 !important;
  border-radius: 14px !important;
  min-height: 48px !important;
}
.stTextArea textarea { min-height: 120px !important; }
.stTextInput input::placeholder, .stTextArea textarea::placeholder {
  color: #cbb59a !important;
}
[data-baseweb="select"] svg, .stSelectbox svg { fill: #f7eedb !important; }
div[role="radiogroup"] label, .stRadio label, .stCheckbox label {
  color: #f7eedb !important;
}
.stRadio div[role="radiogroup"] > label, .stRadio [data-testid="stMarkdownContainer"] p {
  color: #f7eedb !important;
}
[data-testid="stExpander"] {
  background: #23160f !important;
  border: 1px solid #7a5638 !important;
  border-radius: 16px !important;
}
[data-testid="stExpander"] summary, [data-testid="stExpander"] p {
  color: #f7eedb !important;
}
.stAlert, [data-testid="stAlert"] { color: #1d1d1f !important; }
.stSlider label, .stSelectSlider label { color: #f7eedb !important; }
[data-testid="stMetricValue"], [data-testid="stMetricDelta"] { color: #f7eedb !important; }
[data-testid="stMetricLabel"] { color: #e6d3bb !important; }

.mac-hero {
  position: relative;
  background: linear-gradient(180deg, rgba(56,36,24,0.88) 0%, rgba(28,19,13,0.86) 100%);
  border: 1px solid rgba(208,162,74,0.38);
  border-radius: 28px;
  padding: 30px 26px;
  box-shadow: 0 18px 40px rgba(0,0,0,0.38), inset 0 1px 0 rgba(255,236,210,0.12);
  margin-bottom: 20px;
  backdrop-filter: blur(18px) saturate(1.15);
  -webkit-backdrop-filter: blur(18px) saturate(1.15);
}
.mac-hero:before {
  content: "";
  position: absolute;
  top: 10px; left: 12px; right: 12px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(247,238,219,0.28), transparent);
  pointer-events: none;
}

.mac-kicker {
  font-family: 'Yatra One', cursive;
  font-size: 13px;
  letter-spacing: 2px;
  color: var(--brass);
  text-transform: uppercase;
  margin-bottom: 8px;
}

.mac-card {
  background: linear-gradient(180deg, rgba(48,32,22,0.86) 0%, rgba(30,20,14,0.82) 100%);
  border: 1px solid rgba(208,162,74,0.26);
  border-radius: 24px;
  padding: 20px;
  box-shadow: 0 12px 26px rgba(0,0,0,0.24), inset 0 1px 0 rgba(255,236,210,0.08);
  margin-bottom: 14px;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}
.mac-card:hover { border-color: var(--brass); }

.icon-dot {
  width: 44px; height: 44px;
  border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  background: #251810;
  border: 1px solid var(--line);
  font-size: 18px;
  margin-bottom: 10px;
}

.pill {
  display: inline-block;
  padding: 7px 14px;
  margin: 4px;
  border-radius: 999px;
  background: #251810;
  border: 1px solid var(--line);
  color: var(--bhojpatra);
  font-size: 13px;
  font-weight: 600;
}

.quote-box {
  background: rgba(25,16,10,0.75);
  border: 1px solid var(--border-carved);
  border-radius: 24px;
  padding: 22px;
  text-align: center;
  font-family: 'Rozha One', serif;
  font-size: 18px;
  color: #eed5b5;
  margin: 20px 0;
  line-height: 1.7;
}

.kid-hint {
  background: #201710;
  border-left: 4px solid var(--brass);
  padding: 12px 16px;
  border-radius: 0 8px 8px 0;
  font-size: 14px;
  margin-bottom: 14px;
  color: #eed5b5;
}

.level-bar {
  height: 10px;
  background: #110905;
  border-radius: 99px;
  overflow: hidden;
  border: 1px solid var(--line);
}
.level-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--gerua), var(--brass));
}

.traffic { display: flex; gap: 7px; margin-bottom: 12px; }
.traffic span { width: 10px; height: 10px; border-radius: 50%; display: inline-block; opacity: 0.85; }

.style-chip {
  border: 1px solid var(--border-carved);
  border-radius: 22px;
  padding: 16px;
  background: rgba(30,20,14,0.72);
  min-height: 96px;
  margin-bottom: 8px;
  backdrop-filter: blur(14px);
}
.style-chip b { color: var(--bhojpatra); display: block; margin-bottom: 4px; font-family: 'Rozha One', serif; }
.style-chip span { color: var(--muted); font-size: 13px; line-height: 1.45; display: block; }

div[data-testid="stMetric"] {
  background: rgba(30,20,14,0.72);
  border: 1px solid var(--border-carved);
  border-radius: 22px;
  padding: 10px 12px;
}
.settings-title {
  font-family: 'Rozha One', serif;
  font-size: 34px;
  color: #f7eedb;
  margin: 4px 0 16px;
}
.settings-profile {
  display: flex;
  align-items: center;
  gap: 14px;
  background: rgba(42,28,18,0.88);
  border-radius: 20px;
  padding: 14px 16px;
  margin-bottom: 18px;
  border: 1px solid rgba(208,162,74,0.22);
}
.settings-avatar {
  width: 56px; height: 56px; border-radius: 18px;
  background: linear-gradient(180deg,#d36a34,#9a3d18);
  display: flex; align-items: center; justify-content: center;
  font-size: 24px; color: #fff;
}
.settings-group {
  background: rgba(36,24,16,0.9);
  border: 1px solid rgba(208,162,74,0.18);
  border-radius: 18px;
  padding: 6px 14px 12px;
  margin: 6px 0 16px;
}
.settings-label {
  font-size: 13px;
  color: #c4ad99;
  font-weight: 700;
  padding: 10px 4px 2px;
}
div[data-testid="stSlider"] [data-baseweb="slider"] > div:first-child {
  background: #2a1c14 !important;
  height: 10px !important;
  border-radius: 99px !important;
}
div[data-testid="stSlider"] [data-baseweb="slider"] > div > div {
  background: linear-gradient(90deg, #c45b28, #d0a24a) !important;
  height: 10px !important;
  border-radius: 99px !important;
}
div[data-testid="stSlider"] [role="slider"] {
  background: #f7eedb !important;
  width: 26px !important;
  height: 26px !important;
  border: 0 !important;
  box-shadow: 0 6px 14px rgba(0,0,0,0.35) !important;
}

@keyframes fadeRise {
  0% { opacity: 0; transform: translateY(24px) scale(0.96); }
  70% { opacity: 1; transform: translateY(-3px) scale(1.015); }
  100% { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes heroSheen {
  0%, 100% { box-shadow: 0 18px 40px rgba(0,0,0,0.38), inset 0 1px 0 rgba(255,236,210,0.08); }
  50% { box-shadow: 0 20px 44px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,236,210,0.22), 0 0 18px rgba(208,162,74,0.18); }
}
@keyframes brassPulse {
  0%, 100% { opacity: 0.35; }
  50% { opacity: 0.8; }
}
@keyframes diyaFlicker {
  0%, 100% { transform: scale(1); filter: brightness(1); }
  50% { transform: scale(1.08); filter: brightness(1.16); }
}
@keyframes barShine {
  0% { background-position: 0% 50%; }
  100% { background-position: 200% 50%; }
}

.mac-hero {
  animation: fadeRise 0.85s var(--ios), heroSheen 3.4s ease-in-out infinite !important;
}
.mac-hero:before {
  animation: brassPulse 3s ease-in-out infinite !important;
}
.mac-card, .style-chip, .quote-box {
  animation: fadeRise 0.8s var(--ios) both !important;
  transition: transform 0.45s var(--ios), box-shadow 0.45s var(--ios) !important;
}
.mac-card:hover, .style-chip:hover {
  transform: translateY(-4px) scale(1.015) !important;
}
.mac-card:active, .style-chip:active, .pill:active {
  transform: scale(0.97) !important;
}
.icon-dot { animation: diyaFlicker 2.4s ease-in-out infinite !important; }
.level-fill {
  background-size: 200% 100%;
  animation: barShine 2.4s linear infinite !important;
}

.stButton>button, section[data-testid="stSidebar"] .stButton>button {
  transition: transform 0.42s var(--ios), opacity 0.42s var(--ios) !important;
  -webkit-tap-highlight-color: transparent !important;
}
.stButton>button:hover { transform: scale(1.02) !important; }
.stButton>button:active, section[data-testid="stSidebar"] .stButton>button:active {
  transform: scale(0.96) !important;
  opacity: 0.88 !important;
}

@media (max-width: 768px) {
  .main .block-container { padding: 1rem !important; }
  .mac-hero { padding: 22px 16px !important; }
}
</style>
""")


# ============================================================
# HEAVENLY VEDIC THEME (overlay: dawn-gold on indigo, lotuses)
# ============================================================
_LOTUS = ("<svg viewBox='0 0 100 70' xmlns='http://www.w3.org/2000/svg'>"
  "<g fill='%s' fill-opacity='.85'><path d='M50 8C60 22 60 42 50 58 40 42 40 22 50 8Z'/>"
  "<path d='M50 58C34 52 18 40 16 22 32 26 44 40 50 58Z' fill-opacity='.7'/>"
  "<path d='M50 58C66 52 82 40 84 22 68 26 56 40 50 58Z' fill-opacity='.7'/>"
  "<path d='M50 60C30 60 8 50 2 36 22 36 40 46 50 60Z' fill-opacity='.5'/>"
  "<path d='M50 60C70 60 92 50 98 36 78 36 60 46 50 60Z' fill-opacity='.5'/></g></svg>")
def _lotus_uri(c):
    return "data:image/svg+xml;base64," + base64.b64encode((_LOTUS % c).encode()).decode()

@st.cache_data(show_spinner=False)
def _heaven_theme():
    pink, gold = _lotus_uri("#ffb6c9"), _lotus_uri("#ffd98a")
    lotus = "".join(
        f"<i style=\"left:{l}%;width:{w}px;height:{w*0.7:.0f}px;animation-duration:{d}s;"
        f"animation-delay:-{dl}s;background-image:url({pink if k%2 else gold})\"></i>"
        for k,(l,w,d,dl) in enumerate([(6,64,26,0),(20,42,32,9),(38,78,30,4),(56,50,36,16),
                                       (72,70,28,7),(88,46,34,12),(47,34,40,22)]))
    stars = "".join(
        f"<b style=\"left:{(i*37)%100}%;top:{(i*53)%100}%;animation-delay:{(i%7)*.6}s\"></b>"
        for i in range(36))
    return """
<style>
:root{--bg:#0b0a24;--gold:#f6c86a;--brass:#e3b04b;--dawn:#ffb36b;
--surface:rgba(30,26,72,.55);--surface2:rgba(42,34,92,.62);
--line:rgba(246,200,106,.28);--border-carved:rgba(246,200,106,.34);
--muted:#cfc6ec;--bhojpatra:#fff6e0;--spring:cubic-bezier(.34,1.56,.64,1)}
html,body,[class*="css"]{font-family:'Inter','Eczar',system-ui,sans-serif!important;background:var(--bg)!important}
h1,h2,h3,.mac-kicker{font-family:'Cinzel','Eczar',serif!important;letter-spacing:.02em}
.stApp,[data-testid="stMain"],[data-testid="stAppViewContainer"]>section,.main .block-container{
background:radial-gradient(ellipse 120% 55% at 50% -8%,rgba(255,179,107,.55) 0%,rgba(246,200,106,.18) 30%,transparent 62%),
radial-gradient(circle at 50% 110%,rgba(120,90,220,.28),transparent 55%),
linear-gradient(180deg,#2a2160 0%,#151238 45%,#0b0a24 100%)!important}
[data-testid="stSidebar"]{background:linear-gradient(180deg,rgba(26,22,66,.92),rgba(11,10,36,.96))!important;
border-right:1px solid var(--line)!important;backdrop-filter:blur(18px)}
/* floating lotuses + star-dust (GPU-only, pointer-events off, fast) */
#vr-heaven{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}
#vr-heaven i{position:absolute;bottom:-90px;background-size:contain;background-repeat:no-repeat;
opacity:.55;filter:drop-shadow(0 0 14px rgba(255,200,140,.6));animation:vrRise linear infinite;will-change:transform}
#vr-heaven b{position:absolute;width:2px;height:2px;border-radius:50%;background:#fff3cf;
box-shadow:0 0 6px 1px rgba(255,230,160,.9);animation:vrTwinkle 4s ease-in-out infinite}
@keyframes vrRise{0%{transform:translate3d(0,0,0) rotate(-6deg);opacity:0}10%{opacity:.6}
50%{transform:translate3d(26px,-55vh,0) rotate(6deg)}100%{transform:translate3d(-16px,-115vh,0) rotate(-4deg);opacity:0}}
@keyframes vrTwinkle{0%,100%{opacity:.15}50%{opacity:1}}
.main .block-container,[data-testid="stSidebar"]{position:relative;z-index:1}
/* temple-brass glass cards */
.mac-hero,.mac-card,.settings-group,.settings-profile,.quote-box{
background:linear-gradient(145deg,rgba(60,48,130,.55),rgba(24,20,64,.62))!important;
border:1px solid var(--border-carved)!important;border-radius:22px!important;
backdrop-filter:blur(20px) saturate(140%);
box-shadow:0 0 0 1px rgba(255,236,190,.06) inset,0 10px 34px rgba(0,0,0,.38),0 0 28px rgba(246,200,106,.14)!important;
animation:vrLift .7s var(--spring) both;transition:transform .35s var(--spring),box-shadow .35s}
.mac-card:hover,.mac-hero:hover{transform:translateY(-4px);
box-shadow:0 14px 40px rgba(0,0,0,.45),0 0 40px rgba(246,200,106,.32)!important}
.mac-hero{background-image:url(LOTUS_G),linear-gradient(145deg,rgba(70,54,150,.6),rgba(24,20,64,.66))!important;
background-repeat:no-repeat!important;background-position:right 18px top 14px,0 0!important;background-size:88px,auto!important}
.mac-hero:before{background:radial-gradient(circle,rgba(246,200,106,.32),transparent 65%)!important}
@keyframes vrLift{from{opacity:0;transform:translateY(18px) scale(.985)}to{opacity:1;transform:none}}
.traffic{display:none!important}
/* buttons */
.stButton>button,.stDownloadButton>button,[data-testid="stFormSubmitButton"]>button{
background:linear-gradient(135deg,#f6c86a,#e39a3b)!important;color:#2a1a06!important;font-weight:700;
border:0!important;border-radius:999px!important;box-shadow:0 6px 20px rgba(246,200,106,.35);
transition:transform .25s var(--spring),box-shadow .25s}
.stButton>button:hover{transform:translateY(-2px) scale(1.03);box-shadow:0 10px 28px rgba(246,200,106,.55)}
.stButton>button:active{transform:scale(.97)}
input,textarea,[data-baseweb="select"]>div{background:rgba(20,17,56,.7)!important;
border:1px solid var(--line)!important;border-radius:14px!important;color:var(--bhojpatra)!important}
[data-testid="stSidebar"] *{color:var(--bhojpatra)}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
@media(max-width:768px){#vr-heaven i:nth-child(n+5){display:none}}
</style>
<div id="vr-heaven">""".replace("LOTUS_G", gold) + lotus + stars + "</div>"

md(_heaven_theme())

# ============================================================
# CURRICULUM
# ============================================================
BOARDS = ["CBSE", "ICSE", "State Board"]

SUBJECTS_CATALOG = {
    "Mathematics — गणित शास्त्रम्": "Mathematics",
    "Science — विज्ञान शास्त्रम्": "Science",
    "Hindi — हिन्दी भाषा": "Hindi",
    "English — आङ्ग्ल भाषा": "English",
}

MATH_SYLLABUS = {
    "Grade 5": [
        {"ch": "1. Let Us Recall (पुनरावर्तनम्)",
         "notes": "Simple practice of addition, subtraction, multiplication, and sharing numbers."},
        {"ch": "2. My Numbers (सङ्ख्या परिचयः)",
         "notes": "Place value, ones, tens, hundreds, thousands, and reading big numbers easily."},
        {"ch": "3. Multiples & Factors (गुणक-अवयवाः)",
         "notes": "Finding tables, factors, prime numbers, and simple tricks for LCM and HCF."},
        {"ch": "4. Fractions & Decimals (भिन्न शास्त्रम्)",
         "notes": "Halves, quarters, pizza slice fractions, and understanding decimals with money rupees and paise."},
    ],
    "Grade 6": [
        {"ch": "1. Knowing Our Numbers (सङ्ख्या बोधः)",
         "notes": "Reading lakhs and crores easily, Roman numbers, and rounding numbers off."},
        {"ch": "2. Whole Numbers (पूर्ण सङ्ख्याः)",
         "notes": "Counting from zero upwards and doing easy math steps along a number line."},
        {"ch": "3. Integers (पूर्णाङ्काः)",
         "notes": "Understanding positive (+) and negative (-) minus numbers using steps forward and backward."},
        {"ch": "4. Algebra Introduction (बीजगणितम्)",
         "notes": "Using letters like 'x' and 'y' to solve mystery puzzle numbers."},
    ],
    "Grade 7": [
        {"ch": "1. Integers Operations (पूर्णाङ्क गुणाकारः)",
         "notes": "Clear rules for plus (+) and minus (-) multiplication: minus times minus equals plus!"},
        {"ch": "2. Simple Equations (सरल समीकरणाः)",
         "notes": "Balancing equations just like a vegetable weighing scale to find unknown values."},
        {"ch": "3. Lines and Angles (रेखाः कोणाश्च)",
         "notes": "Straight lines, acute angles, right angles, and parallel railway track lines."},
    ],
    "Grade 8": [
        {"ch": "1. Rational Numbers (परिमेय सङ्ख्याः)",
         "notes": "Fractions that can be written as p/q, with easy step-by-step plus and minus rules."},
        {"ch": "2. Linear Equations (एकचर समीकरणाः)",
         "notes": "Solving word puzzles and algebra equations where letters appear on both sides."},
        {"ch": "3. Squares & Square Roots (वर्ग-वर्गमूलम्)",
         "notes": "Multiplying a number by itself (like 5 × 5 = 25) and finding its root back."},
    ],
    "Grade 9": [
        {"ch": "1. Number Systems (वास्तव सङ्ख्या पद्धतिः)",
         "notes": "Irrational numbers like √2 and √3, decimals that never repeat, and exponent power rules."},
        {"ch": "2. Polynomials (बहुपदानि)",
         "notes": "Algebra expressions, finding zeroes, and standard formula shortcuts like (a+b)²."},
        {"ch": "3. Coordinate Geometry (निर्देशांक ज्यामितिः)",
         "notes": "Locating any point on a 2D graph paper map using (x, y) coordinates."},
    ],
    "Grade 10": [
        {"ch": "1. Real Numbers (वास्तव सङ्ख्याः)",
         "notes": "Euclid's division trick for HCF, prime factor trees, and proving why √5 is irrational."},
        {"ch": "2. Quadratic Equations (द्विघात समीकरणाः)",
         "notes": "Solving ax² + bx + c = 0 equations using simple middle-term splitting and formulas."},
        {"ch": "3. Trigonometry Introduction (त्रिकोणमितिः)",
         "notes": "Right-angled triangle formulas: sin, cos, and tan ratios explained with simple ladder and tree shadow examples."},
    ],
}

SCIENCE_SYLLABUS = {
    "Grade 5": [
        {"ch": "1. Water & Environment (जलम् पर्यावरणञ्च)",
         "notes": "Where rain comes from, the water cycle, and easy methods to save water at home and school."},
        {"ch": "2. Human Organ Systems (शरीर तन्त्राणि)",
         "notes": "How our bones, muscles, and stomach work together like a team to digest food and keep us running."},
        {"ch": "3. Matter & Energy (पदार्थाः ऊर्जा च)",
         "notes": "Solids (hard objects), liquids (water, milk), and gases (air, steam), and how heat changes them."},
    ],
    "Grade 6": [
        {"ch": "1. Components of Food (आहार घटकाः)",
         "notes": "Why our body needs rice (carbs), dal (proteins), milk (calcium), and fruits (vitamins) to stay strong."},
        {"ch": "2. Sorting Materials (पदार्थ वर्गीकरणम्)",
         "notes": "Why iron sinks, wood floats, glass is see-through, and metals shine."},
        {"ch": "3. Light & Shadows (प्रकाशः छाया च)",
         "notes": "How light travels in straight lines and why shadows form when an object blocks the sun."},
    ],
    "Grade 7": [
        {"ch": "1. Nutrition in Plants (पादप पोषणम्)",
         "notes": "How green leaves cook food using sunlight, air (CO₂), and water through photosynthesis."},
        {"ch": "2. Acids, Bases & Salts (अम्ल-क्षार-लवणानि)",
         "notes": "Sour things like lemons (acids), slippery bitter things like soap (bases), and litmus paper tests."},
        {"ch": "3. Motion and Time (गतिः समयश्च)",
         "notes": "How fast vehicles move: Speed = Distance ÷ Time, and reading simple distance-time charts."},
    ],
    "Grade 8": [
        {"ch": "1. Crop Production (सस्य उत्पादनम्)",
         "notes": "How Indian farmers prepare fields, sow seeds, use organic manure, and water crops with drip systems."},
        {"ch": "2. Microorganisms (सूक्ष्मजीवाः)",
         "notes": "Tiny living beings seen only under microscopes: helpful yeast in bread, and bacteria that make milk into curd."},
        {"ch": "3. Force & Pressure (बलम् दबावश्च)",
         "notes": "A push or pull that changes speed, direction, or shape; and why sharp knives cut better than blunt ones."},
    ],
    "Grade 9": [
        {"ch": "1. Matter in Surroundings (पदार्थ स्वरूपम्)",
         "notes": "How tiny particles are always moving; and why a spoonful of sugar dissolves in tea and perfume spreads in a room."},
        {"ch": "2. Atoms and Molecules (परमाणुः अणुश्च)",
         "notes": "The smallest building blocks of everything around us, and how chemical names like H₂O are made."},
        {"ch": "3. Laws of Motion (गति नियमाः)",
         "notes": "Newton's 3 simple laws: why we fall forward when a bus stops, and why rocket engines push down to fly up."},
    ],
    "Grade 10": [
        {"ch": "1. Chemical Reactions (रासायनिक क्रियाः)",
         "notes": "What happens when things react (like iron rusting), and how to balance simple chemical equations."},
        {"ch": "2. Electricity (विद्युत् प्रवाहः)",
         "notes": "Current, voltage (V), resistance (R), and Ohm's law: V = I × R, with simple torch bulb battery circuits."},
        {"ch": "3. Life Processes (जीवन क्रियाः)",
         "notes": "How our heart pumps blood through arteries and veins, how lungs take oxygen, and how kidneys clean our blood."},
    ],
}

HINDI_SYLLABUS = {
    "Grade 5": [
        {"ch": "1. सरल गद्य पाठ (Gadya Bodh)",
         "notes": "सरल कहानियों को पढ़कर उनके मुख्य संदेश और नए शब्दों के अर्थ समझना।"},
        {"ch": "2. कविता और भाव (Kavita Bhava)",
         "notes": "सरल और मधुर कविताओं का गायन, लय समझना और उनके भाव का आनंद लेना।"},
        {"ch": "3. संज्ञा और सर्वनाम (Nouns & Pronouns)",
         "notes": "किसी व्यक्ति, वस्तु या स्थान के नाम को संज्ञा और उसके स्थान पर आने वाले शब्द (वह, मैं, तुम) को सर्वनाम कहते हैं।"},
    ],
    "Grade 6": [
        {"ch": "1. कहानी और उसका सार (Story Analysis)",
         "notes": "कहानियों को ध्यान से पढ़ना और अपने शब्दों में उनका सारांश बताना।"},
        {"ch": "2. विशेषण और क्रिया (Adjectives & Verbs)",
         "notes": "विशेषता बताने वाले शब्द (मीठा, बड़ा) विशेषण हैं और काम बताने वाले शब्द (दौड़ना, पढ़ना) क्रिया हैं।"},
        {"ch": "3. वाक्य शुद्धि एवं पत्र (Sentence & Letter)",
         "notes": "सही वाक्य बनाना, विराम चिह्नों का प्रयोग और स्कूल के लिए सरल पत्र लिखना।"},
    ],
    "Grade 7": [
        {"ch": "1. गद्य साहित्य (Literary Stories)",
         "notes": "अच्छी कहानियाँ पढ़कर पात्रों के अच्छे गुणों और नैतिक मूल्यों को समझना।"},
        {"ch": "2. सरल संधि (Sandhi Rules)",
         "notes": "दो ध्वनियों के मेल से होने वाले बदलाव, जैसे: विद्या + आलय = विद्यालय।"},
    ],
    "Grade 8": [
        {"ch": "1. समास परिचय (Compound Words)",
         "notes": "दो या अधिक शब्दों को मिलाकर छोटा और नया शब्द बनाना (जैसे: राजा का पुत्र = राजपुत्र)।"},
        {"ch": "2. निबंध और संवाद (Essay & Dialogue)",
         "notes": "दिए गए विषय पर अपने विचार सुंदर और स्पष्ट वाक्यों में लिखना।"},
    ],
    "Grade 9": [
        {"ch": "1. काव्य सौंदर्य एवं रस (Poetics)",
         "notes": "कविता में अलंकारों (उपमा, रूपक) की पहचान और भाषा की सुंदरता को समझना।"},
        {"ch": "2. व्याकरण एवं प्रत्यय (Grammar)",
         "notes": "उपसर्ग और प्रत्यय जोड़कर नए शब्द बनाना और वाक्य भेद समझना।"},
    ],
    "Grade 10": [
        {"ch": "1. बोर्ड स्तरीय गद्य समीक्षा (Board Prose)",
         "notes": "बोर्ड परीक्षा के स्तर के गद्यांशों को समझकर पूछे गए प्रश्नों के सटीक उत्तर देना।"},
        {"ch": "2. रचनात्मक लेखन (Creative Writing)",
         "notes": "औपचारिक पत्र, विज्ञापन लेखन और महत्वपूर्ण समसामयिक विषयों पर निबंध लिखना।"},
    ],
}

ENGLISH_SYLLABUS = {
    "Grade 5": [
        {"ch": "1. The True Friend",
         "notes": "A heartwarming story showing why real friendship means honesty, sharing, and helping during tough times."},
        {"ch": "2. Parts of Speech Made Easy",
         "notes": "Fun ways to spot nouns (naming words), verbs (action words), and adjectives (describing words)."},
        {"ch": "3. Writing Neat Sentences",
         "notes": "Using capital letters, full stops, question marks, and keeping words in the right order."},
    ],
    "Grade 6": [
        {"ch": "1. Who Did Patrick's Homework?",
         "notes": "An inspiring tale proving that doing your own daily homework makes you smart and capable."},
        {"ch": "2. Everyday Tenses",
         "notes": "Talking about things happening now (Present), things already done (Past), and things to come (Future)."},
        {"ch": "3. Short Paragraphs & Notes",
         "notes": "Writing clear 5-line descriptions about your school, a pet, or your favorite festival."},
    ],
    "Grade 7": [
        {"ch": "1. Three Questions (Leo Tolstoy)",
         "notes": "A wise fable showing that the most important time is NOW, and the most important person is the one with you."},
        {"ch": "2. Active and Passive Voice",
         "notes": "Saying 'Rohan kicked the ball' (Active) versus 'The ball was kicked by Rohan' (Passive)."},
    ],
    "Grade 8": [
        {"ch": "1. The Best Christmas Present in the World",
         "notes": "A touching historical letter from soldiers in the trenches celebrating friendship during wartime."},
        {"ch": "2. Direct and Reported Speech",
         "notes": "How to report what someone said to another person without using quotes."},
    ],
    "Grade 9": [
        {"ch": "1. The Fun They Had / The Road Not Taken",
         "notes": "Reflections on robotic future schools versus human classrooms, and Robert Frost's poem on choices."},
        {"ch": "2. Clauses and Linking Words",
         "notes": "Joining ideas smoothly with conjunctions like 'although', 'because', and relative words like 'which' and 'who'."},
    ],
    "Grade 10": [
        {"ch": "1. A Letter to God / Nelson Mandela",
         "notes": "Stories of unshakeable faith, human innocence, courage, and triumph over injustice."},
        {"ch": "2. Analytical Paragraph Writing",
         "notes": "Reading a chart or graph and writing a clear, balanced paragraph for CBSE/ICSE board exams."},
    ],
}

SUBJECT_DB_MAP = {
    "Mathematics": MATH_SYLLABUS,
    "Science": SCIENCE_SYLLABUS,
    "Hindi": HINDI_SYLLABUS,
    "English": ENGLISH_SYLLABUS,
}

CBSE_CHAPTERS = {
    "Grade 5": {
        "Mathematics": ["The Fish Tale", "Shapes and Angles", "How Many Squares?", "Parts and Wholes", "Does it Look the Same?", "Be My Multiple, I'll be Your Factor", "Can You See the Pattern?", "Mapping Your Way", "Boxes and Sketches", "Tenths and Hundredths", "Area and Its Boundary", "Smart Charts", "Ways to Multiply and Divide"],
        "Science": ["Super Senses", "A Snake Charmer's Story", "From Tasting to Digesting", "Mangoes Round the Year", "Seeds and Seeds", "Every Drop Counts", "Experiments with Water", "A Treat for Mosquitoes", "Up You Go!", "Walls Tell Stories", "Sunita in Space", "What if it Finishes...?", "A Shelter so High!", "When the Earth Shook!", "Blow Hot, Blow Cold", "Who will do this Work?", "Across the Wall", "No Place for Us?", "A Seed Tells a Farmer's Story", "Whose Forests?", "Like Father, Like Daughter", "On the Move Again"],
        "Hindi": ["Rakh ki Rassi", "Fasal ke Tyohar", "Khilonewala", "Nanha Fanhara", "Jahan Chah Wahan Rah", "Chitthi ka Safar", "Dakbabu", "Ek Ma ki Bebasi", "Ek din ki Bachat", "Chawal ki Rotiyan", "Guru aur Chela", "Swami ki Dadi", "Bagh aya Us Raat", "Bis Bis Kile", "Pani re Pani", "Baaz aur Saanp"],
        "English": ["Ice-cream Man", "Wonderful Waste", "Teamwork", "Flying Together", "My Shadow", "Robinson Crusoe", "Crying", "The Talkative Barber", "Gopal and the Hilsa Fish", "Nobody's Friend", "The Little Bully", "Sing a Song of People", "Malu Bhalu", "Who Will Be Ningthou?"],
    },
    "Grade 6": {
        "Mathematics": ["Knowing Our Numbers", "Whole Numbers", "Playing with Numbers", "Basic Geometrical Ideas", "Understanding Elementary Shapes", "Integers", "Fractions", "Decimals", "Data Handling", "Mensuration", "Algebra", "Ratio and Proportion"],
        "Science": ["Food Sources", "Components of Food", "Fibre to Fabric", "Sorting Materials", "Separation of Substances", "Changes Around Us", "Getting to Know Plants", "Body Movements", "Living Organisms", "Motion and Measurement", "Light and Shadows", "Electricity and Circuits", "Magnets", "Water", "Air", "Garbage In, Garbage Out"],
        "Social Science": ["What, Where, How and When?", "From Hunting-Gathering to Growing Food", "In the Earliest Cities", "What Books and Burials Tell Us", "Kingdoms, Kings and an Early Republic", "New Questions and Ideas", "Ashoka, The Emperor Who Gave Up War", "Vital Villages, Thriving Towns", "Traders, Kings and Pilgrims", "New Empires and Kingdoms", "Buildings, Paintings and Books", "The Earth in the Solar System", "Globe: Latitudes and Longitudes", "Motions of the Earth", "Maps", "Major Domains of the Earth", "Major Landforms of the Earth", "India: Climate, Vegetation and Wildlife", "Understanding Diversity", "Government", "Panchayati Raj", "Rural Administration", "Urban Administration", "Rural Livelihoods", "Urban Livelihoods"],
        "Hindi": ["Vah Chidiya Jo", "Bachpan", "Naadan Dost", "Chaand se Thodi si Gappe", "Saathi Haath Badhana", "Aksharon ka Mahatva", "Paath ke Sath", "Nanak", "Sansar Pustak Hai", "Main Sabse Chhoti Hoon", "Jhansi ki Rani", "Ticket Album"],
        "English": ["Who Did Patrick's Homework?", "How the Dog Found Himself", "Taro's Reward", "An Indian-American Woman in Space", "A Different Kind of School", "Who I Am", "Fair Play", "A Game of Chance", "Desert Animals", "The Banyan Tree"],
    },
    "Grade 7": {
        "Mathematics": ["Integers", "Fractions and Decimals", "Data Handling", "Simple Equations", "Lines and Angles", "The Triangle and its Properties", "Comparing Quantities", "Rational Numbers", "Perimeter and Area", "Algebraic Expressions", "Exponents and Powers", "Symmetry", "Visualising Solid Shapes"],
        "Science": ["Nutrition in Plants", "Nutrition in Animals", "Fibre to Fabric", "Heat", "Acids, Bases and Salts", "Physical and Chemical Changes", "Weather, Climate and Adaptations", "Winds, Storms and Cyclones", "Soil", "Respiration in Organisms", "Transportation in Animals and Plants", "Reproduction in Plants", "Motion and Time", "Electric Current and its Effects", "Light", "Water: A Precious Resource", "Forests: Our Lifeline", "Wastewater Story"],
        "Social Science": ["Tracing Changes Through a Thousand Years", "New Kings and Kingdoms", "The Delhi Sultans", "The Mughal Empire", "Rulers and Buildings", "Towns, Traders and Craftspersons", "Tribes, Nomads and Settled Communities", "Devotional Paths to the Divine", "The Making of Regional Cultures", "Eighteenth-Century Political Formations", "Environment", "Inside Our Earth", "Our Changing Earth", "Air", "Water", "Natural Vegetation and Wildlife", "Human Environment", "Life in the Deserts", "On Equality", "Role of the Government in Health", "How the State Government Works", "Growing up as Boys and Girls", "Women Change the World", "Understanding Media", "Markets Around Us", "A Shirt in the Market", "Struggles for Equality"],
        "Hindi": ["Hum Panchhi Unmukt Gagan ke", "Dadi Maa", "Himalaya ki Betiyan", "Kathputli", "Mithaiwala", "Rakt aur Hamara Sharir", "Papa Kho Gaye", "Sham — Ek Kisan", "Rahim ke Dohe", "Mahabharat"],
        "English": ["Three Questions", "A Gift of Chappals", "Gopal and the Hilsa Fish", "The Ashes That Made Trees Bloom", "Quality", "Expert Detectives", "The Invention of Vita-Wonk", "Fire: Friend and Foe", "Meadow Surprises", "The Story of Cricket"],
    },
    "Grade 8": {
        "Mathematics": ["Rational Numbers", "Linear Equations in One Variable", "Understanding Quadrilaterals", "Data Handling", "Squares and Square Roots", "Cubes and Cube Roots", "Comparing Quantities", "Algebraic Expressions and Identities", "Mensuration", "Exponents and Powers", "Direct and Inverse Proportions", "Factorisation", "Introduction to Graphs"],
        "Science": ["Crop Production and Management", "Microorganisms: Friend and Foe", "Synthetic Fibres and Plastics", "Materials: Metals and Non-Metals", "Coal and Petroleum", "Combustion and Flame", "Conservation of Plants and Animals", "Cell — Structure and Functions", "Reproduction in Animals", "Reaching the Age of Adolescence", "Force and Pressure", "Friction", "Sound", "Chemical Effects of Electric Current", "Some Natural Phenomena", "Light", "Stars and the Solar System", "Pollution of Air and Water"],
        "Social Science": ["How, When and Where", "From Trade to Territory", "Ruling the Countryside", "Tribals, Dikus and the Vision of a Golden Age", "When People Rebel 1857", "Civilising the Native, Educating the Nation", "Women, Caste and Reform", "The Making of the National Movement", "Resources", "Land, Soil, Water, Natural Vegetation and Wildlife", "Agriculture", "Industries", "Human Resources", "The Indian Constitution", "Understanding Secularism", "Why Do We Need a Parliament?", "Understanding Laws", "Judiciary", "Understanding Marginalisation", "Confronting Marginalisation", "Public Facilities", "Law and Social Justice"],
        "Hindi": ["Lakh ki Chudiyan", "Bus ki Yatra", "Deewanon ki Hasti", "Bhagwan ke Dakie", "Kya Nirash Hua Jaye", "Yeh Sabse Kathin Samay Nahi", "Kabir ki Sakhiyan", "Sudama Charit", "Jahaan Pahiya Hai", "Akbari Lota", "Surdas ke Pad", "Pani ki Kahani"],
        "English": ["The Best Christmas Present in the World", "The Tsunami", "Glimpses of the Past", "Bepin Choudhury's Lapse of Memory", "The Summit Within", "This is Jody's Fawn", "A Visit to Cambridge", "A Short Monsoon Diary"],
    },
    "Grade 9": {
        "Mathematics": ["Number Systems", "Polynomials", "Coordinate Geometry", "Linear Equations in Two Variables", "Introduction to Euclid's Geometry", "Lines and Angles", "Triangles", "Quadrilaterals", "Circles", "Heron's Formula", "Surface Areas and Volumes", "Statistics"],
        "Science": ["Matter in Our Surroundings", "Is Matter Around Us Pure?", "Atoms and Molecules", "Structure of the Atom", "The Fundamental Unit of Life", "Tissues", "Motion", "Force and Laws of Motion", "Gravitation", "Work and Energy", "Sound", "Improvement in Food Resources"],
        "Social Science": ["The French Revolution", "Socialism in Europe and the Russian Revolution", "Nazism and the Rise of Hitler", "Forest Society and Colonialism", "Pastoralists in the Modern World", "India — Size and Location", "Physical Features of India", "Drainage", "Climate", "Natural Vegetation and Wildlife", "What is Democracy? Why Democracy?", "Constitutional Design", "Electoral Politics", "Working of Institutions", "Democratic Rights", "The Story of Village Palampur", "People as Resource", "Poverty as a Challenge", "Food Security in India"],
        "Hindi": ["Do Bailon ki Katha", "Lhasa ki Ore", "Upbhoktavad ki Sanskriti", "Saandebazi", "Nana Saheb ki Putri", "Premchand ke Phate Jute", "Mere Bachpan ke Din", "Sakhiyan", "Vaakh", "Savaiye", "Kaidi aur Kokila", "Gram Shree", "Megh Aaye"],
        "English": ["The Fun They Had", "The Sound of Music", "The Little Girl", "A Truly Beautiful Mind", "The Snake and the Mirror", "My Childhood", "Reach for the Top", "Kathmandu", "If I Were You", "The Lost Child", "The Adventures of Toto", "Iswaran the Storyteller", "In the Kingdom of Fools", "The Happy Prince"],
        "Computer": ["Employability Skills", "Digital Documentation", "Electronic Spreadsheet", "Digital Presentation", "Database Management", "Web Applications"],
    },
    "Grade 10": {
        "Mathematics": ["Real Numbers", "Polynomials", "Pair of Linear Equations in Two Variables", "Quadratic Equations", "Arithmetic Progressions", "Triangles", "Coordinate Geometry", "Introduction to Trigonometry", "Some Applications of Trigonometry", "Circles", "Areas Related to Circles", "Surface Areas and Volumes", "Statistics", "Probability"],
        "Science": ["Chemical Reactions and Equations", "Acids, Bases and Salts", "Metals and Non-metals", "Carbon and its Compounds", "Life Processes", "Control and Coordination", "How do Organisms Reproduce?", "Heredity", "Light — Reflection and Refraction", "The Human Eye and the Colourful World", "Electricity", "Magnetic Effects of Electric Current", "Our Environment"],
        "Social Science": ["The Rise of Nationalism in Europe", "Nationalism in India", "The Making of a Global World", "The Age of Industrialisation", "Print Culture and the Modern World", "Resources and Development", "Forest and Wildlife Resources", "Water Resources", "Agriculture", "Minerals and Energy Resources", "Manufacturing Industries", "Lifelines of National Economy", "Power Sharing", "Federalism", "Gender, Religion and Caste", "Political Parties", "Outcomes of Democracy", "Development", "Sectors of the Indian Economy", "Money and Credit", "Globalisation and the Indian Economy", "Consumer Rights"],
        "Hindi": ["Surdas", "Tulsidas", "Dev", "Jayashankar Prasad", "Suryakant Tripathi Nirala", "Nagarjun", "Girija Kumar Mathur", "Manglesh Dabral", "Swayam Prakash", "Ramvriksh Benipuri", "Yashpal", "Manu Bhandari", "Mata ka Anchal", "George Pancham ki Naak", "Sana Sana Hath Jodi"],
        "English": ["A Letter to God", "Nelson Mandela: Long Walk to Freedom", "Two Stories about Flying", "From the Diary of Anne Frank", "Glimpses of India", "Mijbil the Otter", "Madam Rides the Bus", "The Sermon at Benares", "The Proposal", "A Triumph of Surgery", "The Thief's Story", "The Midnight Visitor", "A Question of Trust", "Footprints without Feet", "The Making of a Scientist", "The Necklace", "Bholi"],
        "Computer": ["Advanced Digital Documentation", "Advanced Spreadsheets", "Database Management", "Web Applications and Security"],
    },
}


ICSE_CHAPTERS = {
    "Grade 5": {
        "Mathematics": ["Large Numbers and Place Value", "Operations on Numbers", "Factors and Multiples (LCM, HCF)", "Operations on Fractions", "Introduction to Decimals", "Percentage", "Profit and Loss", "Simple Interest", "Angles", "Triangles", "Circles", "Perimeter, Area and Volume", "Bar Graphs and Pictographs"],
        "Science": ["Reproduction in Plants", "Animals: Living and Survival", "Skeletal System", "Muscular System", "Nervous System", "Health and Hygiene", "Solids, Liquids and Gases", "Work and Energy", "Simple Machines", "Interdependence in Nature", "Pollution", "Natural Disasters"],
        "Social Science": ["Latitudes and Longitudes", "Reading Maps", "Evolution of Mankind", "Stone Age", "Climate Zones", "Democratic Republic of Congo", "Saudi Arabia", "Greenland", "The United Nations", "Indian Constitution and Government"],
        "Hindi": ["Sangya", "Sarvanam", "Visheshan", "Kriya", "Kaal", "Vilom Shabd", "Paryayvachi", "Muhavare", "Ling aur Vachan", "Panchatantra Stories"],
        "English": ["Reading Comprehension", "Nouns and Pronouns", "Verbs and Tenses", "Adjectives and Adverbs", "Letter Writing", "Story Writing"],
    },
    "Grade 6": {
        "Mathematics": ["Integers", "Fractions", "Decimals", "Playing with Numbers", "Introduction to Algebra", "Ratio and Proportion", "Unitary Method", "Basic Geometrical Concepts", "Angles", "Constructions", "Triangles", "Quadrilaterals", "Perimeter and Area", "Presentation of Data"],
        "Science": ["Matter", "Physical Quantities and Measurement", "Force", "Energy", "Light", "Magnetism", "Introduction to Chemistry", "Elements, Compounds and Mixtures", "Separation Techniques", "Air and Atmosphere", "The Leaf", "The Flower", "Cell Structure", "Digestive System", "Respiratory System", "Circulatory System", "Health and Hygiene", "Adaptation"],
        "Social Science": ["River Valley Civilizations", "Vedic Civilization", "Mahajanapadas", "Jainism and Buddhism", "Mauryan Empire", "Local Self-Government", "Representation of Geographical Features", "Landforms", "Minerals", "North America", "South America"],
        "Hindi": ["Ling", "Vachan", "Karak", "Swar Sandhi", "Muhavare", "Kavita", "Prerak Kahaniyan"],
        "English": ["Comprehension", "Tenses", "Active and Passive Voice", "Letter and Notice", "Composition"],
    },
    "Grade 7": {
        "Mathematics": ["Integers", "Rational Numbers", "Exponents and Powers", "Algebraic Expressions", "Linear Equations in One Variable", "Ratio and Proportion", "Percentage", "Profit, Loss and Discount", "Simple Interest", "Lines and Angles", "Triangles", "Congruence", "Symmetry", "Area of Plane Figures", "Volume and Surface Area", "Mean, Median, Mode", "Probability"],
        "Science": ["Measurement", "Motion", "Energy", "Light Energy", "Heat", "Sound", "Electricity and Magnetism", "Matter and its Composition", "Physical and Chemical Changes", "Atomic Structure", "Language of Chemistry", "Metals and Non-metals", "Tissue", "Kingdom Classification", "Photosynthesis", "Respiration in Plants", "Excretory System", "Nervous System"],
        "Social Science": ["Medieval Period", "Delhi Sultanate", "Mughal Empire", "Indian Constitution", "Fundamental Rights and Duties", "Topographical Sheets", "Atmosphere", "Weathering and Soil", "Industries", "Europe", "Africa"],
        "Hindi": ["Upsarg", "Pratyay", "Viram Chinh", "Paryayvachi", "Vilom", "Premchand Kahaniyan", "Deshbhakti Kavita"],
        "English": ["Comprehension", "Grammar Workshop", "Letter Writing", "Essay", "Story Writing"],
    },
    "Grade 8": {
        "Mathematics": ["Rational Numbers", "Squares and Square Roots", "Cubes and Cube Roots", "Exponents", "Algebraic Expressions and Identities", "Factorisation", "Linear Equations and Inequalities", "Compound Interest", "Direct and Inverse Variations", "Time and Work", "Understanding Quadrilaterals", "Constructions", "Circles", "Surface Area and Volume", "Histograms and Pie Charts", "Probability"],
        "Science": ["Matter", "Force and Pressure", "Energy", "Light Energy", "Heat Transfer", "Sound", "Electricity", "Atomic Structure", "Chemical Reactions", "Hydrogen", "Water", "Carbon and its Compounds", "Transport in Plants", "Reproduction", "Ecosystems", "Endocrine System", "Health and Hygiene"],
        "Social Science": ["Decline of Mughals and Rise of the East India Company", "British Policies", "Great Uprising of 1857", "National Movement", "Judiciary", "UN Agencies", "Topographic Maps", "Population Dynamics", "Migration", "Urbanisation", "Asia", "India"],
        "Hindi": ["Muhavare aur Lokoktiyan", "Patra Lekhan", "Apathit Gadyansh", "Nibandh Lekhan", "Kabir ke Dohe", "Rahim ke Dohe"],
        "English": ["Comprehension", "Grammar", "Formal Letter", "Informal Letter", "Composition"],
    },
    "Grade 9": {
        "Mathematics": ["Pure Arithmetic", "Compound Interest", "Expansions", "Factorisation", "Simultaneous Linear Equations", "Indices", "Logarithms", "Triangles", "Mid-point Theorem", "Pythagoras Theorem", "Circles", "Statistics", "Mensuration", "Trigonometry", "Coordinate Geometry"],
        "Science": ["Measurements and Experimentation", "Motion in One Dimension", "Laws of Motion", "Fluids", "Heat and Energy", "Light", "Sound", "Electricity and Magnetism", "Language of Chemistry", "Chemical Changes and Reactions", "Water", "Atomic Structure and Chemical Bonding", "The Periodic Table", "Study of Hydrogen", "Study of Gas Laws", "Atmospheric Pollution", "Cell: The Unit of Life", "Tissues", "Flowering Plants", "Five Kingdom Classification", "Nutrition", "Health and Hygiene"],
        "Social Science": ["Harappan Civilization", "Vedic Period", "The Mauryas", "Delhi Sultanate", "The Mughal Empire", "Renaissance", "Reformation", "Our Constitution", "Elections", "Local Self-Government", "Earth as a Planet", "Latitudes and Longitudes", "Structure of the Earth", "Landforms of the Earth", "Rocks", "Hydrosphere", "Atmosphere", "Pollution"],
        "Hindi": ["Vilom", "Paryayvachi", "Muhavare", "Patra Lekhan", "Nibandh", "Sahitya Sagar", "Naya Rasta / Ekanki Sanchay"],
        "English": ["Composition", "Letter Writing", "Notice and Email", "Unseen Passage", "Grammar", "Treasure Trove"],
    },
    "Grade 10": {
        "Mathematics": ["GST", "Banking", "Shares and Dividends", "Linear Inequations", "Quadratic Equations", "Factor Theorem", "Matrices", "Arithmetic and Geometric Progression", "Reflection", "Section Formula", "Equation of a Straight Line", "Similarity", "Circles", "Cylinder, Cone and Sphere", "Trigonometric Identities", "Heights and Distances", "Statistics", "Probability"],
        "Science": ["Force", "Work, Power and Energy", "Machines", "Refraction through Lenses", "Spectrum", "Sound", "Current Electricity", "Household Circuits", "Electromagnetism", "Calorimetry", "Radioactivity", "Periodic Properties", "Chemical Bonding", "Acids, Bases and Salts", "Mole Concept and Stoichiometry", "Electrolysis", "Metallurgy", "Organic Chemistry", "Cell Cycle and Cell Division", "Genetics", "Photosynthesis", "Circulatory System", "Excretory System", "Nervous System", "Endocrine System", "Reproductive System", "Pollution"],
        "Social Science": ["The Union Legislature", "The Union Executive", "The Judiciary", "The Revolt of 1857", "The Indian National Movement", "Mass Phase of the National Movement", "The First World War", "The Second World War", "United Nations", "Non-Aligned Movement", "Interpretation of Topographical Maps", "Map of India", "Climate of India", "Soils of India", "Natural Vegetation", "Water Resources", "Minerals of India", "Agriculture in India", "Manufacturing Industries", "Transport", "Waste Management"],
        "Hindi": ["Nibandh Lekhan", "Patra Lekhan", "Apathit Gadyansh", "Vyakaran", "Sahitya Sagar", "Naya Rasta / Ekanki Sanchay"],
        "English": ["Composition", "Letter Writing", "Notice and Email", "Unseen Passage", "Grammar", "Treasure Trove / Merchant of Venice"],
    },
}


def subject_catalog():
    cat = {
        "Mathematics — गणित शास्त्रम्": "Mathematics",
        "Science — विज्ञान शास्त्रम्": "Science",
        "Hindi — हिन्दी भाषा": "Hindi",
        "English — आङ्ग्ल भाषा": "English",
    }
    if st.session_state.get("board") in ("CBSE", "ICSE"):
        cat["Social Science — सामाजिक विज्ञान"] = "Social Science"
        if st.session_state.get("board") == "CBSE":
            cat["Computer / IT"] = "Computer"
    return cat


def chapters_for(subject, grade=None):
    grade = grade or st.session_state.get("grade", "Grade 5")
    board = st.session_state.get("board", "CBSE")
    table = CBSE_CHAPTERS if board == "CBSE" else ICSE_CHAPTERS if board == "ICSE" else None
    if table:
        titles = table.get(grade, {}).get(subject, [])
        return [{"ch": f"{i}. {t}", "notes": f"{board} {grade} · {subject}. {t}. Ask Guru AI if you want this chapter explained."} for i, t in enumerate(titles, 1)]
    return SUBJECT_DB_MAP.get(subject, {}).get(grade, [])

GURU_STYLES = {
    "Super Simple": {
        "emoji": "🌱",
        "blurb": "Tiny words. One example. Like explaining to a younger sibling.",
        "instruction": (
            "Explain as if the student is 10 years old. Use very short sentences, no hard words, "
            "and one everyday example from home or school. End with one line: Remember this. "
            "Keep under 100 words."
        ),
    },
    "Friendly Tutor": {
        "emoji": "😊",
        "blurb": "Kind teacher sitting next to you. Cheerful and clear.",
        "instruction": (
            "Explain like a friendly school tutor. Warm tone, short sentences, "
            "one Indian daily-life example (cricket, tiffin, bus, market). Keep under 120 words."
        ),
    },
    "Step-by-Step Detective": {
        "emoji": "🕵️",
        "blurb": "Clue by clue. No rushing. Case closed at the end.",
        "instruction": (
            "Act as a calm detective. Numbered clues only: "
            "Clue 1 what we know, Clue 2 what we need, Clue 3 the method, "
            "Clue 4 the answer, Case closed one-line recap. Do not skip steps."
        ),
    },
    "Exam Marks Booster": {
        "emoji": "🎯",
        "blurb": "Definition, method, common trap, and a board-style answer.",
        "instruction": (
            "Teach for marks. Give: 1) 1-line definition, 2) exam method, "
            "3) one common mistake, 4) a short answer the student can write in the paper. Be crisp."
        ),
    },
    "Shortcut & Trick": {
        "emoji": "⚡",
        "blurb": "The fastest school-safe trick, then why it works.",
        "instruction": (
            "Give one honest shortcut a school student can use, then 3 tiny steps, "
            "then why the trick works. No silly memory lies. Keep it clean and useful."
        ),
    },
    "Story Memory": {
        "emoji": "📖",
        "blurb": "A mini story so the idea sticks in your head.",
        "instruction": (
            "Teach with a short story of 1 or 2 school-age characters. "
            "The story must carry the concept. End with: The idea to remember is..."
        ),
    },
    "Mistake Doctor": {
        "emoji": "🩺",
        "blurb": "Finds the usual mix-up and shows the correct way.",
        "instruction": (
            "Start with the usual student mistake for this topic, explain why it happens, "
            "then show the correct way with one small example. Kind tone, never mocking."
        ),
    },
    "Rapid Revision": {
        "emoji": "⏱️",
        "blurb": "Last-night revision: 5 bullets and 1 recap line.",
        "instruction": (
            "Write a last-minute revision card. Exactly 5 short bullets plus one recap line. "
            "No stories. Only what a student should remember."
        ),
    },
    "Practice Coach": {
        "emoji": "🏋️",
        "blurb": "Short recap, then 2 practice questions with answers.",
        "instruction": (
            "First explain the idea in 4 short lines. Then give 2 similar practice questions. "
            "After each question, give the answer and one-line reason. Keep it school-safe and clear."
        ),
    },
    "Visual Thinker": {
        "emoji": "🖼️",
        "blurb": "Paint the idea with pictures in words.",
        "instruction": "Explain by describing a simple picture the student can imagine. Then 3 short labels. Under 120 words.",
    },
    "Why-First Curious": {
        "emoji": "🤔",
        "blurb": "Start with why it matters, then how it works.",
        "instruction": "Start with why this idea matters in real life, then how it works, then one tiny example.",
    },
    "Slow & Patient": {
        "emoji": "🐢",
        "blurb": "One small step at a time. No rush.",
        "instruction": "Go very slowly. One sentence per step. Repeat the key line twice in simpler words.",
    },
    "Flashcard Mode": {
        "emoji": "🃏",
        "blurb": "Front: question. Back: short answer.",
        "instruction": "Make 3 flashcards. Each has Q: and A: in one line. School-safe and short.",
    },
    "Classroom Teacher": {
        "emoji": "🏫",
        "blurb": "Like a calm class period on the blackboard.",
        "instruction": "Speak as a classroom teacher. Heading, 3 board points, one example, one homework line.",
    },
    "Sports Coach": {
        "emoji": "🏏",
        "blurb": "Explain like cricket or running practice.",
        "instruction": "Use a sports practice metaphor. Drill 1, Drill 2, Match tip. Keep it kind and clear.",
    },
    "Recipe Cook": {
        "emoji": "🍳",
        "blurb": "Ingredients, steps, done.",
        "instruction": "Teach as a recipe: Ingredients (what we need), Steps (what we do), Taste test (final answer).",
    },
    "Mind Map": {
        "emoji": "🗺️",
        "blurb": "Center idea with 4 branches.",
        "instruction": "Write a mind map: center idea plus 4 short branches. One example at the end.",
    },
    "Compare Two": {
        "emoji": "⚖️",
        "blurb": "This vs that, then the difference.",
        "instruction": "Compare two close ideas. Same, different, when to use which. Very short.",
    },
    "Memory Poem": {
        "emoji": "🪶",
        "blurb": "A tiny rhyme to remember it.",
        "instruction": "Give a 4-line clean school rhyme that teaches the idea, then one plain-English meaning line.",
    },
    "Topper Notes": {
        "emoji": "🥇",
        "blurb": "Neat high-score notes only.",
        "instruction": "Write topper-style notes: definition, formula or rule, 1 example, 1 caution. No extra talk.",
    },
    "Question Storm": {
        "emoji": "❓",
        "blurb": "Learn by answering 3 tiny questions.",
        "instruction": "Ask 3 tiny questions and answer them yourself immediately. Then one recap line.",
    },
}


# ============================================================
# DATABASE
# ============================================================
_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vidhyaradhana_simple.json")
_DB_LOCK = threading.Lock()


def _supabase_cfg():
    url = (_secret("SUPABASE_URL") or "").strip().rstrip("/")
    key = (_secret("SUPABASE_KEY") or _secret("SUPABASE_SERVICE_ROLE_KEY") or "").strip()
    return url, key


def _remote_load():
    url, key = _supabase_cfg()
    if not url or not key:
        return None
    req = urllib.request.Request(
        f"{url}/rest/v1/vidhyaradhana_state?id=eq.1&select=payload",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            rows = json.loads(resp.read().decode("utf-8"))
        if rows and isinstance(rows[0].get("payload"), dict):
            return rows[0]["payload"]
    except Exception:
        return None
    return None


def _remote_save(payload_text):
    url, key = _supabase_cfg()
    if not url or not key:
        return False
    body = json.dumps({"id": 1, "payload": json.loads(payload_text)}).encode("utf-8")
    req = urllib.request.Request(
        f"{url}/rest/v1/vidhyaradhana_state",
        data=body,
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=12):
            return True
    except Exception:
        return False


@st.cache_resource
def get_global_database():
    data = {
        "registered_accounts": {},
        "student_photos": {},
        "quiz_results": [],
        "student_xp": {},
        "student_badges": {},
        "student_streaks": {},
        "student_last_active": {},
        "daily_quests": {},
        "student_nest_notes": {},
        "dhyana_counts": {},
    }
    remote = _remote_load()
    if isinstance(remote, dict) and remote:
        data.update(remote)
        return data
    if os.path.exists(_DATA_PATH):
        try:
            with open(_DATA_PATH, "r", encoding="utf-8") as fh:
                saved = json.load(fh)
            if isinstance(saved, dict):
                data.update(saved)
        except Exception:
            pass
    return data


db = get_global_database()


def persist_db():
    try:
        payload = json.dumps(db, ensure_ascii=False, default=str)
        with _DB_LOCK:
            tmp = _DATA_PATH + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                fh.write(payload)
            os.replace(tmp, _DATA_PATH)
        _remote_save(payload)
    except Exception:
        pass


def get_student_notes(sid):
    return db.setdefault("student_nest_notes", {}).setdefault(sid, [])


def add_student_note(sid, subject, title, body):
    if not sid or not body.strip():
        return False
    entry = {
        "id": f"VN-{int(time.time() * 1000)}",
        "subject": subject,
        "title": title.strip() or "Untitled Sutra",
        "body": body.strip(),
        "time": datetime.now().strftime("%d %b %Y, %I:%M %p"),
    }
    db.setdefault("student_nest_notes", {}).setdefault(sid, []).append(entry)
    persist_db()
    return True


# ============================================================
# GAMIFICATION
# ============================================================
BADGE_CATALOG = {
    "first_quiz": {"name": "Aarambha (आरम्भ)", "emoji": "🪔",
                   "desc": "Started your learning journey with your first Quiz!"},
    "streak_7": {"name": "Sadhaka (साधक)", "emoji": "🔥", "desc": "Kept a steady 7-day daily study habit!"},
    "math_wizard": {"name": "Ganita Acharya (गणित आचार्य)", "emoji": "📐", "desc": "Scored 100% on a Mathematics Quiz!"},
    "science_lab": {"name": "Vigyana Rishi (विज्ञान ऋषि)", "emoji": "🔬",
                    "desc": "Mastered a Science Quiz with flying colors!"},
    "dhyana_master": {"name": "Dhyana Yogi (ध्यानी)", "emoji": "🧘",
                      "desc": "Finished 15 calm 25-minute focus sessions!"},
    "gold_scroll": {"name": "Brahma Patra (ब्रह्म पत्र)", "emoji": "📜", "desc": "Earned over 5,000 Tejas Stars!"},
}


def get_student_xp(sid=None):
    sid = sid or st.session_state.get("student_id", "")
    return db.get("student_xp", {}).get(sid, 0)


def get_level_from_xp(xp):
    return max(1, int(math.sqrt(max(0, xp) / 45)) + 1)


def xp_for_next_level(level):
    return (level ** 2) * 45


def award_xp(amount, reason="", save=True):
    sid = st.session_state.get("student_id", "")
    if not sid:
        return
    db.setdefault("student_xp", {})
    db["student_xp"][sid] = db["student_xp"].get(sid, 0) + amount
    if db["student_xp"][sid] >= 5000:
        grant_badge("gold_scroll", save=False)
    if save:
        persist_db()
    return amount


def grant_badge(badge_id, save=True):
    sid = st.session_state.get("student_id", "")
    if not sid or badge_id not in BADGE_CATALOG:
        return False
    badges = db.setdefault("student_badges", {}).setdefault(sid, [])
    if badge_id not in badges:
        badges.append(badge_id)
        if save:
            persist_db()
        return True
    return False


def update_streak():
    sid = st.session_state.get("student_id", "")
    if not sid:
        return
    today = datetime.now().strftime("%Y-%m-%d")
    last = db.setdefault("student_last_active", {}).get(sid)
    cur = db.setdefault("student_streaks", {}).get(sid, 0)
    if last != today:
        if last:
            try:
                gap = (datetime.strptime(today, "%Y-%m-%d") - datetime.strptime(last, "%Y-%m-%d")).days
            except Exception:
                gap = 99
            cur = cur + 1 if gap == 1 else 1
        else:
            cur = 1
        db["student_last_active"][sid] = today
        db["student_streaks"][sid] = cur
        if cur >= 7:
            grant_badge("streak_7", save=False)
        persist_db()
    return cur


def get_streak(sid=None):
    sid = sid or st.session_state.get("student_id", "")
    return db.get("student_streaks", {}).get(sid, 0)


# ============================================================
# AI
# ============================================================
def call_gemini(messages, temperature=0.3, max_tokens=450, timeout=22):
    if not GEMINI_API_KEY:
        return None, "Gemini key missing"
    system_bits = []
    contents = []
    for msg in messages or []:
        role = msg.get("role")
        text = msg.get("content") or ""
        if role == "system":
            system_bits.append(text)
            continue
        contents.append({
            "role": "model" if role == "assistant" else "user",
            "parts": [{"text": text}],
        })
    if not contents:
        contents = [{"role": "user", "parts": [{"text": "Hello"}]}]
    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }
    if system_bits:
        payload["systemInstruction"] = {"parts": [{"text": "\n".join(system_bits)}]}
    body = json.dumps(payload).encode("utf-8")
    models = ["gemini-3.5-flash", "gemini-flash-latest", "gemini-3.8-flash"]
    last_err = None
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            parts = (((data.get("candidates") or [{}])[0].get("content") or {}).get("parts") or [])
            text = "".join(p.get("text", "") for p in parts if not p.get("thought")).strip()
            if text:
                return text, None
            last_err = "Empty Gemini reply"
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8", errors="ignore")
            last_err = f"Gemini HTTP {e.code}: {err[:140]}"
            if e.code in (401, 403):
                return None, "Gemini key was rejected."
        except Exception as e:
            last_err = str(e)
    return None, last_err or "Gemini is busy."


def call_mistral(messages, temperature=0.3, max_tokens=450, timeout=22):
    return call_gemini(messages, temperature, max_tokens, timeout)


# ============================================================
# QUIZ
# ============================================================
def _fallback_pariksha(subject, difficulty, count, chapter=""):
    title = (chapter or subject or "this chapter").strip()
    qlist = []
    ideas = [
        f"What is the main idea of {title}?",
        f"Which example fits {title}?",
        f"A student is studying {title}. What should they do first?",
        f"Which word belongs with {title}?",
        f"In {title}, what are we asked to look at carefully?",
        f"Which sentence is true for {title}?",
        f"What would a Grade student draw for {title}?",
        f"Which step comes first in {title}?",
        f"What should you count or notice in {title}?",
        f"Which answer stays inside the chapter {title}?",
    ]
    good = [
        f"The idea taught in {title}",
        "An example from this chapter",
        "Read the chapter example, then try one yourself",
        title,
        "The shapes, numbers, or story in this chapter",
        f"{title} is about the topic in its name",
        "A simple picture from the chapter",
        "Read the question, then mark what you see",
        "The pattern or count asked in the chapter",
        "Only facts from this chapter",
    ]
    bad_pool = [
        "A cricket score only",
        "A random song",
        "A bus ticket number",
        "Yesterday's weather only",
        "The school bell time",
        "A shop receipt",
        "A phone wallpaper",
        "A lunch menu",
    ]
    for i in range(count):
        ans = good[i % len(good)]
        distractors = [b for b in bad_pool if b != ans]
        opts = [ans] + random.sample(distractors, 3)
        random.shuffle(opts)
        qlist.append({"question": ideas[i % len(ideas)], "options": opts, "answer": ans})
    return qlist


def generate_pariksha(subject, difficulty="Medium", count=10, chapter=""):
    grade = st.session_state.get("grade", "Grade 5")
    board = st.session_state.get("board", "CBSE")
    chapter = (chapter or "").strip() or subject
    prompt = (
        f"Create a school quiz for Indian students.\n"
        f"Board: {board}\nGrade: {grade}\nSubject: {subject}\nChapter: {chapter}\n"
        f"Difficulty: {difficulty}\n"
        f"Give EXACTLY 10 multiple-choice questions and EXACTLY 1 short written question.\n"
        f"Every question must teach or test ONLY this chapter: {chapter}.\n"
        f"Use the chapter name in the questions. Do not ask random multiplication unless the chapter is about multiplication.\n"
        f"Grade {grade} words only.\n"
        f"Return ONLY JSON, no markdown:\n"
        f'{{"mcq":[{{"question":"...","options":["A","B","C","D"],"answer":"A"}}],'
        f'"subjective":{{"question":"...","hint":"write 3 to 5 lines"}}}}'
    )
    raw, err = call_mistral(
        [
            {"role": "system", "content": "Return only valid JSON for a school quiz. No markdown fences."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=2200,
        timeout=40,
    )
    parsed = []
    subjective = None
    if raw:
        try:
            cleaned = raw.replace("```json", "").replace("```", "")
            if "{" in cleaned and '"mcq"' in cleaned:
                blob = cleaned[cleaned.find("{"): cleaned.rfind("}") + 1]
                data = json.loads(blob)
                items = data.get("mcq") or []
                sub = data.get("subjective") or {}
                if sub.get("question"):
                    subjective = {"question": str(sub.get("question")).strip(), "hint": str(sub.get("hint") or "Write 3 to 5 lines.")}
            else:
                blob = cleaned[cleaned.find("["): cleaned.rfind("]") + 1]
                items = json.loads(blob)
            for item in items:
                q = str(item.get("question") or "").strip()
                opts = [str(o).strip() for o in (item.get("options") or []) if str(o).strip()]
                ans = str(item.get("answer") or "").strip()
                if q and len(opts) >= 2:
                    if ans not in opts:
                        ans = opts[0]
                    random.shuffle(opts)
                    parsed.append({"question": q, "options": opts[:4], "answer": ans})
        except Exception:
            parsed = []
    if not subjective:
        subjective = {
            "question": f"In 4 or 5 lines, explain the main idea of {chapter}.",
            "hint": "Write in your own words.",
        }
    st.session_state.quiz_subjective = subjective
    st.session_state.last_quiz_err = None if parsed else (err or "Could not read quiz JSON")
    if len(parsed) >= 4:
        st.session_state.last_quiz_source = "gemini"
        st.session_state.last_quiz_err = None
        return parsed[:10]
    extra = _fallback_pariksha(subject, difficulty, 10, chapter)
    seen = {p["question"] for p in parsed}
    for item in extra:
        if item["question"] not in seen:
            parsed.append(item)
        if len(parsed) >= 10:
            break
    st.session_state.last_quiz_source = "mixed"
    return parsed[:10]


# ============================================================
# SESSION
# ============================================================
if "_boot" not in st.session_state:
    st.session_state.update({
        "current_page": "landing", "user": "", "email": "", "phone": "",
        "student_id": "", "plan": "Free", "grade": "Grade 5",
        "board": "CBSE", "active_quiz": [], "quiz_run_id": 0,
        "guru_style": "Friendly Tutor",
        "pinned_styles": ["Super Simple", "Friendly Tutor", "Step-by-Step Detective", "Exam Marks Booster", "Practice Coach"],
        "voice_on": False, "voice_volume": 0.9, "voice_speed": 1.0, "voice_stability": 0.62,
        "voice_name": "Sarah (English)", "voice_id": ELEVENLABS_VOICE_ID,
        "answer_lang": "English (India)",
        "_boot": True,
    })

for _k, _v in {
    "pinned_styles": ["Super Simple", "Friendly Tutor", "Step-by-Step Detective", "Exam Marks Booster", "Practice Coach"],
    "voice_on": False, "voice_volume": 0.9, "voice_speed": 1.0, "voice_stability": 0.62,
    "guru_style": "Friendly Tutor",
    "voice_name": "Sarah (English)", "voice_id": ELEVENLABS_VOICE_ID,
    "answer_lang": "English (India)",
}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v
if st.session_state.get("voice_name") not in VOICE_CATALOG:
    st.session_state.voice_name = "Sarah (English)"
    st.session_state.voice_id = ELEVENLABS_VOICE_ID
    st.session_state.last_guru_audio = None


def account_store():
    db.setdefault("registered_accounts", {})
    return db["registered_accounts"]


def save_account(sid, data):
    accs = account_store()
    current = accs.get(sid, {})
    current.update(data)
    accs[sid] = current
    persist_db()
    return current


def load_account_into_session(sid, acc):
    st.session_state.user = acc.get("name", "")
    st.session_state.email = acc.get("email", "")
    st.session_state.phone = acc.get("phone", "")
    st.session_state.grade = acc.get("grade", "Grade 5")
    st.session_state.board = acc.get("board", "CBSE")
    st.session_state.student_id = sid
    st.session_state.plan = acc.get("plan") or "Free"


def render_id_card():
    sid = st.session_state.get("student_id", "")
    photo = db.get("student_photos", {}).get(sid, "")
    photo_html = (
        f'<img src="{photo}" alt="photo" style="width:88px;height:110px;object-fit:cover;border-radius:8px;border:1px solid #c9933b;">'
        if photo else
        '<div style="width:88px;height:110px;border-radius:8px;border:1px solid #573826;display:flex;align-items:center;justify-content:center;background:#281b13;color:#c9933b;font-family:Rozha One,serif;">चित्रम्</div>'
    )
    stars = get_student_xp()
    md(f"""
    <div class="mac-card" style="display:flex;gap:18px;align-items:center;">
      <div>{photo_html}</div>
      <div>
        <div class="mac-kicker">ATHMANVESHI • विद्यार्थिपत्रम्</div>
        <div style="font-size:24px;color:#f7eedb;font-family:'Rozha One',serif;">{html.escape(str(st.session_state.get("user") or "Student"))}</div>
        <div style="font-size:13px;color:#c4ad99;margin-top:3px;">ID <b>{html.escape(str(sid))}</b> · {st.session_state.get('grade')} · {st.session_state.get('board')}</div>
        <div style="font-size:13.5px;color:#c9933b;margin-top:6px;">⭐ {stars} Tejas Stars · {st.session_state.get('plan')} Tier</div>
      </div>
    </div>
    """)


# ============================================================
# PAGES
# ============================================================

# 1. LANDING
if st.session_state.current_page == "landing":
    top_col1, top_col2 = st.columns([3.5, 1.2])
    with top_col2:
        if st.button("प्रवेश द्वारम् • Login ➜", type="primary", use_container_width=True):
            st.session_state.current_page = "login"
            st.rerun()

    md("""
    <div class="mac-hero" style="text-align:center;">
      <div class="mac-kicker">॥ आत्मन्वेषी प्रस्तुतम् ॥</div>
      <h1 style="font-size: clamp(34px, 5.5vw, 62px); margin: 4px 0 10px;">विद्याराधना • VIDHYARADHANA</h1>
      <p style="font-size:16.5px;color:#d8beaa;max-width:760px;margin:0 auto 18px;line-height:1.7;">
        A calm gurukula for CBSE, ICSE and State Board. Notes, pariksha, dhyana timer, and Guru AI that can speak as a mitra, a detective, or an acharya.
      </p>
      <div>
        <span class="pill">🏛️ CBSE / ICSE / State</span>
        <span class="pill">🪔 ९ व्याख्या शैल्यः</span>
        <span class="pill">🧘 25-min Dhyana</span>
      </div>
    </div>
    """)

    md("""
    <div class="quote-box">
      विद्या ददाति विनयं विनयाद् याति पात्रताम्।<br>
      पात्रत्वाद् धनमाप्नोति धनाद् धर्मं ततः सुखम्॥
      <div style="font-size:13.5px;color:#e6d3bb;margin-top:8px;">
        Learning gives humility; humility brings worthiness; worthiness brings success and lasting peace.
      </div>
    </div>
    """)

    st.markdown('<h3 style="text-align:center;margin-top:28px;">What you can study</h3>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        md("""
        <div class="mac-card">
          <div class="icon-dot">📐</div>
          <div style="font-size:17px;font-weight:700;color:#f7eedb;margin-bottom:4px;">Mathematics</div>
          <div style="font-size:14px;line-height:1.6;">Addition to algebra, explained like a puzzle you can actually finish.</div>
        </div>
        """)
        md("""
        <div class="mac-card">
          <div class="icon-dot">🕉️</div>
          <div style="font-size:17px;font-weight:700;color:#f7eedb;margin-bottom:4px;">Hindi</div>
          <div style="font-size:14px;line-height:1.6;">Stories, poems, Sangya, Sandhi, and Samas with easy summaries.</div>
        </div>
        """)
    with c2:
        md("""
        <div class="mac-card">
          <div class="icon-dot">🔬</div>
          <div style="font-size:17px;font-weight:700;color:#f7eedb;margin-bottom:4px;">Science</div>
          <div style="font-size:14px;line-height:1.6;">Water, plants, circuits, magnets — why things work, not just definitions.</div>
        </div>
        """)
        md("""
        <div class="mac-card">
          <div class="icon-dot">✍️</div>
          <div style="font-size:17px;font-weight:700;color:#f7eedb;margin-bottom:4px;">English</div>
          <div style="font-size:14px;line-height:1.6;">Tenses, sentences, reading, and writing that feels clear instead of scary.</div>
        </div>
        """)

    st.write("")
    if st.button("गुरुकुलम् प्रविशतु • Enter the Gurukula ➜", type="primary", use_container_width=True):
        st.session_state.current_page = "login"
        st.rerun()

# 2. LOGIN
elif st.session_state.current_page == "login":
    md("""
    <div class="mac-hero" style="text-align:center;">
      <div class="mac-kicker">ATHMANVESHI • प्रवेश द्वारम्</div>
      <h2 style="margin:0 0 4px;">स्वागतम् • Welcome back</h2>
      <p style="margin:0;">Who is entering the gurukula today?</p>
    </div>
    """)

    role = st.radio("Who are you?", ["Student", "Parent"], horizontal=True)

    if role == "Student":
        uid = st.text_input("Your Student ID or Email", key="login_shishya_id",
                            placeholder="e.g. rahul-g5 or your email")
        pwd = st.text_input("Password", type="password", key="login_shishya_pwd")
        if st.button("Log In as Student ➜", type="primary", use_container_width=True):
            uid_clean = (uid or "").strip()
            pwd_clean = pwd or ""
            accs = account_store()
            sid = uid_clean if uid_clean in accs else next((k for k, a in accs.items() if a.get("email") == uid_clean), None)
            acc = accs.get(sid) if sid else None
            if acc and acc.get("password") == pwd_clean:
                load_account_into_session(sid, acc)
                st.session_state.current_page = "dashboard"
                st.rerun()
            else:
                st.error("Could not find this ID or password. Please check or register a new student below.")

        if st.button("Create a New Student Account (Free)", use_container_width=True):
            st.session_state.current_page = "register"
            st.rerun()

    else:
        p_uid = st.text_input("Enter your child's Student ID to check their progress", placeholder="e.g. rahul-g5")
        if st.button("View Child's Report Card", type="primary", use_container_width=True):
            accs = account_store()
            if p_uid in accs:
                st.session_state.parent_monitor_sid = p_uid
                st.session_state.current_page = "parent_portal"
                st.rerun()
            else:
                st.warning("No student found with that ID. Please check with your child.")

    if st.button("⬅ Back to Home"):
        st.session_state.current_page = "landing"
        st.rerun()

# 3. REGISTER
elif st.session_state.current_page == "register":
    md("""
    <div class="mac-hero">
      <div class="mac-kicker">New student</div>
      <h2 style="margin:0 0 4px;">Create your account</h2>
      <p style="margin:0;">Fill this once to get your Student ID card.</p>
    </div>
    """)
    r_name = st.text_input("Your Full Name", placeholder="e.g. Rahul Sharma")
    r_email = st.text_input("Parent's or Student's Email", placeholder="e.g. parent@gmail.com")
    r_phone = st.text_input("Phone Number")
    r_pwd = st.text_input("Create a Simple Password (at least 5 characters)", type="password")

    col_b, col_g = st.columns(2)
    with col_b:
        r_board = st.selectbox("Your School Board", BOARDS)
    with col_g:
        r_grade = st.selectbox("Your Class", ["Grade 5", "Grade 6", "Grade 7", "Grade 8", "Grade 9", "Grade 10"])

    if st.button("Create Account & Start Learning ➜", type="primary", use_container_width=True):
        if not r_name or "@" not in r_email or len(r_pwd) < 5:
            st.error("Please fill in your name, a valid email, and a password of at least 5 letters.")
        else:
            accs = account_store()
            existing = next((k for k, a in accs.items() if a.get("email") == r_email.strip()), None)
            if existing:
                st.error("That email already has an account. Please log in instead.")
            else:
                first = "".join(ch for ch in r_name.lower().split()[0] if ch.isalnum()) or "student"
                base = f"{first}-g{r_grade.replace('Grade ', '')}"
                sid = base
                n = 2
                while sid in accs:
                    sid = f"{base}-{n}"
                    n += 1
                save_account(sid, {
                    "name": r_name.strip(), "email": r_email.strip(), "phone": r_phone.strip(),
                    "password": r_pwd, "grade": r_grade, "board": r_board, "plan": "Free"
                })
                load_account_into_session(sid, account_store()[sid])
                st.session_state.current_page = "dashboard"
                st.rerun()

    if st.button("⬅ Back to Login"):
        st.session_state.current_page = "login"
        st.rerun()

# 4. PARENT
elif st.session_state.current_page == "parent_portal":
    monitored_sid = st.session_state.get("parent_monitor_sid")
    acc = account_store().get(monitored_sid or "", {})
    if not monitored_sid or not acc:
        st.warning("No student is selected. Enter the Student ID on the login page.")
        if st.button("Back to login"):
            st.session_state.current_page = "login"
            st.rerun()
    else:
        md(f"""
        <div class="mac-hero">
          <div class="mac-kicker">Parent view</div>
          <h2 style="margin:0 0 4px;">Report for {html.escape(acc.get('name', 'Student'))}</h2>
          <p style="margin:0;">Student ID <b>{html.escape(str(monitored_sid))}</b> · {html.escape(str(acc.get('grade', '')))} · {html.escape(str(acc.get('board', 'CBSE')))}</p>
        </div>
        """)
        c1, c2, c3, c4 = st.columns(4)
        xp = db.get("student_xp", {}).get(monitored_sid, 0)
        streak = db.get("student_streaks", {}).get(monitored_sid, 0)
        quizzes = [q for q in db.get("quiz_results", []) if q.get("student_id") == monitored_sid]
        notes = db.get("student_nest_notes", {}).get(monitored_sid, [])
        c1.metric("Study points", f"{xp}")
        c2.metric("Streak", f"{streak} days")
        c3.metric("Quizzes", f"{len(quizzes)}")
        c4.metric("Focus blocks", f"{db.get('dhyana_counts', {}).get(monitored_sid, 0)}")
        st.markdown("### Recent quiz scores")
        if not quizzes:
            st.info("No quizzes yet.")
        else:
            for q in reversed(quizzes[-8:]):
                st.write(f"- **{q.get('subject')}** · {q.get('score')}/{q.get('total')} ({q.get('percentage')}%) · {q.get('taken_at')}")
        badges = db.get("student_badges", {}).get(monitored_sid, [])
        st.markdown("### Badges")
        if badges:
            st.write(", ".join(BADGE_CATALOG.get(b, {}).get("name", b) for b in badges))
        else:
            st.caption("No badges yet.")
        st.markdown("### Notes")
        if notes:
            for n in reversed(notes[-5:]):
                st.write(f"- **{n.get('title')}** ({n.get('subject')}) · {n.get('time')}")
        else:
            st.caption("No saved notes yet.")
        if st.button("Back to login"):
            st.session_state.current_page = "login"
            st.rerun()

# 5. DASHBOARD
elif st.session_state.current_page == "dashboard":
    update_streak()
    xp = get_student_xp()

    nav_items = [
        ("🏠 Home", "Dashboard"),
        ("🪪 Student Card", "Card"),
        ("📖 Chapters", "Subjects"),
        ("📝 Quiz", "Pariksha"),
        ("⚡ Guru AI", "Guru AI"),
        ("🧘 Focus Timer", "Dhyana"),
        ("📜 Saved Notes", "Notes"),
        ("🏆 Badges", "Honors"),
        ("⚙️ Settings", "Settings"),
    ]

    if "student_nav" not in st.session_state or st.session_state.student_nav not in [x[0] for x in nav_items]:
        st.session_state.student_nav = nav_items[0][0]

    open_sidebar_button()
    with st.sidebar:
        st.caption("VIDHYARADHANA")
        st.markdown(f"### {html.escape(str(st.session_state.user))}")
        st.caption(f"{st.session_state.grade} · {st.session_state.board} · ⭐ {xp}")
        st.caption("Hide with « at the top. Open again with ☰.")
        st.markdown("---")

        for label, short in nav_items:
            selected = st.session_state.student_nav == label
            if st.button(label, use_container_width=True,
                         type="primary" if selected else "secondary",
                         key=f"side_nav_{label}"):
                st.session_state.student_nav = label
                st.rerun()

        st.markdown("---")
        if st.button("Log Out", use_container_width=True, key="side_logout_btn"):
            st.session_state.update({
                "current_page": "login", "user": "", "email": "", "phone": "",
                "student_id": "", "plan": "Free", "grade": "Grade 5",
                "board": "CBSE", "active_quiz": [], "quiz_run_id": st.session_state.get("quiz_run_id", 0) + 1,
                "guru_style": "Friendly Tutor", "student_nav": "🏠 Home",
                "last_guru_answer": "", "last_guru_style": "", "quiz_feedback": None,
            })
            st.rerun()

    curr = st.session_state.student_nav

    # HOME
    if curr == "🏠 Home":
        md(f"""
        <div class="mac-hero">
          <div class="mac-kicker">॥ कक्षा ॥ ATHMANVESHI</div>
          <h2 style="margin:0 0 4px;">स्वागतम्, {html.escape(st.session_state.user)}</h2>
          <p style="margin:0;">{st.session_state.board} · {st.session_state.grade}</p>
        </div>
        """)
        render_id_card()

        c1, c2 = st.columns(2)
        with c1:
            level = get_level_from_xp(xp)
            next_xp = xp_for_next_level(level)
            prev_xp = xp_for_next_level(level - 1) if level > 1 else 0
            progress = min(100, int(((xp - prev_xp) / max(1, next_xp - prev_xp)) * 100))
            streak = get_streak()
            md(f"""
            <div class="mac-card">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                  <div class="mac-kicker">Level {level}</div>
                  <div style="font-size:22px;font-weight:750;color:#f7eedb;font-family:'Rozha One',serif;">⭐ {xp} stars</div>
                </div>
                <div style="text-align:right;">
                  <div style="font-size:22px;">🔥</div>
                  <div style="font-size:12px;font-weight:700;color:#e6d3bb;">{streak}-day streak</div>
                </div>
              </div>
              <div class="level-bar" style="margin-top:12px;"><div class="level-fill" style="width:{progress}%;"></div></div>
              <div style="font-size:12px;color:#e6d3bb;margin-top:6px;">{xp - prev_xp} / {next_xp - prev_xp} to Level {level + 1}</div>
            </div>
            """)
        with c2:
            st.markdown("#### Badges")
            badges = db.setdefault("student_badges", {}).get(st.session_state.student_id, [])
            if not badges:
                st.caption("Finish a quiz or a focus session to unlock your first badge.")
            else:
                h = "".join(
                    [f'<span class="pill">{BADGE_CATALOG[b]["emoji"]} {BADGE_CATALOG[b]["name"]}</span>' for b in
                     badges if b in BADGE_CATALOG])
                st.markdown(h, unsafe_allow_html=True)

        st.markdown("### Subjects")
        cols = st.columns(2)
        for i, (bilingual_title, english_sub) in enumerate(subject_catalog().items()):
            with cols[i % 2]:
                md(f"""
                <div class="mac-card" style="padding:16px;">
                  <div style="font-weight:700;color:#f7eedb;font-size:15px;">{bilingual_title}</div>
                </div>
                """)

    elif curr == "🪪 Student Card":
        md("""<div class="mac-hero"><div class="mac-kicker">Identity</div><h2 style="margin:0;">Your student card</h2></div>""")
        render_id_card()
        pic = st.file_uploader("Upload your photo", type=["png", "jpg", "jpeg", "webp"])
        if pic:
            sig = f"{pic.name}-{pic.size}"
            if st.session_state.get("last_photo_sig") != sig:
                raw = pic.getvalue()
                mime = pic.type or "image/jpeg"
                db.setdefault("student_photos", {})[
                    st.session_state.student_id] = f"data:{mime};base64," + base64.b64encode(raw).decode("ascii")
                persist_db()
                st.session_state.last_photo_sig = sig
                st.success("Photo saved to your card.")
                st.rerun()

    elif curr == "📖 Chapters":
        md(f"""
        <div class="mac-hero">
          <div class="mac-kicker">Notes</div>
          <h2 style="margin:0 0 4px;">{st.session_state.board} · {st.session_state.grade}</h2>
          <p style="margin:0;">Short chapter notes in plain language.</p>
        </div>
        """)

        catalog = subject_catalog()
        chosen_subject_label = st.selectbox("Subject", list(catalog.keys()))
        selected_internal_subject = catalog[chosen_subject_label]
        chapters = chapters_for(selected_internal_subject)

        if not chapters:
            st.info(f"Chapters for {chosen_subject_label} are being organized.")
        else:
            for c in chapters:
                with st.expander(f"📖 {c['ch']}"):
                    st.write(c["notes"])
                    if st.button("Practice quiz on this chapter", key=f"btn_pariksha_{c['ch']}"):
                        with st.spinner("Making a chapter quiz..."):
                            st.session_state.active_quiz = generate_pariksha(selected_internal_subject, "Easy", 10, c["ch"])
                        st.session_state.quiz_subject = chosen_subject_label
                        st.session_state.quiz_chapter = c["ch"]
                        st.session_state.quiz_run_id = st.session_state.get("quiz_run_id", 0) + 1
                        st.session_state.quiz_feedback = None
                        st.session_state.student_nav = "📝 Quiz"
                        st.rerun()

    elif curr == "📝 Quiz":
        md("""<div class="mac-hero"><div class="mac-kicker">Pariksha</div><h2 style="margin:0 0 4px;">Practice quiz</h2><p style="margin:0;">Answer, earn stars, level up.</p></div>""")
        catalog = subject_catalog()
        subj_choice = st.selectbox("Subject", list(catalog.keys()))
        selected_internal_subject = catalog[subj_choice]
        ch_rows = chapters_for(selected_internal_subject)
        ch_titles = [c["ch"] for c in ch_rows] or [selected_internal_subject]
        chapter_choice = st.selectbox("Chapter", ch_titles)
        diff = st.select_slider("Difficulty", ["Easy", "Medium", "Hard"], value="Easy")

        if st.button("Generate quiz", type="primary"):
            try:
                with st.spinner(f"Writing 10 MCQs and 1 written question for {chapter_choice}..."):
                    st.session_state.active_quiz = generate_pariksha(selected_internal_subject, diff, 10, chapter_choice)
            except Exception as e:
                st.session_state.active_quiz = _fallback_pariksha(selected_internal_subject, diff, 10)
                st.session_state.last_quiz_err = str(e)
                st.session_state.quiz_subjective = {
                    "question": f"In 4 or 5 lines, explain the main idea of {chapter_choice}.",
                    "hint": "Write in your own words.",
                }
            st.session_state.quiz_subject = subj_choice
            st.session_state.quiz_chapter = chapter_choice
            st.session_state.quiz_run_id = st.session_state.get("quiz_run_id", 0) + 1
            st.session_state.quiz_feedback = None
            st.rerun()

        fb = st.session_state.get("quiz_feedback")
        if fb:
            if fb.get("pct", 0) >= 80:
                st.balloons()
                st.success(fb.get("msg"))
            else:
                st.info(fb.get("msg"))

        if st.session_state.active_quiz:
            st.caption(f"{st.session_state.get('quiz_subject','')} · {st.session_state.get('quiz_chapter','')} · 10 MCQs + 1 written")
            if st.session_state.get("last_quiz_err"):
                st.caption("Live teacher is busy, so this quiz uses saved school questions. You can still answer and score.")
            run_id = st.session_state.get("quiz_run_id", 0)
            with st.form(f"quiz_form_{run_id}"):
                user_ans = []
                for i, q in enumerate(st.session_state.active_quiz):
                    st.markdown(f"**MCQ {i + 1}: {q['question']}**")
                    user_ans.append(st.radio("Pick one:", q["options"], index=0, key=f"q_choice_{run_id}_{i}"))
                subq = st.session_state.get("quiz_subjective") or {}
                st.markdown(f"**Written question:** {subq.get('question', 'Explain the chapter in your own words.')}")
                st.text_area(subq.get("hint", "Write 3 to 5 lines."), key=f"q_subjective_{run_id}", height=120)
                if st.form_submit_button("Submit & check score", type="primary"):
                    if any(a is None for a in user_ans):
                        st.warning("Please answer every question.")
                    else:
                        score = sum(1 for i, q in enumerate(st.session_state.active_quiz) if user_ans[i] == q["answer"])
                        total = len(st.session_state.active_quiz)
                        pct = round(score / total * 100, 1)
                        award_xp(score * 10, "Quiz Passed", save=False)
                        grant_badge("first_quiz", save=False)
                        subj = st.session_state.get("quiz_subject", "")
                        if score == total:
                            if "Mathematics" in subj:
                                grant_badge("math_wizard", save=False)
                            elif "Science" in subj:
                                grant_badge("science_lab", save=False)
                        db.setdefault("quiz_results", []).append({
                            "student_id": st.session_state.student_id,
                            "subject": subj,
                            "score": score, "total": total, "percentage": pct,
                            "taken_at": datetime.now().strftime("%d %b %Y, %I:%M %p")
                        })
                        persist_db()
                        st.session_state.quiz_feedback = {
                            "pct": pct,
                            "msg": f"You scored {score}/{total} ({pct}%). +{score * 10} stars.",
                        }
                        st.session_state.active_quiz = []
                        st.rerun()

    elif curr == "⚡ Guru AI":
        md("""
        <div class="mac-hero">
          <div class="mac-kicker">॥ गुरुः प्रश्नम् ॥</div>
          <h2 style="margin:0 0 4px;">Guru AI • व्याख्या शैली</h2>
          <p style="margin:0;">Pick up to 5 styles. {st.session_state.get("voice_name", VOICE_NAME)} speaks in {st.session_state.get("answer_lang", "English (India)")}.</p>
        </div>
        """)

        all_styles = list(GURU_STYLES.keys())
        raw_pinned = st.multiselect(
            "Your 5 styles (maximum 5)",
            all_styles,
            default=[s for s in st.session_state.get("pinned_styles", []) if s in all_styles][:5],
            max_selections=5,
        )
        if raw_pinned:
            st.session_state.pinned_styles = raw_pinned[:5]
        pinned = [s for s in st.session_state.get("pinned_styles", []) if s in all_styles][:5] or ["Friendly Tutor"]
        chosen_style = st.radio("Use this style now", pinned, horizontal=True)
        st.session_state.guru_style = chosen_style
        info_now = GURU_STYLES.get(chosen_style, {})
        st.caption(f"{info_now.get('emoji', '')} {info_now.get('blurb', '')}")
        want_voice = st.radio(
            "Voice for this answer",
            ["Text only", "Read aloud"],
            index=1 if st.session_state.get("voice_on") else 0,
            horizontal=True,
        )
        st.session_state.voice_on = want_voice == "Read aloud"

        q = st.text_area(
            "Your question",
            placeholder="e.g. Why is the sky blue?  or  How do fractions work?",
            height=120,
        )

        if st.button("Explain this", type="primary", use_container_width=True):
            if not q.strip():
                st.warning("Type a question first.")
            else:
                style = GURU_STYLES[chosen_style]
                with st.spinner(f"{style['emoji']} {VOICE_NAME} is explaining in {chosen_style} style..."):
                    lang = st.session_state.get("answer_lang", "English (India)")
                    prompt = (
                        f"Answer this school question for a {st.session_state.grade} {st.session_state.board} student.\n"
                        f"Language: {lang} only.\n"
                        f"Question: {q}\n"
                        f"Write the answer itself. Do not repeat the style name. Do not say 'Grade 5 level?'.\n"
                        f"Style: {style['instruction']}"
                    )
                    ans, _ = call_gemini([
                        {"role": "system",
                         "content": f"You are a kind school teacher. Answer the student's question directly in {lang}. No meta talk."},
                        {"role": "user", "content": prompt}
                    ], temperature=0.4, max_tokens=900, timeout=30)
                    if not ans:
                        ans = (
                            f"**{chosen_style}**\n\n"
                            f"Great question about your {st.session_state.grade} work. "
                            f"Break it into 3 small parts, write one example from school or home, "
                            f"then say the idea in one line. Ask again in a moment if the teacher is busy."
                        )
                        st.session_state.last_guru_voice_err = _ or "Teacher is busy right now."
                    award_xp(5, "AI Inquired")
                    st.session_state.last_guru_answer = ans
                    st.session_state.last_guru_style = chosen_style
                    st.session_state.last_guru_audio = None
                    if st.session_state.get("voice_on"):
                        audio_b64, err = generate_elevenlabs_speech(ans)
                        if audio_b64:
                            st.session_state.last_guru_audio = audio_b64
                        else:
                            st.session_state.last_guru_voice_err = err
                            speak_browser_fallback(_speech_text(ans))

        if st.session_state.get("last_guru_answer"):
            used = st.session_state.get("last_guru_style", chosen_style)
            info = GURU_STYLES.get(used, {"emoji": "🪔"})
            st.markdown(f"### {info['emoji']} {used}")
            st.markdown(st.session_state.last_guru_answer)
            if st.session_state.get("voice_on") and st.session_state.get("last_guru_audio"):
                play_named_voice(st.session_state.last_guru_audio)
            elif st.session_state.get("voice_on") and st.session_state.get("last_guru_voice_err"):
                st.caption("Voice is unavailable right now. The written answer is ready.")

    elif curr == "🧘 Focus Timer":
        md("""
        <div class="mac-hero" style="text-align:center;">
          <div class="mac-kicker">Focus</div>
          <h2 style="margin:0 0 6px;">25-minute study block</h2>
          <p style="margin:0;">Start the clock. Stay with one chapter until it ends.</p>
        </div>
        """)
        if "timer_end" not in st.session_state:
            st.session_state.timer_end = None
            st.session_state.timer_running = False
            st.session_state.timer_awarded = False
        left = 25 * 60
        if st.session_state.timer_end:
            left = max(0, int(st.session_state.timer_end - time.time()))
        mins, secs = divmod(left, 60)
        md(f"""
        <div class="mac-card" style="text-align:center;padding:42px 20px;">
          <div class="mac-kicker">Timer</div>
          <div style="font-size:72px;font-weight:750;letter-spacing:-0.04em;color:#f7eedb;margin:4px 0;">{mins:02d}:{secs:02d}</div>
          <div style="font-size:14px;color:#c4ad99;">Notebook open. One topic only.</div>
        </div>
        """)
        c1, c2, c3 = st.columns(3)
        if c1.button("Start", type="primary", use_container_width=True):
            remain = st.session_state.get("timer_left", 25 * 60) or (25 * 60)
            if st.session_state.timer_running:
                remain = 25 * 60
            st.session_state.timer_end = time.time() + remain
            st.session_state.timer_running = True
            st.session_state.timer_awarded = False
            st.rerun()
        if c2.button("Pause", use_container_width=True):
            if st.session_state.timer_running and st.session_state.timer_end:
                st.session_state.timer_left = max(0, int(st.session_state.timer_end - time.time()))
                st.session_state.timer_running = False
                st.session_state.timer_end = None
            st.rerun()
        if c3.button("Reset", use_container_width=True):
            st.session_state.timer_end = None
            st.session_state.timer_running = False
            st.session_state.timer_left = 25 * 60
            st.rerun()
        if st.session_state.timer_running and left > 0:
            time.sleep(1)
            st.rerun()
        if st.session_state.timer_running and left == 0 and not st.session_state.timer_awarded:
            sid = st.session_state.get("student_id", "")
            counts = db.setdefault("dhyana_counts", {})
            counts[sid] = counts.get(sid, 0) + 1
            award_xp(15, "Dhyana", save=False)
            if counts[sid] >= 15:
                grant_badge("dhyana_master", save=False)
            persist_db()
            st.session_state.timer_awarded = True
            st.session_state.timer_running = False
            st.balloons()
            st.success(f"25 minutes done. +15 stars. Sessions: {counts[sid]}/15 for the Dhyana badge.")
        elif st.session_state.get("timer_awarded") and left == 0:
            st.success("This block is finished. Reset to start another.")

    elif curr == "📜 Saved Notes":
        md("""<div class="mac-hero"><div class="mac-kicker">Notebook</div><h2 style="margin:0 0 4px;">Your notes</h2><p style="margin:0;">Write what you understood in your own words.</p></div>""")
        n_sub = st.selectbox("Subject", list(subject_catalog().keys()))
        n_title = st.text_input("Title", placeholder="e.g. Shortcut for multiplication")
        n_body = st.text_area("Notes", placeholder="Write what you understood today...")
        if st.button("Save note", type="primary"):
            if not (n_body or "").strip():
                st.warning("Write something before saving.")
            elif add_student_note(st.session_state.student_id, n_sub, n_title, n_body):
                award_xp(5, "Notes")
                st.success("Saved.")
                st.rerun()

        notes = get_student_notes(st.session_state.student_id)
        if notes:
            st.markdown("### Saved")
            for n in reversed(notes[-4:]):
                with st.expander(f"📝 {n.get('title')} ({n.get('subject')})"):
                    st.write(n.get("body"))
                    st.caption(f"Saved on {n.get('time')}")

    elif curr == "🏆 Badges":
        md("""<div class="mac-hero"><div class="mac-kicker">Honors</div><h2 style="margin:0;">Medals and badges</h2></div>""")
        badges = db.setdefault("student_badges", {}).get(st.session_state.student_id, [])
        for bid, info in BADGE_CATALOG.items():
            unlocked = bid in badges
            status = "Unlocked" if unlocked else "Locked"
            st.write(f"{info['emoji']} **{info['name']}** — {info['desc']} · `{status}`")

    elif curr == "⚙️ Settings":
        uname = html.escape(str(st.session_state.get("user") or "Student"))
        initial = (st.session_state.get("user") or "S")[:1].upper()
        md(f"""
        <div class="settings-title">Settings</div>
        <div class="settings-profile">
          <div class="settings-avatar">{initial}</div>
          <div>
            <div style="font-size:20px;font-weight:700;color:#f7eedb;">{uname}</div>
            <div style="font-size:13px;color:#d8c4ae;">{html.escape(str(st.session_state.get('grade','')))} · {html.escape(str(st.session_state.get('board','')))}</div>
          </div>
        </div>
        """)
        md('<div class="settings-label">Audio</div><div class="settings-group">')
        voice_choice = st.radio(
            "Read answers aloud",
            ["Off", "On"],
            index=1 if st.session_state.get("voice_on") else 0,
            horizontal=True,
        )
        st.session_state.voice_on = voice_choice == "On"
        if st.session_state.voice_on:
            st.session_state.voice_volume = st.slider("Volume", 0.2, 1.0, float(st.session_state.get("voice_volume", 0.9)), 0.05)
            spd_label = st.radio("Speed", ["Slow", "Normal", "Fast"], horizontal=True,
                                 index={"Slow": 0, "Normal": 1, "Fast": 2}.get(
                                     "Slow" if st.session_state.get("voice_speed", 1.0) < 0.9 else "Fast" if st.session_state.get("voice_speed", 1.0) > 1.1 else "Normal", 1))
            st.session_state.voice_speed = {"Slow": 0.8, "Normal": 1.0, "Fast": 1.2}[spd_label]
            sm_label = st.radio("Tone", ["Soft", "Balanced", "Crisp"], horizontal=True,
                                index=1 if 0.5 <= float(st.session_state.get("voice_stability", 0.62)) <= 0.72 else (0 if float(st.session_state.get("voice_stability", 0.62)) < 0.5 else 2))
            st.session_state.voice_stability = {"Soft": 0.45, "Balanced": 0.62, "Crisp": 0.82}[sm_label]
        md('</div>')

        md('<div class="settings-label">Language</div><div class="settings-group">')
        lang = st.selectbox(
            "Text language",
            INDIAN_LANGUAGES,
            index=INDIAN_LANGUAGES.index(st.session_state.get("answer_lang", "English (India)"))
            if st.session_state.get("answer_lang") in INDIAN_LANGUAGES else 0,
        )
        if lang != st.session_state.get("answer_lang"):
            st.session_state.answer_lang = lang
            st.session_state.last_guru_audio = None
        voice_names = list(VOICE_CATALOG.keys())
        vname = st.selectbox(
            "Speaker",
            voice_names,
            index=voice_names.index(st.session_state.get("voice_name"))
            if st.session_state.get("voice_name") in VOICE_CATALOG else 0,
        )
        if vname != st.session_state.get("voice_name"):
            st.session_state.voice_name = vname
            st.session_state.voice_id = VOICE_CATALOG[vname]
            st.session_state.last_guru_audio = None
        md('</div>')

        md('<div class="settings-label">Guru Styles</div><div class="settings-group">')
        picked = st.multiselect(
            "Pinned styles · max 5",
            list(GURU_STYLES.keys()),
            default=[s for s in st.session_state.get("pinned_styles", []) if s in GURU_STYLES][:5],
            max_selections=5,
        )
        if picked:
            st.session_state.pinned_styles = picked[:5]
            if st.session_state.get("guru_style") not in st.session_state.pinned_styles:
                st.session_state.guru_style = st.session_state.pinned_styles[0]
        st.caption(f"{st.session_state.get('voice_name', VOICE_NAME)} · {st.session_state.get('answer_lang')} · {len(st.session_state.get('pinned_styles', []))}/5")
        md('</div>')

else:
    st.session_state.current_page = "landing"
    st.rerun()
