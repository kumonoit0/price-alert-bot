#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CoinGecko price alerts -> Telegram (stdlib only, no deps).

Watches coins and sends a Telegram message once per threshold crossing.
Without TG_TOKEN it just prints alerts (dry run).

Usage:
    python alert.py --once                 # single check
    TG_TOKEN=123:ABC TG_CHAT=12345 python alert.py --watch
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

API_URL = (
    "https://api.coingecko.com/api/v3/simple/price"
    "?ids=bitcoin,ethereum,solana&vs_currencies=usd"
)
THRESHOLDS = {"bitcoin": 90000, "ethereum": 3000, "solana": 130}
STATE_FILE = "alert_state.json"
WATCH_SEC = 300

TG_TOKEN = os.environ.get("TG_TOKEN", "")
TG_CHAT = os.environ.get("TG_CHAT", "")


def log(msg):
    print(f"{datetime.now(timezone.utc).isoformat()} {msg}")


def fetch(retries=4):
    wait = 5
    for a in range(1, retries + 1):
        try:
            req = urllib.request.Request(API_URL, headers={"User-Agent": "price-alert-demo/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            log(f"fetch try {a}/{retries}: {type(e).__name__}, wait {wait}s")
            time.sleep(wait)
            wait *= 2
    raise RuntimeError("fetch failed")


def notify(text):
    if not (TG_TOKEN and TG_CHAT):
        print("DRY-RUN ALERT:", text)
        return
    data = json.dumps({"chat_id": TG_CHAT, "text": text}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
        data=data, headers={"Content-Type": "application/json"},
    )
    urllib.request.urlopen(req, timeout=30).read()


def load_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(s):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(s, f)


def check_once():
    prices = fetch()
    state = load_state()
    for coin, limit in THRESHOLDS.items():
        price = (prices.get(coin) or {}).get("usd")
        if price is None:
            continue
        was_above = state.get(coin)
        above = price >= limit
        if above and not was_above:
            notify(f"{coin.upper()} ${price} crossed above ${limit}")
        state[coin] = above
    save_state(state)
    log("check ok")


if __name__ == "__main__":
    if "--watch" in sys.argv:
        while True:
            try:
                check_once()
            except Exception as e:
                log(f"skip: {e}")
            time.sleep(WATCH_SEC)
    else:
        check_once()
