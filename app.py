# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "student_roll_number" not in st.session_state:
    st.session_state.student_roll_number = None
if "master_df" not in st.session_state:
    st.session_state.master_df = pd.DataFrame(columns=["Roll Number", "Name", "Principles of AI", "Software Construction", "Computer Networks", "Object Oriented Programming Using Java", "Mathematics"])

# Teacher login for different subjects
teachers = {
    "POAI": "kalpana.d",
    "SC": "ravi.k",
    "CN": "raj.m",
    "OOPJ": "sita.p",
    "Maths": "arun.s"
}

# Admin (HoD) login credentials
admin_credentials = {"username": "hod", "password": "adminpass"}

# Student login credentials
students = {
    "2025CS101": {"password": "studentpass1"},
    "2025CS102": {"password": "studentpass2"},
    # Add more student roll numbers and passwords as needed
}

# Modified teacher login callback
def teacher_login_callback():
    if st.session_state.teacher_username in teachers.values() and st.session_state.teacher_password == "rec":
        st.session_state.logged_in = True
        st.session_state.user_role = "teacher"
        st.success("Teacher login successful!")
    else:
        st.error("Invalid username or password.")

# Modified student login callback
def student_login_callback():
    roll_number = str(st.session_state.student_roll)
    if roll_number in students and students[roll_number]["password"] == st.session_state.student_password:
        st.session_state.logged_in = True
        st.session_state.user_role = "student"
        st.session_state.student_roll_number = roll_number
        st.success("Student login successful!")
    else:
        st.error("Invalid Roll Number or Password.")

# Admin login callback
def admin_login_callback():
    if st.session_state.admin_username == admin_credentials["username"] and st.session_state.admin_password == admin_credentials["password"]:
        st.session_state.logged_in = True
        st.session_state.user_role = "admin"
        st.success("Admin login successful!")
    else:
        st.error("Invalid username or password.")

# Login function
def login():
    st.title("Student Mark Management System")
    role = st.selectbox("Select your role:", ["Teacher", "Student", "Admin"], key="login_role")

    if role == "Teacher":
        username = st.text_input("Username:", key="teacher_username")
        password = st.text_input("Password:", type="password", key="teacher_password")
        login_button = st.button("Teacher Login", on_click=teacher_login_callback)

    elif role == "Student":
        roll_number = st.text_input("Enter your Roll Number:", key="student_roll")
        password = st.text_input("Enter your Password:", type="password", key="student_password")
        login_button = st.button("Student Login", on_click=student_login_callback)

    elif role == "Admin":
        username = st.text_input("Username:", key="admin_username")
        password = st.text_input("Password:", type="password", key="admin_password")
        login_button = st.button("Admin Login", on_click=admin_login_callback)

# Teacher Dashboard
def teacher_dashboard():
    # Teacher-specific functionality as before
    pass  # Keep your existing teacher dashboard code here

# Student Dashboard
def student_dashboard():
    # Student-specific functionality as before
    pass  # Keep your existing student dashboard code here

# Admin Dashboard
def admin_dashboard():
    st.subheader("Admin (HoD) Dashboard")
    st.button("Logout", on_click=logout_callback)
    st.subheader("Master Mark Table")

    if not st.session_state.master_df.empty:
        st.session_state.master_df["Total"] = st.session_state.master_df.apply(calculate_total, axis=1)

        # Define the display column names
        display_columns = {
            "Roll Number": "Roll No.",
            "Name": "Student Name",
            "Principles of AI": "POAI",
            "Software Construction": "SC",
            "Computer Networks": "Comp. Networks",
            "Object Oriented Programming Using Java": "OOPJ",
            "Mathematics": "Maths",
            "Total": "Total Marks"
        }

        # Create a new DataFrame with renamed columns for display
        display_df = st.session_state.master_df.rename(columns=display_columns)
        st.dataframe(display_df)
    else:
        st.info("No student marks data available yet.")

# Logout callback
def logout_callback():
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.student_roll_number = None
    st.success("Logged out successfully!")

# Main App Flow
if not st.session_state.logged_in:
    login()
else:
    if st.session_state.user_role == "teacher":
        teacher_dashboard()
    elif st.session_state.user_role == "student":
        student_dashboard()
    elif st.session_state.user_role == "admin":
        admin_dashboard()
