"""
AI 服务
负责调用 LLM API 进行猫粮成分分析
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

import requests

from config.settings import settings

logger = logging.getLogger(__name__)


class AIService:
    """AI 服务类"""

    def __init__(self):
        """初始化 AI 服务"""
        # 从统一配置获取
        self.api_key = settings.LLM_API_KEY
        self.api_url = settings.LLM_API_URL
        self.model = settings.LLM_MODEL
        self.timeout = 120

    def is_configured(self) -> bool:
        """检查 API 是否已配置"""
        return settings.is_ai_configured()

    def analyze_ingredients(
        self, ingredients: str, timeout: Optional[int] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        分析猫粮成分

        Args:
            ingredients: 成分列表字符串
            timeout: 超时时间（秒）

        Returns:
            Tuple[成功标志, 分析结果, 错误信息]
        """
        if not self.is_configured():
            logger.error("LLM API 未配置")
            return False, None, "LLM API 未配置"

        if not ingredients or not ingredients.strip():
            return False, None, "成分列表不能为空"

        timeout = timeout or self.timeout

        try:
            # 构建提示词
            prompt = self._build_prompt(ingredients.strip())

            # 调用 LLM API
            success, response_data, error = self._call_llm_api(prompt, timeout)

            if not success:
                return False, None, error

            # 解析响应
            result = self._parse_llm_response(response_data)

            if not result:
                return False, None, "LLM 返回数据解析失败"

            logger.info(f"成功分析成分: {ingredients[:50]}...")
            return True, result, None

        except Exception as e:
            logger.exception("分析成分异常")
            return False, None, f"服务器错误: {str(e)}"

    def _build_prompt(self, ingredients: str) -> str:
        """构建 LLM 提示词"""
        return f"""你是一个专业的猫粮成分分析专家。请分析以下猫粮配料表：

{ingredients}

请按照以下要求进行分析：

1. **识别添加剂**：从成分列表中识别所有的添加剂（如维生素、矿物质、防腐剂等），输出为数组。
2. **识别配料**：从成分列表中识别所有的配料（如肉类、谷物等，不含添加剂），输出为数组。
3. **产品标签**：根据成分特点给出2-4个标签（如"高蛋白"、"无谷物"、"成猫粮"等）。
4. **安全性分析**：评估成分的安全性（约50字）。
5. **营养分析**：对整体营养成分进行详细评价（约300字），包括优点和缺点。
6. **百分比数据提取**：
   - 仔细检查配料表中是否明确标注了营养成分的百分比（如"粗蛋白≥30%"、"脂肪15%"、"水分≤10%"等）
   - 如果有，将所有带百分比的营养成分提取到 percent_data 中，字段名使用英文下划线命名
   - 字段名根据实际营养成分动态生成，不限于固定字段（如：crude_protein、crude_fat、moisture、crude_fiber、crude_ash、carbohydrates、calcium、phosphorus、taurine 等）
   - 如果没有明确标注百分比，则 percentage 为 false，percent_data 为空对象

请严格按照以下 JSON 格式返回，不要添加任何额外的说明文字：

{{
  "additive": ["维生素A", "维生素D3"],
  "ingredient": ["鸡肉粉", "鱼肉"],
  "tags": ["高蛋白", "成猫粮"],
  "safety": "安全性分析内容（约50字）",
  "nutrient": "营养分析内容（约300字）",
  "percentage": true,
  "percent_data": {{
    "crude_protein": 30.0,
    "crude_fat": 15.0,
    "moisture": 10.0,
    "crude_fiber": 5.0,
    "crude_ash": 8.0,
    "calcium": 1.2,
    "phosphorus": 1.0
  }}
}}

重要提示：
- percentage: 仅当配料表中明确标注了营养成分百分比时才为 true
- percent_data: 字段名和字段数量完全根据配料表中实际出现的营养成分动态生成，有什么加什么
- 字段名统一使用英文下划线命名（如 crude_protein、crude_fat、crude_fiber、crude_ash、moisture、carbohydrates、calcium、phosphorus、taurine、omega_3、omega_6 等）
- 百分比值为数字类型，不带百分号
- 如果配料表中没有任何百分比标注，percentage 为 false，percent_data 为空对象 {{}}"""

    def _call_llm_api(
        self, prompt: str, timeout: int
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        调用 LLM API

        Returns:
            Tuple[成功标志, 响应数据, 错误信息]
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的猫粮成分分析专家，请严格按照JSON格式返回结果。",
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.3,
                "max_tokens": 2000,
            }

            response = requests.post(
                self.api_url, headers=headers, json=payload, timeout=timeout
            )

            if response.status_code != 200:
                error_msg = f"LLM API 返回错误: {response.status_code}"
                logger.error(error_msg)
                return False, None, error_msg

            return True, response.json(), None

        except requests.Timeout:
            logger.error("LLM API 请求超时")
            return False, None, "请求超时，请稍后重试"

        except Exception as e:
            logger.exception("LLM API 请求异常")
            return False, None, f"API 调用失败: {str(e)}"

    def _parse_llm_response(
        self, response_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        解析 LLM 响应

        Returns:
            解析后的结果字典，或 None
        """
        try:
            # 提取 content
            choices = response_data.get("choices", [])
            if not choices:
                logger.error("LLM 响应中没有 choices")
                return None

            message = choices[0].get("message", {})
            content = message.get("content", "").strip()

            if not content:
                logger.error("LLM 响应内容为空")
                return None

            # 尝试提取 JSON
            json_match = re.search(r"\{[\s\S]*\}", content)
            if json_match:
                json_str = json_match.group()
                result = json.loads(json_str)
            else:
                # 如果没有找到 JSON，尝试直接解析
                result = json.loads(content)

            # 确保必需字段存在
            required_fields = {
                "additive": [],
                "ingredient": [],
                "tags": [],
                "safety": "",
                "nutrient": "",
                "percentage": False,
                "percent_data": {},
            }

            for field, default_value in required_fields.items():
                if field not in result:
                    result[field] = default_value

            # 规范化列表字段
            result["additive"] = self._to_str_list(result.get("additive", []))
            result["ingredient"] = self._to_str_list(result.get("ingredient", []))
            result["tags"] = self._to_str_list(result.get("tags", []))

            # 确保 percentage 是布尔值
            if not isinstance(result.get("percentage"), bool):
                result["percentage"] = False

            # 确保 percent_data 是字典
            if not isinstance(result.get("percent_data"), dict):
                result["percent_data"] = {}

            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {str(e)}")
            return None

        except Exception:
            logger.exception("解析 LLM 响应异常")
            return None

    @staticmethod
    def _to_str_list(value: Any) -> List[str]:
        """
        将各种格式的数据转换为字符串列表

        规则:
        - None -> []
        - list -> 转换为字符串并去除空白
        - str -> 尝试 JSON 解析，或按分隔符分割
        - 其他类型 -> 单元素列表
        """
        if value is None:
            return []

        if isinstance(value, list):
            result = []
            for item in value:
                if item is None:
                    continue
                s = str(item).strip()
                if s:
                    result.append(s)
            return result

        if isinstance(value, str):
            # 尝试 JSON 列表解析
            try:
                loaded = json.loads(value)
                if isinstance(loaded, list):
                    return [
                        str(x).strip()
                        for x in loaded
                        if x is not None and str(x).strip()
                    ]
            except Exception:
                pass

            # 按常见分隔符分割
            parts = [p.strip() for p in re.split(r"[;,，、\n]", value) if p.strip()]
            if parts:
                return parts

            return [value.strip()]

        # fallback
        return [str(value).strip()]


# 全局单例
ai_service = AIService()
