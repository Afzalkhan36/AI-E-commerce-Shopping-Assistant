import streamlit as st
from chatbot import initialize_chatbot, get_chatbot_response
from intent_handler import get_intent_response


# -------------------------------------------------------------------------
# CHATBOT LOADER
# -------------------------------------------------------------------------

@st.cache_resource
def load_chatbot():
    """
    Loads and initializes the chatbot only once.

    Streamlit caches the initialized chatbot resources,
    so the dataset and TF-IDF model are not rebuilt on
    every user interaction.
    """
    return initialize_chatbot()


# -------------------------------------------------------------------------
# MAIN APPLICATION
# -------------------------------------------------------------------------

def main():
    """
    Main Streamlit application.
    """

    # -------------------------------------------------------------
    # PAGE CONFIGURATION
    # -------------------------------------------------------------
    st.set_page_config(
        page_title="AI E-commerce FAQ Chatbot",
        page_icon="🤖",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    # -------------------------------------------------------------
    # SESSION STATE INITIALIZATION
    # -------------------------------------------------------------
    # Initialize the list for conversation history if it does not exist
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # -------------------------------------------------------------
    # SIDEBAR
    # -------------------------------------------------------------
    with st.sidebar:
        st.title("🤖 Chatbot Menu")
        st.success("✅ Chatbot Ready")
        st.divider()

        # Project details display block
        st.markdown("### 📋 Project Information")
        st.markdown("**Project Name:** AI E-commerce FAQ Chatbot")
        st.markdown("**Technology:** Python, NLTK, TF-IDF, Cosine Similarity, Streamlit")
        st.markdown("**Dataset Size:** Loading...")
        st.markdown("**Developer:** Student Project")

        st.divider()

        # About information block
        st.markdown("### ℹ️ About")
        st.write("This chatbot answers e-commerce FAQs using Natural Language Processing and Machine Learning techniques.")

    # -------------------------------------------------------------
    # INITIALIZE CHATBOT (Runs only once because of caching)
    # -------------------------------------------------------------
    dataframe, vectorizer, tfidf_matrix = load_chatbot()

    # -------------------------------------------------------------
    # PAGE HEADER
    # -------------------------------------------------------------
    st.title("🛒 AI E-commerce FAQ Chatbot")

    st.markdown(
        """
Ask any **e-commerce-related question**.

This chatbot uses:

- **Natural Language Processing (NLP)**
- **TF-IDF Vectorization**
- **Cosine Similarity**

to find the most relevant FAQ answer.
"""
    )

    st.divider()

    st.info(
        """
    👋 Welcome!

    Ask any shopping-related question.

    Examples:

    • Where is my order?

    • How do I return a product?

    • What payment methods are accepted?

    • Tell me a joke 😊
    """
    )

    st.divider()

    # -------------------------------------------------------------
    # USER INPUT
    # -------------------------------------------------------------
    with st.form("chat_form", clear_on_submit=False):

        user_query = st.text_input(
            label="Ask your question",
            placeholder="Example: Where is my order?"
        )

        ask_button = st.form_submit_button("Ask")

    # -------------------------------------------------------------
    # BUTTON CLICK
    # -------------------------------------------------------------
    if ask_button and not user_query.strip():
        st.warning("Please enter a question before clicking Ask.")

    elif ask_button:

        # -------------------------------------------------------------
        # CHECK FOR GREETINGS / SMALL TALK / JOKES
        # -------------------------------------------------------------
        intent_response = get_intent_response(user_query)

        # -------------------------------------------------------------
        # INTENT RESPONSE FOUND
        # -------------------------------------------------------------
        if intent_response is not None:

            # Save intent conversation
            st.session_state.chat_history.append({
                "user": user_query,
                "bot": intent_response,
                "type": "intent",
                "score": None
            })

            st.subheader("💬 Response")
            st.success(intent_response)

        # -------------------------------------------------------------
        # OTHERWISE USE FAQ ENGINE
        # -------------------------------------------------------------
        else:

            response = get_chatbot_response(
                user_query=user_query,
                dataframe=dataframe,
                vectorizer=vectorizer,
                tfidf_matrix=tfidf_matrix
            )

            if response is None:
                st.error("Unable to process your question.")

            else:

                # Save FAQ conversation
                st.session_state.chat_history.append({
                    "user": user_query,
                    "bot": response["answer"],
                    "type": "faq",
                    "score": response["similarity_score"]
                })

                st.subheader("🤖 Chatbot Response")

                # -----------------------------
                # FALLBACK RESPONSE
                # -----------------------------
                if response["best_index"] is None:

                    st.warning(response["answer"])

                    st.write(
                        f"**📊 Similarity Score:** "
                        f"{response['similarity_score']:.4f}"
                    )

                # -----------------------------
                # MATCH FOUND
                # -----------------------------
                else:

                    st.write(
                        f"**📌 Matched FAQ:**\n\n"
                        f"{response['question']}"
                    )

                    st.write(
                        f"**📊 Similarity Score:** "
                        f"{response['similarity_score']:.4f}"
                    )

                    st.success(response["answer"])

    # -------------------------------------------------------------
    # DISPLAY CHAT HISTORY
    # -------------------------------------------------------------
    # Only render history if there is at least one stored message
    if st.session_state.chat_history:
        st.divider()
        st.subheader("💬 Chat History")

        # Action button to reset session state
        if st.button("🗑 Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

        # Display history from oldest to newest
        for chat in st.session_state.chat_history:

            st.markdown("### 👤 You")
            st.write(chat["user"])

            st.markdown("### 🤖 Bot")
            st.write(chat["bot"])

            # Show similarity score only for FAQ responses
            if chat["type"] == "faq":
                st.caption(
                    f"Similarity Score: {chat['score']:.4f}"
                )

            st.divider()
        # ---------- FOOTER ----------
        st.divider()

        st.caption(
            "Built using Python • NLTK • TF-IDF • Cosine Similarity • Streamlit"
        )


# -------------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------------

if __name__ == "__main__":
    main()