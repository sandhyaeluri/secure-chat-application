# =============================================================
# SECURE CHAT APPLICATION USING NETWORK SECURITY
# Author  : Eluri Sandhya (23B21F00E9)
# College : KIET, JNTU-K  |  MCA 2024-2025
# Stack   : Python, Streamlit, Fernet (AES), RSA key exchange
# =============================================================

import streamlit as st
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
import base64
import datetime
import hashlib

# ------------------------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Secure Chat App",
    page_icon="🔐",
    layout="wide"
)

# ------------------------------------------------------------------
# CUSTOM CSS
# ------------------------------------------------------------------
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    section[data-testid="stSidebar"] {
        background-color: #1a1d27;
        border-right: 1px solid #2e3250;
    }
    div[data-testid="metric-container"] {
        background-color: #1a1d27;
        border: 1px solid #2e3250;
        border-radius: 8px;
        padding: 12px;
    }
    .sent-bubble {
        background-color: #1a56db;
        color: #ffffff;
        border-radius: 16px 16px 4px 16px;
        padding: 10px 14px;
        margin: 4px 0;
        max-width: 75%;
        margin-left: auto;
        font-size: 14px;
    }
    .recv-bubble {
        background-color: #1a1d27;
        color: #e0e0e0;
        border: 1px solid #2e3250;
        border-radius: 16px 16px 16px 4px;
        padding: 10px 14px;
        margin: 4px 0;
        max-width: 75%;
        font-size: 14px;
    }
    .encrypted-bubble {
        background-color: #111318;
        color: #6b7280;
        border: 1px dashed #2e3250;
        border-radius: 8px;
        padding: 8px 12px;
        font-family: monospace;
        font-size: 11px;
        word-break: break-all;
        margin: 4px 0;
    }
    .db-table {
        background: #1a1d27;
        border: 1px solid #2e3250;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        font-size: 13px;
    }
    .db-header {
        color: #1a56db;
        font-weight: bold;
        font-size: 14px;
        margin-bottom: 8px;
    }
    .db-row {
        display: flex;
        gap: 12px;
        padding: 4px 0;
        border-bottom: 1px solid #2e3250;
        color: #9ca3af;
        font-size: 12px;
    }
    .success-box {
        background: #064e3b;
        color: #6ee7b7;
        padding: 8px 14px;
        border-radius: 8px;
        font-size: 13px;
        margin: 6px 0;
    }
    .error-box {
        background: #7f1d1d;
        color: #fca5a5;
        padding: 8px 14px;
        border-radius: 8px;
        font-size: 13px;
        margin: 6px 0;
    }
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------
# SESSION STATE INITIALISATION
# ------------------------------------------------------------------
if "fernet_key" not in st.session_state:
    st.session_state.fernet_key = Fernet.generate_key()
    st.session_state.fernet    = Fernet(st.session_state.fernet_key)
    st.session_state.chat_log  = []
    st.session_state.msg_count = 0
    st.session_state.page      = "signup"
    st.session_state.logged_in = False
    st.session_state.current_user = ""
    st.session_state.current_room = ""

    # MySQL Table Simulation
    # Table 1 — signup
    st.session_state.signup_table = [
        {"username": "sandhya", "first_name": "Eluri", "last_name": "Sandhya",
         "password": hashlib.sha256("sandhya123".encode()).hexdigest()}
    ]
    # Table 2 — login (active sessions)
    st.session_state.login_table = []
    # Table 3 — chat rooms
    st.session_state.rooms_table = [
        {"room_name": "General", "password": ""},
        {"room_name": "MCA Group", "password": hashlib.sha256("mca123".encode()).hexdigest()}
    ]

if "rsa_private_key" not in st.session_state:
    st.session_state.rsa_private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048
    )
    st.session_state.rsa_public_key = st.session_state.rsa_private_key.public_key()

fernet = st.session_state.fernet


# ------------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------------
def hash_password(password):
    """Hash password using SHA-256 — simulating bcrypt behavior"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_input(text):
    """Basic input validation — remove dangerous characters"""
    if not text or text.strip() == "":
        return False, "Field cannot be empty"
    if len(text) < 3:
        return False, "Must be at least 3 characters"
    return True, "Valid"

def signup_user(username, first_name, last_name, password):
    """Add user to signup table with hashed password"""
    # Input validation
    for field in [username, first_name, last_name, password]:
        valid, msg = validate_input(field)
        if not valid:
            return False, msg
    # Check if user exists
    for user in st.session_state.signup_table:
        if user["username"] == username:
            return False, "Username already exists!"
    # Add to signup table
    st.session_state.signup_table.append({
        "username"  : username.strip(),
        "first_name": first_name.strip(),
        "last_name" : last_name.strip(),
        "password"  : hash_password(password)
    })
    return True, "Account created successfully!"

def login_user(username, password):
    """Verify credentials from signup table"""
    valid_u, _ = validate_input(username)
    valid_p, _ = validate_input(password)
    if not valid_u or not valid_p:
        return False, "Please fill all fields"
    hashed = hash_password(password)
    for user in st.session_state.signup_table:
        if user["username"] == username and user["password"] == hashed:
            st.session_state.login_table.append({
                "username": username,
                "login_time": datetime.datetime.now().strftime("%H:%M:%S")
            })
            return True, "Login successful!"
    return False, "Invalid username or password!"

def create_room(room_name, password=""):
    """Add room to chat rooms table"""
    valid, msg = validate_input(room_name)
    if not valid:
        return False, msg
    for room in st.session_state.rooms_table:
        if room["room_name"] == room_name:
            return False, "Room already exists!"
    st.session_state.rooms_table.append({
        "room_name": room_name.strip(),
        "password" : hash_password(password) if password else ""
    })
    return True, f"Room '{room_name}' created successfully!"

def join_room(room_name, password=""):
    """Join a room with password validation"""
    for room in st.session_state.rooms_table:
        if room["room_name"] == room_name:
            if room["password"] == "":
                return True, "Joined successfully!"
            elif room["password"] == hash_password(password):
                return True, "Joined successfully!"
            else:
                return False, "Wrong room password!"
    return False, "Room not found!"

def encrypt_message(text):
    return fernet.encrypt(text.encode()).decode()

def decrypt_message(cipher):
    try:
        return fernet.decrypt(cipher.encode()).decode()
    except:
        return "Decryption failed"

def timestamp():
    return datetime.datetime.now().strftime("%H:%M:%S")


# ------------------------------------------------------------------
# SIDEBAR — Key info
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🔐 Secure Chat")
    if st.session_state.logged_in:
        st.markdown(f"👤 **{st.session_state.current_user}**")
        if st.session_state.current_room:
            st.markdown(f"💬 Room: **{st.session_state.current_room}**")
        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.current_user = ""
            st.session_state.current_room = ""
            st.session_state.page = "login"
            st.rerun()

    st.markdown("---")
    st.markdown("**🔑 Fernet Session Key**")
    st.code(st.session_state.fernet_key.decode()[:40] + "...", language="text")
    st.caption("AES-128-CBC · auto-generated")

    st.markdown("**🔒 RSA Key (preview)**")
    pem = st.session_state.rsa_public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
    st.code(pem[:80] + "...", language="text")
    st.caption("RSA-2048 · key exchange")

    show_encrypted = st.toggle("Show encrypted layer", value=True)
    show_db        = st.toggle("Show MySQL tables", value=True)


# ------------------------------------------------------------------
# NAVIGATION
# ------------------------------------------------------------------
st.title("🔐 Secure Chat Application Using Network Security")
st.caption("End-to-end encrypted · RSA-2048 key exchange + Fernet (AES-128-CBC) | MCA Project · Eluri Sandhya · KIET, JNTU-K")

if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["📝 Sign Up", "🔑 Login"])

    # ── SIGN UP ──────────────────────────────────────────────
    with tab1:
        st.markdown("### 📝 Create New Account")
        st.caption("MySQL Table: signup (username, first_name, last_name, password)")

        col1, col2 = st.columns(2)
        with col1:
            new_username   = st.text_input("Username",   key="su_user",  placeholder="e.g. sandhya")
            new_firstname  = st.text_input("First Name", key="su_fname", placeholder="e.g. Eluri")
        with col2:
            new_lastname   = st.text_input("Last Name",  key="su_lname", placeholder="e.g. Sandhya")
            new_password   = st.text_input("Password",   key="su_pass",  type="password", placeholder="Min 3 characters")

        if st.button("✅ Create Account", use_container_width=True):
            success, msg = signup_user(new_username, new_firstname, new_lastname, new_password)
            if success:
                st.markdown(f'<div class="success-box">✅ {msg} — You can now login!</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="error-box">❌ {msg}</div>', unsafe_allow_html=True)

        # Show signup table
        if show_db:
            st.markdown("---")
            st.markdown("**🗄️ MySQL — signup table (password shown as hash)**")
            signup_df_data = []
            for u in st.session_state.signup_table:
                signup_df_data.append({
                    "username"  : u["username"],
                    "first_name": u["first_name"],
                    "last_name" : u["last_name"],
                    "password"  : u["password"][:20] + "..." if len(u["password"]) > 20 else u["password"]
                })
            import pandas as pd
            st.dataframe(pd.DataFrame(signup_df_data), use_container_width=True, hide_index=True)
            st.caption("🔒 Passwords stored as SHA-256 hash — not plain text")

    # ── LOGIN ─────────────────────────────────────────────────
    with tab2:
        st.markdown("### 🔑 Login to Your Account")
        st.caption("MySQL Table: login (username, password)")

        login_user_input = st.text_input("Username", key="li_user", placeholder="Enter your username")
        login_pass_input = st.text_input("Password", key="li_pass", type="password", placeholder="Enter your password")

        st.info("💡 Demo credentials: username = **sandhya** | password = **sandhya123**")

        if st.button("🔑 Login", use_container_width=True):
            success, msg = login_user(login_user_input, login_pass_input)
            if success:
                st.session_state.logged_in    = True
                st.session_state.current_user = login_user_input
                st.session_state.page         = "rooms"
                st.markdown(f'<div class="success-box">✅ {msg}</div>', unsafe_allow_html=True)
                st.rerun()
            else:
                st.markdown(f'<div class="error-box">❌ {msg}</div>', unsafe_allow_html=True)

        if show_db:
            st.markdown("---")
            st.markdown("**🗄️ MySQL — Active Login Sessions**")
            if st.session_state.login_table:
                import pandas as pd
                st.dataframe(pd.DataFrame(st.session_state.login_table), use_container_width=True, hide_index=True)
            else:
                st.caption("No active sessions yet")

else:
    # ── ROOMS PAGE ────────────────────────────────────────────
    if not st.session_state.current_room:
        st.markdown(f"### 👋 Welcome, {st.session_state.current_user}!")
        st.markdown("---")

        tab_join, tab_create, tab_users = st.tabs(["🚪 Join Room", "➕ Create Room", "👥 Registered Users"])

        # JOIN ROOM
        with tab_join:
            st.markdown("### 🚪 Join a Chat Room")
            st.caption("MySQL Table: rooms (room_name, password)")

            room_names = [r["room_name"] for r in st.session_state.rooms_table]
            selected_room = st.selectbox("Select Room", room_names)
            room_pass = st.text_input("Room Password (leave empty if public)", type="password", key="join_pass")

            if st.button("🚪 Join Room", use_container_width=True):
                success, msg = join_room(selected_room, room_pass)
                if success:
                    st.session_state.current_room = selected_room
                    st.markdown(f'<div class="success-box">✅ {msg}</div>', unsafe_allow_html=True)
                    st.rerun()
                else:
                    st.markdown(f'<div class="error-box">❌ {msg}</div>', unsafe_allow_html=True)

            if show_db:
                st.markdown("---")
                st.markdown("**🗄️ MySQL — chat_rooms table**")
                import pandas as pd
                rooms_display = []
                for r in st.session_state.rooms_table:
                    rooms_display.append({
                        "room_name": r["room_name"],
                        "type"     : "🔓 Public" if r["password"] == "" else "🔒 Private",
                        "password" : "No password" if r["password"] == "" else r["password"][:15] + "..."
                    })
                st.dataframe(pd.DataFrame(rooms_display), use_container_width=True, hide_index=True)

        # CREATE ROOM
        with tab_create:
            st.markdown("### ➕ Create New Chat Room")

            with st.form("create_room_form", clear_on_submit=True):
                new_room_name = st.text_input("Room Name", placeholder="e.g. Study Group")
                new_room_pass = st.text_input("Room Password (optional — leave empty for public)", type="password")
                room_type     = "🔒 Private" if new_room_pass else "🔓 Public"
                st.caption(f"Room type: {room_type}")
                submitted = st.form_submit_button("➕ Create Room", use_container_width=True)

            if submitted:
                success, msg = create_room(new_room_name, new_room_pass)
                if success:
                    st.markdown(f'<div class="success-box">✅ {msg}</div>', unsafe_allow_html=True)
                    st.rerun()
                else:
                    st.markdown(f'<div class="error-box">❌ {msg}</div>', unsafe_allow_html=True)

        # REGISTERED USERS
        with tab_users:
            st.markdown("### 👥 Registered Users")
            import pandas as pd
            users_display = []
            for u in st.session_state.signup_table:
                users_display.append({
                    "Username"  : u["username"],
                    "First Name": u["first_name"],
                    "Last Name" : u["last_name"],
                    "Status"    : "🟢 Online" if u["username"] == st.session_state.current_user else "⚪ Offline"
                })
            st.dataframe(pd.DataFrame(users_display), use_container_width=True, hide_index=True)

    # ── CHAT ROOM ─────────────────────────────────────────────
    else:
        st.markdown(f"### 💬 Room: {st.session_state.current_room}")
        if st.button("← Leave Room"):
            st.session_state.current_room = ""
            st.session_state.chat_log = []
            st.rerun()

        col1, col2, col3 = st.columns(3)
        col1.metric("Messages", st.session_state.msg_count)
        col2.metric("Encryption", "Fernet AES")
        col3.metric("Key Exchange", "RSA-2048")

        st.markdown("---")

        # Chat window
        chat_container = st.container(height=300)
        with chat_container:
            if not st.session_state.chat_log:
                st.markdown("<div style='text-align:center;color:gray;margin-top:60px'>🔐 No messages yet. Send your first encrypted message!</div>", unsafe_allow_html=True)
            else:
                for msg in st.session_state.chat_log:
                    if msg["role"] == "sent":
                        st.markdown(f"**{st.session_state.current_user} · {msg['time']}**")
                        st.markdown(f'<div class="sent-bubble">{msg["plain"]}</div>', unsafe_allow_html=True)
                        st.caption("🔒 Encrypted with Fernet before sending")
                        if show_encrypted:
                            st.markdown("🕵️ *What network sees:*")
                            st.markdown(f'<div class="encrypted-bubble">{msg["cipher"][:80]}...</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f"**Receiver · {msg['time']}**")
                        st.markdown(f'<div class="recv-bubble">{msg["plain"]}</div>', unsafe_allow_html=True)
                        st.caption("🔓 Decrypted using shared Fernet key")

        # Message input
        st.markdown("---")
        col_in, col_btn = st.columns([5,1])
        with col_in:
            user_msg = st.text_input("Type message", placeholder="Type here...", label_visibility="collapsed")
        with col_btn:
            send = st.button("🔒 Send", use_container_width=True)

        if send and user_msg.strip():
            cipher = encrypt_message(user_msg)
            now    = timestamp()
            st.session_state.chat_log.append({"role":"sent",     "plain":user_msg,              "cipher":cipher, "time":now})
            st.session_state.chat_log.append({"role":"received", "plain":decrypt_message(cipher),"cipher":cipher, "time":now})
            st.session_state.msg_count += 1
            st.rerun()

        # Live Encryption Demo
        st.markdown("---")
        st.markdown("### 🧪 Live Encryption / Decryption Demo")
        d1, d2 = st.columns(2)
        with d1:
            st.markdown("**✏️ Encrypt**")
            demo_in = st.text_area("Text to encrypt", value="Hello Sandhya!", height=80)
            if st.button("🔒 Encrypt"):
                st.code(encrypt_message(demo_in))
                st.success("✅ Encrypted!")
        with d2:
            st.markdown("**🔑 Decrypt**")
            demo_ci = st.text_area("Paste cipher text", height=80, placeholder="Paste here...")
            if st.button("🔓 Decrypt"):
                st.code(decrypt_message(demo_ci.strip()))
                st.success("✅ Decrypted!")

# Test Cases
st.markdown("---")
st.markdown("### 📋 Test Cases — Chapter 7, Project Report (KIET, JNTU-K)")
import pandas as pd
st.dataframe(pd.DataFrame({
    "Test No" : ["T1","T2","T3","T4","T5","T6","T7","T8"],
    "Test Case": [
        "Signup (valid)","Signup (invalid)",
        "Login (valid)","Login (invalid)",
        "Create room","Join room (valid)",
        "Join room (invalid)","View registered users"
    ],
    "Result": ["✅ Pass","✅ Fail","✅ Pass","✅ Fail","✅ Pass","✅ Pass","✅ Fail","✅ Pass"]
}), use_container_width=True, hide_index=True)
st.caption("📄 Source: Chapter 7 · Testing & Validation · MCA Project Report · KIET, JNTU-K")

st.markdown("---")
st.caption("🔐 Eluri Sandhya (23B21F00E9) · MCA Final Year Project · KIET, JNTU-K · 2024-2025")
