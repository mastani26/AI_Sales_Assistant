import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Sentiment Analyzer", layout="wide")

# Session state for history
if "history" not in st.session_state:
    st.session_state["history"] = []

st.title("🎤 Voice & Text Sentiment Analyzer")

# Input section
tab1, tab2 = st.tabs(["💬 Text Input", "🎙️ Audio Upload"])

with tab1:
    user_text = st.text_area("Enter text to analyze")
    if st.button("Analyze Text"):
        if user_text.strip():
            response = requests.post(f"{API_URL}/analyze-text", json={"text": user_text})
            result = response.json()

            st.subheader("Analysis Results")
            st.write(f"**Transcript:** {result['text']}")
            st.write(f"**Sentiment:** {result['sentiment']}")
            st.write(f"**Tone:** {result['explanation']}")

            # Save to history
            st.session_state["history"].append(result)
        else:
            st.warning("Please enter some text.")

with tab2:
    uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "webm"])
    if uploaded_file and st.button("Analyze Audio"):
        files = {"file": uploaded_file.getvalue()}
        response = requests.post(f"{API_URL}/analyze-audio", files={"file": (uploaded_file.name, uploaded_file, "audio/webm")})
        result = response.json()

        st.subheader("Analysis Results")
        st.write(f"**Transcript:** {result['text']}")
        st.write(f"**Sentiment:** {result['sentiment']}")
        st.write(f"**Tone:** {result['explanation']}")

        # Save to history
        st.session_state["history"].append(result)

# Sidebar for history and analytics
st.sidebar.header("📜 Conversation History")
for item in st.session_state["history"]:
    st.sidebar.write(f"\"{item['text']}\" → Sentiment: {item['sentiment']} | Tone: {item['explanation']}")

# Analytics Tab
st.subheader("📊 Analytics")

if st.session_state["history"]:
    df = pd.DataFrame(st.session_state["history"])
    col1, col2 = st.columns(2)

    with col1:
        st.bar_chart(df["sentiment"].value_counts())

    with col2:
        st.write("### Sentiment Distribution")
        st.dataframe(df[["text", "sentiment", "explanation"]])
else:
    st.info("No analysis yet. Start by entering text or uploading audio.")
