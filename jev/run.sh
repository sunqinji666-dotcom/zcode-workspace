#!/bin/zsh
# Jev 运行器:读取同目录 .env 里的 OPENROUTER_API_KEY,然后跑脚本
# 用法: ./run.sh quickstart.py
cd "$(dirname "$0")"

if [[ -f .env ]]; then
  set -a; source .env; set +a
fi

if [[ -z "$OPENROUTER_API_KEY" ]]; then
  echo "还没有 API key:把 key 填进 $(pwd)/.env 的 OPENROUTER_API_KEY= 后面,再运行。"
  exit 1
fi

exec .venv/bin/python "$@"
