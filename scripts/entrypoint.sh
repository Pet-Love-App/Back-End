#!/bin/bash
# entrypoint.sh

set -e

echo "等待数据库启动..."
# 使用nc等待MySQL端口
max_attempts=30
attempt=0
while ! nc -z db 3306; do
  attempt=$((attempt + 1))
  if [ $attempt -ge $max_attempts ]; then
    echo "❌ 数据库连接超时"
    exit 1
  fi
  echo "等待数据库... (${attempt}/${max_attempts})"
  sleep 2
done
echo "✅ 数据库已启动！"

# 等待MySQL完全启动
echo "等待MySQL初始化完成..."
sleep 5

# 不在 entrypoint 中执行迁移，让 Makefile 控制
echo "✅ 启动Django应用..."
exec "$@"