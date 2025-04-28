import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from io import BytesIO

# Constants
TEACHER_CREDENTIALS = {"username": "teacher", "password": "password123"}

# Initialize session state variables
for key in ["logged_in", "user_role", "student_roll_number", "master_df"]:
    if key not in st.session_state:
        st.session_state[key] = False if key != "master_df" else pd.DataFrame(
            columns=["Roll Number", "Name", "Principles of AI", "Software Construction", "Computer Networks", "Object Oriented Programming Using Java", "Mathematics"]
        )

# Function to calculate total marks
def calculate_total(row):
    marks = [row["Principles of AI"], row["Software Construction"], row["Computer Networks"], row["Object Oriented Programming Using Java"], row["Mathematics"]]
    valid_marks = [mark for mark in marks if mark is not None]
    return sum(valid_marks)

def teacher_login_callback():
    if st.session_state.teacher_username == TEACHER_CREDENTIALS["username"] and st.session_state.teacher_password == TEACHER_CREDENTIALS["password"]:
        st.session_state.logged_in = True
        st.session_state.user_role = "teacher"
        st.toast("Teacher login successful!", icon="✅")
    else:
        st.error("Invalid username or password.")

def student_login_callback():
    if st.session_state.student_roll in st.session_state.master_df["Roll Number"].astype(str).values:
        st.session_state.logged_in = True
        st.session_state.user_role = "student"
        st.session_state.student_roll_number = st.session_state.student_roll
        st.toast("Student login successful!", icon="✅")
    else:
        st.error("Invalid Roll Number.")

def logout_callback():
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.student_roll_number = None
    st.toast("Logged out successfully!", icon="👋")

def add_or_update_marks(new=True):
    if st.session_state.new_roll_number and st.session_state.new_name:
        new_row = pd.DataFrame({
            "Roll Number": [st.session_state.new_roll_number],
            "Name": [st.session_state.new_name],
            "Principles of AI": [st.session_state.new_pai_marks],
            "Software Construction": [st.session_state.new_sc_marks],
            "Computer Networks": [st.session_state.new_cn_marks],
            "Object Oriented Programming Using Java": [st.session_state.new_oopj_marks],
            "Mathematics": [st.session_state.new_math_marks],
        })

        if new:
            if st.session_state.new_roll_number in st.session_state.master_df["Roll Number"].values:
                st.error(f"Roll Number '{st.session_state.new_roll_number}' already exists.")
            else:
                st.session_state.master_df = pd.concat([st.session_state.master_df, new_row], ignore_index=True)
                st.success("New student marks added successfully!")
        else:
            idx = st.session_state.master_df[st.session_state.master_df["Roll Number"] == st.session_state.new_roll_number].index[0]
            st.session_state.master_df.iloc[idx] = new_row.iloc[0]
            st.success("Student marks updated successfully!")

def delete_student(roll_no):
    st.session_state.master_df = st.session_state.master_df[st.session_state.master_df["Roll Number"] != roll_no]
    st.success(f"Deleted student with Roll Number: {roll_no}")

def login_page():
    st.title("🎓 Student Mark Management System")
    role = st.selectbox("Select your role:", ["Teacher", "Student"], key="login_role")

    if role == "Teacher":
        st.text_input("Username:", key="teacher_username")
        st.text_input("Password:", type="password", key="teacher_password")
        st.button("Teacher Login", on_click=teacher_login_callback)

    elif role == "Student":
        st.text_input("Enter your Roll Number:", key="student_roll")
        st.button("View Marks", on_click=student_login_callback)

def teacher_dashboard():
    colA, colB = st.columns([7,1])
    with colA:
        st.subheader("🧑‍🏫 Teacher Dashboard")
    with colB:
        st.button("Logout", on_click=logout_callback)

    st.markdown("---")

    if not st.session_state.master_df.empty:
        df = st.session_state.master_df.copy()
        df["Total"] = df.apply(calculate_total, axis=1)
        df["Percentage"] = df["Total"] / 5

        display_df = df.rename(columns={
            "Roll Number": "Roll No.",
            "Name": "Student Name",
            "Principles of AI": "POAI",
            "Software Construction": "SC",
            "Computer Networks": "CN",
            "Object Oriented Programming Using Java": "OOPJ",
            "Mathematics": "Maths",
            "Total": "Total Marks",
            "Percentage": "Percentage (%)"
        })
        st.dataframe(display_df)

        st.subheader("📊 Data Analysis")
        col1, col2 = st.columns(2)

        with col1:
            st.write("Average Marks per Subject")
            avg_marks = df[["Principles of AI", "Software Construction", "Computer Networks", "Object Oriented Programming Using Java", "Mathematics"]].mean()
            st.bar_chart(avg_marks)

        with col2:
            st.write("Total Marks Distribution")
            fig = px.histogram(df, x="Total", nbins=10)
            st.plotly_chart(fig)

        st.subheader("🏆 Top Performers")
        top3 = df.sort_values(by="Total", ascending=False).head(3)[["Roll Number", "Name", "Total", "Percentage"]]
        st.dataframe(top3)

        st.subheader("⬇️ Download Full Data")
        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        st.download_button(
            "Download Excel",
            data=buffer,
            file_name="master_marks.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    else:
        st.info("No data available yet.")

    st.subheader("➕ Add / Edit Student Marks")
    with st.form("marks_form"):
        st.text_input("Roll Number:", key="new_roll_number")
        st.text_input("Name:", key="new_name")
        st.number_input("POAI Marks:", min_value=0, max_value=100, key="new_pai_marks")
        st.number_input("SC Marks:", min_value=0, max_value=100, key="new_sc_marks")
        st.number_input("CN Marks:", min_value=0, max_value=100, key="new_cn_marks")
        st.number_input("OOPJ Marks:", min_value=0, max_value=100, key="new_oopj_marks")
        st.number_input("Maths Marks:", min_value=0, max_value=100, key="new_math_marks")

        cols = st.columns(2)
        with cols[0]:
            st.form_submit_button("Add Marks", on_click=lambda: add_or_update_marks(new=True))
        with cols[1]:
            st.form_submit_button("Update Marks", on_click=lambda: add_or_update_marks(new=False))

    st.subheader("🗑️ Delete Student")
    delete_roll = st.text_input("Enter Roll Number to Delete:")
    if st.button("Delete Student"):
        if delete_roll in st.session_state.master_df["Roll Number"].astype(str).values:
            delete_student(delete_roll)
        else:
            st.error("Roll Number not found!")

def student_dashboard():
    colA, colB = st.columns([7,1])
    with colA:
        st.subheader("🎓 Student Dashboard")
    with colB:
        st.button("Logout", on_click=logout_callback)

    roll = st.session_state.student_roll_number
    df = st.session_state.master_df
    if roll in df["Roll Number"].astype(str).values:
        student = df[df["Roll Number"].astype(str) == roll].iloc[0]
        total = calculate_total(student)
        percentage = total / 5 if total else 0

        st.markdown(f"### Welcome, {student['Name']}!")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Marks", total)
        with col2:
            st.metric("Percentage", f"{percentage:.2f}%")

        marks = {
            "POAI": student["Principles of AI"],
            "SC": student["Software Construction"],
            "CN": student["Computer Networks"],
            "OOPJ": student["Object Oriented Programming Using Java"],
            "Maths": student["Mathematics"]
        }

        st.subheader("📚 Your Marks")
        st.bar_chart(marks)

        # PDF Download
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Marks for {student['Name']} (Roll No: {roll})", ln=True, align="C")
        for sub, mark in marks.items():
            pdf.cell(100, 10, txt=f"{sub}:", border=1)
            pdf.cell(40, 10, txt=str(mark), border=1, ln=True)
        pdf.cell(100, 10, txt="Total Marks:", border=1)
        pdf.cell(40, 10, txt=str(total), border=1, ln=True)
        pdf.cell(100, 10, txt="Percentage:", border=1)
        pdf.cell(40, 10, txt=f"{percentage:.2f}%", border=1, ln=True)

        st.download_button(
            "Download PDF Report",
            data=bytes(pdf.output(dest="S")),
            file_name=f"marks_{roll}.pdf",
            mime="application/pdf"
        )
    else:
        st.error("Student data not found.")

# Main flow
if not st.session_state.logged_in:
    login_page()
else:
    if st.session_state.user_role == "teacher":
        teacher_dashboard()
    elif st.session_state.user_role == "student":
        student_dashboard()
