import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage

# 1. PAGE CONFIGURATION (Updated for All Degrees)
st.set_page_config(
    page_title="UAE Universal Scholarship Hunter", # New Powerful Name
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.linkedin.com/in/aadil',
        'About': "The First AI Agent dedicated to finding Scholarships for Bachelors, Masters, and PhD in the UAE."
    }
)

# 2. HIDE STREAMLIT BRANDING (The "Make it Mine" CSS Hack)
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stApp {
                background-color: #0E1117; /* Professional Dark Mode */
            }
            /* Add a custom footer with YOUR name */
            .custom-footer {
                position: fixed;
                bottom: 0;
                width: 100%;
                background-color: #262730;
                color: white;
                text-align: center;
                padding: 10px;
                font-size: 14px;
                z-index: 999;
            }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.markdown('<div class="custom-footer">Built by Aadil | UAE Scholarship Intelligence</div>', unsafe_allow_html=True)

# 3. SIDEBAR WITH DEVELOPER INFO (SEO Booster)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712009.png", width=100) # Graduation Icon
    st.title("👨‍💻 Developer: Aadil")
    st.markdown("""
    **Status:** Final Year AI Student  
    **Goal:** Master's in UAE (2026 Intake)  
    **Specialization:** Autonomous Agents
    
    ---
    **About this App:**
    This agent searches **Live Admission Data** from top UAE universities.
    It ignores general blogs and focuses on:
    * Full Scholarships
    * Application Deadlines
    * Research Assistantships
    """)
    if st.button("Clear Conversation"):
        st.session_state.chat_history = []
        st.rerun()

# 4. LOAD API KEYS (Secure)
# Try loading from local .env file first (for your laptop)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Check for secrets (for Streamlit Cloud)
if "GROQ_API_KEY" not in os.environ and "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
if "TAVILY_API_KEY" not in os.environ and "TAVILY_API_KEY" in st.secrets:
    os.environ["TAVILY_API_KEY"] = st.secrets["TAVILY_API_KEY"]

# 5. SETUP THE SPECIALIST BRAIN (The "UAE Admission Officer")
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
search_tool = TavilySearchResults(max_results=5) # increased to 5 for deeper research

# UPDATE THIS SYSTEM PROMPT IN YOUR CODE
system_prompt = """
You are Aadil's 'Universal UAE Scholarship Hunter' Agent. 
Your GOAL is to help ANY student (High School, Graduate, or Researcher) find scholarships and admission in the UAE.

SCOPE OF WORK:
You must handle queries for:
1. **Undergraduate (Bachelors):** Look for "Merit Scholarships", "High School Leaver Discounts", "Chancellor's Scholarship".
2. **Postgraduate (Masters & PhD):** Look for "Research Assistantships", "Tuition Waivers", "Teaching Assistantships".
3. **General Admission:** Look for "Application Deadlines", "Required Documents", "IELTS/TOEFL Scores", "Visa Process".

STRICT SEARCH RULES:
- SEARCH official university domains (.ac.ae, .edu) FIRST.
- IF the user does not specify their degree (e.g., "Find me a scholarship"), ASK THEM: "Are you looking for Bachelors, Masters, or PhD?"
- ALWAYS extract:
   * Exact Deadline Dates (e.g., "June 30, 2026")
   * Minimum Grades/CGPA needed (e.g., "90% in High School" or "3.0 CGPA")
   * Direct Application Links (if available)

You are an expert consultant. If a student asks "How do I apply?", give them a step-by-step list:
1. Prepare Documents (Transcripts, Passport, Photo).
2. Take English Test (IELTS/TOEFL).
3. Apply via [University Link].
4. Pay Application Fee.

Refuse to answer non-education topics (cooking, games, etc).
"""

# Create the Agent
agent = create_react_agent(llm, [search_tool])

# 6. MAIN CHAT INTERFACE
st.title("🎓 Aadil's Scholarship Hunter")
st.caption("Tracking Full Funding & Deadlines for UAE Universities (Live Data)")

# Memory Setup
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display History
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle User Input
user_input = st.chat_input("Ask about scholarships (e.g., 'MBZUAI deadlines for 2026')...")

if user_input:
    # Add user message to memory
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Generate Response
    with st.chat_message("assistant"):
        with st.status("🔍 Searching University Databases...", expanded=True):
            
            # NEW LOGIC: Combine System Prompt + Chat History
            messages = [SystemMessage(content=system_prompt)] + st.session_state.chat_history
            
            # Send the combined list
            response = agent.invoke({"messages": messages})
            
            st.write("✅ Found relevant data.")
        # Display Final Answer
        st.markdown(response["messages"][-1].content)
        
        # Add AI message to memory
        st.session_state.chat_history.append({"role": "assistant", "content": response["messages"][-1].content})