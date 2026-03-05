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
        max_tokens=500,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content":
            f"Найди актуальные новости об Ормузском проливе на {date.today()}. "
            "Ответь СТРОГО в таком формате (ничего лишнего):\n"
            "СТАТУС: ОТКРЫТ или ПЕРЕКРЫТ\n"
            "УГРОЗА: LOW или MEDIUM или HIGH\n"
            "ПРИЧИНА: одно предложение максимум\n"
            "Отвечай на русском."
        }]
    )
    return "".join(b.text for b in response.content if b.type == "text")

def parse_and_send(text):
    # Определяем статус
    upper = text.upper()
    if "ПЕРЕКРЫТ" in upper or "ЗАКРЫТ" in upper or "BLOCKED" in upper:
        status_emoji = "🔴"
        status_text  = "ПЕРЕКРЫТ"
    elif "ОТКРЫТ" in upper or "OPEN" in upper:
        status_emoji = "🟢"
        status_text  = "ОТКРЫТ"
    else:
        status_emoji = "🟡"
        status_text  = "НЕИЗВЕСТНО"

    # Определяем уровень угрозы
    if "HIGH" in upper:
        threat = "🔥 HIGH"
    elif "MEDIUM" in upper:
        threat = "⚠️ MEDIUM"
    else:
        threat = "✅ LOW"

    # Извлекаем причину
    cause = ""
    for line in text.splitlines():
        if "ПРИЧИНА" in line.upper():
            cause = line.split(":", 1)[-1].strip()
            break

    message = (
        f"🌊 *Ормузский пролив — {date.today().strftime('%d.%m.%Y')}*\n\n"
        f"{status_emoji} *{status_text}*\n"
    )
    if cause:
        message += f"_{cause}_"

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
    print("Проверяю состояние пролива...")
    result = check_strait()
    print("AI ответ:", result)
    parse_and_send(result)
