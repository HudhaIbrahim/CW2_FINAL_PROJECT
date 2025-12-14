import streamlit as st
import sys
from pathlib import Path

# parent directory to python path 
parent_path = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(parent_path))


from app.services.auth_manager import AuthManager
from app.data.users import User

st.set_page_config(
    page_title="Login / Register",
    page_icon="🔑",
    layout="centered"
)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""

st.title("🔐 Welcome")

# If already logged in, go straight to dashboard (optional)
if st.session_state.logged_in:
    st.success(f"Logged in as **{st.session_state.username}**.")
    page_choice = st.selectbox(
        "Select Dashboard",
        [
            "Cybersecurity Dashboard",
            "Data Science Dashboard",
            "IT Operations Dashboard",
        ],
    )

    if st.button("Go", type="primary"):
        if page_choice == "Cybersecurity Dashboard":
            st.switch_page("pages/Cybersecurity.py")
        elif page_choice == "Data Science Dashboard":
            st.switch_page("pages/Data_Science.py")
        elif page_choice == "IT Operations Dashboard":
            st.switch_page("pages/IT_Operations.py")



    st.stop()  

# Login / Register Tabs
tab_login, tab_register = st.tabs(["Login", "Register"])

# Login tab
with tab_login:
    st.subheader("Login")
    login_username = st.text_input("Username",key="login_username")
    login_password = st.text_input("Password", type="password",key="login_password")
    if st.button("Log in", type="primary"):
        if not login_username or not login_password:
            st.error("Please enter both username and password.")
        else:
            
            success, message = AuthManager.login_user(login_username, login_password)
            if success:
                # Fetch user data to get roles and other info
                user = User.get_user_by_username(login_username)
                st.session_state.logged_in = True
                st.session_state.username = user[1]  # username column
                st.session_state.role = user[3]      # role column
                st.rerun()
            else:
                # Either username not found or wrong password
                st.error("Invalid username or password. Please register if you don't have an account.")

# Register tab
with tab_register:
     st.subheader("Register")
     new_username = st.text_input("Choose a username", key="register_username")
     new_password = st.text_input("Choose a password", type="password", key="register_password")
     confirm_password = st.text_input("Confirm password", type="password", key="register_confirm")
     new_role = st.selectbox("Choose a role", ["user", "admin", "analyst"], key="register_role")
     if st.button("Create account", type="primary"):
         if not new_username or not new_password:
             st.warning("Please enter username and password.")
         elif new_password != confirm_password:
             st.error("Passwords do not match.")
         else:
             # Validate username and password
             username_valid, username_msg = AuthManager.validate_username(new_username)
             if not username_valid:
                st.error(username_msg)
             else:
                ok , msg = AuthManager.validate_password(new_password)
                if not ok:
                    st.error(msg)
                else:
                    existing = User.get_user_by_username(new_username)
                    if existing: #not none
                        st.error("Username already exists. Choose another username.")
                    else:
                        success, msg = AuthManager.register_user(new_username, new_password,new_role)
                        st.success("Account created! You can now log in.")