import streamlit as st
import requests
import tempfile
import os
import mimetypes

API_BASE_URL = "http://backend:8001"
  # Change if hosted remotely

st.set_page_config(page_title="Morning Market Brief", page_icon="📊")
st.title("📊 Morning Market Brief - Finance Assistant")
st.write("Ask your question or upload a voice recording to get market updates powered by AI.")

# -------------------- TEXT QUESTION -------------------- #
st.markdown("### 📝 Ask via Text")

question = st.text_input("Type your finance question:")

if st.button("Get Answer (Text)"):
    if not question.strip():
        st.error("❗ Please enter a question.")
    else:
        with st.spinner("⏳ Thinking..."):
            try:
                response = requests.post(f"{API_BASE_URL}/ask_llm", json={"question": question})
                response.raise_for_status()
                data = response.json()

                st.success("✅ Answer received!")
                st.write("**You asked:**", data["question"])
                st.write("**Answer:**", data["answer"])
            except Exception as e:
                st.error(f"❌ Error getting answer: {e}")

# -------------------- AUDIO UPLOAD -------------------- #
st.markdown("---")
st.markdown("### 🎤 Ask via Audio")
audio_file = st.file_uploader("Upload a recorded question (wav, mp3, m4a):", type=["wav", "mp3", "m4a"])

if audio_file is not None:
    if st.button("Get Answer (Audio)"):
        with st.spinner("⏳ Processing your audio..."):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.name)[1]) as tmp_file:
                    tmp_file.write(audio_file.read())
                    tmp_filename = tmp_file.name

                # Send to FastAPI
                with open(tmp_filename, "rb") as f:
                    files = {"file": (audio_file.name, f)}
                    response = requests.post(f"{API_BASE_URL}/ask_audio", files=files)
                    response.raise_for_status()
                    data = response.json()

                st.success("✅ Answer received!")
                st.write("**You asked:**", data["question"])
                st.write("**Answer:**", data["answer"])

                # Play generated answer audio
                audio_resp = requests.get(f"{API_BASE_URL}/audio/{data['answer_audio_file']}")
                if audio_resp.status_code == 200:
                    mime_type, _ = mimetypes.guess_type(data["answer_audio_file"])
                    st.audio(audio_resp.content, format=mime_type or "audio/mp3")
                else:
                    st.warning("⚠️ Could not fetch the answer audio.")
            except Exception as e:
                st.error(f"❌ Error: {e}")
            finally:
                if os.path.exists(tmp_filename):
                    os.remove(tmp_filename)
