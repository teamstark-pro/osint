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
    url = f"https://encorexapi.vercel.app/ayushgendutg?id={uid}"
    data = await fetch(url)
    
    if not data:
        return "❌ Error fetching data."

    # Remove all variations of credits
    if isinstance(data, dict):
        data.pop("credit", None)
        data.pop("api by", None)
        data.pop("API BY", None)
        data.pop("Owner", None)
    
    # Format as Monospace JSON
    formatted_json = json.dumps(data, indent=2)
    return f"```json\n{formatted_json}\n```\n" + Config.FOOTER

# --- API 2: Number Info ---
async def handle_num(number):
    url = f"https://usesirosint.vercel.app/api/numinfo?key=ayushz&num={number}"
    data = await fetch(url)
    
    if not data:
        return "❌ No data found.", None

    # Header with Mobile Number
    header = f"📱 **Target:** `{number}`\n\n"
    
    # Remove credits
    if isinstance(data, dict):
        data.pop("API BY", None)
        data.pop("api by", None)
        data.pop("Owner", None)
        text_data = json.dumps(data, indent=2)
    else:
        text_data = str(data)

    # If too long, return as file
    if len(text_data) > 3500:
        file = io.BytesIO(text_data.encode())
        file.name = "result.json" # Fixed filename bug
        return header + "⚠️ Data too long, sent as file.\n" + Config.FOOTER, file
    else:
        # Formatted as monospace JSON!
        return header + f"```json\n{text_data}\n```\n" + Config.FOOTER, None

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
    url = f"https://api.b77bf911.workers.dev/v2?query={vnum}"
    data = await fetch(url)
    
    if not data:
        return "❌ Error."

    if isinstance(data, dict):
        return json.dumps(data, indent=2) + Config.FOOTER
    return str(data) + Config.FOOTER

# --- API 5: Aadhar ---
async def handle_aadhar(uid):
    # Hidden API
    url = f"https://encorexapi.vercel.app/adharayu?adr={uid}"
    data = await fetch(url)
    
    if not data:
        return "❌ Error fetching data."

    # Remove all variations of credits
    if isinstance(data, dict):
        data.pop("api by", None)
        data.pop("API BY", None)
        data.pop("Owner", None)
        data.pop("credit", None)
        formatted_json = json.dumps(data, indent=2)
    else:
        formatted_json = str(data)
        
    return f"```json\n{formatted_json}\n```\n" + Config.FOOTER

# --- API 6: UPI ---
async def handle_upi(upi_id):
    # Hidden API
    url = f"https://api.b77bf911.workers.dev/upi?id={upi_id}"
    data = await fetch(url)
    
    if not data:
        return "❌ Error fetching data."

    # Format as Monospace JSON (Click to Copy)
    if isinstance(data, dict):
        formatted_json = json.dumps(data, indent=2)
    else:
        formatted_json = str(data)

    return f"```json\n{formatted_json}\n```\n" + Config.FOOTER
