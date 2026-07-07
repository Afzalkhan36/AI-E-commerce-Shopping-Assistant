import time
import html
import random
import streamlit as st
from chatbot import initialize_chatbot, get_chatbot_response, DEFAULT_SIMILARITY_THRESHOLD
from intent_handler import get_intent_response


# -------------------------------------------------------------------------
# CHATBOT LOADER (CACHED)
# -------------------------------------------------------------------------

@st.cache_resource
def load_chatbot():
    """
    Loads and initializes the chatbot only once.
    """
    return initialize_chatbot()


# -------------------------------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------------------------------

def sync_current_chat():
    """
    Syncs the active chat session history to the list of saved chats.
    """
    if not st.session_state.chat_history:
        return
    
    if st.session_state.current_chat_id is None:
        st.session_state.current_chat_id = str(time.time())
        
    # Get title from the first question in the thread
    first_q = st.session_state.chat_history[0]["content"]
    title = first_q.strip()
    if len(title) > 25:
        title = title[:25] + "..."
        
    found = False
    for chat in st.session_state.saved_chats:
        if chat["id"] == st.session_state.current_chat_id:
            chat["history"] = st.session_state.chat_history
            chat["title"] = title
            chat["timestamp"] = time.time()
            found = True
            break
            
    if not found:
        st.session_state.saved_chats.append({
            "id": st.session_state.current_chat_id,
            "title": title,
            "history": st.session_state.chat_history,
            "timestamp": time.time()
        })


def get_grouped_chats():
    """
    Groups saved chats by recency (Today, Yesterday, and Previous Chats).
    """
    now = time.time()
    today = []
    yesterday = []
    previous = []
    
    sorted_chats = sorted(st.session_state.saved_chats, key=lambda x: x["timestamp"], reverse=True)
    
    for chat in sorted_chats:
        diff_sec = now - chat["timestamp"]
        diff_days = diff_sec / 86400.0
        
        if diff_days < 1.0:
            today.append(chat)
        elif diff_days < 2.0:
            yesterday.append(chat)
        else:
            previous.append(chat)
            
    return today, yesterday, previous


def get_follow_up_suggestions(dataframe, current_question=None):
    """
    Returns 2 or 3 follow-up questions from the dataframe that are not the current question.
    """
    questions = dataframe["Question"].tolist()
    # Filter out empty or "Who are you?"
    questions = [q for q in questions if q.strip() and q != "Who are you?"]
    
    if current_question in questions:
        questions.remove(current_question)
        
    random.seed(int(time.time()))
    count = min(3, len(questions))
    return random.sample(questions, count)


# -------------------------------------------------------------------------
# MAIN STREAMLIT APPLICATION
# -------------------------------------------------------------------------

def main():
    # 1. Page Configuration
    st.set_page_config(
        page_title="AI E-commerce Shopping Assistant",
        page_icon="🛍️",
        layout="centered",
        initial_sidebar_state="expanded"
    )

    # 2. Premium CSS Styling (Strictly abiding by rules)
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Main page configuration & radial background */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #0F172A, #020617) !important;
        font-family: 'Inter', sans-serif !important;
        color: #F8FAFC !important;
    }

    h1, h2, h3, h4, h5, h6, p, label, input {
        font-family: 'Inter', sans-serif !important;
    }

    /* Hide standard Streamlit main menu and footer */
    #MainMenu, footer {
        visibility: hidden !important;
        height: 0 !important;
    }

    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 800px !important;
    }

    /* Custom Scrollbars */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.15);
    }

    /* Sidebar Custom Styling */
    section[data-testid="stSidebar"] {
        background-color: #020617 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
        padding-top: 1rem !important;
    }

    .sidebar-header {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 16px 20px 16px;
    }

    .sidebar-logo {
        font-size: 1.5rem;
    }

    .sidebar-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.01em;
    }

    .sidebar-group-title {
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        color: #475569 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        margin-top: 24px !important;
        margin-bottom: 10px !important;
        padding-left: 12px !important;
    }

    /* Styled Marker Elements & Sibling Selectors for Buttons */

    /* New Chat Button Styling */
    div.new-chat-btn-marker + div[data-testid="stButton"] button {
        background: linear-gradient(135deg, #3B82F6, #1D4ED8) !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        padding: 12px !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15) !important;
        transition: all 0.25s ease-in-out !important;
        width: 100% !important;
    }
    div.new-chat-btn-marker + div[data-testid="stButton"] button:hover {
        background: linear-gradient(135deg, #2563EB, #1E40AF) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.25) !important;
    }

    /* Clear Chats Button Styling */
    div.clear-chats-btn-marker + div[data-testid="stButton"] button {
        background-color: rgba(239, 68, 68, 0.05) !important;
        color: #FCA5A5 !important;
        border: 1px solid rgba(239, 68, 68, 0.15) !important;
        border-radius: 12px !important;
        padding: 10px !important;
        transition: all 0.25s ease !important;
        width: 100% !important;
    }
    div.clear-chats-btn-marker + div[data-testid="stButton"] button:hover {
        background-color: rgba(239, 68, 68, 0.15) !important;
        border-color: #EF4444 !important;
        color: #FFFFFF !important;
    }

    /* Active History Item Styling */
    div.active-chat-btn-marker + div[data-testid="stButton"] button {
        background-color: rgba(59, 130, 246, 0.08) !important;
        color: #3B82F6 !important;
        border: 1px solid rgba(59, 130, 246, 0.2) !important;
        border-radius: 10px !important;
        padding: 8px 12px !important;
        text-align: left !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        justify-content: flex-start !important;
        width: 100% !important;
    }

    /* Standard History Item Styling */
    div.history-chat-btn-marker + div[data-testid="stButton"] button {
        background-color: transparent !important;
        color: #94A3B8 !important;
        border: 1px solid transparent !important;
        border-radius: 10px !important;
        padding: 8px 12px !important;
        text-align: left !important;
        font-size: 0.9rem !important;
        justify-content: flex-start !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }
    div.history-chat-btn-marker + div[data-testid="stButton"] button:hover {
        background-color: rgba(255, 255, 255, 0.04) !important;
        color: #F8FAFC !important;
    }

    /* Force left alignment on sidebar button texts */
    section[data-testid="stSidebar"] button p {
        text-align: left !important;
        justify-content: flex-start !important;
        width: 100% !important;
    }
    section[data-testid="stSidebar"] button {
        justify-content: flex-start !important;
    }

    /* Main Hero Header Styling */
    .hero-section {
        text-align: center;
        padding: 24px 0 16px 0;
    }

    .hero-title {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        letter-spacing: -0.03em !important;
        margin-bottom: 8px !important;
    }

    .hero-subtitle {
        font-size: 1.05rem !important;
        color: #94A3B8 !important;
        max-width: 600px;
        margin: 0 auto 16px auto !important;
        line-height: 1.5 !important;
    }

    /* Welcome Card Styling */
    .welcome-card {
        background-color: #111827 !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 16px !important;
        padding: 28px !important;
        text-align: center;
        max-width: 600px;
        margin: 24px auto !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3) !important;
    }

    .welcome-hand {
        font-size: 2.8rem;
        margin-bottom: 12px;
        display: inline-block;
        animation: wave 1.8s infinite ease-in-out;
        transform-origin: 70% 70%;
    }

    @keyframes wave {
        0%, 100% { transform: rotate(0deg); }
        50% { transform: rotate(12deg); }
    }

    .welcome-header {
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        margin-bottom: 6px !important;
    }

    .welcome-text {
        font-size: 0.95rem !important;
        color: #94A3B8 !important;
        margin: 0 !important;
    }

    /* Chat Input Styling */
    div[data-testid="stChatInput"] {
        background-color: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
    }

    textarea[data-testid="stChatInputTextArea"] {
        color: #F1F5F9 !important;
    }

    button[data-testid="stChatInputSubmitButton"] {
        background-color: #3B82F6 !important;
        border-radius: 10px !important;
        color: #FFFFFF !important;
        transition: all 0.2s ease !important;
    }
    button[data-testid="stChatInputSubmitButton"]:hover {
        background-color: #2563EB !important;
    }

    /* NATIVE CHAT MESSAGE OVERRIDES (NO BOXES INSIDE BOXES) */

    /* Force transparency and eliminate default border/shadows on stChatMessage */
    div[data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        padding: 8px 0 !important;
        margin-bottom: 12px !important;
        box-shadow: none !important;
    }

    /* Styling User Messages specifically (Right-Aligned Bubble) */
    div[class*="st-key-user_container"] div[data-testid="stChatMessage"] {
        flex-direction: row-reverse !important;
    }
    div[class*="st-key-user_container"] div[data-testid="stChatMessageContent"] {
        background-color: #3B82F6 !important;
        color: #FFFFFF !important;
        padding: 12px 18px !important;
        border-radius: 16px 16px 4px 16px !important;
        margin-right: 12px !important;
        margin-left: auto !important;
        max-width: 75% !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15) !important;
    }
    div[class*="st-key-user_container"] div[data-testid="stChatMessageContent"] p {
        color: #FFFFFF !important;
    }

    /* Styling Assistant Messages specifically (Left-Aligned Dark Bubble) */
    div[class*="st-key-assistant_container"] div[data-testid="stChatMessageContent"] {
        background-color: #111827 !important;
        color: #F8FAFC !important;
        padding: 14px 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px 16px 16px 4px !important;
        margin-left: 12px !important;
        max-width: 75% !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    }
    div[class*="st-key-assistant_container"] div[data-testid="stChatMessageContent"] p {
        color: #F8FAFC !important;
    }

    .followup-section-title {
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        color: #475569 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        margin-top: 16px !important;
        margin-bottom: 8px !important;
        padding-left: 4px !important;
    }

    /* Suggestion Grid Button Styling for Follow-ups */
    div.suggestion-row + div[data-testid="stHorizontalBlock"] button {
        background-color: #111827 !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 12px !important;
        padding: 8px 12px !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        color: #E2E8F0 !important;
        text-align: center !important;
        justify-content: center !important;
        transition: all 0.2s ease-in-out !important;
        width: 100% !important;
    }
    div.suggestion-row + div[data-testid="stHorizontalBlock"] button:hover {
        background-color: rgba(59, 130, 246, 0.08) !important;
        border-color: #3B82F6 !important;
        color: #3B82F6 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # 3. Session State Initialization
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        
    if "saved_chats" not in st.session_state or not isinstance(st.session_state.saved_chats, list):
        st.session_state.saved_chats = []

    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = None

    if "prompt_to_submit" not in st.session_state:
        st.session_state.prompt_to_submit = None

    # 4. Initialize Chatbot Backend
    dataframe, vectorizer, tfidf_matrix = load_chatbot()

    # 5. Sidebar Layout
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <span class="sidebar-logo">🛍️</span>
            <span class="sidebar-title">Shopping Assistant</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Action: New Chat Thread
        st.markdown("<div class='new-chat-btn-marker'></div>", unsafe_allow_html=True)
        if st.button("➕ New Chat", key="new_chat_btn", use_container_width=True):
            if st.session_state.chat_history:
                sync_current_chat()
            st.session_state.chat_history = []
            st.session_state.current_chat_id = None
            st.rerun()
        
        st.divider()
        
        # Load and render saved threads grouped by recency
        today_chats, yesterday_chats, previous_chats = get_grouped_chats()
        
        has_history = False
        
        if today_chats:
            has_history = True
            st.markdown("<div class='sidebar-group-title'>Today's Chats</div>", unsafe_allow_html=True)
            for chat in today_chats:
                is_active = (chat["id"] == st.session_state.current_chat_id)
                if is_active:
                    st.markdown("<div class='active-chat-btn-marker'></div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='history-chat-btn-marker'></div>", unsafe_allow_html=True)
                if st.button(f"💬 {chat['title']}", key=f"chat_{chat['id']}", use_container_width=True):
                    st.session_state.chat_history = chat["history"]
                    st.session_state.current_chat_id = chat["id"]
                    st.rerun()
                    
        if yesterday_chats:
            has_history = True
            st.markdown("<div class='sidebar-group-title'>Yesterday</div>", unsafe_allow_html=True)
            for chat in yesterday_chats:
                is_active = (chat["id"] == st.session_state.current_chat_id)
                if is_active:
                    st.markdown("<div class='active-chat-btn-marker'></div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='history-chat-btn-marker'></div>", unsafe_allow_html=True)
                if st.button(f"💬 {chat['title']}", key=f"chat_{chat['id']}", use_container_width=True):
                    st.session_state.chat_history = chat["history"]
                    st.session_state.current_chat_id = chat["id"]
                    st.rerun()
                    
        if previous_chats:
            has_history = True
            st.markdown("<div class='sidebar-group-title'>Previous Chats</div>", unsafe_allow_html=True)
            for chat in previous_chats:
                is_active = (chat["id"] == st.session_state.current_chat_id)
                if is_active:
                    st.markdown("<div class='active-chat-btn-marker'></div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='history-chat-btn-marker'></div>", unsafe_allow_html=True)
                if st.button(f"💬 {chat['title']}", key=f"chat_{chat['id']}", use_container_width=True):
                    st.session_state.chat_history = chat["history"]
                    st.session_state.current_chat_id = chat["id"]
                    st.rerun()
                    
        if not has_history:
            st.caption("No conversation history")
            
        st.divider()
        st.markdown("<div class='clear-chats-btn-marker'></div>", unsafe_allow_html=True)
        if st.button("🗑 Clear All Chats", key="clear_all_btn", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.saved_chats = []
            st.session_state.current_chat_id = None
            st.rerun()

    # 6. Main Header Layout
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">AI E-commerce Shopping Assistant</h1>
        <p class="hero-subtitle">Get instant answers about orders, returns, refunds, shipping and payments.</p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    # 7. Render Active Conversation History Thread
    for idx, chat in enumerate(st.session_state.chat_history):
        role = chat["role"]
        with st.container(key=f"{role}_container_{idx}"):
            with st.chat_message(role, avatar="👤" if role == "user" else "🤖"):
                st.markdown(chat["content"])

    # 8. Generation Loop (If the last message is a new user prompt)
    if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
        user_query = st.session_state.chat_history[-1]["content"]
        
        with st.container(key=f"assistant_container_{len(st.session_state.chat_history)}"):
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Thinking..."):
                    time.sleep(0.8) # Natural thinking delay for smooth feel
                    
                    # Retrieve answer from backend
                    intent_response = get_intent_response(user_query)
                    
                    if intent_response is not None:
                        bot_entry = {
                            "role": "assistant",
                            "content": intent_response,
                            "type": "intent",
                            "score": None,
                            "matched_question": None,
                            "best_index": None
                        }
                    else:
                        response = get_chatbot_response(
                            user_query=user_query,
                            dataframe=dataframe,
                            vectorizer=vectorizer,
                            tfidf_matrix=tfidf_matrix
                        )
                        if response is not None:
                            bot_entry = {
                                "role": "assistant",
                                "content": response["answer"],
                                "type": "faq",
                                "score": response["similarity_score"],
                                "matched_question": response.get("question"),
                                "best_index": response.get("best_index")
                            }
                        else:
                            bot_entry = {
                                "role": "assistant",
                                "content": "Sorry, I couldn't process that question.",
                                "type": "error",
                                "score": None,
                                "matched_question": None,
                                "best_index": None
                            }
                
                # Render answer content
                st.markdown(bot_entry["content"])
                    
        st.session_state.chat_history.append(bot_entry)
        sync_current_chat()
        st.rerun()

    # 8. Follow-up Suggestions (rendered after bot responses)
    if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "assistant":
        last_chat = st.session_state.chat_history[-1]
        current_question = last_chat.get("matched_question")
        suggestions = get_follow_up_suggestions(dataframe, current_question)
        
        if suggestions:
            st.markdown("<div class='followup-section-title'>Suggested Follow-ups</div>", unsafe_allow_html=True)
            st.markdown("<div class='suggestion-row'></div>", unsafe_allow_html=True)
            cols = st.columns(len(suggestions))
            for i, question in enumerate(suggestions):
                with cols[i]:
                    if st.button(f"🔍 {question}", key=f"followup_{i}", use_container_width=True):
                        st.session_state.prompt_to_submit = question
                        st.rerun()

    # 9. Welcome Onboarding Screen (rendered when active thread has no logs)
    if not st.session_state.chat_history:
        st.markdown("""
        <div class="welcome-card">
            <div class="welcome-hand">👋</div>
            <h2 class="welcome-header">Hello!</h2>
            <p class="welcome-text">How can I help today?</p>
        </div>
        """, unsafe_allow_html=True)

    # 10. Native Bottom Input Area (using st.chat_input)
    prompt = None
    if "prompt_to_submit" in st.session_state and st.session_state.prompt_to_submit:
        prompt = st.session_state.prompt_to_submit
        st.session_state.prompt_to_submit = None
    else:
        prompt = st.chat_input("Ask anything about your shopping...")

    if prompt:
        # Append User query thread log
        st.session_state.chat_history.append({
            "role": "user",
            "content": prompt
        })
        sync_current_chat()
        st.rerun()


# -------------------------------------------------------------------------
# MAIN ENTRYPOINT
# -------------------------------------------------------------------------

if __name__ == "__main__":
    main()
