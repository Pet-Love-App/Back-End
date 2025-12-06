"""
OCR 服务
负责调用阿里云 OCR API 进行文字识别
"""

import base64
import logging
import re
from typing import Optional, Tuple

import requests

from config.settings import settings

logger = logging.getLogger(__name__)


class OCRService:
    """OCR 服务类"""

    def __init__(self):
        """初始化 OCR 服务"""
        # 从统一配置获取
        self.appcode = settings.ALIYUN_OCR_APPCODE
        self.api_url = settings.ALIYUN_OCR_URL
        self.timeout = 30
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_content_types = [
            "image/jpeg",
            "image/png",
            "image/jpg",
            "image/bmp",
            "image/gif",
        ]

    def is_configured(self) -> bool:
        """检查 API 是否已配置"""
        return settings.is_ocr_configured()

    def recognize(
        self, image_bytes: bytes, content_type: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        识别图片中的文字

        Args:
            image_bytes: 图片二进制数据
            content_type: 图片 MIME 类型

        Returns:
            Tuple[成功标志, 识别文本, 错误信息]
        """
        # 检查配置
        if not self.is_configured():
            logger.error("OCR API 未配置")
            return False, None, "OCR API 未配置"

        # 验证文件类型
        if content_type not in self.allowed_content_types:
            return False, None, f"不支持的文件类型: {content_type}"

        # 验证文件大小
        if len(image_bytes) > self.max_file_size:
            return False, None, "文件过大，最大支持 10MB"

        try:
            # 转换为 base64
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")

            # 调用 OCR API
            success, response_data, error = self._call_ocr_api(image_base64)

            if not success:
                return False, None, error

            # 解析响应
            text = self._parse_ocr_response(response_data)

            if not text:
                return False, None, "OCR 识别失败，未提取到文本"

            logger.info(f"OCR 识别成功，文本长度: {len(text)}")
            return True, text, None

        except Exception as e:
            logger.exception("OCR 识别异常")
            return False, None, f"服务器错误: {str(e)}"

    def _call_ocr_api(
        self, image_base64: str
    ) -> Tuple[bool, Optional[dict], Optional[str]]:
        """
        调用阿里云 OCR API

        Returns:
            Tuple[成功标志, 响应数据, 错误信息]
        """
        try:
            headers = {
                "Authorization": f"APPCODE {self.appcode}",
                "Content-Type": "application/json; charset=UTF-8",
            }

            payload = {
                "img": image_base64,
                "prob": False,  # 不需要置信度
            }

            response = requests.post(
                self.api_url, headers=headers, json=payload, timeout=self.timeout
            )

            if response.status_code != 200:
                error_msg = f"OCR API 返回错误: {response.status_code}"
                logger.error(error_msg)
                return False, None, error_msg

            return True, response.json(), None

        except requests.Timeout:
            logger.error("OCR API 请求超时")
            return False, None, "请求超时，请稍后重试"

        except Exception as e:
            logger.exception("OCR API 请求异常")
            return False, None, f"API 调用失败: {str(e)}"

    def _parse_ocr_response(self, response_data: dict) -> Optional[str]:
        """
        解析 OCR API 响应

        Returns:
            识别的文本，或 None
        """
        try:
            # 检查响应状态
            ret = response_data.get("ret", [])
            if not ret:
                logger.error("OCR 响应中没有 ret 字段")
                return None

            # 提取所有识别到的文本行
            text_lines = []
            for item in ret:
                word = item.get("word", "").strip()
                if word:
                    text_lines.append(word)

            if not text_lines:
                logger.warning("OCR 未识别到任何文本")
                return None

            # 合并所有文本行
            full_text = "\n".join(text_lines)

            # 清理文本（移除多余空白）
            full_text = re.sub(r"\s+", " ", full_text).strip()

            return full_text

        except Exception:
            logger.exception("解析 OCR 响应异常")
            return None


# 全局单例
ocr_service = OCRService()
