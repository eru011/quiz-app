import os
import streamlit as st
import google.generativeai as genai
import json

# Set page config
st.set_page_config(page_title="Quiz Generator", layout="wide")

# Configure API key using Streamlit secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
)

# Create the UI
st.title("Quiz Generator")

# Create two columns for input controls
col1, col2 = st.columns([2, 1])

with col1:
    # File uploader
    uploaded_file = st.file_uploader("Choose a file", type=['txt', 'pdf', 'docx'])

with col2:
    # Add difficulty selector
    difficulty = st.selectbox(
        "Select Quiz Difficulty",
        ["Easy (True/False)", "Medium (Multiple Choice)", "Hard (Fill in the Blanks)"]
    )
    # Generate quiz button
    generate_button = st.button("Generate Quiz")

if uploaded_file is not None:
    # Read and display file content
    file_type = uploaded_file.name.split('.')[-1].lower()
    
    if file_type == 'txt':
        try:
            content = uploaded_file.read().decode('utf-8')
        except UnicodeDecodeError:
            content = uploaded_file.read().decode('latin-1')
    elif file_type == 'pdf':
        import PyPDF2
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        content = ""
        for page in pdf_reader.pages:
            content += page.extract_text()
    elif file_type == 'docx':
        import docx
        doc = docx.Document(uploaded_file)
        content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    
    # Show file content
    st.subheader("File Content:")
    st.text(content)
    
    if generate_button:
        with st.spinner("Generating quiz..."):
            chat = model.start_chat(history=[])
            
            try:
                json_instruction = """You are a JSON generator. Your response must ONLY contain a valid JSON object, nothing else. No explanations, no markdown, no additional text.
                ONLY return a JSON object in this exact format:"""
                
                if "Easy" in difficulty:
                    prompt = f"""{json_instruction}
                    {{
                        "questions": [
                            {{"question": "Sample true/false question?"}}
                        ]
                    }}
                    Generate exactly 5 True/False questions about this content: {content}"""
                    
                elif "Medium" in difficulty:
                    prompt = f"""{json_instruction}
                    {{
                        "questions": [
                            {{
                                "question": "Sample multiple choice question?",
                                "options": {{
                                    "a": "Option 1",
                                    "b": "Option 2",
                                    "c": "Option 3",
                                    "d": "Option 4"
                                }}
                            }}
                        ]
                    }}
                    Generate exactly 5 multiple choice questions about this content: {content}"""
                    
                else:  # Hard
                    prompt = f"""{json_instruction}
                    {{
                        "questions": [
                            {{"question": "Sample fill-in-the-blank with _____?"}}
                        ]
                    }}
                    Generate exactly 5 fill-in-the-blank questions about this content: {content}"""
                
                response = chat.send_message(prompt)
                
                # Clean up the response text
                response_text = response.text.strip()
                if response_text.startswith('```') and response_text.endswith('```'):
                    response_text = response_text[3:-3].strip()
                if response_text.lower().startswith('json'):
                    response_text = response_text[4:].strip()
                
                # Try to parse JSON to validate it
                json.loads(response_text)  # Validate JSON format
                
                # Store the generated quiz in session state
                st.session_state.quiz_content = content
                st.session_state.quiz_data = response_text  # Store cleaned response
                st.session_state.quiz_difficulty = difficulty
                
                # Show button to go to quiz page
                st.success("Quiz generated successfully!")
                st.button("Take Quiz", on_click=lambda: st.switch_page("pages/quiz.py"))
                
            except Exception as e:
                st.error(f"Failed to generate quiz: {str(e)}")