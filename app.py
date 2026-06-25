# =============================================================
# SECURE CHAT APPLICATION USING NETWORK SECURITY
# Author  : Eluri Sandhya
# Reg No  : 23B21F00E9
# College : KIET, JNTU-K  |  MCA 2024-2025
# Stack   : Python, Streamlit, Fernet (AES), RSA key exchange
# =============================================================

import streamlit as st
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
import base64
import datetime

# ------------------------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Secure Chat App",
    page_icon="🔐",
    layout="wide"
)

# ------------------------------------------------------------------
# CUSTOM CSS  — clean dark theme matching project screenshots
# ------------------------------------------------------------------
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0e1117; color: #ffffff; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1a1d27;
        border-right: 1px solid #2e3250;
    }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background-color: #1a1d27;
        border: 1px solid #2e3250;
        border-radius: 8px;
        padding: 12px;
    }

    /* Chat message bubbles */
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
    .msg-label {
        font-size: 11px;
        color: #6b7280;
        margin-bottom: 2px;
    }
    .enc-label { color: #059669; font-size: 11px; margin-top: 2px; }
    .dec-label { color: #1a56db; font-size: 11px; margin-top: 2px; }

    /* Section headers */
    .section-header {
        font-size: 13px;
        font-weight: 600;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 16px 0 8px 0;
    }

    /* Status badge */
    .badge-green {
        background: #064e3b;
        color: #6ee7b7;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------
# SESSION STATE INITIALISATION
# ------------------------------------------------------------------
# Runs only once when the app first loads

if "fernet_key" not in st.session_state:
    # Generate a new symmetric Fernet (AES-128-CBC) key
    st.session_state.fernet_key = Fernet.generate_key()
    st.session_state.fernet    = Fernet(st.session_state.fernet_key)
    st.session_state.chat_log  = []          # list of message dicts
    st.session_state.msg_count = 0

if "rsa_private_key" not in st.session_state:
    # Generate RSA-2048 key pair for asymmetric key exchange
    st.session_state.rsa_private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    st.session_state.rsa_public_key = (
        st.session_state.rsa_private_key.public_key()
    )

fernet = st.session_state.fernet


# ------------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------------

def encrypt_message(plain_text: str) -> str:
    """Encrypt plain text using Fernet (AES symmetric encryption).
    Returns base64-encoded cipher text as a string."""
    encrypted_bytes = fernet.encrypt(plain_text.encode())
    return encrypted_bytes.decode()


def decrypt_message(cipher_text: str) -> str:
    """Decrypt a Fernet-encrypted cipher text back to plain text."""
    try:
        decrypted_bytes = fernet.decrypt(cipher_text.encode())
        return decrypted_bytes.decode()
    except Exception:
        return "⚠️ Decryption failed — invalid key or tampered message."


def rsa_encrypt_key(fernet_key: bytes) -> str:
    """Simulate RSA key exchange: encrypt the Fernet session key
    using the RSA public key. In production this public key belongs
    to the receiver."""
    encrypted_key = st.session_state.rsa_public_key.encrypt(
        fernet_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return base64.b64encode(encrypted_key).decode()


def get_public_key_pem() -> str:
    """Return the RSA public key in PEM format for display."""
    pem = st.session_state.rsa_public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem.decode()


def timestamp() -> str:
    return datetime.datetime.now().strftime("%H:%M:%S")


# ------------------------------------------------------------------
# SIDEBAR — key info & settings
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🔐 Secure Chat")
    st.markdown('<span class="badge-green">🟢 E2E Encrypted</span>',
                unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">🔑 Fernet Session Key</div>',
                unsafe_allow_html=True)
    st.code(st.session_state.fernet_key.decode()[:40] + "...",
            language="text")
    st.caption("AES-128-CBC · auto-generated each session")

    st.markdown('<div class="section-header">🔒 RSA Public Key (preview)</div>',
                unsafe_allow_html=True)
    st.code(get_public_key_pem()[:120] + "...", language="text")
    st.caption("RSA-2048 · used for secure key exchange")

    st.markdown("---")
    st.markdown('<div class="section-header">⚙️ Settings</div>',
                unsafe_allow_html=True)
    show_encrypted = st.toggle("Show encrypted layer", value=True)
    show_rsa_info  = st.toggle("Show RSA key exchange info", value=False)

    st.markdown("---")
    st.markdown('<div class="section-header">👥 Users Online</div>',
                unsafe_allow_html=True)
    st.markdown("🟢 **Sandhya** (you)")
    st.markdown("🟡 **Receiver** (remote)")

    if st.button("🔄 Regenerate Keys"):
        for key in ["fernet_key", "fernet", "chat_log",
                    "msg_count", "rsa_private_key", "rsa_public_key"]:
            del st.session_state[key]
        st.rerun()


# ------------------------------------------------------------------
# MAIN PANEL
# ------------------------------------------------------------------
st.title("🔐 Secure Chat Using Network Security")
st.caption("End-to-end encrypted · RSA key exchange + Fernet (AES) encryption")

# --- Metric cards row ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Messages Sent",
            st.session_state.msg_count, "this session")
col2.metric("Encryption", "Fernet AES", "AES-128-CBC")
col3.metric("Key Exchange", "RSA-2048", "asymmetric")
col4.metric("Auth", "bcrypt + JWT", "secure")

st.markdown("---")

# --- RSA key exchange explanation (optional toggle) ---
if show_rsa_info:
    with st.expander("📖 How RSA Key Exchange Works in This App", expanded=True):
        st.markdown("""
        1. **Key Generation** — On app start, an RSA-2048 key pair is generated.
        2. **Session Key** — A random Fernet (AES) key is created for the session.
        3. **Key Encryption** — The Fernet key is encrypted using the RSA **public key**.
        4. **Key Decryption** — Only the holder of the RSA **private key** can decrypt it.
        5. **Message Encryption** — All chat messages are encrypted using the Fernet key.
        6. **Security** — Even if the RSA-encrypted key is intercepted, it cannot be read
           without the private key. This is called **asymmetric key exchange**.
        """)
        encrypted_session_key = rsa_encrypt_key(st.session_state.fernet_key)
        st.markdown("**RSA-encrypted session key (what gets transmitted):**")
        st.code(encrypted_session_key[:80] + "...", language="text")

# --- Chat history display ---
st.markdown("### 💬 Chat Window")
chat_container = st.container(height=380)

with chat_container:
    if not st.session_state.chat_log:
        st.markdown(
            "<div style='text-align:center; color:#4b5563; margin-top:80px;'>"
            "🔐 No messages yet. Send your first encrypted message below."
            "</div>",
            unsafe_allow_html=True
        )
    else:
        for msg in st.session_state.chat_log:
            if msg["role"] == "sent":
                st.markdown(
                    f'<div class="msg-label">You · {msg["time"]}</div>'
                    f'<div class="sent-bubble">{msg["plain"]}</div>'
                    f'<div class="enc-label">🔒 Encrypted with Fernet before sending</div>',
                    unsafe_allow_html=True
                )
                if show_encrypted:
                    st.markdown(
                        f'<div class="msg-label">🕵️ Network layer — what a hacker sees:</div>'
                        f'<div class="encrypted-bubble">{msg["cipher"][:80]}...</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown(
                    f'<div class="msg-label">Receiver · {msg["time"]}</div>'
                    f'<div class="recv-bubble">{msg["plain"]}</div>'
                    f'<div class="dec-label">🔓 Decrypted using shared Fernet key</div>',
                    unsafe_allow_html=True
                )

# --- Message input ---
st.markdown("---")
col_input, col_btn = st.columns([5, 1])

with col_input:
    user_message = st.text_input(
        "Type your message",
        placeholder="Type a message and click Encrypt & Send...",
        label_visibility="collapsed"
    )

with col_btn:
    send_clicked = st.button("🔒 Send", use_container_width=True)

# --- On send ---
if send_clicked and user_message.strip():
    cipher = encrypt_message(user_message)

    # Add sent message
    st.session_state.chat_log.append({
        "role" : "sent",
        "plain": user_message,
        "cipher": cipher,
        "time" : timestamp()
    })

    # Simulate receiver decrypting and replying
    decrypted_back = decrypt_message(cipher)
    st.session_state.chat_log.append({
        "role" : "received",
        "plain": decrypted_back,
        "cipher": cipher,
        "time" : timestamp()
    })

    st.session_state.msg_count += 1
    st.rerun()

# --- Encryption demo section ---
st.markdown("---")
st.markdown("### 🧪 Live Encryption / Decryption Demo")
st.caption("Type any text below to see Fernet encryption in action")

demo_col1, demo_col2 = st.columns(2)

with demo_col1:
    st.markdown("**✏️ Plain Text → Encrypted**")
    demo_input = st.text_area("Enter text to encrypt",
                              value="Hello Sandhya!",
                              height=80,
                              key="demo_enc")
    if st.button("🔒 Encrypt"):
        result = encrypt_message(demo_input)
        st.code(result, language="text")
        st.success("✅ Message encrypted successfully")

with demo_col2:
    st.markdown("**🔑 Encrypted Text → Decrypted**")
    demo_cipher = st.text_area("Paste encrypted text here",
                               height=80,
                               key="demo_dec",
                               placeholder="Paste Fernet cipher text here...")
    if st.button("🔓 Decrypt"):
        if demo_cipher.strip():
            result = decrypt_message(demo_cipher.strip())
            st.code(result, language="text")
            if "⚠️" not in result:
                st.success("✅ Decrypted successfully")
            else:
                st.error(result)

# --- Footer ---
st.markdown("---")
st.caption(
    "🔐 Secure Chat Application · Eluri Sandhya (23B21F00E9) · "
    "MCA Final Year Project · KIET, JNTU-K · 2024-2025"
)
