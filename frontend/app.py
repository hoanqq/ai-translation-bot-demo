import streamlit as st
import requests

# Streamlit app
st.title("AI Translation Bot")

# Language options
languages = ["English", "Spanish", "Chinese", "Japanese"]

# Language selection
source_language = st.selectbox("Select source language", languages)
target_language = st.selectbox("Select target language", languages)

# Text input
text = st.text_area("Enter text to translate")

# Translation button
if st.button("Translate"):
    response = requests.post(
        "http://localhost:8000/translate/",
        json={"text": text, "source_language": source_language, "target_language": target_language},
    )
    if response.status_code == 200:
        translated_text = response.json().get("translated_text")
        st.success("Translation successful!")
        st.text_area("Translated text", translated_text)
    else:
        st.error("Translation failed!")

# Feedback buttons
if st.button("Thumbs Up"):
    st.success("Thank you for your feedback!")
    requests.post("http://localhost:8000/feedback/", json={"translation_id": "some_id", "feedback": "thumbs_up"})

if st.button("Thumbs Down"):
    st.error("Thank you for your feedback!")
    requests.post("http://localhost:8000/feedback/", json={"translation_id": "some_id", "feedback": "thumbs_down"})
