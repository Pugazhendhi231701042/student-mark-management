import streamlit as st
import pandas as pd
from fpdf import FPDF

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "student_roll_number" not in st.session_state:
    st.session_state.student_roll_number = None
if "master_df" not in st.session_state:
    st.session_state.master_df = pd.DataFrame(columns=["Roll Number", "Name", "POAI", "SC", "CN", "OOPJ", "Maths"])

# Function to calculate the total marks
def calculate_total(row):
    marks = [row["POAI"], row["SC"], row["CN"], row["OOPJ"], row["Maths"]]
    valid_marks = [mark for mark in marks if mark is not None]
    return sum(valid_marks)

def add_marks():
    # Initialize missing session state variables for marks
    if "new_pai_marks" not in st.session_state:
        st.session_state.new_pai_marks = None
    if "new_sc_marks" not in st.session_state:
        st.session_state.new_sc_marks = None
    if "new_cn_marks" not in st.session_state:
        st.session_state.new_cn_marks = None
    if "new_oopj_marks" not in st.session_state:
        st.session_state.new_oopj_marks = None
    if "new_math_marks" not in st.session_state:
        st.session_state.new_math_marks = None
    if "new_roll_number" not in st.session_state:
        st.session_state.new_roll_number = ""
    if "new_name" not in st.session_state:
        st.session_state.new_name = ""

    if st.session_state.new_roll_number and st.session_state.new_name:
        new_row = pd.DataFrame({
            "Roll Number": [st.session_state.new_roll_number],
            "Name": [st.session_state.new_name],
            "Principles of AI": [st.session_state.new_pai_marks if st.session_state.new_pai_marks is not None else None],
            "Software Construction": [st.session_state.new_sc_marks if st.session_state.new_sc_marks is not None else None],
            "Computer Networks": [st.session_state.new_cn_marks if st.session_state.new_cn_marks is not None else None],
            "Object Oriented Programming Using Java": [st.session_state.new_oopj_marks if st.session_state.new_oopj_marks is not None else None],
            "Mathematics": [st.session_state.new_math_marks if st.session_state.new_math_marks is not None else None],
        })
        # Check if the roll number already exists
        if st.session_state.new_roll_number in st.session_state.master_df["Roll Number"].values:
            st.error(f"Roll Number '{st.session_state.new_roll_number}' already exists.")
        else:
            st.session_state.master_df = pd.concat([st.session_state.master_df, new_row], ignore_index=True)
            st.success(f"Marks for '{st.session_state.new_name}' added successfully!")
            # Clear the form inputs after successful submission
            st.session_state.new_roll_number = ""
            st.session_state.new_name = ""
            st.session_state.new_pai_marks = None
            st.session_state.new_sc_marks = None
            st.session_state.new_cn_marks = None
            st.session_state.new_oopj_marks = None
            st.session_state.new_math_marks = None
    else:
        st.error("Roll Number and Name are required.")


def staff_login_callback():
    staff = {
        "preethi": {"password": "rec", "subject": "POAI"},
        "kalpana": {"password": "rec", "subject": "SC"},
        "gunasekar": {"password": "rec", "subject": "CN"},
        "vijayakumar": {"password": "rec", "subject": "OOPJ"},
        "sriram": {"password": "rec", "subject": "Maths"},
    }

    if st.session_state.staff_username in staff and st.session_state.staff_password == staff[st.session_state.staff_username]["password"]:
        st.session_state.logged_in = True
        st.session_state.user_role = "staff"
        st.session_state.staff_subject = staff[st.session_state.staff_username]["subject"]
        st.success(f"{st.session_state.staff_username} login successful!")
    else:
        st.error("Invalid username or password.")

def student_login_callback():
    if st.session_state.student_roll in st.session_state.master_df["Roll Number"].astype(str).values and st.session_state.student_password == "rec":
        st.session_state.logged_in = True
        st.session_state.user_role = "student"
        st.session_state.student_roll_number = st.session_state.student_roll
        st.success("Student login successful!")
    else:
        st.error("Invalid Roll Number or Password.")

def admin_login_callback():
    if st.session_state.admin_username == "admin" and st.session_state.admin_password == "rec":
        st.session_state.logged_in = True
        st.session_state.user_role = "admin"
        st.success("Admin login successful!")
    else:
        st.error("Invalid username or password.")

def logout_callback():
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.student_roll_number = None
    st.session_state.staff_subject = None
    st.success("Logged out successfully!")

def login():
    st.title("Student Mark Management System")
    role = st.selectbox("Select your role:", ["Teacher", "Student", "Admin"], key="login_role")

    if role == "Teacher":
        username = st.text_input("Username:", key="staff_username")
        password = st.text_input("Password:", type="password", key="staff_password")
        login_button = st.button("Teacher Login", on_click=staff_login_callback)

    elif role == "Student":
        roll_number = st.text_input("Enter your Roll Number:", key="student_roll")
        password = st.text_input("Enter your Password:", type="password", key="student_password")
        login_button = st.button("View Marks", on_click=student_login_callback)

    elif role == "Admin":
        username = st.text_input("Admin Username:", key="admin_username")
        password = st.text_input("Admin Password:", type="password", key="admin_password")
        login_button = st.button("Admin Login", on_click=admin_login_callback)

def staff_dashboard():
    st.subheader(f"{st.session_state.staff_subject} Staff Dashboard")
    st.button("Logout", on_click=logout_callback)
    
    st.subheader(f"Enter {st.session_state.staff_subject} Marks")
    with st.form("subject_marks_form"):
        roll_number = st.text_input("Student Roll Number:", key="new_roll_number")
        name = st.text_input("Student Name:", key="new_name")
        if st.session_state.staff_subject == "POAI":
            marks = st.number_input("POAI Marks:", min_value=0, max_value=100, key="new_pai_marks")
        elif st.session_state.staff_subject == "SC":
            marks = st.number_input("SC Marks:", min_value=0, max_value=100, key="new_sc_marks")
        elif st.session_state.staff_subject == "CN":
            marks = st.number_input("CN Marks:", min_value=0, max_value=100, key="new_cn_marks")
        elif st.session_state.staff_subject == "OOPJ":
            marks = st.number_input("OOPJ Marks:", min_value=0, max_value=100, key="new_oopj_marks")
        elif st.session_state.staff_subject == "Maths":
            marks = st.number_input("Maths Marks:", min_value=0, max_value=100, key="new_math_marks")
        
        st.form_submit_button("Add Marks", on_click=add_marks)

def student_dashboard():
    st.subheader("Student Dashboard")
    st.button("Logout", on_click=logout_callback)
    
    if "student_roll_number" in st.session_state:
        roll_number = st.session_state.student_roll_number
        st.write(f"Welcome, Student with Roll Number: {roll_number}!")
        student_data = st.session_state.master_df[st.session_state.master_df["Roll Number"].astype(str) == roll_number].iloc[0]
        total_marks = calculate_total(student_data)

        st.subheader("Your Marks:")
        st.metric(label="POAI", value=student_data["POAI"] if pd.notna(student_data["POAI"]) else "N/A")
        st.metric(label="SC", value=student_data["SC"] if pd.notna(student_data["SC"]) else "N/A")
        st.metric(label="CN", value=student_data["CN"] if pd.notna(student_data["CN"]) else "N/A")
        st.metric(label="OOPJ", value=student_data["OOPJ"] if pd.notna(student_data["OOPJ"]) else "N/A")
        st.metric(label="Maths", value=student_data["Maths"] if pd.notna(student_data["Maths"]) else "N/A")
        st.metric(label="Total Marks", value=total_marks if total_marks is not None else "N/A")

def admin_dashboard():
    st.subheader("Admin (HoD) Dashboard")
    st.button("Logout", on_click=logout_callback)

    if not st.session_state.master_df.empty:
        st.subheader("Master Mark Table")
        st.session_state.master_df["Total"] = st.session_state.master_df.apply(calculate_total, axis=1)
        
        display_columns = {
            "Roll Number": "Roll No.",
            "Name": "Student Name",
            "POAI": "POAI",
            "SC": "SC",
            "CN": "CN",
            "OOPJ": "OOPJ",
            "Maths": "Maths",
            "Total": "Total Marks"
        }

        display_df = st.session_state.master_df.rename(columns=display_columns)
        st.dataframe(display_df)

def main():
    login()
    if st.session_state.logged_in:
        if st.session_state.user_role == "student":
            student_dashboard()
        elif st.session_state.user_role == "staff":
            staff_dashboard()
        elif st.session_state.user_role == "admin":
            admin_dashboard()

if __name__ == "__main__":
    main()
