# 部署指南

## 首次部署

```bash
# 1. 克隆代码
git clone <your-repo> pet_love
cd pet_love

# 2. 启动 Docker 服务
make deploy

# 3. 配置系统 Nginx（只需一次）
chmod +x scripts/setup_nginx.sh
sudo ./scripts/setup_nginx.sh

# 完成！访问 http://服务器IP
```

---

## 📋 常用命令

| 命令 | 说明 |
|------|------|
| `make deploy` | 首次部署（构建+启动+迁移） |
| `make update` | 更新代码并重启 |
| `make up` | 启动服务 |
| `make down` | 停止服务 |
| `make restart` | 重启服务 |
| `make logs` | 查看日志 |
| `make status` | 查看服务状态 |
| `make shell` | 进入容器 |
| `make migrate` | 执行数据库迁移 |

---

## 🔄 日常更新流程

提交新代码后：

```bash
make update
```

## 🐛 故障排查

### 问题 1：容器无法启动

```bash
# 查看日志
make logs

# 重新构建
make build
make up
```

### 问题 2：API 返回 404

```bash
# 检查服务状态
make status

# 查看 Nginx 日志
sudo tail -f /var/log/nginx/pet_love_error.log
```

### 问题 3：数据库连接失败

```bash
# 检查数据库容器
docker-compose exec db mysql -u root -prootpassword -e "SHOW DATABASES;"

# 重新导入数据
docker-compose exec -T db mysql -u root -prootpassword backend_db < sql/additive.sql
```
