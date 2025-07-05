import aiohttp
import json
import urllib.parse

async def google_translate(text: str, target: str = "en") -> str:
    try:
        base = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": target,
            "dt": "t",
            "q": text,
        }
        url = base + "?" + urllib.parse.urlencode(params)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.text()
                try:
                    result = json.loads(data)
                    return ''.join([part[0] for part in result[0] if part[0]])
                except Exception:
                    return text
    except Exception:
        return text

async def translate_subtitles(content: str, lang: str, update_progress):
    lines = content.splitlines()
    total = len(lines)
    result = []

    for i, line in enumerate(lines):
        if "-->" in line or line.strip() == "" or line[0].isdigit():
            result.append(line)
        else:
            result.append(await google_translate(line, target=lang))
        if i % (total // 5 + 1) == 0:
            await update_progress(f"🔄 Progress: {int((i/total)*100)}%")

    await update_progress("✅ Translation complete.")
    return "\n".join(result)
