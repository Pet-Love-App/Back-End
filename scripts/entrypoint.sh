#!/bin/bash
set -e

echo "==================================="
echo "Pet Love Backend Starting..."
echo "==================================="

# 等待网络就绪
echo "Waiting for network..."
sleep 2

# 检查环境变量
echo "Checking environment variables..."
if [ -z "$SUPABASE_URL" ]; then
    echo "WARNING: SUPABASE_URL is not set!"
fi

if [ -z "$SUPABASE_ANON_KEY" ]; then
    echo "WARNING: SUPABASE_ANON_KEY is not set!"
fi

# 收集静态文件
echo "Collecting static files..."
python manage.py collectstatic --noinput || true

# 创建日志目录
mkdir -p /app/logs

echo "==================================="
echo "Starting application..."
echo "==================================="

# 执行传入的命令
exec "$@"
