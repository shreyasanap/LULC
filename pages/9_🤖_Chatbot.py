import os
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

load_dotenv()

# add your API key in .env file
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
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        system_instruction="Assume you are a GIS expert. User can ask any doubt, and they can add images/text. You have to answer anything related to it.",
    )

    st.title("Ask Questions + Get Insights 🤖")

    # Session state for managing the uploaded image and file
    if 'uploaded_image' not in st.session_state:
        st.session_state.uploaded_image = None
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None

    # Radio button to select mode
    mode = st.radio("Select input mode:", ["Text Input", "Upload Image"])

    if mode == "Upload Image":
        # Upload image
        uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

        if uploaded_image is not None:
            # Display the image
            st.image(uploaded_image, caption='Uploaded Image.', use_column_width=True)

            # Convert image to bytes
            image_bytes = uploaded_image.read()
            st.session_state.uploaded_image = image_bytes

            # Add a submit button for processing the image
            if st.button("Submit"):
                try:
                    # Save the uploaded image temporarily
                    temp_path = "temp_uploaded_image.png"
                    image = Image.open(io.BytesIO(st.session_state.uploaded_image))
                    image.save(temp_path)

                    # Upload the image to Gemini
                    uploaded_file = genai.upload_file(temp_path, mime_type="image/png")
                    st.session_state.uploaded_file = uploaded_file
                    st.write(f"Uploaded file '{uploaded_file.display_name}' as: {uploaded_file.uri}")
                    st.write("You can now ask questions about the uploaded image.")
                except Exception as e:
                    st.error(f"An error occurred while processing the image: {e}")

        # Ask a question about the uploaded image
        if st.session_state.uploaded_file is not None:
            user_input = st.text_input("Type your question about the image:")

            if st.button("Get Response"):
                if user_input:
                    try:
                        chat_session = model.start_chat()

                        # Send the image and the user's question
                        uploaded_file = st.session_state.uploaded_file
                        chat_session.send_message({
                            "role": "user",
                            "parts": [uploaded_file]
                        })
                        
                        response = chat_session.send_message(user_input)
                        st.write("Model Response:")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
                else:
                    st.write("Please enter a query.")

    elif mode == "Text Input":
        user_input = st.text_input("Type your question:")

        if st.button("Get Response"):
            if user_input:
                try:
                    chat_session = model.start_chat()
                    response = chat_session.send_message(user_input)
                    st.write("Model Response:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"An error occurred: {e}")
            else:
                st.write("Please enter a query.")
