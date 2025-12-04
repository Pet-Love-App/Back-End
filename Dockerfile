# Dockerfile for Pet Love Backend (Supabase)
FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# 使用国内镜像源加速
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources || true

# 安装系统依赖（包括 Tesseract OCR 用于文字识别）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    wget \
    netcat-openbsd \
    libjpeg-dev \
    zlib1g-dev \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    default-libmysqlclient-dev \
    pkg-config \
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# 配置 pip 使用清华源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn

# 复制依赖文件（利用 Docker 缓存）
COPY requirements.txt ./

# 安装 Python 依赖（使用清华源）
RUN pip install -r requirements.txt

# 复制项目代码
COPY . .

# 创建必要的目录
RUN mkdir -p staticfiles media logs

# 收集静态文件
RUN python manage.py collectstatic --noinput || true

# 复制并设置入口脚本
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/auth/login/ || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "back_end.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120"]
