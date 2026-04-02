import os
import anthropic
import requests
from datetime import date, timedelta

ANTHROPIC_KEY = os.environ["ANTHROPIC_API_KEY"]
TG_TOKEN      = os.environ["TG_BOT_TOKEN"]
TG_CHAT_ID    = os.environ["TG_CHAT_ID"]

YESTERDAY = (date.today() - timedelta(days=1)).strftime("%d.%m.%Y")

def check_s7():
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=800,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content":
            f"Найди упоминания авиакомпании S7 Airlines в крупных российских СМИ за {YESTERDAY}. "
            "Искать в: РБК, Коммерсантъ, Ведомости, ТАСС, Интерфакс, РИА Новости, Известия.\n\n"
            "Ответь СТРОГО в таком формате:\n"
            "УПОМИНАНИЯ: ЕСТЬ или НЕТ\n"
            "КОЛИЧЕСТВО: число найденных публикаций\n"
            "ТЕМЫ: перечисли темы через запятую (1 строка, кратко)\n"
            "ИСТОЧНИКИ: перечисли СМИ где упоминалась S7\n"
            "Отвечай на русском."
        }]
    )
    return "".join(b.text for b in response.content if b.type == "text")

def parse_and_send(text):
    upper = text.upper()

    # Есть ли упоминания
    if "НЕТ" in upper and "УПОМИНАНИЯ" in upper:
        mention_emoji = "⚪️"
        mention_text  = "НЕТ"
    else:
        mention_emoji = "🔵"
        mention_text  = "ЕСТЬ"

    # Извлекаем поля
    fields = {"КОЛИЧЕСТВО": "", "ТЕМЫ": "", "ИСТОЧНИКИ": ""}
    for line in text.splitlines():
        for key in fields:
            if key in line.upper():
                fields[key] = line.split(":", 1)[-1].strip()

    message = (
        f"✈️ *S7 Airlines в СМИ — {YESTERDAY}*\n\n"
        f"{mention_emoji} *Упоминания: {mention_text}*\n"
    )
    if fields["КОЛИЧЕСТВО"]:
        message += f"📰 Публикаций: {fields['КОЛИЧЕСТВО']}\n"
    if fields["ТЕМЫ"]:
        message += f"📌 Темы: {fields['ТЕМЫ']}\n"
    if fields["ИСТОЧНИКИ"]:
        message += f"🗞 Источники: {fields['ИСТОЧНИКИ']}\n"

    response = requests.post(
        f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
        json={
            "chat_id": TG_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
    )
    print("Telegram:", response.status_code, response.text)

if __name__ == "__main__":
    print(f"Проверяю упоминания S7 за {YESTERDAY}...")
    result = check_s7()
    print("AI ответ:", result)
    parse_and_send(result)
