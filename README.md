# Telegram Bot Arianto

### Community Moderation & Automation Bot

A Telegram bot project focused on practical community automation, including moderation workflows, spam handling, link management, and welcome messages.

## ✨ Capabilities

- Community moderation automation
- Link and mention filtering
- Join and welcome workflows
- Admin bypass for moderation rules
- Environment-based bot configuration
- Automated linting and unit tests with GitHub Actions

## 🧰 Stack

**Python · python-telegram-bot 21.7 · Telegram Bot API · pytest · flake8 · GitHub Actions**

## ⚙️ Configuration

The bot token is intentionally not stored in source code.

Set the following environment variable before running the bot:

```bash
export TELEGRAM_BOT_TOKEN="your-bot-token"
python bot_telegram.py
```

For hosted deployments, configure `TELEGRAM_BOT_TOKEN` as a platform secret/environment variable.

## 🧪 Tests

Run the test suite locally with:

```bash
pip install -r requirements.txt
pip install pytest flake8
pytest -q
flake8 . --count --max-complexity=10 --max-line-length=127 --statistics
```

GitHub Actions runs linting and tests automatically on pushes and pull requests targeting `main`.

## 🔐 Security

Never commit bot tokens, credentials, or other secrets to the repository. The bot expects `TELEGRAM_BOT_TOKEN` from the runtime environment.

If a token has previously been exposed in source control, revoke it through BotFather and generate a new token before deploying.

---

**Arianto Eka Putra · Software Engineer**
