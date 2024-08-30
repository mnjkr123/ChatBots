import os
from dotenv import load_dotenv
import streamlit as st
from pathlib import Path
from streamlit_chat import message
from langchain.llms import HuggingFaceEndpoint
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationSummaryMemory

# Load environment variables from .env file
load_dotenv()

# Set up the Huggingface API token
API_Key = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# Setting page title and header
st.set_page_config(page_title="Chat GPT Clone", page_icon=":robot_face:")
st.markdown(
    """
    <h2 style='text-align: center; margin-top: 2px;'>How can I assist you?</h2>
    """,
    unsafe_allow_html=True
)
st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)

# Custom CSS for styling
st.markdown("""
    <style>
        .css-1d391kg { /* Sidebar container */
            background-color: #0033a0; /* Blue background color for sidebar */
            color: white;
        }
        .css-1d391kg button { /* Sidebar button styling */
            color: white; /* Button text color */
            border: none;
            background: transparent; /* Remove default button background */
        }
        .css-1d391kg .css-14xtw13 { /* Sidebar content */
            color: white; /* Sidebar content color */
        }
        .css-14xtw13 { /* Sidebar elements container */
            background-color: #0033a0; /* Blue background color for the summarize button area */
        }
        .chatbot-section {
            background-color: #0033a0; /* Blue background color for the chatbot section */
            padding: 20px;
            border-radius: 10px;
            color: white;
        }
        .chatbot-section h2 {
            font-size: 1.5rem;
            font-weight: bold;
            color: white;
            margin-bottom: 20px;
        }
        .st-chatbox {
            background-color: #ffffff; /* White background for the chatbox */
            color: #000000; /* Black text for the chatbox */
        }
    </style>
""", unsafe_allow_html=True)

# Path to the image
image_path = str(Path(__file__).parent / '../assets/images/about-img-3.jpg')

# Display image using Streamlit's built-in functions
st.sidebar.image(image_path, use_column_width=True, caption="Chatbot")

# Streamlit button for "Summarise the conversation"
summarise_button = st.sidebar.button("Summarise the conversation", key="summarise")
if summarise_button:
    st.sidebar.write("Summary:\n\n" + st.session_state['conversation'].memory.buffer)

# Optional: Additional CSS to style the button
st.sidebar.markdown(
    """
    <style>
    div.stButton > button {
        background-color:#1f77b4;
        color:white;
        padding:10px 24px;
        border:none;
        border-radius:5px;
        cursor:pointer;
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state variables
if 'conversation' not in st.session_state:
    st.session_state['conversation'] = None
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Function to get a response from the Huggingface model
def getresponse(userInput):
    # Initialize the conversation memory if not already done
    if st.session_state['conversation'] is None:
        llm = HuggingFaceEndpoint(
            repo_id="mistralai/Mistral-7B-Instruct-v0.2",
            huggingfacehub_api_token=API_Key,
            temperature=0.3,  # Lower temperature for more concise responses
            max_tokens=150     # Increased token limit for longer responses
        )

        # Using ConversationSummaryMemory to retain context
        st.session_state['conversation'] = ConversationChain(
            llm=llm,
            verbose=True,
            memory=ConversationSummaryMemory(llm=llm)  # Memory to retain conversation context
        )

    # Predict the response and store the conversation memory
    response = st.session_state['conversation'].predict(input=userInput)

    # Ensure there is no "Human" label in the response
    response = response.replace("Human:", "").strip()

    return response

# Response container for displaying the chat
response_container = st.container()

# Container for user input text box
container = st.container()

with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("Your question goes here:", key='input', height=100)
        submit_button = st.form_submit_button(label='Send')

        if submit_button:
            st.session_state['messages'].append(user_input)
            model_response = getresponse(user_input)
            st.session_state['messages'].append(model_response)

            with response_container:
                for i in range(len(st.session_state['messages'])):
                    if (i % 2) == 0:
                        message(
                            st.session_state['messages'][i],
                            is_user=True,
                            key=str(i) + '_user',
                        )
                    else:
                        # Format the AI response into multiple paragraphs
                        formatted_response = st.session_state['messages'][i].replace('\n', '').replace('\r', '')
                        paragraphs = formatted_response.split('\n\n')  # Split response into paragraphs
                        for para in paragraphs:
                            st.markdown(
                                f"""
                                <div style="background-color: #f0f0f5; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                                    <p style="font-family: Arial, sans-serif; font-size: 16px; color: #333;">{para}</p>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

