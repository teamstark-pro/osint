import aiohttp
import json
import io
from bot.config import Config

# --- Helper to safely fetch data without revealing URL ---
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

# --- API 1: TG Info ---
async def handle_tg(uid):
    url = f"https://tgh-seven.vercel.app/?id={uid}"
    data = await fetch(url)
    
    if not data:
        return "❌ Error fetching data."

    # Remove credits as requested
    if isinstance(data, dict) and "credit" in data:
        del data["credit"]
    
    # Format as Monospace JSON
    formatted_json = json.dumps(data, indent=2)
    return f"```json\n{formatted_json}\n```" + Config.FOOTER

# --- API 2: Number Info ---
async def handle_num(number):
    url = f"https://api.b77bf911.workers.dev/mobile?number={number}"
    data = await fetch(url)
    
    if not data:
        return "❌ No data found.", None

    # Header with Mobile Number
    header = f"📱 **Target:** `{number}`\n\n"
    
    # Convert to string for length check
    if isinstance(data, dict):
        text_data = json.dumps(data, indent=2)
    else:
        text_data = str(data)

    # If too long, return as file
    if len(text_data) > 3500:
        file = io.BytesIO(text_data.encode())
        file.name = f"{number}_info.json"
        return header + "⚠️ Data too long, sent as file." + Config.FOOTER, file
    else:
        return header + text_data + Config.FOOTER, None

# --- API 3: Pic ---
async def handle_pic(number):
    # Hidden API URL
    url = f"https://mp-pied-ten.vercel.app/api?fuxkedapi={number}"
    data = await fetch(url)
    
    if not data:
        return "❌ Error."
    
    # Send AS IS (Not Monospace)
    if isinstance(data, dict):
        return json.dumps(data, indent=2) + Config.FOOTER
    return str(data) + Config.FOOTER

# --- API 4: Vehicle ---
async def handle_vnum(vnum):
    url = f"http://13.53.42.188:1689/?key=ayushgandu&regnum={vnum}"
    data = await fetch(url)
    
    if not data:
        return "❌ Error."

    if isinstance(data, dict):
        return json.dumps(data, indent=2) + Config.FOOTER
    return str(data) + Config.FOOTER
