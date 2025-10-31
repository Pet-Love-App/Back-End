# Dockerfile
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION=1.8.2

# 使用国内 Debian 镜像源（加速系统包下载）
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# 安装Poetry（使用清华源）
RUN pip install "poetry==$POETRY_VERSION" -i https://pypi.tuna.tsinghua.edu.cn/simple

# 配置Poetry不使用虚拟环境
RUN poetry config virtualenvs.create false

# 配置 Poetry 使用国内源
RUN poetry config repositories.tuna https://pypi.tuna.tsinghua.edu.cn/simple/ && \
    poetry config http-basic.tuna "" ""

# 复制Poetry配置文件
COPY pyproject.toml poetry.lock* ./

# 安装生产依赖（使用清华源）
RUN poetry install --only=main --no-interaction --no-ansi

# 复制项目代码
COPY . .

# 复制并设置入口脚本
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]