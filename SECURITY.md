# Security Policy

## 🔒 Supported Versions

| Version | Supported |
|---------|-----------|
| Latest  | ✅ Yes    |
| < Latest| ❌ No     |

## 🛡️ Reporting a Vulnerability

**Do NOT create a public GitHub issue for security vulnerabilities.**

Please email: **CaputoDav@gmail.com**

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Timeline

| Timeframe | Action |
|-----------|--------|
| 24 hours | Acknowledgment |
| 72 hours | Initial assessment |
| 7 days | Status update |
| 30 days | Resolution target |

## 🔐 Security Best Practices

### For Users

1. **Never commit credentials** to version control
2. **Use environment variables** for secrets
3. **Keep dependencies updated**
4. **Rotate credentials** regularly

### Configuration Security

```bash
# ❌ Bad - Credentials in code
SLACK_TOKEN = "xoxb-secret-token"

# ✅ Good - Environment variable
SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
```

## ✅ Security Checklist

- [ ] Secrets stored in environment variables
- [ ] `.env` file is gitignored
- [ ] API tokens have minimum required permissions
- [ ] Debug mode disabled in production

---

Thank you for helping keep this project secure! 🙏
