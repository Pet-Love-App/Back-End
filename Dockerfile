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
    libjpeg-dev \
    zlib1g-dev \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 安装Poetry（使用清华源）
RUN pip install "poetry==$POETRY_VERSION" -i https://pypi.tuna.tsinghua.edu.cn/simple

# 配置Poetry不使用虚拟环境
RUN poetry config virtualenvs.create false

# 复制Poetry配置文件
COPY pyproject.toml poetry.lock* ./

# 安装生产依赖（使用pip和清华源，避免Poetry网络问题）
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple \
    django==5.2.0 \
    djangorestframework==3.15.0 \
    django-cors-headers==4.3.0 \
    mysqlclient==2.1.0 \
    djangorestframework-simplejwt==5.5.1 \
    djoser==2.3.3 \
    pydantic==2.12.3 \
    pillow==10.4.0 \
    python-dotenv==1.0.0 \
    gunicorn==21.2.0 \
    requests==2.32.5 \
    paddleocr==3.3.1 \
    paddlepaddle==3.2.1 \
    opencv-contrib-python==4.10.0 \
    numpy==2.0.2

# 复制项目代码
COPY . .

# 复制并设置入口脚本
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]