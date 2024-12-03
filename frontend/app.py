import streamlit as st
import requests

# Define the language map
LANGUAGE_MAP = {
    'English': 'en',
    'Spanish': 'es',
    'French': 'fr',
    'German': 'de',
    'Japanese': 'ja',
    # Add more languages as needed
}

# Streamlit app
st.title("AI Translation Bot")

# Language options
source_text = st.text_area("Enter text to translate")
source_language = st.selectbox("Source Language", list(LANGUAGE_MAP.keys()))
target_language = st.selectbox("Target Language", list(LANGUAGE_MAP.keys()))


# Translation button
if st.button("Translate"):
    payload = {
        "source_text": source_text,
        "source_language": LANGUAGE_MAP[source_language],
        "target_language": LANGUAGE_MAP[target_language]
    }

    response = requests.post("http://localhost:8000/translate", json=payload)

    if response.status_code == 200:
        data = response.json()
        st.success("Translation successful!")
        st.text_area("Translated text", data['target_text'])
    else:
        st.error("Translation failed")

# Feedback buttons
# if st.button("Thumbs Up"):
#     st.success("Thank you for your feedback!")
#     requests.post("http://localhost:8000/feedback",
#                   json={"translation_id": "some_id", "feedback": "thumbs_up"})

# if st.button("Thumbs Down"):
#     st.error("Thank you for your feedback!")
#     requests.post("http://localhost:8000/feedback/",
#                   json={"translation_id": "some_id", "feedback": "thumbs_down"})
