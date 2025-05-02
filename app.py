import streamlit as st
import pandas as pd
from fpdf import FPDF
import io
import zipfile

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "staff_username" not in st.session_state:
    st.session_state.staff_username = None
if "student_roll_number" not in st.session_state:
    st.session_state.student_roll_number = None
if "master_df" not in st.session_state:
    student_data = {
        "Roll Number": [231701001, 231701002, 231701003, 231701004, 231701005],
        "Name": ["AADHITH KUMAR S V", "AASHISH P", "AKASH E", "ANISH D", "ARJUN V"],
        "POAI": [None] * 5,
        "SC": [None] * 5,
        "CN": [None] * 5,
        "OOPJ": [None] * 5,
        "Maths": [None] * 5,
    }
    st.session_state.master_df = pd.DataFrame(student_data).set_index("Roll Number")

STAFF_CREDENTIALS = {
    "preethi": {"password": "rec", "subject": "POAI"},
    "kalpana": {"password": "rec", "subject": "SC"},
    "gunasekar": {"password": "rec", "subject": "CN"},
    "vijayakumar": {"password": "rec", "subject": "OOPJ"},
    "sriram": {"password": "rec", "subject": "Maths"},
}

def calculate_total(row):
    marks = [row["POAI"], row["SC"], row["CN"], row["OOPJ"], row["Maths"]]
    valid_marks = [mark for mark in marks if mark is not None]
    return sum(valid_marks)

def staff_login_callback():
    if st.session_state.staff_username in STAFF_CREDENTIALS and st.session_state.staff_password == STAFF_CREDENTIALS[st.session_state.staff_username]["password"]:
        st.session_state.logged_in = True
        st.session_state.user_role = "staff"
        st.session_state.staff_subject = STAFF_CREDENTIALS[st.session_state.staff_username]["subject"]
        st.success(f"{st.session_state.staff_username} login successful for {st.session_state.staff_subject}!")
    else:
        st.error("Invalid username or password.")

def student_login_callback():
    if st.session_state.student_roll in st.session_state.master_df.index.astype(str).values and st.session_state.student_password == "rec":
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
    st.session_state.staff_username = None
    st.session_state.student_roll_number = None
    st.session_state.staff_subject = None
    st.success("Logged out successfully!")

def login():
    st.title("Student Mark Management System")
    role = st.selectbox("Select your role:", ["Teacher", "Student", "Admin"], key="login_role")

    if role == "Teacher":
        username = st.text_input("Username:", key="staff_username")
        password = st.text_input("Password:", type="password", key="staff_password")
        st.button("Teacher Login", on_click=staff_login_callback)

    elif role == "Student":
        roll_number = st.text_input("Enter your Roll Number:", key="student_roll")
        password = st.text_input("Enter your Password:", type="password", key="student_password")
        st.button("View Marks", on_click=student_login_callback)

    elif role == "Admin":
        username = st.text_input("Admin Username:", key="admin_username")
        password = st.text_input("Admin Password:", type="password", key="admin_password")
        st.button("Admin Login", on_click=admin_login_callback)

def staff_dashboard():
    st.subheader(f"{st.session_state.staff_subject} - Enter Marks")
    st.button("Logout", on_click=logout_callback)

    subject = st.session_state.staff_subject
    students_df = st.session_state.master_df.reset_index()[["Roll Number", "Name"]].set_index("Roll Number")

    st.write(f"Enter marks for subject: **{subject}**")
    marks_data = {}

    # Subject Analytics
    subject_marks = st.session_state.master_df[subject]
    st.subheader("Subject Analytics")
    st.write(f"Average: {subject_marks.mean():.2f}")
    st.write(f"Highest: {subject_marks.max()}")
    st.write(f"Lowest: {subject_marks.min()}")
    st.write(f"Missing Entries: {subject_marks.isna().sum()}")

    with st.form(f"{subject}_marks_form"):
        for roll, name in students_df["Name"].items():
            marks_data[roll] = st.number_input(
                f"Marks for {name} ({roll}):",
                min_value=0,
                max_value=100,
                key=f"{subject}_{roll}",
                value=st.session_state.master_df.loc[roll, subject] if pd.notna(st.session_state.master_df.loc[roll, subject]) else 0
            )

        if st.form_submit_button("Submit Marks"):
            updated_df = st.session_state.master_df.copy()
            for roll, mark in marks_data.items():
                updated_df.loc[roll, subject] = mark
            st.session_state.master_df = updated_df
            st.success(f"Marks for {subject} updated successfully!")

def student_dashboard():
    st.subheader("Your Marks")
    st.button("Logout", on_click=logout_callback)

    if "student_roll_number" in st.session_state:
        roll_number = st.session_state.student_roll_number
        student_data = st.session_state.master_df.loc[int(roll_number)]
        total_marks = calculate_total(student_data)

        st.write(f"**Roll Number:** {roll_number}")
        st.write(f"**Name:** {student_data['Name']}")

        st.subheader("Subject-wise Marks:")
        for col in ["POAI", "SC", "CN", "OOPJ", "Maths"]:
            st.metric(label=col, value=student_data[col] if pd.notna(student_data[col]) else "N/A")

        st.metric(label="Total Marks", value=total_marks if total_marks is not None else "N/A")

        # Class average comparison
        class_avg = st.session_state.master_df[["POAI", "SC", "CN", "OOPJ", "Maths"]].mean(numeric_only=True)
        st.subheader("Class Average Comparison:")
        for col in ["POAI", "SC", "CN", "OOPJ", "Maths"]:
            student_mark = student_data[col] if pd.notna(student_data[col]) else 0
            avg = class_avg[col]
            st.metric(label=f"{col} - Class Average", value=f"{avg:.2f}", delta=student_mark - avg)

        if st.button("Download Marksheet (PDF)"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Marksheet - Roll Number: {roll_number}", ln=1, align="C")
            pdf.cell(200, 10, txt=f"Name: {student_data['Name']}", ln=1, align="L")
            pdf.cell(200, 10, txt="----------------------------------------", ln=1, align="L")
            for col in ["POAI", "SC", "CN", "OOPJ", "Maths"]:
                mark = student_data[col] if pd.notna(student_data[col]) else "N/A"
                pdf.cell(200, 10, txt=f"{col}: {mark}", ln=1, align="L")
            pdf.cell(200, 10, txt="----------------------------------------", ln=1, align="L")
            pdf.cell(200, 10, txt=f"Total Marks: {total_marks if total_marks is not None else 'N/A'}", ln=1, align="L")

            pdf_bytes = pdf.output(dest="S").encode("latin-1")
            st.download_button(
                label="Download PDF",
                data=pdf_bytes,
                file_name=f"marksheet_{roll_number}.pdf",
                mime="application/pdf",
            )

def admin_dashboard():
    st.subheader("Admin (HoD) Dashboard")
    st.button("Logout", on_click=logout_callback)

    st.subheader("Add New Student")
    with st.form("add_student_form"):
        new_roll_number = st.number_input("New Student Roll Number:", min_value=1, step=1)
        new_student_name = st.text_input("New Student Name:")
        add_button = st.form_submit_button("Add Student")

        if add_button:
            if new_roll_number in st.session_state.master_df.index:
                st.error(f"Roll Number {new_roll_number} already exists.")
            elif new_student_name:
                new_student_data = pd.DataFrame({
                    "Name": [new_student_name],
                    "POAI": [None],
                    "SC": [None],
                    "CN": [None],
                    "OOPJ": [None],
                    "Maths": [None],
                }, index=[new_roll_number])
                st.session_state.master_df = pd.concat([st.session_state.master_df, new_student_data])
                st.success(f"Student '{new_student_name}' with Roll Number {new_roll_number} added successfully!")
            else:
                st.error("Student Name cannot be empty.")

    if not st.session_state.master_df.empty:
        st.subheader("Master Mark Table")
        master_df_with_total = st.session_state.master_df.copy()
        master_df_with_total["Total"] = master_df_with_total.apply(calculate_total, axis=1)
        st.dataframe(master_df_with_total)

        st.subheader("Analytics Overview")
        st.write("### Subject-wise Averages")
        avg_df = master_df_with_total[["POAI", "SC", "CN", "OOPJ", "Maths"]].mean().reset_index()
        avg_df.columns = ["Subject", "Average"]
        st.dataframe(avg_df)

        st.write("### Performance Chart")
        chart_data = master_df_with_total[["POAI", "SC", "CN", "OOPJ", "Maths"]]
        st.bar_chart(chart_data)

        st.write("### Total Marks Distribution")
        st.line_chart(master_df_with_total["Total"])

        st.subheader("Download Options")
        col1, col2 = st.columns(2)
        with col1:
            def download_xlsx():
                output = io.BytesIO()
                master_df_with_total.to_excel(output, index=True, sheet_name="Student Marks")
                return output.getvalue()

            xlsx_file = download_xlsx()
            st.download_button(
                label="Download All Marks (XLSX)",
                data=xlsx_file,
                file_name="all_student_marks.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        with col2:
            if st.button("Download All Marksheets (ZIP)"):
                pdf_bytes_list = []
                for roll, row in st.session_state.master_df.iterrows():
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    pdf.cell(200, 10, txt=f"Marksheet - Roll Number: {roll}", ln=1, align="C")
                    pdf.cell(200, 10, txt=f"Name: {row['Name']}", ln=1, align="L")
                    pdf.cell(200, 10, txt="----------------------------------------", ln=1, align="L")
                    for col in ["POAI", "SC", "CN", "OOPJ", "Maths"]:
                        mark = row[col] if pd.notna(row[col]) else "N/A"
                        pdf.cell(200, 10, txt=f"{col}: {mark}", ln=1, align="L")
                    pdf.cell(200, 10, txt="----------------------------------------", ln=1, align="L")
                    total_marks = calculate_total(row)
                    pdf.cell(200, 10, txt=f"Total Marks: {total_marks if total_marks is not None else 'N/A'}", ln=1, align="L")
                    pdf_bytes_list.append(pdf.output(dest="S").encode("latin-1"))

                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                    for i, pdf_bytes in enumerate(pdf_bytes_list):
                        roll_number = st.session_state.master_df.index[i]
                        zf.writestr(f"marksheet_{roll_number}.pdf", pdf_bytes)

                st.download_button(
                    label="Download All Marksheets (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name="all_marksheets.zip",
                    mime="application/zip",
                )

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
