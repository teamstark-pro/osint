import aiohttp
import json
import io
from bot.config import Config

# --- Helper: Fetch URL ---
async def fetch(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    return None
                try:
                    return await response.json()
                except:
                    return await response.text()
        except Exception:
            return None

# --- Helper: Pretty Print & File Check ---
def prepare_response(data, title):
    """
    Formats data. Returns tuple: (text_message, file_object)
    """
    if not data:
        return "❌ No Data Found.", None

    # 1. Format JSON (Clean, Indented, Hindi Supported)
    if isinstance(data, (dict, list)):
        # ensure_ascii=False is KEY for Hindi text
        content = json.dumps(data, indent=2, ensure_ascii=False)
    else:
        content = str(data)

    header = f"📱 **{title}**\n\n"

    # 2. Check Length (Telegram limit is 4096)
    if len(content) > 3500:
        # Too long? Send as .json file
        bio = io.BytesIO(content.encode('utf-8'))
        bio.name = f"{title.replace(' ', '_').lower()}.json"
        caption = header + "⚠️ **Data too long. Sent as file.**" + Config.FOOTER
        return caption, bio
    else:
        # Short enough? Send as text
        text = header + f"```json\n{content}\n```" + Config.FOOTER
        return text, None

# --- API Handlers ---

async def handle_tg(uid):
    url = f"[https://tgh-seven.vercel.app/?id=](https://tgh-seven.vercel.app/?id=){uid}"
    data = await fetch(url)
    if isinstance(data, dict) and "credit" in data:
        del data["credit"]
    return prepare_response(data, "TG Info")

async def handle_num(number):
    url = f"[https://api.b77bf911.workers.dev/mobile?number=](https://api.b77bf911.workers.dev/mobile?number=){number}"
    data = await fetch(url)
    return prepare_response(data, f"Target: {number}")

async def handle_pic(number):
    url = f"[https://mp-pied-ten.vercel.app/api?fuxkedapi=](https://mp-pied-ten.vercel.app/api?fuxkedapi=){number}"
    data = await fetch(url)
    return prepare_response(data, "Pic Info")

async def handle_vnum(vnum):
    url = f"[http://13.53.42.188:1689/?key=ayushgandu&regnum=](http://13.53.42.188:1689/?key=ayushgandu&regnum=){vnum}"
    data = await fetch(url)
    return prepare_response(data, f"Vehicle: {vnum}")

async def handle_aadhar(uid):
    url = f"[https://api.b77bf911.workers.dev/aadhaar?id=](https://api.b77bf911.workers.dev/aadhaar?id=){uid}"
    data = await fetch(url)
    return prepare_response(data, "Aadhar Info")

async def handle_upi(upi_id):
    url = f"[https://api.b77bf911.workers.dev/upi?id=](https://api.b77bf911.workers.dev/upi?id=){upi_id}"
    data = await fetch(url)
    return prepare_response(data, f"UPI: {upi_id}")
