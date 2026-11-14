# Yes Bot — Laravel Cloud deployment

This application is an independent Laravel 12 / Filament 4 Telegram bot management system. Create a NEW Laravel Cloud application pointing to this repository's main branch. Use PHP 8.4+ and separate PostgreSQL, Redis/Valkey and S3-compatible storage services for this bot. Never share a database, APP_KEY, Telegram token, webhook secret, promo inventory, or user audience with another bot.

## Required Laravel Cloud environment

APP_NAME="Yes Bot"
APP_ENV=production
APP_DEBUG=false
APP_URL=https://YOUR-APP-DOMAIN
APP_DISPLAY_TIMEZONE=Africa/Addis_Ababa
QUEUE_CONNECTION=redis
CACHE_STORE=redis
SESSION_DRIVER=redis
FILESYSTEM_DISK=s3

Set APP_KEY (generate a distinct key), DB_*, REDIS_*, AWS_* from your Laravel Cloud services. Set TELEGRAM_BOT_TOKEN, TELEGRAM_BOT_USERNAME, TELEGRAM_WEBHOOK_SECRET to credentials of this new Telegram bot only. Configure SEED_ADMIN_EMAIL and a unique SEED_ADMIN_PASSWORD of at least 16 characters before the first production seed. Use HTTPS for APP_URL and configure Laravel Cloud storage as durable S3 storage for image uploads.

## Build and deploy

1. Install PHP dependencies: composer install --no-dev --no-interaction --prefer-dist --optimize-autoloader
2. Publish Filament assets (including fonts): php artisan filament:assets
3. Install frontend dependencies: npm ci
4. Build frontend: npm run build
5. Run database migrations: php artisan migrate --force
6. Initial setup (once only, when SEED_ADMIN_* is configured): php artisan db:seed --force
7. Clear cached config: php artisan optimize:clear
8. Restart workers: php artisan queue:restart
9. Once the app has its HTTPS URL and token: php artisan telegram:set-webhook
10. Check: php artisan rewards:diagnose

Use migrate, NEVER migrate:fresh, on production data.

## Four independent worker queues

Run one continuous Laravel Cloud worker for each queue:

- php artisan queue:work redis --queue=telegram-interactive --sleep=1 --tries=3 --timeout=120
- php artisan queue:work redis --queue=telegram-broadcast --sleep=1 --tries=3 --timeout=120
- php artisan queue:work redis --queue=automation --sleep=1 --tries=3 --timeout=120
- php artisan queue:work redis --queue=default --sleep=1 --tries=3 --timeout=120

Enable the scheduler (every minute): php artisan schedule:run. The 660-second queue retry_after in .env.example must remain longer than the longest worker timeout; match those values to the configured workload. Deploying a new repository does not transfer the original bot's subscribers or Telegram identity. Configure your separate channel and membership checks in Admin Settings.

## Verification

After the deploy, test /admin, login, /start, forced channel join, images, auto replies, broadcasts, queue workers, and isolated promo code redemptions. Run php artisan test with an isolated PostgreSQL test DB before go-live. Backend and HTTP tasks require a unique Telegram BotFather token. Historical README examples and local passwords are not production secrets.
