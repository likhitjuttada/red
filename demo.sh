#!/usr/bin/env bash
set -e

echo "=== Red Agent Demo ==="

# Step 1: init OverClaw (idempotent)
if [ ! -d ".overclaw" ]; then
  echo "[setup] Initializing OverClaw..."
  overclaw init
fi

# Step 2: build Giskard attack cache (skip if already built)
if [ ! -f "attack_cache.json" ]; then
  echo "[setup] Building Giskard attack cache (this takes ~2-5 min)..."
  python -m red.main --rebuild-cache --iterations 0
fi

# Step 3: run Red agent
echo "[demo] Starting Red agent..."
python -m red.main \
  --target "${TARGET_MODEL:-openai/gpt-4o-mini}" \
  --iterations "${ITERATIONS:-4}" \
  --attacks-per-iter "${ATTACKS:-10}" \
  --threshold 0.7 \
  --stop-on 3
