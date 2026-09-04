# RoyalInstitute Secure Bridge

This service is the server-side boundary between the Android controller and the Windows MT5/RoyalInstitute engine.

## Run

```bash
python -m venv .venv
# activate the environment
pip install -r requirements.txt
# set ROYAL_BRIDGE_TOKEN to a long random secret
python main.py
```

The default bind address is localhost (`127.0.0.1`). For a VPS deployment, put the service behind HTTPS/reverse proxy and a firewall. Do not expose the MT5 terminal or broker credentials to the Android app.

## Adapter

`/api/orders` intentionally returns 501 until an MT5 execution adapter is wired to the original RoyalInstitute engine. This prevents the mobile project from placing accidental live orders while the integration is incomplete.
