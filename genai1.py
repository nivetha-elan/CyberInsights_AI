import os
import streamlit as st
from transformers import BartTokenizer, BartForConditionalGeneration
from PyPDF2 import PdfReader
import openai
import random
import io
import json
from fpdf import FPDF
import base64
 
 
# Set OpenAI API key from environment variable
openai.api_key = '****'
 
# Load the BART summarization model
tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')
 
# List of recommended questions for the user
RECOMMENDED_QUESTIONS = [
    "Does the organization have a well-defined cybersecurity policy that aligns with industry standards (e.g., NIST, ISO 27001)?",
    "Are roles and responsibilities for cybersecurity clearly defined and communicated across the organization?",
    "Is there a formal incident response plan in place, and is it regularly tested?",
    "Has the organization conducted a comprehensive risk assessment recently?",
    "Are there clear access control policies in place to manage user privileges?",
    "Is sensitive data encrypted both at rest and in transit?",
    "Are firewalls, intrusion detection systems (IDS), and intrusion prevention systems (IPS) in place?",
    "How are cybersecurity threats monitored and identified within the organization?",
    "Does the organization conduct regular cybersecurity training and awareness programs?",
    "Are there disaster recovery (DR) and business continuity (BC) plans in place that include cybersecurity incidents?"
]
 
# Function to extract text from PDF files
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text
def truncate_text(text, max_tokens=1500):
    tokens = text.split()  # Splitting text by spaces (token approximation)
    if len(tokens) > max_tokens:
        return ' '.join(tokens[:max_tokens])  # Return only up to max tokens
    return text
   
 
def generate_pdf(search_history):
    pdf = FPDF()
    pdf.add_page()
 
    # Update the path to the font file
    font_path = "E://Adarsh//AI//ChatwithPDF//dejavu-fonts-ttf-2.37//ttf//DejaVuSans.ttf"
   
    # Add the DejaVu font
    pdf.add_font("DejaVu", "", font_path, uni=True)
   
    # Set the font to DejaVu for the whole document
    pdf.set_font("DejaVu", size=12)
 
    # Add the title
    pdf.cell(200, 10, txt="Search History", ln=True, align='C')
    pdf.ln(10)  # Add some space after the title
 
    # Iterate over the search history entries and add them to the PDF
    for entry in search_history:
        question = entry.get('question', 'No question provided')
        response = entry.get('response', 'No response provided')
 
        # Add question
        pdf.cell(200, 10, txt=f"Question: {question}", ln=True, align='L')
       
        # Add response with multi_cell to handle longer text wrapping
        pdf.multi_cell(0, 10, txt=f"Response: {response}")
       
        # Add some space between each entry
        pdf.ln(5)
 
    # Save the PDF to a bytes buffer
    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
 
    return pdf_output.read(), "search_history.pdf"
 
def analyze_sentiment(text):
    try:
        # Truncate the text if it's too long for the model
        truncated_text = truncate_text(text, max_tokens=3000)  # Adjust max_tokens if necessary
 
        # Create a prompt with sentiment classification examples
        prompt = f"""
        Classify the sentiment of the following text as 'positive', 'neutral', or 'negative':
       
        Examples:
        1. Text: "This audit report is great and very detailed." Sentiment: positive
        2. Text: "The report highlights significant improvements." Sentiment: positive
        3. Text: "The report is okay but could use some improvements." Sentiment: neutral
        4. Text: "The audit report covers the necessary points." Sentiment: neutral
        5. Text: "The audit report is lacking key information and is poorly done." Sentiment: negative
        6. Text: "This report misses the essential details and is confusing." Sentiment: negative
 
        Now classify this text:
        Text: "{truncated_text}"
        Sentiment:"""
       
        # Use OpenAI's API to generate the sentiment classification
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that classifies the sentiment of texts."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,  # Limit the response to prevent overflow
            temperature=0,
        )
       
        # Extract the sentiment from the response
        sentiment = response['choices'][0]['message']['content'].strip()
        return sentiment
 
    except openai.error.InvalidRequestError as e:
        st.error(f"Invalid request: {e}")
    except openai.error.AuthenticationError as e:
        st.error(f"Authentication error: {e}")
    except Exception as e:
        st.error(f"Error analyzing sentiment: {e}")
    return None
 
# Function to summarize text using BART
def summarize_text(text):
    inputs = tokenizer(text, return_tensors='pt', max_length=1024, truncation=True)
    summary_ids = model.generate(inputs['input_ids'], max_length=150, min_length=50, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary
 
# Function to generate response using OpenAI GPT
def generate_chat_response(prompt, history=[]):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=history + [{"role": "user", "content": prompt}],
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7
    )
    return response['choices'][0]['message']['content'].strip()
 
# Function to shuffle and display 4 random questions
def get_random_questions():
    return random.sample(RECOMMENDED_QUESTIONS, 4)
#ef get_chat_history_as_json():
    #return json.dumps(st.session_state.chat_history, indent=4)
 
# Streamlit app interface
def main():
    # Set the page config
    st.set_page_config(page_title="Cybersecurity Audit Analyzer", page_icon="🔍", layout="wide")
    st.markdown("""
    <style>
    .title-clean {
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 32px;
        color: #000000;
        font-weight: bold;
        text-align: center;
    }
    .subtitle-clean {
        font-family: 'Arial', sans-serif;
        font-size: 20px;
        color: #214cce;
        font-weight: bold;  /* Changed to bold */
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
 
    # Use the custom CSS classes to style the text
    st.markdown('<h2 class="title-clean">CHAT WITH AUDIT BOT 🤖</h2>', unsafe_allow_html=True)
    st.markdown('<h5 class="subtitle-clean">Feel free to ask the bot about cybersecurity audits, or upload additional reports for comparison</h5>', unsafe_allow_html=True)
 
 
    # Initialize session state for chat history, user input, report text, and random questions
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'user_input' not in st.session_state:
        st.session_state.user_input = ""
    if 'report_text' not in st.session_state:
        st.session_state.report_text = ""
    if 'recommended_questions' not in st.session_state:
        st.session_state.recommended_questions = get_random_questions()
 
    # Sidebar for file upload and summarization
    with st.sidebar:
        st.markdown("<h2 style='color: #214cce;'> 🛡️ Audit Report Tools</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #333;'>Upload a PDF audit report and summarize it.</p>", unsafe_allow_html=True)
 
        # File uploader to upload the PDF report
        uploaded_file = st.file_uploader("📄 Upload a Cybersecurity Audit Report (PDF)", type=["pdf"])
 
        if uploaded_file is not None:
            st.success("File uploaded successfully!")
            with st.spinner('⏳ Extracting text from the report...'):
                st.session_state.report_text = extract_text_from_pdf(uploaded_file)
           
            if st.button("📝 Summarize Report"):
                with st.spinner('⏳ Summarizing the report...'):
                    summary = summarize_text(st.session_state.report_text)
                st.session_state.chat_history.append({"role": "assistant", "content": f"Summarized Report: {summary}"})
            if st.button("🔍 Analyze Sentiment"):
                with st.spinner("Analyzing sentiment..."):
                    sentiment = analyze_sentiment(st.session_state.report_text)
                    if sentiment:
                        st.markdown(f"### Sentiment of the Report: {sentiment}")
 
        # Add the image at the bottom of the sidebar
        st.sidebar.image('E:\\Adarsh\\AI\\ChatwithPDF\\CHAT_WITH_PDF\\Files\\photo_2024-10-09_01-13-06-Vy0Uc9P2e-transformed.png', use_column_width=True)
 
    # Main section for chatbot interaction
    #st.markdown("<h2 style='color: #000000; text-align: center;'>CHAT WITH AUDIT BOT 🤖</h2>", unsafe_allow_html=True)
    #st.write("<h5 style='color: #326633; text-align: center;'> Feel free to ask the bot about cybersecurity audits, or upload additional reports for comparison</h5>", unsafe_allow_html=True)
 
    # Container for chat history
    chat_history_container = st.container()
    with chat_history_container:
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        for entry in st.session_state.chat_history:
            if entry["role"] == "user":
                st.chat_message("user").markdown(entry["content"])
            elif entry["role"] == "assistant":
                st.chat_message("assistant").markdown(entry["content"])
        st.markdown("</div>", unsafe_allow_html=True)
 
    # Custom input UI for chat with recommended questions as buttons
    st.markdown("### Ask a Question:")
 
    # Display 4 random recommended questions as clickable buttons
    col1, col2 = st.columns(2)
    for idx, question in enumerate(st.session_state.recommended_questions):
        if idx % 2 == 0:
            with col1:
                if st.button(question, key=f"btn_{idx}"):
                    st.session_state.user_input = question
                    handle_user_input(st.session_state.user_input)
                    st.experimental_rerun()  # Force rerun to display the response immediately
        else:
            with col2:
                if st.button(question, key=f"btn_{idx}"):
                    st.session_state.user_input = question
                    handle_user_input(st.session_state.user_input)
                    st.experimental_rerun()  # Force rerun to display the response immediately
 
    # Input section for user-typed questions
    user_input = st.text_input("Your Question", key="user_input", placeholder="Ask your own question here...")
 
    if st.button("Send"):
        if user_input:
            handle_user_input(user_input)
 
    # Add floating circular download button at bottom-right for chat history
    st.markdown("""
        <style>
        .floating-download-button {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            background-color: #00ABF0;
            color: white;
            border: none;
            border-radius: 50%;
            font-size: 24px;
            font-weight: bold;
            text-align: center;
            line-height: 60px;
            box-shadow: 2px 2px 19BDFF5px rgba(0,0,0,0.3);
            cursor: pointer;
            z-index: 9999;
            transition: all 0.3s ease;
        }
        .floating-download-button:hover {
            background-color: #19BDFF;
            transform: scale(1.1);
        }
        </style>
    """, unsafe_allow_html=True)
 
    if st.session_state.chat_history:
    # Generate PDF from chat history
        pdf_bytes, pdf_file_name = generate_pdf(st.session_state.chat_history)
       
        # Base64 encode the PDF file for download
        b64_pdf = base64.b64encode(pdf_bytes).decode()
 
        # Create a floating download button for the PDF
        download_button_html = f"""
        <a href="data:application/pdf;base64,{b64_pdf}" download="{pdf_file_name}">
            <button class="floating-download-button">⬇</button>
        </a>
        """
        st.markdown(download_button_html, unsafe_allow_html=True)
 
 
 
   
# Handle user input and add to chat history
def handle_user_input(user_input):
    if user_input:
        user_message = {"role": "user", "content": user_input}
        st.session_state.chat_history.append(user_message)
 
        # Generate response from GPT based on the conversation history
        with st.spinner('🤔 Thinking...'):
            response = generate_chat_response(user_input, st.session_state.chat_history)
        assistant_message = {"role": "assistant", "content": response}
        st.session_state.chat_history.append(assistant_message)
 
        # Refresh the random questions after each interaction
        st.session_state.recommended_questions = get_random_questions()
 
 
# Run the Streamlit app
if __name__ == '__main__':
    main()
