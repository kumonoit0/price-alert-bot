# CoinGecko Price Alerts -> Telegram

Watches BTC/ETH/SOL and sends one Telegram message per threshold crossing.
Stdlib only, polite rate limits, retry with back-off, state file so alerts
don't repeat.

## Run

```bash
python alert.py --once                 # dry run (prints, no Telegram needed)
TG_TOKEN=123:ABC TG_CHAT=12345 python alert.py --watch
```

Edit `THRESHOLDS` for your coins and levels.
