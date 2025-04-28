import pandas as pd
import streamlit as st

# Initialize session state for login and mark entry
def initialize_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_role" not in st.session_state:
        st.session_state.user_role = ""
    if "student_marks" not in st.session_state:
        st.session_state.student_marks = pd.DataFrame(columns=["Roll Number", "Name", "POAI", "SC", "CN", "OOPJ", "Maths"])

initialize_session_state()

# Dummy student data (using the list you provided)
student_data = {
    "Roll Number": [231701001, 231701002, 231701003, 231701004, 231701005],
    "Name": ["AADHITH KUMAR S V", "AASHISH P", "AKASH E", "ANISH D", "ARJUN V"]
}

student_df = pd.DataFrame(student_data)

# Define teacher login function
def teacher_login():
    st.title("Teacher Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if username == "kalpana.d" and password == "rec":
        st.session_state.logged_in = True
        st.session_state.user_role = "SC"
        st.success("Logged in successfully as SC teacher!")
    elif username == "preethi" and password == "rec":
        st.session_state.logged_in = True
        st.session_state.user_role = "POAI"
        st.success("Logged in successfully as POAI teacher!")
    elif username == "gunasekar" and password == "rec":
        st.session_state.logged_in = True
        st.session_state.user_role = "CN"
        st.success("Logged in successfully as CN teacher!")
    elif username == "vijayakumar" and password == "rec":
        st.session_state.logged_in = True
        st.session_state.user_role = "OOPJ"
        st.success("Logged in successfully as OOPJ teacher!")
    elif username == "sriram" and password == "rec":
        st.session_state.logged_in = True
        st.session_state.user_role = "Maths"
        st.success("Logged in successfully as Maths teacher!")
    elif username == "admin" and password == "rec":
        st.session_state.logged_in = True
        st.session_state.user_role = "Admin"
        st.success("Logged in successfully as Admin!")
    else:
        st.error("Invalid username or password")

# Teacher mark entry
def teacher_mark_entry():
    if st.session_state.user_role != "Admin":
        st.title(f"Enter Marks for {st.session_state.user_role} Subject")
        
        roll_number = st.selectbox("Select Student Roll Number", student_df["Roll Number"])
        student_name = student_df[student_df["Roll Number"] == roll_number]["Name"].values[0]
        
        mark = st.number_input(f"Enter Marks for {student_name} ({roll_number})", min_value=0, max_value=100, step=1)

        if st.button("Submit Marks"):
            student_index = st.session_state.student_marks[st.session_state.student_marks["Roll Number"] == roll_number].index
            if student_index.empty:
                new_row = pd.DataFrame({
                    "Roll Number": [roll_number],
                    "Name": [student_name],
                    "POAI": None,
                    "SC": None,
                    "CN": None,
                    "OOPJ": None,
                    "Maths": None,
                })
                st.session_state.student_marks = pd.concat([st.session_state.student_marks, new_row], ignore_index=True)
            
            # Update marks based on the subject
            if st.session_state.user_role == "POAI":
                st.session_state.student_marks.at[student_index[0], "POAI"] = mark
            elif st.session_state.user_role == "SC":
                st.session_state.student_marks.at[student_index[0], "SC"] = mark
            elif st.session_state.user_role == "CN":
                st.session_state.student_marks.at[student_index[0], "CN"] = mark
            elif st.session_state.user_role == "OOPJ":
                st.session_state.student_marks.at[student_index[0], "OOPJ"] = mark
            elif st.session_state.user_role == "Maths":
                st.session_state.student_marks.at[student_index[0], "Maths"] = mark
            
            st.success(f"Marks for {student_name} updated successfully!")

# Admin mark viewing and downloading
def admin_mark_viewing():
    st.title("Admin View: Student Marks")
    st.write(st.session_state.student_marks)
    st.download_button("Download Marks as CSV", st.session_state.student_marks.to_csv(), file_name="student_marks.csv")

# Main function to switch between login and content
def main():
    if not st.session_state.logged_in:
        teacher_login()
    else:
        if st.session_state.user_role == "Admin":
            admin_mark_viewing()
        else:
            teacher_mark_entry()

if __name__ == "__main__":
    main()
