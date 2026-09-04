# Jk-bot — RoyalInstitute Mobile

Android control-app foundation for the RoyalInstitute MT5 trading engine.

## Architecture

```text
Android App → HTTPS Secure Bridge → Windows VPS → RoyalInstitute Engine → MT5 → Broker
```

The Android app is a controller/monitor. The trading engine should remain on a Windows VPS/PC where the MT5 Python integration can run reliably.

## Current phase

- Android Kotlin + Jetpack Compose project
- Dark trading dashboard
- Secure bridge URL/token fields
- Connect / Start / Stop controls
- Balance and equity cards
- Signal list foundation
- REST API client for `/api/state`, `/api/start`, `/api/stop`

## Roadmap

1. Secure VPS bridge + authentication
2. WebSocket live state
3. Positions/orders screen
4. Live candlestick chart
5. Buy/Sell signal details
6. SL/TP and risk controls
7. News filter/calendar
8. Push notifications
9. Build and release APK

## Safety

No broker credentials or API keys are hard-coded into the Android source. Do not expose the MT5/robot API directly to the public internet; use HTTPS, authentication and a restricted bridge.
