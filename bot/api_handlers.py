import aiohttp
import json
from bot.config import Config

# --- Helper: Fetch & Simple Format ---
async def get_api_response(url, title):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    return "❌ API Error: Server returned error."
                
                try:
                    data = await response.json()
                except:
                    data = await response.text() # Fallback if not JSON
                
                # Credits removal for TG API
                if isinstance(data, dict) and "credit" in data:
                    del data["credit"]

                # FORMATTING: Indent=2, Allow Hindi chars
                if isinstance(data, (dict, list)):
                    formatted = json.dumps(data, indent=2, ensure_ascii=False)
                else:
                    formatted = str(data)

                # Return the final Monospace String
                return f"📱 **{title}**\n\n```json\n{formatted}\n```" + Config.FOOTER
                
        except Exception as e:
            return f"❌ Connection Error: {e}"

# --- API Functions ---

async def handle_tg(uid):
    return await get_api_response(f"https://tgh-seven.vercel.app/?id={uid}", "TG Info")

async def handle_num(number):
    return await get_api_response(f"https://api.b77bf911.workers.dev/mobile?number={number}", "Number Info")

async def handle_pic(number):
    return await get_api_response(f"https://mp-pied-ten.vercel.app/api?fuxkedapi={number}", "Pic Info")

async def handle_vnum(vnum):
    return await get_api_response(f"http://13.53.42.188:1689/?key=ayushgandu&regnum={vnum}", "Vehicle Info")

async def handle_aadhar(uid):
    return await get_api_response(f"https://api.b77bf911.workers.dev/aadhaar?id={uid}", "Aadhar Info")

async def handle_upi(upi_id):
    return await get_api_response(f"https://api.b77bf911.workers.dev/upi?id={upi_id}", "UPI Info")
