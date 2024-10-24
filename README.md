# CyberInsights-AI
The CyberInsights-AI is a Streamlit web application designed to help users interact with cybersecurity audit reports, summarize them, and get real-time insights using a chatbot powered by the Google Gemini API and BART model. The app allows users to upload PDF audit reports for summarization and ask questions related to cybersecurity audits through a chat interface.

# Features
PDF Report Summarization: Upload a cybersecurity audit report in PDF format, and the app will extract text from the report and generate a summarized version using the BART model. Chatbot Interaction: Ask questions about cybersecurity audits or the uploaded report via a chatbot powered by Google Gemini API. Random Cybersecurity Questions: The app displays four recommended cybersecurity questions that users can click to get immediate insights. Clear Chat History: Users can reset the chat interface and generate new random questions by clearing the conversation. User-Typed Questions: Users can also type and submit their own questions for the chatbot to answer.

# Python Dependencies
The required Python packages are listed below. You can install them using the following command: pip install -r requirements.txt

# API Key
You need a valid Google Gemini API key to enable chatbot functionality. Ensure you replace the placeholder API key in the script with your actual API key, or store it as an environment variable for security.

# Set up the Google Gemini API key: Replace the placeholder API key in the code (GEMINI_API_KEY = 'YOUR_API_KEY') or store it in an environment variable:
export GEMINI_API_KEY='your-api-key-here'

# Run the Streamlit app: Start the application by running:
streamlit run app.py

# Usage
Upload a Cybersecurity Audit Report:
Upload a PDF file containing a cybersecurity audit report via the sidebar. The app will extract the text and generate a summary using the BART model.

# Ask Cybersecurity Questions:
The app provides four random recommended cybersecurity questions. You can click any of the buttons to ask the chatbot, or you can type your own question in the input field.

# Interact with the Chatbot:
The chatbot powered by Google Gemini API will provide responses to your queries based on the uploaded audit report or general cybersecurity questions.
