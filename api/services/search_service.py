"""
搜索服务
负责调用第三方搜索 API（百度百科）
"""

import logging
import urllib.parse
from typing import Any, Optional, Tuple

import requests

from config.settings import settings

logger = logging.getLogger(__name__)


class SearchService:
    """搜索服务类"""

    def __init__(self):
        """初始化搜索服务"""
        # 从统一配置获取
        self.api_key = settings.BAIDU_API_KEY
        self.timeout = 20

    def is_configured(self) -> bool:
        """检查 API 是否已配置"""
        return settings.is_search_configured()

    def search_ingredient(
        self, ingredient: str, timeout: Optional[int] = None
    ) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
        """
        搜索成分信息

        Args:
            ingredient: 成分名称
            timeout: 超时时间（秒）

        Returns:
            Tuple[成功标志, 标题, 摘要, 错误信息]
        """
        if not self.is_configured():
            logger.error("百度 API 密钥未配置")
            return False, None, None, "API key not configured"

        if not ingredient or not ingredient.strip():
            return False, None, None, "成分名称不能为空"

        ingredient = ingredient.strip()
        timeout = timeout or self.timeout

        try:
            status_code, data = self._fetch_from_baidu(ingredient, timeout)

            if status_code == 0:
                logger.error(f"百度 API 请求失败: {data}")
                return False, None, None, "网络请求失败"

            if not isinstance(data, dict):
                logger.error(f"百度 API 返回格式错误: {type(data)}")
                return False, None, None, "API 返回格式错误"

            # 解析百度百科响应
            title = data.get("title") or ingredient
            result = data.get("result") or {}
            extract = result.get("summary", "")

            if not extract:
                logger.info(f"未找到成分信息: {ingredient}")
                return False, None, None, "未找到相关信息"

            logger.info(f"成功获取成分信息: {ingredient}")
            return True, title, extract, None

        except requests.Timeout:
            logger.error(f"请求超时: {ingredient}")
            return False, None, None, "请求超时，请稍后重试"

        except Exception as e:
            logger.exception(f"搜索成分信息异常: {ingredient}")
            return False, None, None, f"服务器错误: {str(e)}"

    def _fetch_from_baidu(self, ingredient: str, timeout: int) -> Tuple[int, Any]:
        """
        从百度 AppBuilder API 获取成分摘要信息

        Args:
            ingredient: 成分名称
            timeout: 超时时间

        Returns:
            Tuple[状态码, 响应数据]
        """
        try:
            safe_title = urllib.parse.quote(ingredient.strip())
            url = (
                f"https://appbuilder.baidu.com/v2/baike/lemma/get_content"
                f"?search_type=lemmaTitle&search_key={safe_title}"
            )

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            response = requests.get(url, headers=headers, timeout=timeout)

            try:
                return response.status_code, response.json()
            except Exception:
                return response.status_code, response.text

        except Exception as e:
            logger.error(f"百度 API 请求异常: {str(e)}")
            return 0, str(e)


# 全局单例
search_service = SearchService()
