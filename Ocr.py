
import streamlit as st
from PIL import Image
import pytesseract
import ollama

# 🔹 Path to Tesseract (adjust if installed elsewhere)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Page setup
st.set_page_config(page_title="OCR Chatbot", page_icon="🤖", layout="wide")

# Initialize State

if "sessions" not in st.session_state:
    st.session_state.sessions = {"Default": {"messages": [], "ocr_text": ""}}
if "current_session" not in st.session_state:
    st.session_state.current_session = "Default"


# Sidebar - Manage Sessions

with st.sidebar:
    st.title("🗂️ Chat Sessions")

    # Create new session
    new_session = st.text_input("➕ New Session Name")
    if st.button("Create Session") and new_session.strip():
        if new_session not in st.session_state.sessions:
            st.session_state.sessions[new_session] = {"messages": [], "ocr_text": ""}
        st.session_state.current_session = new_session
        st.rerun()  # ✅ Updated for new Streamlit

  
    # Reset button (clear current session only)
    if st.button("🗑️ Clear Current Session"):
        st.session_state.sessions[st.session_state.current_session] = {"messages": [], "ocr_text": ""}
        st.rerun()  # ✅ Updated for new Streamlit

# Refresh session reference
session = st.session_state.sessions[st.session_state.current_session]

# Main UI

st.markdown(
    f"""
    <div style="text-align:center;">
        <h1>🤖 OCR </h1>
        <p style="font-size:18px;">Upload images anytime and chat continuously without refreshing!</p>
        <p style="color:gray;">Current Session: <b>{st.session_state.current_session}</b></p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Layout: Image + OCR text
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📂 Upload Image")
    uploaded_file = st.file_uploader("Choose a JPG/PNG", type=["jpg", "jpeg", "png"], key="uploader")

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        # Run OCR and save text
        text = pytesseract.image_to_string(image).strip()
        if text:
            session["ocr_text"] = text
            st.success("✅ OCR Completed (added to memory)")
        else:
            st.warning("⚠️ No text detected")

with col2:
    if session["ocr_text"]:
        st.subheader("📄 Extracted Text (Editable)")
        session["ocr_text"] = st.text_area(
            "Text from OCR",
            session["ocr_text"],
            height=400,
            key="ocr_display"
        )

# Chat Input + Ollama Response

user_input = st.chat_input("💬 Ask something...")

if user_input:
    session["messages"].append({"role": "user", "content": user_input})

    # Build context
    conversation = []
    if session["ocr_text"]:
        conversation.append({"role": "system", "content": f"Extracted text: {session['ocr_text']}"})
    conversation.extend(session["messages"])

    # Call Ollama
    response = ollama.chat(model="llama2", messages=conversation)
    bot_reply = response["message"]["content"]

    session["messages"].append({"role": "assistant", "content": bot_reply})

# Chat History

st.markdown("---")
st.subheader("💬 Conversation")

for msg in session["messages"]:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(msg["content"])
