import asyncio
import hmac
import json
import logging
import os
from http.server import BaseHTTPRequestHandler

from telegram import Update

from telegram_bot import build_application, refresh_state


MAX_UPDATE_SIZE = 1_000_000


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status":"ok"}')

    def do_POST(self):
        expected_secret = os.getenv("TELEGRAM_WEBHOOK_SECRET")
        if not expected_secret:
            self.send_error(503, "Webhook secret is not configured")
            return

        received_secret = self.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if not hmac.compare_digest(received_secret, expected_secret):
            self.send_error(403, "Invalid webhook secret")
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_error(400, "Invalid content length")
            return
        if content_length <= 0 or content_length > MAX_UPDATE_SIZE:
            self.send_error(413, "Invalid request size")
            return

        try:
            update_data = json.loads(self.rfile.read(content_length))
            asyncio.run(self._process_update(update_data))
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON update")
            return
        except Exception:
            logging.exception("Failed to process Telegram webhook update")
            self.send_error(500, "Failed to process update")
            return

        self.send_response(200)
        self.end_headers()

    async def _process_update(self, update_data):
        application = build_application()
        await application.initialize()
        try:
            refresh_state()
            update = Update.de_json(update_data, application.bot)
            await application.process_update(update)
        finally:
            await application.shutdown()
