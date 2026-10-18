# Telegram ID Bot

## Deploy on Vercel

This bot uses Telegram webhooks on Vercel (rather than long polling). The webhook
function is available at `/api/webhook`; a `GET` request to that path returns a
basic health response.

1. Import this repository into Vercel.
2. Add these environment variables in the Vercel project settings:
   - `BOT_TOKEN`: the bot token from BotFather.
   - `ADMIN_IDS`: comma-separated Telegram user IDs for bot administrators.
   - `TELEGRAM_WEBHOOK_SECRET`: a random value containing only letters, numbers,
     underscores, and hyphens. Use the same value when registering the webhook.
   - `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN` (recommended): the
     REST URL and token for an Upstash Redis database to persist users and
     activated groups across function instances. Set both or neither.
3. Deploy the project and note its public domain.
4. Register Telegram's webhook, substituting your deployment URL and secret:

   ```powershell
   $body = @{
       url = "https://YOUR-VERCEL-DOMAIN/api/webhook"
       secret_token = $env:TELEGRAM_WEBHOOK_SECRET
   }
   Invoke-RestMethod -Method Post `
       -Uri "https://api.telegram.org/bot$($env:BOT_TOKEN)/setWebhook" `
       -Body $body
   ```

   Set `BOT_TOKEN` and `TELEGRAM_WEBHOOK_SECRET` in the PowerShell environment
   before running the command. Never commit these values to the repository.
5. For local polling, set `BOT_TOKEN` and optionally `ADMIN_IDS`, then run
   `python telegram_bot.py`.

## State storage

When both Upstash variables are configured, registered users and activated
groups are stored in Redis and shared between serverless instances. Without
them, Vercel falls back to `/tmp`, which is temporary and isolated to a function
instance, so this data may be lost or differ between instances. Configure
`USER_FILE` and `GROUP_FILE` for local/custom deployments. Logs are written to
the platform's standard error stream on Vercel.
