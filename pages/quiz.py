import streamlit as st

# Set page config
st.set_page_config(page_title="Take Quiz", layout="wide")

# Check if quiz data exists
if 'quiz_data' not in st.session_state:
    st.error("No quiz generated yet! Please go back and generate a quiz first.")
    st.button("Back to Generator", on_click=lambda: st.switch_page("gem.py"))
else:
    st.title("Take Your Quiz")
    
    # Display quiz based on difficulty
    quiz_data = st.session_state.quiz_data
    difficulty = st.session_state.quiz_difficulty
    
    try:
        import json
        # Clean up the quiz data if needed
        quiz_data = st.session_state.quiz_data.strip()
        if quiz_data.startswith('```') and quiz_data.endswith('```'):
            quiz_data = quiz_data[3:-3].strip()
        if quiz_data.lower().startswith('json'):
            quiz_data = quiz_data[4:].strip()
            
        quiz = json.loads(quiz_data)
        
        # Validate quiz structure
        if "questions" not in quiz:
            raise ValueError("Invalid quiz format: missing questions")
            
        # Initialize answers if not exists
        if 'user_answers' not in st.session_state:
            st.session_state.user_answers = {}
        
        # Display questions
        for i, q in enumerate(quiz["questions"]):
            st.write(f"\n**Question {i+1}:** {q['question']}")
            
            if "Easy" in difficulty:
                st.session_state.user_answers[i] = st.radio(
                    f"Select answer for question {i+1}:",
                    ["True", "False"],
                    key=f"q_{i}",
                    index=None
                )
            
            elif "Medium" in difficulty:
                if 'options' not in q:
                    raise ValueError(f"Question {i+1} is missing options")
                options = q['options']
                st.session_state.user_answers[i] = st.radio(
                    f"Select answer for question {i+1}:",
                    options.items(),
                    format_func=lambda x: f"{x[0]}) {x[1]}",
                    key=f"q_{i}",
                    index=None
                )
            
            else:  # Hard
                st.session_state.user_answers[i] = st.text_input(
                    f"Enter answer for question {i+1}:",
                    key=f"q_{i}"
                )
        
        # Submit button
        if st.button("Submit Quiz"):
            st.success("Quiz submitted! Your responses have been recorded.")
            # Here you could add functionality to store or process the answers
            
        # Back button
        st.button("Back to Generator", on_click=lambda: st.switch_page("gem.py"))
        
    except Exception as e:
        st.error(f"Error displaying quiz: {str(e)}")
        st.button("Back to Generator", on_click=lambda: st.switch_page("gem.py"))
