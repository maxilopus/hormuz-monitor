import os
import anthropic
import requests
from datetime import date

ANTHROPIC_KEY = os.environ["ANTHROPIC_API_KEY"]
TG_TOKEN      = os.environ["TG_BOT_TOKEN"]
TG_CHAT_ID    = os.environ["TG_CHAT_ID"]

def check_strait():
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": 
            f"Найди актуальные новости об Ормузском проливе на {date.today()}. "
            "Пролив ОТКРЫТ или ПЕРЕКРЫТ? Дай краткий анализ на русском (3-4 предложения)."
        }]
    )
    return "".join(b.text for b in response.content if b.type == "text")

def send_telegram(text):
    requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", json={
        "chat_id": TG_CHAT_ID,
        "text": f"🌊 *Ормузский пролив — {date.today()}*\n\n{text}",
        "parse_mode": "Markdown"
    })

send_telegram(check_strait())

def send_telegram(text):
    emoji = "🟢" if "открыт" in text.lower() else "🔴" if "перекрыт" in text.lower() else "🟡"
    response = requests.post(
        f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
        json={
            "chat_id": TG_CHAT_ID,
            "text": f"{emoji} *Ормузский пролив — {date.today()}*\n\n{text}",
            "parse_mode": "Markdown"
        }
    )
    print("Telegram ответ:", response.status_code, response.text)
