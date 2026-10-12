# Security Policy

## 🔒 Supported Versions

| Version | Supported |
|---------|-----------|
| 12.x    | ✅        |
| 11.x    | ✅        |
| 10.x    | ❌        |

## 🚨 Reporting a Vulnerability

**Please do NOT report security vulnerabilities via public GitHub issues.**

Instead, send an email to: **security@smartprice.eg**

Include:
- 📝 Description of the vulnerability
- 🔄 Steps to reproduce
- 💥 Potential impact
- 🔧 Possible fix (if any)

## ⏱️ Response Timeline

- **Within 24 hours**: Initial acknowledgment
- **Within 72 hours**: Assessment and severity rating
- **Within 7 days**: Fix or mitigation plan
- **Within 14 days**: Public disclosure (if appropriate)

## 🛡️ Security Best Practices in This Project

- 🔐 Passwords hashed with bcrypt
- 🔐 No secrets committed to repo
- 🔐 `.gitignore` excludes sensitive files
- 🔐 Data anonymization for monitoring
- 🔐 HTTPS enforced on production

## 📋 Known Issues

Currently, authentication uses local storage (demo). For production, migrate to a secure backend (Supabase/Firebase).

## 🙏 Acknowledgments

We appreciate responsible disclosure from security researchers.
