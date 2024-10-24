import time
import openai
from collections import defaultdict
from PyPDF2 import PdfReader
import streamlit as st
import plotly.express as px
import pandas as pd
from transformers import BartTokenizer, BartForConditionalGeneration

# Set OpenAI API key
openai.api_key = '****'

# Load the BART summarization model
tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')

# Key questions for overall report analysis
KEY_DECISION_QUESTIONS = [
    "Is there an incident response plan?",
    "Is data encrypted at rest and in transit?",
    "Are there regular cybersecurity training programs?",
    "Are firewalls and intrusion detection systems in place?",
    "Is there a disaster recovery plan?",
    "Does the organization conduct regular vulnerability assessments and penetration testing?",
    "Is there a patch management policy in place to ensure timely software updates?",
    "Does the organization implement multi-factor authentication (MFA) for access to sensitive systems?",
    "Are backups regularly tested for restoration, and are they stored securely?",
    "Are third-party vendors and partners evaluated for cybersecurity risks?",
    "Is Recent Audit is conducted?"
]

# Risk classification function using keyword matching
def classify_risk(content):
    high_risk_keywords = [
        "critical", "severe", "high risk", "breach", "compromise", "unauthorized access",
        "exploitation", "major vulnerability", "data exfiltration", "incident", "unpatched", "unmitigated"
    ]
    medium_risk_keywords = [
        "moderate", "medium risk", "potential vulnerability", "exposure", "configuration issues",
        "insecure protocols", "firewall misconfiguration", "audit finding", "password weaknesses"
    ]
    low_risk_keywords = [
        "low risk", "minor", "non-critical", "low priority", "compliance gap", "misconfigured settings",
        "isolated incident", "best practices not followed", "limited vulnerability"
    ]

    content_lower = content.lower()

    if any(word in content_lower for word in high_risk_keywords):
        return 'High'
    elif any(word in content_lower for word in medium_risk_keywords):
        return 'Medium'
    elif any(word in content_lower for word in low_risk_keywords):
        return 'Low'
    else:
        return 'No Risk Detected'

# Function to extract text from PDF files
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to analyze the reports and return detailed results
def analyze_reports(texts, file_names):
    detailed_results = []
    total_risks = {'Low': 0, 'Medium': 0, 'High': 0, 'No Risk Detected': 0}

    for i, text in enumerate(texts):
        risk_level = classify_risk(text)
        detailed_results.append({
            'PDF Name': file_names[i],
            'Risk Detected': 'Yes' if risk_level in ['Low', 'Medium', 'High'] else 'No',
            'Risk Level': risk_level
        })
        total_risks[risk_level] += 1

    return detailed_results, total_risks

# Function to analyze the reports and return content related to each key question
def analyze_reports_with_content(texts, questions, pdf_names):
    analysis_results = defaultdict(lambda: {'yes': [], 'no': [], 'content': defaultdict(list)})

    for pdf_name, text in zip(pdf_names, texts):
        truncated_text = truncate_text(text)

        for question in questions:
            prompt = f"Does the following report mention '{question}'? Answer with 'yes' or 'no'. If yes, extract the relevant content.\n\nReport: {truncated_text}"
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0
            )
            answer = response['choices'][0]['message']['content'].strip().lower()

            if 'yes' in answer:
                analysis_results[question]['yes'].append(pdf_name)
                analysis_results[question]['content'][pdf_name].append(answer)  # Store relevant content
            else:
                analysis_results[question]['no'].append(pdf_name)

    return analysis_results

# Function to truncate long text to fit the model's token limit
def truncate_text(text, max_tokens=3000):
    tokens = text.split()
    if len(tokens) > max_tokens:
        return ' '.join(tokens[:max_tokens])
    return text

# Function to generate an advanced interactive bar chart using Plotly
def generate_plotly_bar_chart_for_question(question, analysis_results, pdf_names):
    common_pdf_names = [f"Report {i+1}" for i in range(len(pdf_names))]
   
    results = analysis_results[question]
    yes_counts = [1 if pdf_name in results['yes'] else 0 for pdf_name in pdf_names]
    no_counts = [1 if pdf_name in results['no'] else 0 for pdf_name in pdf_names]

    data = pd.DataFrame({
        'Common PDF Name': common_pdf_names,
        'Actual PDF Name': pdf_names,
        'Yes': yes_counts,
        'No': no_counts
    })

    data_melted = data.melt(['Common PDF Name', 'Actual PDF Name'], var_name='Response', value_name='Count')

    fig = px.bar(
        data_melted,
        x='Count',
        y='Common PDF Name',
        color='Response',
        orientation='h',
        title=f"Analysis of '{question}' Across Reports",
        text='Response',
        hover_data={'Actual PDF Name': True},
        color_discrete_map={'Yes': '#4CAF50', 'No': '#F44336'}
    )

    fig.update_layout(
        xaxis_title="Count",
        yaxis_title="Report",
        legend_title="Response",
        height=400
    )

    st.plotly_chart(fig)

# Function to display relevant content for the selected question
def display_relevant_content_for_question(question, analysis_results, pdf_names):
    common_pdf_names = [f"Report {i+1}" for i in range(len(pdf_names))]

    st.markdown(f"### Relevant Content for '{question}'")
   
    for idx, pdf_name in enumerate(pdf_names):
        common_name = common_pdf_names[idx]
        if pdf_name in analysis_results[question]['yes']:
            st.markdown(f"**{common_name}**")
            for content in analysis_results[question]['content'][pdf_name]:
                with st.expander(f"View content from {common_name}", expanded=True):
                    st.markdown(content)

# Main Streamlit app
def main():
    st.set_page_config(page_title="Cybersecurity Audit Analyzer", page_icon="🔍", layout="wide")

    st.markdown("""
    <style>
    .title-clean {
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 32px;
        color: #214cce;
        font-weight: bold;
        text-align: center;
    }
    .subtitle-clean {
        font-family: 'Arial', sans-serif;
        font-size: 20px;
        color: #000000;
        font-weight: bold;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<h2 class="title-clean">CYBERSECURITY MULTIPLE AUDIT REPORT ANALYZER</h2>', unsafe_allow_html=True)
    st.markdown('<h5 class="subtitle-clean">Upload your reports to analyze key cybersecurity compliance questions and risk levels.</h5>', unsafe_allow_html=True)
    

    with st.sidebar:
        st.markdown("<h2 style='color: #214cce;'> 🛡️ Audit Report Tools</h2>", unsafe_allow_html=True)
        uploaded_files = st.file_uploader("📄 Upload Cybersecurity Audit Reports (PDF)", type=["pdf"], accept_multiple_files=True)
        st.markdown("### Enter Custom Questions:")
        user_question = st.text_input("Type your question here")
    st.sidebar.image('E:\\Adarsh\\AI\\ChatwithPDF\\CHAT_WITH_PDF\\Files\\photo_2024-10-09_01-13-06-Vy0Uc9P2e-transformed.png', use_column_width=True)


    if uploaded_files:
        st.success("Files uploaded successfully!")
        file_names = [file.name for file in uploaded_files]
        report_texts = [extract_text_from_pdf(file) for file in uploaded_files]

        questions_to_analyze = KEY_DECISION_QUESTIONS.copy()
        if user_question:
            questions_to_analyze.append(user_question)

        with st.spinner('⏳ Analyzing reports...'):
            detailed_results, total_risks = analyze_reports(report_texts, file_names)
            analysis_results = analyze_reports_with_content(report_texts, questions_to_analyze, file_names)

        tab1, tab2, tab3 = st.tabs(["Risk Distribution", "Compliance Check", "Question-Based Analysis"])

        # Tab 1: Risk Distribution
        with tab1:
            st.markdown("### Overall Risk Distribution (Heatmap)")
            risk_df = pd.DataFrame(detailed_results)
            risk_levels = ['Low Risk', 'Medium Risk', 'High Risk', 'No Risk Detected']
            colors = ['#E0F7FA', '#81D4FA', '#0288D1', '#01579B']

            heatmap_fig = px.imshow([[total_risks['Low'], total_risks['Medium'], total_risks['High'], total_risks['No Risk Detected']]],
                                    labels=dict(x="Risk Level", y="Reports"),
                                    x=risk_levels,
                                    color_continuous_scale=colors,
                                    title="Overall Risk Distribution Heatmap")
            st.plotly_chart(heatmap_fig)

            st.markdown("### Risk Distribution Data Summary")

            st.table(risk_df)
            

            # Additional visualization: Compliance vs. Risk correlation (density)
            st.markdown("### Risk Density Map")
            
            density_data = {
                'Risk Level': ['Low', 'Medium', 'High', 'No Risk Detected'],
                'Count': [total_risks['Low'], total_risks['Medium'], total_risks['High'], total_risks['No Risk Detected']]
            }

            density_df = pd.DataFrame(density_data)

            # Density plot
            density_fig = px.density_heatmap(density_df, x='Risk Level', y='Count',
                                            title='Risk Distribution Density Map', nbinsx=10, nbinsy=10)
            st.plotly_chart(density_fig)

        # Tab 2: Compliance Check
        # Tab 2: Compliance Check
        with tab2:
            st.markdown("### Compliance Check Results (Yes/No)")

            # Modify compliance data: If any risk is detected (Low, Medium, High), mark as 'Yes' for compliance issues
            compliance_data = {
                'Category': ['Yes', 'No'],
                'Count': [
                    sum([1 for res in detailed_results if res['Risk Level'] in ['Low', 'Medium', 'High']]),  # Yes: Risk detected
                    sum([1 for res in detailed_results if res['Risk Level'] == 'No Risk Detected'])           # No: No risk detected
                ]
            }

            compliance_df = pd.DataFrame(compliance_data)

            # Create a Donut Chart for compliance (Yes/No)
            donut_fig = px.pie(compliance_df, values='Count', names='Category', hole=0.4,
                            title='Compliance (Yes/No) Donut Chart',
                            color_discrete_map={'Yes': '#4CAF50', 'No': '#F44336'})
            st.plotly_chart(donut_fig)

            # Show compliance data summary as a table
            st.markdown("### Compliance Data Summary (Yes/No)")
            compliance_detailed_df = pd.DataFrame({
                'PDF Name': [res['PDF Name'] for res in detailed_results],
                'Compliance Issue': ['Yes' if res['Risk Level'] in ['Low', 'Medium', 'High'] else 'No' for res in detailed_results]
            })
            st.table(compliance_detailed_df)

        # Tab 3: Question-Based Analysis
        with tab3:
            st.markdown("### Select a Question to Visualize the Response Across PDFs")
            combined_questions = KEY_DECISION_QUESTIONS + ([user_question] if user_question else [])
            selected_question = st.selectbox("Select a question:", combined_questions)

            if selected_question:
                st.markdown(f"#### Showing Results for: {selected_question}")
                generate_plotly_bar_chart_for_question(selected_question, analysis_results, file_names)
                display_relevant_content_for_question(selected_question, analysis_results, file_names)
        
        

if __name__ == '__main__':
    main()
