import warnings
warnings.filterwarnings("ignore")
import logging
logging.disable(logging.CRITICAL)

import os
import datetime
import requests
import streamlit as st
from urllib.parse import quote

st.set_page_config(page_title="∞ SynapseGrid", page_icon="∞", layout="centered")


GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

from langchain_groq import ChatGroq


models = {
    "llama_fast": ChatGroq(model="llama-3.1-8b-instant"),
    "llama":      ChatGroq(model="llama-3.3-70b-versatile"),                #multiple models for better response 
    "gemma":      ChatGroq(model="gemma2-9b-it"),
    "mixtral":    ChatGroq(model="mixtral-8x7b-32768")                      #the models used from groq which offers for free
}

def ask(system, user, model_name="llama_fast"):
    response = models[model_name].invoke([
        {"role": "system", "content": system},
        {"role": "user",   "content": user[:500]}
    ], max_tokens=800)
    return response.content


def search_news(query):
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if not results:
                return "No results found"
            output = ""
            for i, r in enumerate(results, 1):
                output += f"{i}. {r['title']}\n{r['body'][:200]}\n\n"
            return output
    except Exception as e:
        return f"Search failed: {e}"

def gen_image(prompt):
    try:
        encoded = quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?nologo=true&model=flux"              # for image generation i used pollinations 
        response = requests.get(url, timeout=60)
        return response.content
    except Exception as e:
        return None

def write_report(topic, model_name):
    return ask("You are a professional report-writing AI that creates detailed, well-structured, research-quality reports with clear headings, summaries, insights, and polished formatting..", f"Write report on: {topic}", model_name)
def write_blog(topic, model_name):
    return ask("Write an engaging blog post.", f"Write blog about: {topic}", model_name)
def write_lyrics(topic, model_name):
    return ask("Write original song lyrics with verses and chorus.", f"Write song lyrics: {topic}", model_name)
def write_code(task, model_name):
    return ask("You are an expert software engineer that writes clean, optimized, scalable, production-ready code with clear explanations, debugging support, and best coding practices..", f"Write code for: {task}", model_name)
def write_story(topic, model_name):
    return ask("Write a creative engaging story.", f"Write story about: {topic}", model_name)                        #multiple agnets 
def create_plan(goal, model_name):
    return ask("Create a clear step by step plan.", f"Plan for: {goal}", model_name)
def music_ideas(topic, model_name):
    return ask("Suggest chord progressions and song structure.", f"Music ideas for: {topic}", model_name)
def create_schedule(task, model_name):
    return ask("Create a practical schedule.", f"Schedule for: {task}", model_name)
def general_chat(query, model_name):
    return ask("You are a helpful assistant. Be concise, accurate and friendly.", query, model_name)

def route(user_input, model_name="llama_fast"):
    p = user_input.lower()
    if any(w in p for w in ["latest","news","current","today","recent","search","find"]):
        raw = search_news(user_input)
        return ("text", ask("Summarize these news results clearly with headlines.", f"Results:\n{raw}", model_name))
    elif any(w in p for w in ["image","generate image","draw","picture","photo"]):
        img = gen_image(user_input)
        return ("image", img)
    elif any(w in p for w in ["report"]):
        return ("text", write_report(user_input, model_name))
    elif any(w in p for w in ["blog","article"]):
        return ("text", write_blog(user_input, model_name))
    elif any(w in p for w in ["lyrics","song","write a song"]):
        return ("text", write_lyrics(user_input, model_name))
    elif any(w in p for w in ["code","python","program","function","script"]):                                     #router thast conects model response  with user input
        return ("text", write_code(user_input, model_name))
    elif any(w in p for w in ["story","fiction","tale"]):
        return ("text", write_story(user_input, model_name))
    elif any(w in p for w in ["plan","steps","roadmap","goal"]):
        return ("text", create_plan(user_input, model_name))
    elif any(w in p for w in ["music","chord","melody","beat"]):
        return ("text", music_ideas(user_input, model_name))
    elif any(w in p for w in ["schedule","routine","timetable"]):
        return ("text", create_schedule(user_input, model_name))
    else:
        return ("text", general_chat(user_input, model_name))

# ── Session State ─────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "llama_fast"
# ══════════════════════════════════════════════════════════
# LANDING PAGE
# ══════════════════════════════════════════════════════════
if st.session_state.page == "landing":
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');

    * { font-family: 'Inter', sans-serif; margin: 0; padding: 0; }
    .block-container { padding-top: 0 !important; max-width: 1000px; }
    
    /* ── Hero ── */
    .hero {
        background: linear-gradient(135deg, #0a0a1a 0%, #1a0a2e 50%, #0a1a2e 100%);
        border-radius: 24px;
        padding: 70px 40px 50px;
        text-align: center;
        margin-bottom: 30px;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(139, 92, 246, 0.3);
    }

    /* ── Infinity Symbol ── */
    .infinity-wrap {
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }
    .infinity {
        font-size: 5em;
        color: transparent;
        background: linear-gradient(135deg, #8b5cf6, #06b6d4, #8b5cf6);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        background-clip: text;
        animation: gradientShift 3s ease infinite, pulse 2s ease-in-out infinite;
        display: inline-block;
        filter: drop-shadow(0 0 20px rgba(139, 92, 246, 0.8));
    }
    @keyframes gradientShift {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50%       { transform: scale(1.1); }
    }

    /* ── Floating Particles ── */
    .particles { position: absolute; top: 0; left: 0; width: 100%; height: 100%; overflow: hidden; pointer-events: none; }
    .particle {
        position: absolute;
        width: 4px; height: 4px;
        border-radius: 50%;
        background: rgba(139,92,246,0.6);
        animation: float linear infinite;
    }
    .particle:nth-child(1)  { left:10%; animation-duration:8s;  animation-delay:0s;   width:3px; height:3px; }
    .particle:nth-child(2)  { left:20%; animation-duration:12s; animation-delay:2s;   background:rgba(6,182,212,0.6); }
    .particle:nth-child(3)  { left:35%; animation-duration:9s;  animation-delay:1s;   width:5px; height:5px; }
    .particle:nth-child(4)  { left:50%; animation-duration:11s; animation-delay:3s;   background:rgba(6,182,212,0.6); }
    .particle:nth-child(5)  { left:65%; animation-duration:10s; animation-delay:0.5s; width:3px; height:3px; }
    .particle:nth-child(6)  { left:80%; animation-duration:13s; animation-delay:1.5s; background:rgba(139,92,246,0.4); }
    .particle:nth-child(7)  { left:90%; animation-duration:7s;  animation-delay:2.5s; width:6px; height:6px; }
    @keyframes float {
        0%   { transform: translateY(100%) rotate(0deg);   opacity: 0; }
        10%  { opacity: 1; }
        90%  { opacity: 1; }
        100% { transform: translateY(-100px) rotate(360deg); opacity: 0; }
    }

    .hero h1 { font-size: 2.8em; font-weight: 900; color: white; margin-bottom: 12px; letter-spacing: -1px; }
    .hero p  { font-size: 1.15em; color: #94a3b8; max-width: 600px; margin: 0 auto 20px; line-height: 1.7; }
    .badge {
        display: inline-block;
        background: rgba(139,92,246,0.15);
        color: #a78bfa;
        border: 1px solid rgba(139,92,246,0.4);
        border-radius: 20px;
        padding: 5px 16px;
        font-size: 0.85em;
        margin-bottom: 20px;
        animation: badgePulse 2s ease infinite;
    }
    @keyframes badgePulse {
        0%,100% { box-shadow: 0 0 0 0 rgba(139,92,246,0.4); }
        50%      { box-shadow: 0 0 0 8px rgba(139,92,246,0); }
    }

    /* ── Stats ── */
    .stats {
        display: flex;
        justify-content: center;
        gap: 40px;
        margin-top: 30px;
        flex-wrap: wrap;
    }
    .stat { text-align: center; }
    .stat-num { font-size: 2em; font-weight: 900; color: #8b5cf6; }
    .stat-label { font-size: 0.8em; color: #64748b; }

    /* ── Section Title ── */
    .section-title {
        text-align: center;
        font-size: 1.8em;
        font-weight: 800;
        color: white;
        margin: 40px 0 20px;
    }
    .section-sub {
        text-align: center;
        color: #64748b;
        margin-bottom: 25px;
        font-size: 0.95em;
    }

    /* ── Agent Cards ── */
    .agent-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 30px; }
    .agent-card {
        background: linear-gradient(135deg, #0f0f1f, #1a1a2e);
        border: 1px solid rgba(139,92,246,0.2);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
        animation: cardFadeIn 0.5s ease both;
        cursor: pointer;
    }
    .agent-card:hover {
        border-color: rgba(139,92,246,0.6);
        transform: translateY(-4px);
        box-shadow: 0 10px 30px rgba(139,92,246,0.2);
        background: linear-gradient(135deg, #1a1030, #0f1a30);
    }
    @keyframes cardFadeIn {
        from { opacity:0; transform:translateY(20px); }
        to   { opacity:1; transform:translateY(0); }
    }
    .agent-card:nth-child(1) { animation-delay: 0.1s; }
    .agent-card:nth-child(2) { animation-delay: 0.2s; }
    .agent-card:nth-child(3) { animation-delay: 0.3s; }
    .agent-card:nth-child(4) { animation-delay: 0.4s; }
    .agent-card:nth-child(5) { animation-delay: 0.5s; }
    .agent-card:nth-child(6) { animation-delay: 0.6s; }
    .agent-card:nth-child(7) { animation-delay: 0.7s; }
    .agent-card:nth-child(8) { animation-delay: 0.8s; }
    .agent-card:nth-child(9) { animation-delay: 0.9s; }
    .agent-icon { font-size: 2.2em; margin-bottom: 10px; }
    .agent-name { color: #e2e8f0; font-weight: 700; font-size: 0.95em; margin-bottom: 6px; }
    .agent-desc { color: #64748b; font-size: 0.8em; line-height: 1.5; }

    /* ── How it works ── */
    .how-box {
        background: linear-gradient(135deg, #0a1628, #1a0a28);
        border: 1px solid rgba(6,182,212,0.2);
        border-radius: 20px;
        padding: 35px;
        margin-bottom: 30px;
    }
    .how-box h2 { color: #06b6d4; font-size: 1.5em; margin-bottom: 25px; text-align: center; }
    .step { display: flex; align-items: flex-start; gap: 15px; margin-bottom: 20px; animation: slideIn 0.5s ease both; }
    @keyframes slideIn { from { opacity:0; transform:translateX(-20px); } to { opacity:1; transform:translateX(0); } }
    .step:nth-child(2) { animation-delay: 0.1s; }
    .step:nth-child(3) { animation-delay: 0.2s; }
    .step:nth-child(4) { animation-delay: 0.3s; }
    .step:nth-child(5) { animation-delay: 0.4s; }
    .step-num {
        background: linear-gradient(135deg, #8b5cf6, #06b6d4);
        color: white; border-radius: 50%;
        width: 35px; height: 35px; min-width: 35px;
        display: flex; align-items: center; justify-content: center;
        font-weight: 800; font-size: 0.9em;
    }
    .step-text h4 { color: #e2e8f0; margin-bottom: 4px; font-size: 0.95em; }
    .step-text p  { color: #64748b; font-size: 0.85em; line-height: 1.5; }

    /* ── Examples ── */
    .examples-box {
        background: #0a0a1a;
        border: 1px solid rgba(139,92,246,0.15);
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 30px;
    }
    .example {
        background: linear-gradient(135deg, #0f0f20, #1a0f20);
        border-left: 3px solid #8b5cf6;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
        color: #94a3b8;
        font-size: 0.9em;
        transition: all 0.3s;
        animation: fadeIn 0.5s ease both;
    }
    .example:hover { background: #1a1030; color: #e2e8f0; transform: translateX(5px); }
    @keyframes fadeIn { from { opacity:0; } to { opacity:1; } }

    /* ── Start Button ── */
    .stButton > button {
        background: linear-gradient(135deg, #8b5cf6, #06b6d4) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        font-size: 1.15em !important;
        font-weight: 700 !important;
        padding: 16px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 25px rgba(139,92,246,0.4) !important;
        letter-spacing: 0.5px !important;
    }
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 35px rgba(139,92,246,0.6) !important;
    }

    /* ── Footer ── */
    .footer { text-align: center; color: #1e293b; font-size: 0.8em; margin-top: 20px; padding-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

    # ── Hero Section ──────────────────────────────────────
    st.markdown("""
    <div class="hero">
        <div class="particles">
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
        </div>
        <div class="infinity-wrap">
            <span class="infinity">∞</span>
        </div>
        <div class="badge">✨ Crafted for Intelligent Automation</div>
        <h1>Aeon Labs</h1>
        <p>An intelligent AI system with specialized agents that think, plan, and act — search the web, write content, generate images and much more.</p>
        <div class="stats">
            <div class="stat"><div class="stat-num">10+</div><div class="stat-label">AI Agents</div></div>
            <div class="stat"><div class="stat-num">∞</div><div class="stat-label">Possibilities</div></div>
            <div class="stat"><div class="stat-num">1</div><div class="stat-label">Simple Chat</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Agents Section ────────────────────────────────────
    st.markdown('<div class="section-title">⚡ Meet the Agents</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Each agent is a specialist — the system picks the right one automatically</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="agent-grid">
        <div class="agent-card">
            <div class="agent-icon">🔍</div>
            <div class="agent-name">Web Search</div>
            <div class="agent-desc">Finds latest news, facts and real-time information from the internet</div>
        </div>
        <div class="agent-card">
            <div class="agent-icon">🎨</div>
            <div class="agent-name">Image Generator</div>
            <div class="agent-desc">Creates stunning AI-generated images from your text descriptions</div>
        </div>
        <div class="agent-card">
            <div class="agent-icon">📄</div>
            <div class="agent-name">Report Writer</div>
            <div class="agent-desc">Writes professional structured reports on any topic</div>
        </div>
        <div class="agent-card">
            <div class="agent-icon">✍️</div>
            <div class="agent-name">Blog Writer</div>
            <div class="agent-desc">Creates engaging SEO-friendly blog posts and articles</div>
        </div>
        <div class="agent-card">
            <div class="agent-icon">🎵</div>
            <div class="agent-name">Lyrics Writer</div>
            <div class="agent-desc">Writes original song lyrics with verses, chorus and bridge</div>
        </div>
        <div class="agent-card">
            <div class="agent-icon">💻</div>
            <div class="agent-name">Code Writer</div>
            <div class="agent-desc">Writes clean code in any language with clear explanations</div>
        </div>
        <div class="agent-card">
            <div class="agent-icon">📖</div>
            <div class="agent-name">Story Writer</div>
            <div class="agent-desc">Creates immersive stories with characters and engaging plots</div>
        </div>
        <div class="agent-card">
            <div class="agent-icon">🗓️</div>
            <div class="agent-name">Planner</div>
            <div class="agent-desc">Creates step-by-step plans and actionable roadmaps for any goal</div>
        </div>
        <div class="agent-card">
            <div class="agent-icon">🎼</div>
            <div class="agent-name">Music Ideas</div>
            <div class="agent-desc">Suggests chord progressions, song structures and instrument ideas</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── How It Works ──────────────────────────────────────
    st.markdown("""
    <div class="how-box">
        <h2>⚙️ How It Works</h2>
        <div class="step">
            <div class="step-num">1</div>
            <div class="step-text"><h4>You type anything naturally</h4><p>No commands needed — just chat like you would with a friend</p></div>
        </div>
        <div class="step">
            <div class="step-num">2</div>
            <div class="step-text"><h4>AI reads and understands your request</h4><p>The system analyzes your message and identifies what you need</p></div>
        </div>
        <div class="step">
            <div class="step-num">3</div>
            <div class="step-text"><h4>Right agent is selected automatically</h4><p>No manual selection — the best specialist agent is picked for you</p></div>
        </div>
        <div class="step">
            <div class="step-num">4</div>
            <div class="step-text"><h4>Agent completes the task</h4><p>The agent uses its specialized skills to give you the best result</p></div>
        </div>
        <div class="step">
            <div class="step-num">5</div>
            <div class="step-text"><h4>Result appears in chat</h4><p>Text, images, code, reports — all delivered right in the conversation</p></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Examples ──────────────────────────────────────────
    st.markdown('<div class="section-title">💡 Try These Examples</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="examples-box">
        <div class="example">🔍 "What is the latest news about AI today?"</div>
        <div class="example">🎨 "Generate an image of a futuristic city at night"</div>
        <div class="example">📄 "Write a report on climate change"</div>
        <div class="example">✍️ "Write a blog post about electric vehicles"</div>
        <div class="example">🎵 "Write a song for chill mood"</div>
        <div class="example">💻 "Write Python code for a calculator"</div>
        <div class="example">📖 "Write a story about a dragon and a knight"</div>
        <div class="example">🗓️ "Create a plan to learn machine learning"</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Start Button ──────────────────────────────────────
    if st.button("∞  Start Chatting Now", use_container_width=True, type="primary"):
        st.session_state.page = "chat"
        st.rerun()

    st.markdown('<div class="footer">Built with ∞ LangChain • Groq • DuckDuckGo • Pollinations • Streamlit</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# CHAT PAGE
# ══════════════════════════════════════════════════════════
elif st.session_state.page == "chat":

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 1rem !important; }

    /* header */
    .chat-header {
        background: linear-gradient(135deg, #0a0a1a, #1a0a2e);
        border-radius: 16px;
        padding: 16px 24px;
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
        border: 1px solid rgba(139,92,246,0.2);
    }
    .chat-title { color: white; font-size: 1.3em; font-weight: 800; }
    .chat-sub   { color: #64748b; font-size: 0.8em; }

    /* infinity small */
    .inf-small {
        font-size: 2em;
        background: linear-gradient(135deg, #8b5cf6, #06b6d4);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        animation: spin 4s linear infinite;
        display: inline-block;
    }
    @keyframes spin {
        0%   { transform: rotate(0deg) scale(1); }
        25%  { transform: rotate(5deg) scale(1.1); }
        50%  { transform: rotate(0deg) scale(1); }
        75%  { transform: rotate(-5deg) scale(1.1); }
        100% { transform: rotate(0deg) scale(1); }
    }

    /* messages */
    .stChatMessage { animation: msgIn 0.4s ease both; }
    @keyframes msgIn { from { opacity:0; transform:translateY(15px); } to { opacity:1; transform:translateY(0); } }

    /* input */
    .stChatInput input {
        background: #0f0f1f !important;
        border: 1px solid rgba(139,92,246,0.3) !important;
        border-radius: 12px !important;
        color: white !important;
    }
    .stChatInput input:focus {
        border-color: rgba(139,92,246,0.8) !important;
        box-shadow: 0 0 0 2px rgba(139,92,246,0.2) !important;
    }

    /* back button */
    .stButton > button {
        background: rgba(139,92,246,0.1) !important;
        color: #a78bfa !important;
        border: 1px solid rgba(139,92,246,0.3) !important;
        border-radius: 10px !important;
        font-size: 0.9em !important;
        transition: all 0.3s !important;
    }
    .stButton > button:hover {
        background: rgba(139,92,246,0.2) !important;
        border-color: rgba(139,92,246,0.6) !important;
    }

    /* clear button */
    .clear-btn > button {
        background: rgba(239,68,68,0.1) !important;
        color: #f87171 !important;
        border: 1px solid rgba(239,68,68,0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        
    
        st.markdown("### 🤖 Choose Model")
        st.session_state.selected_model = st.selectbox(
        "Select AI Model",
        options=["llama_fast", "llama", "gemma", "mixtral"],
        format_func=lambda x: {
            "llama_fast": "⚡ Kaizen 3.1  (⚡️ Fast & Light)",
            "llama":      "🦙 Kaizen 3.3  (Smart)",
            "gemma":      "💎 Gemma 2.1 (Google+Balanced)",
            "mixtral":    "🌀 Halo 3.2 (📚 Reasoning+Long Context)"
        }[x]
    )
    

    
    col1, col2, col3 = st.columns([1, 5, 1])
    with col1:
        if st.button("← Home"):
            st.session_state.page = "landing"
            st.rerun()
    with col2:
        st.markdown("""
        <div class="chat-header">
            <span class="inf-small">∞</span>
            <div>
                <div class="chat-title">Multi Agent AI</div>
                <div class="chat-sub">Ask anything — I'll pick the right agent for you</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        if st.button("🗑️ Clear"):
            st.session_state.chat_history = []
            st.rerun()

    
    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(chat["user"])
        with st.chat_message("assistant"):
            if chat["type"] == "image" and chat["content"]:
                st.image(chat["content"])
            else:
                st.write(chat["content"])

    
    if not st.session_state.chat_history:
        st.markdown("**💡 Quick Start:**")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("🔍 Latest News"):
                st.session_state.quick = "What is the latest news today?"
        with col2:
            if st.button("🎨 Gen Image"):
                st.session_state.quick = "Generate an image of a futuristic city"
        with col3:
            if st.button("💻 Write Code"):
                st.session_state.quick = "Write Python code for a calculator"
        with col4:
            if st.button("📄 Write Report"):
                st.session_state.quick = "Write a report on artificial intelligence"

    
    user_prompt = st.chat_input("Ask anything...")

    
    if "quick" in st.session_state:
        user_prompt = st.session_state.quick
        del st.session_state.quick

    if user_prompt:                                           #user chat section :prompt,spinner,result
        with st.chat_message("user"):
            st.write(user_prompt)

        with st.chat_message("assistant"):
            
            p = user_prompt.lower()
            if any(w in p for w in ["image","draw","picture","generate"]):
                spinner = "🎨 Generating image..."
            elif any(w in p for w in ["news","latest","search"]):
                spinner = "🔍 Searching the web..."
            elif any(w in p for w in ["report","blog","lyrics","story","code"]):
                spinner = "✍️ Writing..."
            else:
                spinner = "💬 Thinking..."

            with st.spinner(spinner):
                try:
                    result_type, result_content = route(user_prompt)

                    if result_type == "image" and result_content:
                        st.image(result_content)
                    elif result_type == "image" and not result_content:
                        st.warning("⚠️ Image generation failed. Try again!")
                        result_content = None
                    else:
                        st.write(result_content)

                    # save to history
                    st.session_state.chat_history.append({
                        "user":    user_prompt,
                        "type":    result_type,
                        "content": result_content
                    })

                except Exception as e:
                    st.error(f"❌ Error: {e}")

    
    if st.session_state.chat_history:
        st.markdown(f"<p style='text-align:center; color:#1e293b; font-size:0.8em; margin-top:10px'>💬 {len(st.session_state.chat_history)} messages in this session</p>", unsafe_allow_html=True)
