# Real MT5 Bridge — Windows/VPS

This bridge must run on the same Windows machine/VPS where MetaTrader 5 is installed and logged into the trading account.

## 1. Install and log in to MT5
- Install the broker's MetaTrader 5 terminal.
- Log in to the intended account.
- Keep the terminal running.
- Confirm the required symbols (for example XAUUSD) are visible in Market Watch.

## 2. Start the bridge
Open Command Prompt in this `bridge` folder and run:

```bat
set ROYAL_BRIDGE_TOKEN=replace-with-a-long-random-secret
set MT5_PATH=C:\Path\To\terminal64.exe
start_windows.bat
```

If MT5 is already discoverable, `MT5_PATH` can be omitted.

## 3. Connect the web/mobile client
Use the VPS HTTPS API URL and the same Bearer token. Do not put the token into GitHub source files or public GitHub Pages.

## 4. Security
Expose the bridge through HTTPS (reverse proxy/VPN/Tailscale) rather than opening port 8765 directly to the public internet. Use a strong random token and restrict access by IP/VPN where possible.

## 5. Trading safety
The `/api/orders` endpoint sends real market orders through MT5. Test on a demo account first. Start/stop does not close existing positions.
