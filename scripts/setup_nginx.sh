#!/bin/bash
# 系统 Nginx 配置脚本（只需运行一次）

set -e

echo "===== 配置系统 Nginx ====="

# 获取服务器 IP
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "YOUR_SERVER_IP")
PROJECT_DIR=$(pwd)

echo "项目目录: $PROJECT_DIR"
echo "服务器 IP: $SERVER_IP"

# 1. 创建必要的目录
echo "1. 创建目录..."
mkdir -p staticfiles
mkdir -p media

# 2. 收集静态文件
echo "2. 收集静态文件..."
docker-compose exec -T web python manage.py collectstatic --noinput || true

# 3. 复制静态文件到宿主机
echo "3. 复制静态文件..."
docker cp backend_web:/app/staticfiles/. ./staticfiles/ 2>/dev/null || true

# 4. 设置权限
echo "4. 设置目录权限..."
sudo chown -R www-data:www-data staticfiles media 2>/dev/null || \
sudo chown -R nginx:nginx staticfiles media 2>/dev/null || \
chmod -R 755 staticfiles media

# 5. 创建 Nginx 配置
echo "5. 创建 Nginx 配置..."
sudo tee /etc/nginx/sites-available/pet_love > /dev/null << EOF
upstream django {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name $SERVER_IP _;
    
    client_max_body_size 100M;
    
    access_log /var/log/nginx/pet_love_access.log;
    error_log /var/log/nginx/pet_love_error.log;

    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://django;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# 6. 启用配置
echo "6. 启用 Nginx 配置..."
sudo ln -sf /etc/nginx/sites-available/pet_love /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 7. 测试配置
echo "7. 测试 Nginx 配置..."
sudo nginx -t

# 8. 重启 Nginx
echo "8. 重启 Nginx..."
sudo systemctl restart nginx
sudo systemctl enable nginx

echo ""
echo "===== ✅ 配置完成！ ====="
echo ""
echo "访问地址: http://$SERVER_IP/additive/search-ingredient/?name=test"
echo ""
echo "后续部署只需运行: make update"

