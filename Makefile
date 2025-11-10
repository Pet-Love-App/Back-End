.PHONY: help build up down restart logs deploy update clean checkout wait-db

# 默认分支
BRANCH ?= back_end

help:
	@echo "可用命令："
	@echo "  make deploy              - 首次部署（包含 Nginx 配置）"
	@echo "  make update              - 更新代码并重启（默认分支）"
	@echo "  make update BRANCH=xxx   - 从指定分支更新"
	@echo "  make checkout BRANCH=xxx - 切换到指定分支"
	@echo "  make up                  - 启动所有服务"
	@echo "  make down                - 停止所有服务"
	@echo "  make restart             - 重启服务"
	@echo "  make logs                - 查看日志"
	@echo "  make build               - 重新构建镜像"
	@echo "  make wait-db             - 等待数据库就绪"
	@echo "  make diagnose            - 诊断问题（查看日志和资源）"
	@echo "  make migrate             - 执行数据库迁移"
	@echo "  make clean               - 清理所有容器和卷（危险）"

# 首次部署
deploy:
	@echo "===== 首次部署 ====="
	@echo "停止并清理旧容器..."
	docker-compose down --remove-orphans -v
	@echo "重新构建并启动..."
	docker-compose up -d --build
	@echo "等待数据库完全启动（30秒）..."
	@sleep 30
	@echo "检查容器状态..."
	@docker-compose ps
	@echo ""
	@echo "执行数据库迁移（重试3次）..."
	@for i in 1 2 3; do \
		echo "尝试迁移（第$$i次）..."; \
		docker-compose exec -T web python manage.py migrate && break || \
		(echo "⏳ 等待10秒后重试..." && sleep 10); \
	done
	docker-compose exec -T web python manage.py collectstatic --noinput
	@echo "✅ 部署完成！"
	@docker-compose ps
	@echo ""
	@echo "访问地址："
	@echo "  http://localhost:8000 (开发)"
	@echo "  http://服务器IP (生产)"

# 切换分支
checkout:
	@echo "===== 切换分支到 $(BRANCH) ====="
	git fetch origin
	git switch $(BRANCH) 2>/dev/null || git switch -c $(BRANCH) origin/$(BRANCH)
	git pull origin $(BRANCH)
	@echo "✅ 已切换到分支: $(BRANCH)"

# 更新代码
update:
	@echo "===== 更新应用（分支: $(BRANCH)）====="
	@echo "当前分支: $$(git branch --show-current)"
	git fetch origin
	git pull origin $(BRANCH)
	@echo "重新构建镜像..."
	docker-compose up -d --build
	@echo "等待服务启动（20秒）..."
	@sleep 20
	@echo "执行数据库迁移..."
	@for i in 1 2 3; do \
		docker-compose exec -T web python manage.py migrate && break || \
		(echo "⏳ 等待5秒后重试..." && sleep 5); \
	done
	docker-compose exec -T web python manage.py collectstatic --noinput
	@echo "✅ 更新完成！"
	@echo "当前分支: $$(git branch --show-current)"

# 构建镜像
build:
	docker-compose build

# 启动服务
up:
	docker-compose up -d
	@echo "✅ 服务已启动"
	@docker-compose ps

# 停止服务
down:
	docker-compose down
	@echo "✅ 服务已停止"

# 重启服务
restart:
	docker-compose restart
	@echo "✅ 服务已重启"

# 查看日志
logs:
	docker-compose logs -f

# 清理（危险操作）
clean:
	@echo "⚠️  警告：这将删除所有容器和数据卷！"
	@read -p "确认继续？(yes/no): " confirm && [ "$$confirm" = "yes" ]
	docker-compose down -v
	@echo "✅ 清理完成"

# 数据库迁移
migrate:
	docker-compose exec web python manage.py makemigrations
	docker-compose exec web python manage.py migrate

# 创建超级用户
createsuperuser:
	docker-compose exec web python manage.py createsuperuser

# 进入容器
shell:
	docker-compose exec web bash

# Django shell
djshell:
	docker-compose exec web python manage.py shell

# 查看状态
status:
	@docker-compose ps
	@echo ""
	@echo "访问地址："
	@echo "  开发: http://localhost:8000"
	@echo "  生产: http://服务器IP"

# 等待数据库就绪
wait-db:
	@echo "⏳ 等待数据库就绪..."
	@for i in $$(seq 1 60); do \
		docker-compose exec -T db mysqladmin ping -h localhost -u root -p$${DB_ROOT_PASSWORD:-rootpassword} 2>/dev/null && \
		echo "✅ 数据库已就绪！" && exit 0 || \
		(echo "等待中... ($$i/60)" && sleep 1); \
	done; \
	echo "❌ 数据库启动超时" && exit 1

# 诊断问题
diagnose:
	@echo "===== 容器状态 ====="
	docker-compose ps
	@echo ""
	@echo "===== Web 容器日志（最后50行）====="
	docker-compose logs --tail=50 web
	@echo ""
	@echo "===== 数据库容器日志（最后20行）====="
	docker-compose logs --tail=20 db
	@echo ""
	@echo "===== 系统资源 ====="
	docker stats --no-stream

