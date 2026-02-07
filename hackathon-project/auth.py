import streamlit as st
import bcrypt
import json
import os

USERS_FILE = "users.json"

# Initialize users.json if it doesn't exist
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def signup(username, password):
    users = load_users()
    if username in users:
        return False
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users[username] = hashed_pw
    save_users(users)
    return True

def login(username, password):
    users = load_users()
    if username not in users:
        return False
    hashed_pw = users[username].encode()
    return bcrypt.checkpw(password.encode(), hashed_pw)

def render():
    st.title("Login / Signup")

    menu = ["Login", "Signup"]
    choice = st.selectbox("Select Action", menu)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if choice == "Signup":
        if st.button("Create Account"):
            if signup(username, password):
                st.success("Account created! You can now login.")
            else:
                st.error("Username already exists.")

    elif choice == "Login":
        if st.button("Login"):
            if login(username, password):
                st.success(f"Welcome {username}!")
                # Update session state
                st.session_state.logged_in = True
                st.session_state.user = username
                # Instead of calling experimental_rerun here, set a flag
                st.session_state.login_success = True
            else:
                st.error("Invalid username or password.")


