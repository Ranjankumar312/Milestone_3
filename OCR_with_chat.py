

import streamlit as st
import requests
import json
from PIL import Image
import pytesseract

# ------------------- CONFIG -------------------
st.set_page_config(page_title="OCR Chatbot (Ollama)", layout="wide")

OLLAMA_URL = "http://localhost:11434/api/generate"  
OLLAMA_MODEL = "llama3.2:1b" 

# ------------------- SESSION STATE -------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ------------------- HELPER FUNCTION -------------------
def get_ollama_response(user_input):
    """Send user query to Ollama and return the reply"""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"You are a helpful assistant.\n\nUser: {user_input}\nAssistant:"
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=120)
        output = ""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode("utf-8"))
                    if "response" in data:
                        output += data["response"]
                except Exception:
                    continue
        return output if output else "⚠️ No response from Ollama"
    except Exception as e:
        return f"⚠️ Request failed: {e}"

# ------------------- SIDEBAR -------------------
with st.sidebar:
    st.markdown("### ⚡ Chat_bot")

    if st.button("📝 New chat"):
        if st.session_state.messages:
            # Save the current chat to history
            st.session_state.chat_history.append(st.session_state.messages.copy())
        st.session_state.messages = []
        st.experimental_rerun()

    st.button("🔍 Search chats")
    st.button("⚙️ Settings ")

    st.markdown("---")
    st.subheader("Previous Chats")
    if st.session_state.chat_history:
        for i, chat in enumerate(st.session_state.chat_history):
            if st.button(f"💬 Chat {i+1}", key=f"history_{i}"):
                # Load the selected chat into current messages
                st.session_state.messages = chat.copy()
                st.experimental_rerun()
    else:
        st.caption("No previous chats yet...")

# ------------------- MAIN CHAT WINDOW -------------------
st.title("💬 OCR + Chatbot (Ollama)")

# Display previous messages in the chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ------------------- OCR Upload Section -------------------
uploaded_file = st.file_uploader("📤 Upload an image for OCR", type=["png", "jpg", "jpeg"])
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Extract text using Tesseract
    extracted_text = pytesseract.image_to_string(image)
    st.text_area("📝 Extracted Text", extracted_text, height=300)  # Large text area

    if st.button("Send Extracted Text to Chatbot"):
        st.session_state.messages.append({"role": "user", "content": extracted_text})
        with st.chat_message("user"):
            st.markdown(extracted_text)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                reply = get_ollama_response(extracted_text)
                st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})

# ------------------- CHAT INPUT -------------------
if prompt := st.chat_input("Type your question..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # ------------------- BOT RESPONSE -------------------
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = get_ollama_response(prompt)
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
