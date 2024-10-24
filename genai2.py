import streamlit as st
from PIL import Image
import base64
from io import BytesIO
import subprocess
import threading

# Function to set a background image using CSS
def add_bg_from_local(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{encoded_string}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

# Set the background image (replace with the path to your image)
add_bg_from_local('output_images/HI (8).png')

# Load images for Single and Multiple Audit reports
single_audit_img = Image.open('output_images/Pic (1).png')  # Replace with your image path
multiple_audit_img = Image.open('output_images/pdf-icon-png-2060.png')  # Replace with your image path

# Helper function to convert PIL images to base64
def image_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

# Convert the images to base64
single_audit_base64 = image_to_base64(single_audit_img)
multiple_audit_base64 = image_to_base64(multiple_audit_img)

# Title with custom font style
st.markdown(
    """
    <h1 style='text-align: center; color: #f0f8ff; font-size: 32px; font-family: Arial, Helvetica, sans-serif;text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.8)'>CYBERSECURITY AUDIT REPORT ANALYSIS</h1>
    """,
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)  # Add some space between the title and the buttons

# Custom CSS for buttons and layout
layout_css = """
<style>
    .interactive-btn {
        display: inline-block;
        padding: 50px 120px;  /* Bigger padding for larger button */
        font-size: 50px;  /* Larger font size */
        font-weight: bold;
        border: 50px solid #41C5D3;
        border-radius: 15px;
        color: #ffffff;
        background-color: #007BFF;
        transition: all 0.3s ease;
        text-align: center;
        box-shadow: 0px 8px 25px rgba(0, 123, 255, 0.5);
        margin-top: 50px;
        cursor: pointer;
    }
    .interactive-btn:hover {
        background-color: #0056b3;
        color: white;
        transform: scale(1.1);
        box-shadow: 0px 12px 30px rgba(0, 123, 255, 0.8);
    }
    .center-text {
        text-align: center;
        font-size: 500px;
        color: white;
    }
    .left-align {
        text-align: left;
        position: relative;
        margin-left: 50px;
    }
    .right-align {
        text-align: right;
        position: relative;
        margin-right: 50px;
    }
</style>
"""

# Apply the custom layout CSS
st.markdown(layout_css, unsafe_allow_html=True)

# Function to open the Streamlit app using subprocess with threading for faster execution
def open_streamlit_app(script_path):
    threading.Thread(target=subprocess.Popen, args=(["streamlit", "run", script_path],)).start()

# Create two columns with custom alignment
col1, col2 = st.columns([1, 1], gap="large")

# Left aligned content (Single Audit Report)
with col1:
    st.markdown(f"""
        <div class="left-align">
            <img src='data:image/png;base64,{single_audit_base64}' width='100%' style="border-radius: 15px; box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.3);margin-left: -100px" />
        </div>
        """, unsafe_allow_html=True)
    if st.button("Single Audit Report"):
        # Run genai1.py as a Streamlit app when Single Audit Report is clicked

        open_streamlit_app("E:\\Adarsh\\AI\\ChatwithPDF\\CHAT_WITH_PDF\\python\\genai1.py")

# Right aligned content (Multiple Audit Report)
with col2:
    st.markdown(f"""
        <div class="right-align">
            <img src='data:image/png;base64,{multiple_audit_base64}' width='100%' style="border-radius: 15px; box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.3);margin-right: 1100px;" />
        </div>
        """, unsafe_allow_html=True)
    if st.button("Multiple Audit Reports"):
        # Run genai3.py as a Streamlit app when Multiple Audit Reports is clicked
        open_streamlit_app("E:\\Adarsh\\AI\\ChatwithPDF\\CHAT_WITH_PDF\\python\\genai3.py")
