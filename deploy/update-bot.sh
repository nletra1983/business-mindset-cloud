#!/bin/sh
set -eu

SRC=/opt/business-mindset-src
DEST=/opt/business-mindset
REPO=https://github.com/nletra1983/business-mindset-cloud.git

if [ ! -d "$DEST/secrets" ] || [ ! -d "$DEST/data/postgres" ]; then
  echo "secrets or database directory is missing, deploy stopped" >&2
  exit 1
fi

if [ ! -d "$SRC/.git" ]; then
  git clone --branch main --single-branch "$REPO" "$SRC"
fi

cd "$SRC"
git fetch origin main
git checkout main
git merge --ff-only origin/main

rsync -a --delete \
  --exclude '.git/' \
  --exclude 'secrets/' \
  --exclude 'data/' \
  "$SRC/" "$DEST/"

cd "$DEST"
docker compose up -d --build bot
install -m 755 "$DEST/deploy/update-bot.sh" /usr/local/sbin/deploy-business-mindset
docker inspect -f '{{.RestartCount}} {{.State.Status}}' business-mindset-bot-1
