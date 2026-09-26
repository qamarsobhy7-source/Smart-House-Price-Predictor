"""Authentication module — Login/Signup with streamlit-authenticator."""
import yaml
import streamlit as st
import streamlit_authenticator as stauth
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
CONFIG_FILE = DATA / "auth_config.yaml"


def _get_config():
    """Load or create auth config."""
    if CONFIG_FILE.exists():
        return yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8"))

    # Default config — demo users
    import bcrypt

    def _hash(pw):
        return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

    config = {
        "credentials": {
            "usernames": {
                "demo": {
                    "email": "demo@smartprice.eg",
                    "name": "Demo User",
                    "password": _hash("demo123"),
                },
                "admin": {
                    "email": "admin@smartprice.eg",
                    "name": "Admin",
                    "password": _hash("admin123"),
                },
            }
        },
        "cookie": {
            "expiry_days": 30,
            "key": "smartprice_secret_key_2026",
            "name": "smartprice_auth",
        },
        "preauthorized": {"emails": []},
    }
    CONFIG_FILE.parent.mkdir(exist_ok=True)
    CONFIG_FILE.write_text(yaml.dump(config, allow_unicode=True), encoding="utf-8")
    return config


def _save_config(config):
    CONFIG_FILE.write_text(yaml.dump(config, allow_unicode=True), encoding="utf-8")


def _hash_password(password):
    import bcrypt
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def render_auth(lang="en"):
    """Render login/signup widget. Returns (name, authentication_status, username, authenticator)."""
    config = _get_config()

    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
        auto_hash=False,
    )

    # Labels
    labels = {
        "ar": {
            "login": "تسجيل الدخول",
            "signup": "إنشاء حساب",
            "username": "اسم المستخدم",
            "password": "كلمة المرور",
            "name": "الاسم",
            "email": "البريد الإلكتروني",
            "submit": "دخول",
            "welcome": "أهلاً",
        },
        "en": {
            "login": "Login",
            "signup": "Sign Up",
            "username": "Username",
            "password": "Password",
            "name": "Name",
            "email": "Email",
            "submit": "Sign In",
            "welcome": "Welcome",
        },
    }[lang]

    # Tab-based login/signup
    try:
        tab_login, tab_signup = st.tabs([labels["login"], labels["signup"]])

        with tab_login:
            authenticator.login(location="main", fields={
                "Form name": labels["login"],
                "Username": labels["username"],
                "Password": labels["password"],
                "Login": labels["submit"],
            })

        with tab_signup:
            try:
                email, username, name = authenticator.register_user(
                    location="main",
                    fields={
                        "Form name": labels["signup"],
                        "Email": labels["email"],
                        "Username": labels["username"],
                        "Name": labels["name"],
                        "Password": labels["password"],
                        "Repeat password": labels["password"] + " (repeat)",
                        "Register": labels["signup"],
                    },
                    pre_authorization=False,
                    auto_hash=True,
                )
                if email:
                    st.success("✅ تم إنشاء الحساب — سجل دخول دلوقتي" if lang == "ar"
                              else "✅ Account created — please login")
                    # Save new user
                    _save_config(config)
            except Exception as e:
                st.error(f"⚠️ {str(e)[:100]}")
    except Exception as e:
        st.error(f"Auth error: {e}")
        return None, None, None, None

    return authenticator, config
