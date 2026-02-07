import streamlit as st
import bcrypt
import json
import os

# Path to the JSON file storing user credentials
USERS_FILE = "users.json"

# Initialize users file if it doesn't exist
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)  # empty dict for no users

# Load users from file
def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

# Save users to file
def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

# Signup a new user
def signup(username, password):
    users = load_users()
    if username in users:
        return False  # User already exists
    # Hash the password before storing
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users[username] = hashed_pw
    save_users(users)
    return True

# Login existing user
def login(username, password):
    users = load_users()
    if username not in users:
        return False
    hashed_pw = users[username].encode()
    return bcrypt.checkpw(password.encode(), hashed_pw)

# Render login/signup page
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
                st.session_state["username"] = username
            else:
                st.error("Invalid username or password.")

