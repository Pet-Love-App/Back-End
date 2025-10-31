# Dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION=1.8.2

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# 安装Poetry
RUN pip install "poetry==$POETRY_VERSION"

# 配置Poetry不使用虚拟环境
RUN poetry config virtualenvs.create false

# 复制Poetry配置文件
COPY pyproject.toml poetry.lock* ./

# 安装生产依赖
RUN poetry install --only=main --no-interaction --no-ansi

# 复制项目代码
COPY . .

# 复制并设置入口脚本
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]