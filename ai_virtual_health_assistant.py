import streamlit as st
from openai import OpenAI
import time

# --- App Configuration ---
st.set_page_config(
    page_title="AI Virtual Health Assistant",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- System Prompt ---
SYSTEM_PROMPT = """
You are a professional and empathetic virtual health assistant. Your primary goal is to help users understand their health concerns better.

Follow this process strictly:
1.  Start by introducing yourself and asking the user about their symptoms or health concerns.
2.  Based on the user's initial input, ask relevant and necessary follow-up questions to gather more specific information. Ask one question at a time. Do not overwhelm the user.
3.  Continue this questioning process until you have sufficient information to form a preliminary assessment.
4.  Once you have gathered enough details, provide a structured response with the following sections:
    - **Probable Diagnosis:** List 1-3 possible conditions that might align with the symptoms. Use clear, simple language.
    - **Recommendation:** Clearly state whether a doctor's visit is necessary (e.g., "Immediate visit recommended," "Consult a doctor soon," or "Monitor symptoms at home for now").
    - **Lifestyle & Dietary Tips:** Provide actionable advice related to lifestyle (e.g., rest, exercise) and diet that could help alleviate the symptoms.
    - **Ayurvedic & Home Remedies:** Suggest simple, safe, and widely known Ayurvedic or home remedies that could offer relief.

**Crucial Safety Instructions:**
- **Always include a disclaimer:** Start and end every single response with a clear disclaimer: "I am an AI assistant and not a medical professional. This is not a substitute for professional medical advice. Please consult a doctor for an accurate diagnosis."
- **Never pretend to be a doctor.**
- **If symptoms sound severe (e.g., chest pain, difficulty breathing, severe bleeding), immediately advise the user to seek emergency medical help.**
"""

# --- UI Styling ---
st.markdown("""
<style>
    .stApp {
        background-color: #F0F2F6;
    }
    .stChatMessage {
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .st-emotion-cache-1c7y2kd {
        border-radius: 10px;
        border: 1px solid #E0E0E0;
    }
    .st-emotion-cache-janbn0 {
        border-radius: 0.5rem;
    }
    h1 {
        color: #1E3A8A; /* Dark Blue */
        text-align: center;
    }
    .disclaimer {
        font-size: 0.8rem;
        text-align: center;
        color: #666;
        background-color: #FFFBEB; /* Light Yellow */
        padding: 0.5rem;
        border-radius: 5px;
        border: 1px solid #FBBF24; /* Amber */
    }
</style>
""", unsafe_allow_html=True)


# --- Main App Title & Disclaimer ---
st.title("🩺 AI Virtual Health Assistant")

st.markdown(
    "<div class='disclaimer'><strong>Disclaimer:</strong> This is an AI-powered assistant and is not a substitute for professional medical advice. Always consult with a qualified healthcare provider for any health concerns.</div>",
    unsafe_allow_html=True
)

# --- Sidebar for API Key ---
with st.sidebar:
    st.header("Configuration")
    st.markdown("Please enter your OpenAI API key to begin.")
    api_key = st.text_input("OpenAI API Key", type="password", key="api_key_input")
    st.markdown("[Get your API key here](https://platform.openai.com/account/api-keys)")
    st.markdown("---")
    st.markdown("Built with [Streamlit](https://streamlit.io) & [OpenAI](https://openai.com)")

# --- Session State ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "I am an AI assistant and not a medical professional. This is not a substitute for professional medical advice. Please consult a doctor for an accurate diagnosis.\n\nHello! I'm your virtual health assistant. How are you feeling today? Please tell me about your symptoms."}
    ]

# --- Initialize OpenAI Client ---
def get_openai_client(key):
    try:
        return OpenAI(api_key=key)
    except Exception as e:
        st.error(f"Error initializing OpenAI client: {e}")
        return None

if not api_key:
    st.warning("Please enter your API key in the sidebar to start the chat.")
    st.stop()

client = get_openai_client(api_key)
if client is None:
    st.stop()

# --- Display Chat History ---
for message in st.session_state.chat_history:
    if message["role"] != "system":  # Hide system prompt
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- User Input ---
if prompt := st.chat_input("Describe your symptoms..."):
    # Add user message
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",  # You can change to gpt-4o or gpt-3.5-turbo
                    messages=st.session_state.chat_history,
                    temperature=0.7
                )
                full_response = response.choices[0].message.content

                # Save AI response
                st.session_state.chat_history.append({"role": "assistant", "content": full_response})

                # Typing effect
                message_placeholder = st.empty()
                display_text = ""
                for char in full_response:
                    display_text += char
                    message_placeholder.markdown(display_text + "▌")
                    time.sleep(0.01)
                message_placeholder.markdown(full_response)

            except Exception as e:
                st.error(f"An error occurred: {e}")
