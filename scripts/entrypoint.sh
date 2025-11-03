#!/bin/bash
# entrypoint.sh

set -e

echo "等待数据库启动..."
# 使用nc等待MySQL端口
while ! nc -z db 3306; do
  sleep 1
done
echo "数据库已启动！"

# 等待MySQL完全启动
sleep 2

# 执行数据库迁移
echo "执行数据库迁移..."
python manage.py migrate

echo "启动Django应用..."
exec "$@"