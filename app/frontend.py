import streamlit as st
import requests

# FastAPI backend URL
API_URL = "http://localhost:8000"

st.set_page_config(page_title="Support Agent", page_icon="🤖", layout="wide")
st.title("🤖 Support Agent")
st.caption("Powered by JLL GPT")

# Sidebar
st.logo(image = "app/JLL Technologies logo positive - RGB.png", size="large", link=None, icon_image=None)
st.sidebar.title("About")
st.sidebar.markdown("""
This is a demo of the Support Agent.

Do you have any questions on JLL HR policy? 
Ask a question and find the answer!

If you need further assistance, you can create a support ticket thorough the feedback form.
""")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Initialize expander state
if "feedback_expanded" not in st.session_state:
    st.session_state.feedback_expanded = False

# Initialize feedback data
if "feedback_data" not in st.session_state:
    st.session_state.feedback_data = {
        "title": "",
        "description": "",
        "priority": 2
    }

def display_chat_history():
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

def clear_history():
    st.session_state.chat_history = []
    st.session_state.feedback_expanded = False
    st.session_state.feedback_data = {"title": "", "description": "", "priority": 2}
    st.rerun()

display_chat_history()

spinner_placeholder = st.empty()

def process_user_input():
    user_question = st.session_state.user_input
    if user_question:
        st.session_state.chat_history.append({"role": "user", "content": user_question})

        with spinner_placeholder:
            with st.spinner("Getting answer..."):
                response = requests.post(f"{API_URL}/ask", json={"question": user_question})

                if response.status_code == 200:
                    data = response.json()
                    answer = data["answer"]
                    ticket_info = data.get("ticket_info")
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})

                    if ticket_info:
                        st.session_state.feedback_data = {
                            "title": ticket_info["title"],
                            "description": ticket_info["description"],
                            "priority": ticket_info["priority"]
                        }

                else:
                    st.error("Failed to get a response. Please try again.")

        st.session_state.user_input = ""

st.text_input("Ask a question:", key="user_input", on_change=process_user_input)
spinner_placeholder.empty()

has_answers = any(msg["role"] == "assistant" for msg in st.session_state.chat_history)

if has_answers:
    expander = st.expander("Provide Feedback", expanded=st.session_state.feedback_expanded)
    with expander:
        resolved = st.radio("Was your last question answered?", ("Absolutely! I'm all set.", "Not quite. I need more info - please raise a ticket"))
        
        if resolved == "Absolutely! I'm all set.":
            if st.button("Submit Feedback"):
                st.success("Thank you for your feedback! We're glad we could help.")
                st.session_state.feedback_expanded = True
        
        elif resolved == "Not quite. I need more info - please raise a ticket":
            st.write("We're sorry we couldn't fully answer your question. Let's create a support ticket to get you more information.")
            
            # Ticket creation form
            st.subheader("Create a Support Ticket")
    
            st.session_state.feedback_data["title"] = st.text_input("Ticket Title", value=st.session_state.feedback_data.get("title", ""))
            st.session_state.feedback_data["description"] = st.text_area(
                "Ticket Description", 
                value=st.session_state.feedback_data.get("description", ""),
                height=200
            )

            user_email = st.text_input("Your Email (if you'd like to be contacted)", value="")

            st.session_state.feedback_data["priority"] = st.selectbox("Priority", [1, 2, 3, 4], 
                                                                    format_func=lambda x: ["High", "Medium", "Low", "Lowest"][x-1], 
                                                                    index=st.session_state.feedback_data.get("priority", 2)-1)
            
            if st.button("Create Ticket"):
                if user_email:
                    st.session_state.feedback_data["description"] += f"\n\nUser email_id: {user_email}"
        
                try:
                    ticket_response = requests.post(
                        f"{API_URL}/create-ticket",
                        json=st.session_state.feedback_data
                    )
                    if ticket_response.status_code == 200:
                        ticket_data = ticket_response.json()
                        st.success(f"Ticket created successfully! Your ticket ID is {ticket_data['ticket_id']}. We'll contact you if needed.")
                        # Clear the form data after successful submission
                        st.session_state.feedback_data = {"title": "", "description": "", "priority": 2}
                        st.session_state.feedback_expanded = True
                    else:
                        st.error("Failed to create ticket. Please try again.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

st.sidebar.markdown("<br>" * 14, unsafe_allow_html=True)

if st.sidebar.button("Clear Chat History"):
    clear_history()