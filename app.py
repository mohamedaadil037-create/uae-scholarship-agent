import streamlit as st
import os
import tempfile
# --- LIBRARIES ---
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.document_loaders import PyPDFLoader, ArxivLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. PAGE CONFIGURATION (MUST BE FIRST)
st.set_page_config(
    page_title="Aadil's Research Intelligence Suite",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. PROFESSIONAL "NEON GLASS" UI STYLING
st.markdown("""
    <style>
    /* Import Modern Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    /* Global Theme Overrides */
    :root {
        --primary-neon: #00F2FF;
        --secondary-neon: #BD00FF;
        --bg-dark: #050A14;
        --glass-bg: rgba(255, 255, 255, 0.05);
        --glass-border: rgba(0, 242, 255, 0.3);
        --text-light: #EAEAEA;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: var(--text-light);
    }

    /* Main Background */
    .stApp {
        background: radial-gradient(ellipse at top, #131A2A, var(--bg-dark));
    }

    /* Glass Sidebar */
    section[data-testid="stSidebar"] {
        background-color: rgba(5, 10, 20, 0.85);
        backdrop-filter: blur(12px);
        border-right: 1px solid var(--glass-border);
    }

    /* Headers & Titles */
    h1, h2, h3 {
        color: white !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }
    h1 {
        background: linear-gradient(90deg, var(--primary-neon), white);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Custom "Glass Card" for Results */
    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 25px;
        margin-top: 20px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 40px rgba(0, 242, 255, 0.2);
        border-color: var(--primary-neon);
    }

    /* Neon Buttons */
    .stButton > button {
        background: transparent;
        border: 1px solid var(--primary-neon);
        color: var(--primary-neon);
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: rgba(0, 242, 255, 0.1);
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.4);
    }
    /* Primary Action Button (The Big One) */
    button[kind="primary"] {
        background: linear-gradient(135deg, var(--primary-neon), var(--secondary-neon)) !important;
        border: none !important;
        color: #000 !important;
        font-weight: 800 !important;
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.3);
    }
    button[kind="primary"]:hover {
        box-shadow: 0 0 30px rgba(0, 242, 255, 0.6);
        transform: scale(1.02);
    }

    /* Input Fields */
    .stTextInput > div > div > input {
        background-color: var(--glass-bg);
        border: 1px solid var(--glass-border);
        color: white;
        border-radius: 8px;
    }
    .stTextInput > div > div > input:focus {
        border-color: var(--primary-neon);
        box-shadow: 0 0 10px rgba(0, 242, 255, 0.2);
    }

    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .viewerBadge_container__1QSob {display: none;}

    /* Developer Badge Footer */
    .dev-footer {
        position: fixed;
        bottom: 20px;
        left: 20px;
        background: rgba(0,0,0,0.6);
        backdrop-filter: blur(5px);
        border: 1px solid var(--primary-neon);
        padding: 8px 15px;
        border-radius: 20px;
        font-size: 12px;
        color: var(--primary-neon);
        display: flex;
        align-items: center;
        z-index: 999;
    }
    .dev-icon { margin-right: 8px; font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)

# 3. API KEYS (SECURE FETCH)
# This looks for keys in .streamlit/secrets.toml (Local) or Streamlit Cloud Secrets (Online)
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
if "TAVILY_API_KEY" in st.secrets:
    os.environ["TAVILY_API_KEY"] = st.secrets["TAVILY_API_KEY"]
# 4. INITIALIZE AI BRAIN
try:
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.3)
    search_tool = TavilySearchResults(max_results=5)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
except Exception as e:
    st.error(f"System Initialization Error: {e}. Check your API Keys.")

# 5. SIDEBAR CONTROLS
with st.sidebar:
    # Custom Neon Title
    st.markdown("<h1>🧬 Research OS <span style='font-size: 14px; color: var(--primary-neon);'>v2.0</span></h1>", unsafe_allow_html=True)
    st.markdown("**Target:** M.Sc AI Full Scholarship 🇦🇪")
    st.divider()
    
    # NAVIGATION MENU
    mode = st.radio("SELECT MODULE:", 
        ["🕵️‍♂️ Faculty Headhunter", 
         "📄 Research Gap Finder", 
         "🎤 Defense Simulator"], label_visibility="collapsed")
    
    st.divider()
    st.info("💡 **Strategy:** Identify faculty -> Find research gaps -> Practice defense.")
    
    st.markdown("""
        <div class="dev-footer">
            <span class="dev-icon">🛡️</span> Verified Builder: <b>Aadil</b>
        </div>
    """, unsafe_allow_html=True)

# 6. APP LOGIC: MODE 1 - FIND PROFESSORS
if mode == "🕵️‍♂️ Faculty Headhunter":
    st.title("🕵️‍♂️ Faculty Headhunter")
    st.markdown("Deploy AI agents to scan university databases for your ideal supervisor.")
    
    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input("Research Domain:", "Autonomous AI Agents & Neuro-symbolic AI")
    with col2:
        uni = st.text_input("Target Institution:", "MBZUAI, Khalifa University")
        
    if st.button("Initiate Scan 🔎", type="primary", use_container_width=True):
        with st.status("🔄 Executing multi-hop search across faculty directories...", expanded=True):
            query = f"Find professors at {uni} working on {topic}. List names, labs, and recent papers."
            try:
                results = search_tool.invoke(query)
                summary_prompt = f"""
                Act as a PhD recruiter. Analyze these search results: {results}
                Task: List 3 high-value professor targets for the topic '{topic}' at '{uni}'.
                Format:
                ### [Professor Name]
                * **Lab/Focus:** [Specific technical focus]
                * **Intelligence:** [Why they are a match]
                """
                response = llm.invoke(summary_prompt)
                # Wrap result in glass card
                st.markdown(f'<div class="glass-card">{response.content}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Search connection failed: {e}")

# 7. APP LOGIC: MODE 2 - RESEARCH GAP FINDER
elif mode == "📄 Research Gap Finder":
    st.title("📄 Research Innovation Engine")
    st.markdown("Ingest academic papers to isolate methodological flaws and generate novel proposals.")
    
    # Initialize memory
    if "loaded_docs" not in st.session_state: st.session_state.loaded_docs = None
    if "paper_title" not in st.session_state: st.session_state.paper_title = ""

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("### Source Channel:")
        source_type = st.radio("Source:", ["ArXiv Database (Auto)", "Manual Upload (PDF)"], label_visibility="collapsed")
    with col2:
        if source_type == "ArXiv Database (Auto)":
            paper_topic = st.text_input("Paper Query / Author:", "Sanjay Singh Manipal Autonomous Vehicles")
            if st.button("📥 Fetch Data Stream", use_container_width=True):
                with st.spinner("Connecting to ArXiv API..."):
                    try:
                        loader = ArxivLoader(query=paper_topic, load_max_docs=1)
                        st.session_state.loaded_docs = loader.load()
                        st.session_state.paper_title = st.session_state.loaded_docs[0].metadata['Title']
                        st.success(f"Acquired: {st.session_state.paper_title}")
                    except Exception as e: st.error(f"Data Fetch Error: {e}")
        else:
            uploaded_file = st.file_uploader("Upload PDF Document", type="pdf")
            if uploaded_file:
                with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_path = tmp_file.name
                loader = PyPDFLoader(tmp_path)
                st.session_state.loaded_docs = loader.load()
                st.session_state.paper_title = uploaded_file.name
                st.success(f"Document Buffered: {uploaded_file.name}")

    if st.session_state.loaded_docs:
        st.divider()
        st.markdown(f"### 🎯 Target: *{st.session_state.paper_title}*")
        
        if st.button("🚀 GENERATE INNOVATION PITCH", type="primary", use_container_width=True):
            with st.spinner("Processing natural language... Analyzing methodology... Identifying gaps..."):
                # RAG Pipeline
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                splits = text_splitter.split_documents(st.session_state.loaded_docs)
                vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
                retriever = vectorstore.as_retriever()
                
                analysis_prompt = """
                Act as a Principal Investigator. Analyze the provided paper context.
                OUTPUT 3 DISTINCT SECTIONS inside a Markdown container:
                1. **🔬 Executive Summary (EL5):** The core contribution in plain English.
                2. **⚠️ Critical Limitation:** The single biggest technical flaw or missed opportunity.
                3. **💡 The Novel Proposal:** A specific, advanced technical improvement using modern AI (e.g., GNNs, Transformers, Neuro-symbolic).
                """
                retrieved_docs = retriever.invoke("limitations future work methodology")
                context = "\n\n".join([doc.page_content for doc in retrieved_docs])
                final_response = llm.invoke(f"Context: {context}\n\n{analysis_prompt}")
                
                # Display Pitch in Glass Card
                st.markdown(f'<div class="glass-card">{final_response.content}</div>', unsafe_allow_html=True)
                
                # Email Draft
                st.divider()
                st.subheader("📨 Outreach Protocol Draft")
                email_prompt = f"Draft a concise, high-impact email to the author proposing this innovation. Subject line included."
                email = llm.invoke(f"Pitch: {final_response.content}\n\n{email_prompt}")
                st.code(email.content, language="markdown")

# 8. APP LOGIC: MODE 3 - INTERVIEW SIMULATOR
elif mode == "🎤 Defense Simulator":
    st.title("🎤 Scholarship Defense Simulator")
    st.markdown("AI-driven mock interview committee to pressure-test your technical knowledge.")
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [{
            "role": "assistant", 
            "content": "Welcome, candidate. Your CGPA is noted, but what unique research capability do you bring to our lab that justifies full funding?"
        }]

    for msg in st.session_state.chat_history:
        role_style = "color: var(--primary-neon); font-weight: bold;" if msg["role"] == "assistant" else "color: white;"
        st.markdown(f'<div style="margin-bottom: 10px;"><span style="{role_style}">{msg["role"].upper()}:</span> {msg["content"]}</div>', unsafe_allow_html=True)
        
    user_ans = st.chat_input("Articulate your response...")
    
    if user_ans:
        st.session_state.chat_history.append({"role": "user", "content": user_ans})
        st.rerun()

    if st.session_state.chat_history[-1]["role"] == "user":
        with st.spinner("Committee is deliberating..."):
            judge_prompt = f"""
            You are a tough MBZUAI Professor. Candidate answered: "{st.session_state.chat_history[-1]['content']}"
            Task: 1. Critique the answer sharply. 2. Ask a deeper, harder technical follow-up question relevant to their answer.
            """
            ai_reply = llm.invoke([SystemMessage(content=judge_prompt)] + [HumanMessage(content=msg["content"]) for msg in st.session_state.chat_history if msg["role"] != "system"])
            st.session_state.chat_history.append({"role": "assistant", "content": ai_reply.content})
            st.rerun()