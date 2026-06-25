# 🔐 Secure Chat Application Using Network Security

> MCA Final Year Project · Eluri Sandhya (23B21F00E9) · KIET, JNTU-K · 2024-2025

A real-time **end-to-end encrypted** chat application built with Python and Streamlit.  
Messages are encrypted using **Fernet (AES-128-CBC)** and the session key is exchanged securely using **RSA-2048** asymmetric encryption — so no one in between can read your messages.

---

## 🚀 Live Demo

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-link.streamlit.app)

> (https://secure-chat-application-jkjacwfpvtgxykhhjrukfy.streamlit.app/)

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend / UI | Python, Streamlit |
| Message Encryption | Fernet (AES-128-CBC) |
| Key Exchange | RSA-2048 (asymmetric) |
| Password Hashing | bcrypt |
| Session Auth | JWT tokens |
| Database | MySQL (signup, login, chat rooms) |
| Security Testing | SQL injection & XSS prevention |
| Load Testing | Apache JMeter (1,000 users @ 220ms) |

---

## ✨ Features

- 🔒 **End-to-end encryption** — every message is encrypted before leaving the device
- 🔑 **RSA key exchange** — session key is shared securely using asymmetric encryption
- 👤 **User authentication** — bcrypt hashed passwords + JWT session tokens
- 🛡️ **Security hardened** — protected against SQL injection and XSS attacks
- 📊 **Live encryption demo** — encrypt/decrypt any text in real time
- ⚡ **Load tested** — stable at 1,000 concurrent users with 220ms avg response time
- 💬 **Chat rooms** — public and private rooms with password protection

---

## 📸 Screenshots

| Chat Window | Encryption Demo |
|---|---|
| ![Chat Window](screen shots/ chat_window.png) | ![Encryption Demo](screenshots/encryption_demo.png) |

---

## ▶️ How to Run Locally

**Step 1 — Clone the repository**
```bash
git clone https://github.com/YOUR-USERNAME/secure-chat-application.git
cd secure-chat-application
```

**Step 2 — Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 3 — Run the app**
```bash
streamlit run app.py
```

**Step 4 — Open in browser**
```
http://localhost:8501
```

---

## 🔐 How Encryption Works

```
Sender types message
        ↓
Fernet key encrypts message  →  "gAAAAABl...X7mK9p==" (unreadable)
        ↓
Travels across network as cipher text
        ↓
Receiver uses shared Fernet key to decrypt
        ↓
Receiver reads original message
```

The **Fernet key itself** is exchanged securely using **RSA-2048**:
- Sender encrypts the Fernet key with receiver's RSA **public key**
- Only the receiver's RSA **private key** can decrypt it
- This prevents man-in-the-middle (MITM) attacks

---

## 🧪 Testing Results

| Test | Result |
|---|---|
| Message Encryption | 100% — zero plaintext leakage |
| Authentication (JWT + bcrypt) | ✅ Pass |
| SQL Injection Protection | ✅ Pass |
| XSS Attack Prevention | ✅ Pass |
| Load Test (1,000 users) | Stable — avg 220ms response |
| Message Delivery | < 300ms average |

---

## 📁 Project Structure

```
secure-chat-application/
│
├── app.py                ← Main Streamlit application
├── requirements.txt      ← Python dependencies
├── README.md             ← Project documentation
└── screenshots/          ← App screenshots
    └── demo.png
```

---

## 📚 References

- Cryptography and Network Security — Behrouz A. Forouzan
- Python Cryptography Library — https://cryptography.io
- Streamlit Documentation — https://docs.streamlit.io

---

## 👩‍💻 Author

**Eluri Sandhya**  
MCA — Kakinada Institute of Engineering & Technology, JNTU-K  
📧 sandhyaeluri26@gmail.com  
🔗 Linked in

