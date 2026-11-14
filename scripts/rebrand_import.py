#!/usr/bin/env python3
"""Brand a complete, newly copied LiyuBetBot source tree for an independent bot.

Run ONLY in YESBOT or TIMEBOT. GitHub Actions clones the source afresh before
calling this script. Every text asset is scanned, including tests and docs.
"""
from __future__ import annotations
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = os.environ.get("GITHUB_REPOSITORY", "").rsplit("/", 1)[-1].upper()
BRANDS = {"YESBOT": ("Yes Bot", "YesBot", "yesbot"),
          "TIMEBOT": ("Time Bot", "TimeBot", "timebot")}
if REPO not in BRANDS:
    raise SystemExit(f"Refusing to modify unexpected repository: {REPO}")
display, ident, slug = BRANDS[REPO]

pairs = [
    ("your-liyubet-site.example", f"your-{slug}-site.example"),
    ("liyubet.co", f"your-{slug}-site.example"),
    ("LiyuBetBot", ident), ("LiyubetBot", ident),
    ("LIYUBETBOT", slug.upper()), ("liyubetbot", slug),
    ("Liyu Bet", display), ("LIYU BET", display.upper()), ("liyu bet", slug),
    ("LiyuBet", display), ("Liyubet", display),
    ("LIYUBET", display.upper()), ("liyubet", slug),
    ("BetnaBot", ident), ("BETNABOT", slug.upper()), ("betnabot", slug),
    ("betna-mark.svg", f"{slug}-alt-mark.svg"),
    ("Betna", display), ("BETNA", display.upper()), ("betna", slug),
    ("KemerBot", ident), ("Kemerbot", ident),
    ("KEMERBOT", slug.upper()), ("kemerbot", slug),
    ("Kemerbet", display), ("KemerBet", display),
    ("KEMERBET", display.upper()), ("kemerbet", slug),
    ("Kemer Bet", display), ("KEMER BET", display.upper()),
    ("kemer.bet", f"your-{slug}-site.example"),
]
pairs.sort(key=lambda x: len(x[0]), reverse=True)

def change(s: str) -> str:
    for old, new in pairs:
        s = s.replace(old, new)
    return s

skip_dirs = {".git", ".github", "vendor", "node_modules"}
skip_files = {"scripts/rebrand_import.py"}
binary_ext = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".ico",
              ".woff", ".woff2", ".pdf", ".zip", ".ttf", ".otf"}
read = updated = 0
for directory, dirs, names in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in skip_dirs]
    for name in names:
        path = Path(directory) / name
        if str(path.relative_to(ROOT)).replace("\\", "/") in skip_files:
            continue
        if path.suffix.lower() in binary_ext:
            continue
        data = path.read_bytes()
        try:
            value = data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        replaced = change(value)
        if path.name == "phpunit.xml":
            replaced = replaced.replace(f"{display}TestBot", f"{ident}TestBot")
        if path.name == ".env.example":
            replaced = re.sub(r"(?m)^APP_NAME=.*$", f'APP_NAME="{display}"', replaced)
            # Every deployment needs its OWN new Telegram bot and secret.
            replaced = re.sub(r"(?m)^TELEGRAM_BOT_TOKEN=.*$", "TELEGRAM_BOT_TOKEN=", replaced)
            replaced = re.sub(r"(?m)^TELEGRAM_WEBHOOK_SECRET=.*$", "TELEGRAM_WEBHOOK_SECRET=", replaced)
            replaced = re.sub(r"(?m)^TELEGRAM_BOT_USERNAME=.*$", "TELEGRAM_BOT_USERNAME=", replaced)
        if replaced != value:
            path.write_bytes(replaced.encode("utf-8"))
            updated += 1
        read += 1

# Rename every inherited brand-specific filename and directory. Do not mutate
# framework class names except when they are brand-specific and all references
# have already been rewritten by the same mapping.
for path in sorted(ROOT.rglob("*"), key=lambda p: len(p.parts), reverse=True):
    if ".git" in path.parts or ".github" in path.parts:
        continue
    if "scripts" in path.relative_to(ROOT).parts:
        continue
    new_name = change(path.name)
    if new_name == path.name:
        continue
    dest = path.with_name(new_name)
    if dest.exists():
        raise SystemExit(f"Branding filename collision: {path} -> {dest}")
    path.rename(dest)

# Use a clear, neutral first-party logo rather than retaining another brand.
# Filament and application views reference the rebranded filenames.
logo = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 100" role="img" aria-label="{display} logo">
<rect width="240" height="100" rx="16" fill="#13283c"/>
<text x="120" y="58" text-anchor="middle" font-family="Arial,sans-serif" font-size="34" font-weight="700" fill="#ffffff">{display}</text>
</svg>
'''
for filename in (f"{slug}-mark.svg", f"{slug}-alt-mark.svg"):
    (ROOT / "public" / filename).write_text(logo, encoding="utf-8")

# A brand-specific Laravel Cloud launch guide. No tokens or secrets are copied.
guide = f"""# {display} — Laravel Cloud installation

This repository is a complete, independent rebranded copy of the original
Laravel 12 source. It contains no production user database or bot token.

## Create the app
1. Create a SEPARATE Laravel Cloud application from this repository's main branch.
2. Configure PHP 8.4+, a PostgreSQL database, Redis/Valkey and persistent S3
   object storage for media uploads. Keep the two bot databases isolated.
3. Configure APP_NAME=\\"{display}\\", APP_ENV=production, APP_DEBUG=false,
   APP_URL (YOUR real HTTPS Laravel Cloud URL), a UNIQUE APP_KEY, DB_*, REDIS_*,
   QUEUE_CONNECTION=redis, CACHE_STORE=redis, FILESYSTEM_DISK=s3.
4. Create a UNIQUE bot in Telegram BotFather and set TELEGRAM_BOT_TOKEN,
   TELEGRAM_BOT_USERNAME and random TELEGRAM_WEBHOOK_SECRET in Laravel Cloud
   environment settings only. Never commit secrets to Git.
5. Set owner seed/admin credentials securely; rotate them after first login.
6. Build frontend with npm ci && npm run build, install Composer dependencies
   using PHP 8.4+, then deploy.

## Deploy commands (run in application root)
    php artisan migrate --force
    php artisan db:seed --force
    php artisan optimize:clear
    php artisan queue:restart
    php artisan telegram:set-webhook
    php artisan rewards:diagnose

Use **migrate**, not **migrate:fresh**, in production.

## Background operations
Keep workers running continuously, ideally separate pools:
- php artisan queue:work redis --queue=telegram-interactive --sleep=1 --tries=3 --timeout=120
- php artisan queue:work redis --queue=telegram-broadcast --sleep=1 --tries=3 --timeout=120
- php artisan queue:work redis --queue=automation --sleep=1 --tries=3 --timeout=120
- php artisan queue:work redis --queue=default --sleep=1 --tries=3 --timeout=120

Enable Laravel scheduler every minute: php artisan schedule:run

## Verify
- Confirm /admin login and separately configure channel ID/URL in Settings.
- Make the new bot admin in its Telegram channel; register HTTPS webhook.
- From a test account run /start, menu, auto reply and image sending.
- Test queued broadcasts and referrals using controlled test audiences.
- Upload REAL unused promo codes (CSV/XLSX) only after verifying their issuer.
- Confirm S3 media persistence after a redeploy and inspect queue failures.
- A new bot token/account does NOT copy the original Telegram audience.

The inherited app includes tests. Re-run PHP/Pest and frontend build against
an isolated test database before promoting each deployment to production.
"""
(ROOT / "DEPLOY-LARAVEL-CLOUD.md").write_text(guide, encoding="utf-8")
residual = []
for directory, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in skip_dirs]
    for n in files:
        p = Path(directory) / n
        if "scripts" in p.relative_to(ROOT).parts or p.suffix.lower() in binary_ext:
            continue
        try:
            s = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for word in ["Liyubet", "LiyuBet", "liyubet", "LIYUBET",
                     "Betna", "betna", "BETNA", "Kemerbot", "KEMERBOT",
                     "Kemerbet", "kemerbet"]:
            if word in s:
                residual.append(f"{p.relative_to(ROOT)}: {word}")
                break
if residual:
    print("Old-brand text remains:\n" + "\n".join(residual[:50]))
    raise SystemExit(1)
print(f"Rebranded {REPO} into {display}; examined {read} UTF-8 files, changed {updated}.")
