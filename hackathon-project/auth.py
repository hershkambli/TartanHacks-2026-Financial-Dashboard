import streamlit as st
import sqlite3
import bcrypt

# ---------- Database Connection ----------
def get_connection():
    return sqlite3.connect("users.db")

# ---------- Signup Function ----------
def signup(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# ---------- Login Function ----------
def login(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    data = c.fetchone()
    conn.close()
    if data and bcrypt.checkpw(password.encode(), data[0]):
        return True
    return False

# ---------- Streamlit Login/Signup UI ----------
def render():
    st.title("Login / Signup")
    menu = ["Login", "Signup"]
    choice = st.selectbox("Select", menu)

    if choice == "Signup":
        st.subheader("Create a new account")
        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")
        if st.button("Signup"):
            if signup(new_user, new_pass):
                st.success("Account created! You can now login.")
            else:
                st.error("Username already exists!")

    elif choice == "Login":
        st.subheader("Login to your account")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if login(username, password):
                st.success(f"Welcome {username}!")
                st.session_state.logged_in = True
                st.session_state.user = username
            else:
                st.error("Invalid username or password")
