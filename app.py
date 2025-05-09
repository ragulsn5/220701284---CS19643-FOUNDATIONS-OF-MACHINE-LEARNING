import streamlit as st
import requests
from datetime import datetime
from openai import OpenAI
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Read API keys from environment variables for security
openai_api_key = os.getenv('OPENAI_API_KEY', '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')  # Replace with actual key
drugbank_api_key = os.getenv('DRUGBANK_API_KEY', 'your_drugbank_api_key')

# Initialize OpenAI client
# Initialize OpenAI client
client = OpenAI(
    api_key=openai_api_key,
    base_url="https://api.upstage.ai/v1/solar"
)

# App title and description
st.title("MediBot - AI Chatbot for Drug, Disease Information, and Diagnosis Support")
st.write("""
MediBot provides real-time, comprehensive drug and disease information, offers diagnosis support, disease prevention education, 
and patient triage based on symptoms. It assists healthcare professionals, patients, and researchers with real-world impact.
""")

# Function to generate Llama 3.1 response
def llama_generate_response(user_content, history):
    try:
        system_content = "You are MediBot, an autonomous AI agent that specializes in providing accurate medical information, diagnosis support, disease prevention education, and patient triage based on symptoms."
        # Use conversation history to adapt responses
        stream = client.chat.completions.create(
            model="solar-pro",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content}
            ],
            stream=True,
        )
        response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                response += chunk.choices[0].delta.content
        return response
    except Exception as e:
        st.error(f"Detailed error: {e}")

        return "There was an error generating the response. Please try again."

# Diagnosis Support
def provide_diagnosis_support(symptoms):
    diagnosis_knowledge_base = {
        "fever, cough, fatigue": "You might be experiencing flu-like symptoms. Common causes include influenza or viral infections.",
        "chest pain, shortness of breath": "These symptoms may indicate a heart problem. It’s advised to seek urgent medical attention.",
        "headache, nausea, sensitivity to light": "These symptoms could be related to a migraine or a severe headache. Rest and hydration are often helpful.",
        # Add more symptom-diagnosis mappings as needed
    }

    for symptom_set, diagnosis in diagnosis_knowledge_base.items():
        if all(symptom.lower() in symptoms.lower() for symptom in symptom_set.split(", ")):
            return diagnosis
    
    return "The symptoms provided do not match any known conditions in our database. Please consult a medical professional for a detailed diagnosis."

# Disease Prevention Education
def provide_disease_prevention(illness):
    prevention_tips = {
        "heart disease": "To prevent heart disease, maintain a healthy diet low in saturated fats, exercise regularly, avoid smoking, and manage stress.",
        "diabetes": "To prevent diabetes, focus on eating a balanced diet with low sugar intake, exercise regularly, and maintain a healthy weight.",
        "COVID-19": "Prevent COVID-19 by wearing masks, washing hands frequently, avoiding crowded places, and getting vaccinated.",
        # Add more diseases and prevention tips
    }

    return prevention_tips.get(illness.lower(), "Sorry, I don't have prevention information for that disease. Please consult a healthcare provider.")

# Patient Triage
def patient_triage(symptoms):
    triage_knowledge_base = {
        "severe chest pain, shortness of breath": "You may be experiencing a medical emergency (e.g., a heart attack). Please seek immediate medical attention.",
        "high fever, persistent vomiting": "These symptoms suggest a serious infection. Please visit a healthcare provider as soon as possible.",
        "mild headache, slight fever": "You may be experiencing a mild illness. Rest, hydration, and over-the-counter medications may help. Monitor your symptoms."
        # Add more triage options based on common symptoms
    }

    for symptom_set, advice in triage_knowledge_base.items():
        if all(symptom.lower() in symptoms.lower() for symptom in symptom_set.split(", ")):
            return advice

    return "Based on your symptoms, it’s difficult to provide a definitive recommendation. Please consult a healthcare provider for a proper assessment."

# Store chat history and feedback
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "feedback" not in st.session_state:
    st.session_state["feedback"] = []

# Function to clear chat history
def clear_chat():
    st.session_state["messages"] = []
    st.session_state["feedback"] = []
    st.success("Chat cleared!")

# Sidebar options
with st.sidebar:
    st.header("MediBot Chatbot - Diagnosis Support and Triage")
    
    if st.button("Start New Chat"):
        clear_chat()  # Clear chat to start fresh
        # st.experimental_rerun()  # Restart the session with fresh context

    # if st.button("Clear Chat"):
    #     clear_chat()

# # Chatbot interface
# st.header("MediBot Chatbot - Diagnosis Support and Triage")

# Display previous messages in the chat
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input through the chat input box
if user_input := st.chat_input("Ask MediBot about drugs, diseases, symptoms, or diagnosis..."):
    # Add user input to message history
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Handle diagnosis support or disease prevention education based on keywords
    if "symptoms" in user_input.lower():
        # Extract symptoms for diagnosis support
        symptoms = user_input.split("symptoms")[-1].strip()
        diagnosis_response = provide_diagnosis_support(symptoms)
        llama_response = diagnosis_response
    elif "prevention" in user_input.lower():
        # Extract illness for prevention tips
        illness = user_input.split("prevention of")[-1].strip()
        prevention_response = provide_disease_prevention(illness)
        llama_response = prevention_response
    elif "triage" in user_input.lower():
        # Extract symptoms for patient triage
        symptoms = user_input.split("triage for")[-1].strip()
        triage_response = patient_triage(symptoms)
        llama_response = triage_response
    else:
        # General query processing using Llama 3.1
        user_history = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state["messages"]]
        llama_response = llama_generate_response(user_input, user_history)

    # Display AI response and add to chat history
    st.session_state["messages"].append({"role": "assistant", "content": llama_response})
    with st.chat_message("assistant"):
        st.markdown(llama_response)

    # Allow user to give feedback on the response for AI learning
    feedback = st.text_input("Was this response helpful? (yes/no)")
    if feedback:
        st.session_state["feedback"].append(feedback)
        st.write("Thank you for your feedback!")
        if feedback.lower() == "no":
            st.write("MediBot will try to improve its responses.")

# Footer with real-time updates
st.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by MediBot Autonomous AI Agent.")
