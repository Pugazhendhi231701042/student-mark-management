# Complete Streamlit App with Updated Dashboards

import streamlit as st
import pandas as pd
import io
import zipfile
from fpdf import FPDF
import matplotlib.pyplot as plt
import seaborn as sns

# Initialize the session state dataframe
if "master_df" not in st.session_state:
    st.session_state.master_df = pd.DataFrame(
        columns=["Name", "POAI", "SC", "CN", "OOPJ", "Maths"]
    )
    st.session_state.master_df.index.name = "Roll Number"

# Helper function

def calculate_total(row):
    marks = row[["POAI", "SC", "CN", "OOPJ", "Maths"]].dropna()
    return marks.sum() if not marks.empty else None

def logout_callback():
    for key in ["role", "student_roll_number", "staff_subject"]:
        if key in st.session_state:
            del st.session_state[key]

def login():
    st.title("Student Marks Portal")
    role = st.selectbox("Login as", ["Student", "Staff", "Admin (HoD)"])
    if role == "Student":
        roll = st.number_input("Enter Roll Number", min_value=1, step=1)
        if st.button("Login"):
            if roll in st.session_state.master_df.index:
                st.session_state.role = "student"
                st.session_state.student_roll_number = roll
                st.rerun()
            else:
                st.error("Roll number not found.")

    elif role == "Staff":
        subject = st.selectbox("Select Subject", ["POAI", "SC", "CN", "OOPJ", "Maths"])
        if st.button("Login"):
            st.session_state.role = "staff"
            st.session_state.staff_subject = subject
            st.rerun()

    elif role == "Admin (HoD)":
        if st.button("Login"):
            st.session_state.role = "admin"
            st.rerun()

def staff_dashboard():
    st.subheader(f"{st.session_state.staff_subject} - Enter Marks")
    st.button("Logout", on_click=logout_callback)

    subject = st.session_state.staff_subject
    df = st.session_state.master_df
    students_df = df.reset_index()[["Roll Number", "Name"]].set_index("Roll Number")
    student_rolls = students_df.index.tolist()

    st.write(f"Enter marks for subject: **{subject}**")
    marks_data = {}
    with st.form(f"{subject}_marks_form"):
        for roll, name in students_df["Name"].items():
            marks_data[roll] = st.number_input(
                f"Marks for {name} ({roll}):",
                min_value=0,
                max_value=100,
                key=f"{subject}_{roll}",
                value=df.loc[roll, subject] if pd.notna(df.loc[roll, subject]) else 0,
            )

        if st.form_submit_button("Submit Marks"):
            updated_df = df.copy()
            for roll, mark in marks_data.items():
                updated_df.loc[roll, subject] = mark
            st.session_state.master_df = updated_df
            st.success(f"Marks for {subject} updated successfully!")

    # Subject Analytics
    st.subheader("Subject Analytics")
    subject_marks = df[subject].dropna()
    if not subject_marks.empty:
        st.metric("Average Mark", f"{subject_marks.mean():.2f}")
        st.metric("Highest Mark", f"{subject_marks.max():.0f}")
        st.metric("Lowest Mark", f"{subject_marks.min():.0f}")

        fig, ax = plt.subplots()
        sns.barplot(x=subject_marks.index.astype(str), y=subject_marks.values, ax=ax)
        ax.set_xlabel("Roll Number")
        ax.set_ylabel("Marks")
        ax.set_title(f"{subject} - Marks Distribution")
        st.pyplot(fig)
    else:
        st.info("No marks entered yet to display analytics.")

def student_dashboard():
    st.subheader("Your Marks")
    st.button("Logout", on_click=logout_callback)

    roll_number = int(st.session_state.student_roll_number)
    df = st.session_state.master_df
    student_data = df.loc[roll_number]
    total_marks = calculate_total(student_data)

    st.write(f"**Roll Number:** {roll_number}")
    st.write(f"**Name:** {student_data['Name']}")

    st.subheader("Subject-wise Marks:")
    subjects = ["POAI", "SC", "CN", "OOPJ", "Maths"]
    for col in subjects:
        st.metric(label=col, value=student_data[col] if pd.notna(student_data[col]) else "N/A")
    st.metric(label="Total Marks", value=total_marks if total_marks is not None else "N/A")

    st.subheader("Performance Analytics")
    subject_averages = df[subjects].mean()
    student_marks = student_data[subjects]

    fig, ax = plt.subplots()
    bar_width = 0.35
    index = range(len(subjects))
    ax.bar(index, student_marks, bar_width, label="Your Marks")
    ax.bar([i + bar_width for i in index], subject_averages, bar_width, label="Average Marks")
    ax.set_xticks([i + bar_width / 2 for i in index])
    ax.set_xticklabels(subjects)
    ax.set_ylabel("Marks")
    ax.set_title("Your Marks vs Average Marks")
    ax.legend()
    st.pyplot(fig)

    if st.button("Download Marksheet (PDF)"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Marksheet - Roll Number: {roll_number}", ln=1, align="C")
        pdf.cell(200, 10, txt=f"Name: {student_data['Name']}", ln=1, align="L")
        pdf.cell(200, 10, txt="----------------------------------------", ln=1, align="L")
        for col in subjects:
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
    if "role" not in st.session_state:
        login()
    elif st.session_state.role == "student":
        student_dashboard()
    elif st.session_state.role == "staff":
        staff_dashboard()
    elif st.session_state.role == "admin":
        admin_dashboard()

if __name__ == "__main__":
    main()
