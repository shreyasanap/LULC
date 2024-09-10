import os
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if api_key is None:
    st.error("API key is not set in the environment.")
else:
    # Configure the Generative AI client
    genai.configure(api_key=api_key)

    # Create the model
    generation_config = {
        "temperature": 2,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )

   
    st.title("Ask Any Questions/Doubt here 🤖")

   
    user_input = st.text_input("")
    if st.button("Get Response"):
        if user_input:
            try:
                chat_session = model.start_chat()
                response = chat_session.send_message(user_input)
                st.write(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.write("Please enter a query.")
