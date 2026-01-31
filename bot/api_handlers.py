import aiohttp
import json
import io
from bot.config import Config

# --- Helper to safely fetch data ---
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

# --- Helper: Pretty Print JSON ---
def pretty_print(data):
    """
    Formats JSON to be human-readable:
    1. indent=2: Adds indentation
    2. ensure_ascii=False: Shows Hindi/Special chars correctly instead of \u09xxx
    """
    if isinstance(data, dict) or isinstance(data, list):
        return json.dumps(data, indent=2, ensure_ascii=False)
    return str(data)

# --- API 1: TG Info ---
async def handle_tg(uid):
    url = f"https://api.b77bf911.workers.dev/telegram?user={uid}"
    data = await fetch(url)
    
    if not data:
        return "❌ Error fetching data."

    if isinstance(data, dict) and "credit" in data:
        del data["credit"]
    
    return f"```json\n{pretty_print(data)}\n```" + Config.FOOTER

# --- API 2: Number Info ---
async def handle_num(number):
    url = f"https://api.b77bf911.workers.dev/mobile?number={number}"
    data = await fetch(url)
    
    if not data:
        return "❌ No data found.", None

    header = f"📱 **Target:** `{number}`\n\n"
    text_data = pretty_print(data)

    if len(text_data) > 3500:
        file = io.BytesIO(text_data.encode('utf-8')) # Encode utf-8 for Hindi support
        file.name = f"{number}_info.json"
        return header + "⚠️ Data too long, sent as file." + Config.FOOTER, file
    else:
        return header + f"```json\n{text_data}\n```" + Config.FOOTER, None

# --- API 3: Pic (FIXED HERE) ---
async def handle_pic(number):
    url = f"https://mp-pied-ten.vercel.app/api?fuxkedapi={number}"
    data = await fetch(url)
    
    if not data:
        return "❌ Error."
    
    # ensure_ascii=False fixes the \u0917 issue
    # We wrap in ```json``` so Telegram respects the indentation
    return f"```json\n{pretty_print(data)}\n```" + Config.FOOTER

# --- API 4: Vehicle ---
async def handle_vnum(vnum):
    url = f"http://13.53.42.188:1689/?key=ayushgandu&regnum={vnum}"
    data = await fetch(url)
    
    if not data:
        return "❌ Error."

    return f"```json\n{pretty_print(data)}\n```" + Config.FOOTER

# --- API 5: Aadhar ---
async def handle_aadhar(uid):
    url = f"https://api.b77bf911.workers.dev/aadhaar?id={uid}"
    data = await fetch(url)
    
    if not data:
        return "❌ Error fetching data."

    return f"```json\n{pretty_print(data)}\n```" + Config.FOOTER

# --- API 6: UPI ---
async def handle_upi(upi_id):
    url = f"https://api.b77bf911.workers.dev/upi?id={upi_id}"
    data = await fetch(url)
    
    if not data:
        return "❌ Error fetching data."

    return f"```json\n{pretty_print(data)}\n```" + Config.FOOTER
