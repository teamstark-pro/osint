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

# --- Helper: Format Data Safe & Pretty ---
def format_response(data, title):
    """
    Returns a tuple: (text_response, file_object)
    - If text < 4000 chars: returns (formatted_text, None)
    - If text > 4000 chars: returns (caption, file_object)
    """
    if not data:
        return "❌ No Data Found.", None

    # Pretty print with Hindi support
    if isinstance(data, (dict, list)):
        content = json.dumps(data, indent=2, ensure_ascii=False)
    else:
        content = str(data)

    header = f"<b>{title}</b>\n\n"
    footer = Config.FOOTER.replace(">", "&gt;").replace("<", "&lt;") # Escape HTML in footer

    # Check Length
    if len(content) > 3500:
        # Too long: Create file
        bio = io.BytesIO(content.encode('utf-8'))
        bio.name = f"{title.lower().replace(' ', '_')}.json"
        return f"{header}⚠️ <i>Data too long, sending as file...</i>{footer}", bio
    else:
        # Short enough: Send as Text with HTML Code Block
        # We use <pre> because it handles special chars better than Markdown
        safe_content = content.replace("<", "&lt;").replace(">", "&gt;")
        return f"{header}<pre>{safe_content}</pre>{footer}", None

# --- API Functions ---

async def handle_tg(uid):
    url = f"https://tgh-seven.vercel.app/?id={uid}"
    data = await fetch(url)
    if isinstance(data, dict) and "credit" in data:
        del data["credit"]
    return format_response(data, "TG Info")

async def handle_num(number):
    url = f"https://api.b77bf911.workers.dev/mobile?number={number}"
    data = await fetch(url)
    return format_response(data, f"📱 Target: {number}")

async def handle_pic(number):
    url = f"https://mp-pied-ten.vercel.app/api?fuxkedapi={number}"
    data = await fetch(url)
    return format_response(data, "📸 Pic Info")

async def handle_vnum(vnum):
    url = f"http://13.53.42.188:1689/?key=ayushgandu&regnum={vnum}"
    data = await fetch(url)
    return format_response(data, f"🚗 Vehicle: {vnum}")

async def handle_aadhar(uid):
    url = f"https://api.b77bf911.workers.dev/aadhaar?id={uid}"
    data = await fetch(url)
    return format_response(data, "🆔 Aadhar Info")

async def handle_upi(upi_id):
    url = f"https://api.b77bf911.workers.dev/upi?id={upi_id}"
    data = await fetch(url)
    return format_response(data, f"💸 UPI: {upi_id}")
