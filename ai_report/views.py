import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

try:
    # Prefer requests if available for simplicity
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # fall back to urllib at runtime


def _post_json(url: str, data: dict, headers: dict, timeout: int = 120) -> tuple[int, str]:
    """Send a POST with JSON using requests if present, otherwise urllib.

    Returns: (status_code, text_body)
    """
    body = json.dumps(data).encode("utf-8")

    if requests is not None:
        try:
            resp = requests.post(url, json=data, headers=headers, timeout=timeout)
            return resp.status_code, resp.text
        except Exception as e:  # pragma: no cover
            # Normalize exception as a 0 status with message
            return 0, str(e)

    req = urllib.request.Request(
        url,
        data=body,
        headers=headers | {"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec B310
            status = resp.status
            text = resp.read().decode("utf-8", errors="replace")
            return status, text
    except urllib.error.HTTPError as e:  # pragma: no cover
        return e.code, e.read().decode("utf-8", errors="replace")
    except Exception as e:  # pragma: no cover
        return 0, str(e)


from typing import List, Optional


class PercentData:
    """百分比数据"""

    carbohydrates: float | None
    crude_ash: float | None
    crude_fat: float | None
    crude_fiber: float | None
    crude_protein: float | None
    others: float | None

    def __init__(
        self,
        carbohydrates: float | None,
        crude_ash: float | None,
        crude_fat: float | None,
        crude_fiber: float | None,
        crude_protein: float | None,
        others: float | None,
    ) -> None:
        self.carbohydrates = carbohydrates
        self.crude_ash = crude_ash
        self.crude_fat = crude_fat
        self.crude_fiber = crude_fiber
        self.crude_protein = crude_protein
        self.others = others


class Request:
    """Request"""

    additive: list[str]
    ingredient: list[str]
    """营养分析"""
    nutrient: str
    """百分比数据"""
    percent_data: PercentData
    """是否支持百分比分析"""
    percentage: bool
    """安全性分析"""
    safety: str
    """标签"""
    tags: list[str]

    def __init__(
        self,
        additive: list[str],
        ingredient: list[str],
        nutrient: str,
        percent_data: PercentData,
        percentage: bool,
        safety: str,
        tags: list[str],
    ) -> None:
        self.additive = additive
        self.ingredient = ingredient
        self.nutrient = nutrient
        self.percent_data = percent_data
        self.percentage = percentage
        self.safety = safety
        self.tags = tags


@csrf_exempt
@require_http_methods(["GET", "POST"])
def llm_chat(request: HttpRequest) -> JsonResponse:
    """
    A minimal JSON API to call an OpenAI-compatible chat completion endpoint.

    GET: returns usage hint
    POST JSON body: { "prompt": str, "system"?: str, "model"?: str, "max_tokens"?: int }
    Response JSON: {
    """

    if request.method == "GET":
        return JsonResponse(
            {
                "ok": True,
                "message": "POST JSON {prompt, system?, model?, max_tokens?} to receive completion.",
            }
        )

    # POST
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse(
            {"ok": False, "error": {"code": "bad_json", "message": "Invalid JSON"}},
            status=400,
        )

    # Require a single field `ingredients` (string) as input.
    ingredients = (payload.get("ingredients") or "").strip()
    if not ingredients:
        return JsonResponse({"error": "missing ingredients"}, status=400)

    # Use ingredients as the user's content; we do not accept arbitrary prompts or system overrides.
    prompt = ingredients
    # Model default can be overridden by environment.
    model: str = os.environ.get("LLM_MODEL", "DeepSeek-V3.2-Exp")
    max_tokens: int = int(payload.get("max_tokens", 2048))

    api_url = os.environ.get("LLM_API_URL") or "https://llmapi.paratera.com/v1/chat/completions"
    api_key = os.environ.get("LLM_API_KEY") or "sk-b4C9_BWHAkjKhYVwq0VD1g"
    if not api_url or not api_key:
        return JsonResponse(
            {
                "ok": False,
                "error": {
                    "code": "config",
                    "message": "Server missing LLM_API_URL and LLM_API_KEY (or OPENAI_API_KEY)",
                },
            },
            status=503,
        )
    messages: list[dict] = []
    # Always set a system instruction in Chinese; JSON field names must stay English.
    system_instruction = (
        "你是宠物食品配方与营养专家。\n"
        "根据用户提供的猫粮配料表，只输出一个 JSON 对象。字段名必须用英文，字段内容用中文。\n"
        "严格要求：\n"
        "- 只能输出 JSON 对象本身，禁止出现任何额外文字（包括‘首先’、‘现在’、‘需要’、‘说明’、‘分析’等词句）、禁止重复题目或解释步骤。\n"
        "- 字段说明（英文字段名，内容中文）：\n"
        "  - tags（array，分析产品特征（幼猫粮，成猫粮，全价猫粮，无谷，高蛋白，泌尿健康，养毛护肤，呵护肠胃，增肥发腮，高含肉量），元素为字符串）。\n"
        "  - additives（array，可选，识别到的添加剂名称列表，元素为字符串）。\n"
        "  - identified_nutrients（array，可选，识别到的营养成分或营养标签的名称列表，元素为字符串）。\n"
        "  - safety（string，必填，大约50个汉字的针对猫粮的简要安全性分析，重点关注添加剂）；\n"
        "  - nutrient（string，必填，大约300个汉字的针对猫粮的简要营养分析）；\n"
        "  - percentage（boolean/null，可选，如果你能分析出以下各成分占比，请在此处填True，否则填False。尽可能分析！）；\n"
        "  - crude_protein、crude_fat、carbohydrates、crude_fiber、crude_ash、others（number，可选，各相应成分百分比。如果能分析占比，percentage=True，需要把每一个比例都填上。没有填0.）。\n"
        "- 数值字段无法判断时返回 null；数组字段无法判断或无识别结果时返回空数组。\n"
        "- 禁止输出推理过程或步骤说明，只保留结论性短句或最终的 JSON 字段内容。\n"
    )

    messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": prompt})

    provider_payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.0,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    status, text = _post_json(api_url, provider_payload, headers)
    if status == 0:
        return JsonResponse(
            {
                "ok": False,
                "error": {"code": "network", "message": "request failed", "detail": text},
            },
            status=502,
        )

    # Attempt to parse JSON - models sometimes return JSON as text
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # try to extract a JSON substring
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                data = json.loads(text[start : end + 1])
            except Exception:
                data = None
        else:
            data = None

    if status >= 400 or data is None:
        # Return the minimal schema with empty/nulls (no extra debug fields)
        result = Request(
            tags=[],
            additive=[],
            ingredient=[],
            nutrient="",
            safety="",
            percentage=False,
            percent_data=PercentData(
                carbohydrates=None,
                crude_ash=None,
                crude_fat=None,
                crude_fiber=None,
                crude_protein=None,
                others=None,
            ),
        )
        resp = {
            "additive": result.additive,
            "ingredient": result.ingredient,
            "nutrient": result.nutrient,
            "percent_data": {
                "carbohydrates": result.percent_data.carbohydrates,
                "crude_ash": result.percent_data.crude_ash,
                "crude_fat": result.percent_data.crude_fat,
                "crude_fiber": result.percent_data.crude_fiber,
                "crude_protein": result.percent_data.crude_protein,
                "others": result.percent_data.others,
            },
            "percentage": result.percentage,
            "safety": result.safety,
            "tags": result.tags,
        }
        return JsonResponse(resp, status=200)

    # Extract assistant text from common provider shapes
    extracted_text = None
    if isinstance(data, dict):
        choices = data.get("choices")
        if isinstance(choices, list) and choices:
            first = choices[0]
            msg = (first or {}).get("message") or {}
            extracted_text = (
                msg.get("content") or msg.get("reasoning_content") or (first or {}).get("text")
            )
        if extracted_text is None and "output" in data:
            out = data.get("output")
            extracted_text = out if isinstance(out, str) else json.dumps(out, ensure_ascii=False)

    # Try to parse the extracted_text as JSON
    parsed = None
    if isinstance(extracted_text, str):
        try:
            parsed = json.loads(extracted_text)
        except Exception:
            s = extracted_text.find("{")
            e = extracted_text.rfind("}")
            if s != -1 and e != -1 and e > s:
                try:
                    parsed = json.loads(extracted_text[s : e + 1])
                except Exception:
                    parsed = None

    def _to_number(v):
        if v is None:
            return None
        if isinstance(v, int | float):
            return float(v)
        try:
            return float(str(v).strip())
        except Exception:
            return None

    def _to_str_list(v):
        """Coerce various shapes into a list of stripped strings.

        Rules:
        - None -> []
        - list -> map str() and strip
        - str -> try to json.loads (if it's a JSON list), otherwise split on common separators and newlines
        - other types -> single-element list with str()
        """
        if v is None:
            return []
        if isinstance(v, list):
            out = []
            for x in v:
                if x is None:
                    continue
                s = str(x).strip()
                if s:
                    out.append(s)
            return out
        if isinstance(v, str):
            # try JSON list
            try:
                loaded = json.loads(v)
                if isinstance(loaded, list):
                    return [str(x).strip() for x in loaded if x is not None and str(x).strip()]
            except Exception:
                pass
            # split on common delimiters
            parts = [p.strip() for p in re.split(r"[;,，、\n]", v) if p.strip()]
            if parts:
                return parts
            return [v.strip()]
        # fallback
        return [str(v).strip()]

    schema = Request(
        tags=[],
        additive=[],
        ingredient=[],
        nutrient="",
        safety="",
        percentage=False,
        percent_data=PercentData(
            carbohydrates=None,
            crude_ash=None,
            crude_fat=None,
            crude_fiber=None,
            crude_protein=None,
            others=None,
        ),
    )

    if isinstance(parsed, dict):
        # Extract tags
        raw_tags = parsed.get("tags") or parsed.get("product_tags")
        # possible tags:幼猫粮，成猫粮，全价猫粮，无谷，高蛋白，泌尿健康，养毛护肤，呵护肠胃，增肥发腮，高含肉量
        schema.tags = _to_str_list(raw_tags)
        for tag in schema.tags:
            if tag not in [
                "幼猫粮",
                "成猫粮",
                "全价猫粮",
                "无谷",
                "高蛋白",
                "泌尿健康",
                "养毛护肤",
                "呵护肠胃",
                "增肥发腮",
                "高含肉量",
            ]:
                schema.tags.remove(tag)
        # additives and identified nutrient names
        raw_add = (
            parsed.get("additives")
            or parsed.get("identified_additives")
            or parsed.get("additive_list")
            or parsed.get("additives_list")
        )
        schema.additive = _to_str_list(raw_add)

        raw_id_nut = (
            parsed.get("identified_nutrients")
            or parsed.get("nutrients")
            or parsed.get("identified_nutrition")
            or parsed.get("nutrition_components")
        )
        schema.ingredient = _to_str_list(raw_id_nut)
        schema.safety = str(parsed.get("safety") or parsed.get("safety_analysis") or "")
        schema.nutrient = str(parsed.get("nutrient") or parsed.get("nutrition") or "")
        pct = (
            parsed.get("percentage")
            if parsed.get("percentage") is not None
            else parsed.get("has_percentage")
        )
        if isinstance(pct, bool):
            schema.percentage = True if pct else False
        elif isinstance(pct, int | float | str):
            try:
                iv = int(pct)
                schema.percentage = True if iv != 0 else False
            except Exception:
                schema.percentage = False

        schema.percent_data.crude_protein = _to_number(
            parsed.get("crude_protein") or parsed.get("protein")
        )
        schema.percent_data.crude_fat = _to_number(parsed.get("crude_fat") or parsed.get("fat"))
        schema.percent_data.carbohydrates = _to_number(
            parsed.get("carbohydrates") or parsed.get("carb")
        )
        schema.percent_data.crude_fiber = _to_number(
            parsed.get("crude_fiber") or parsed.get("fiber")
        )
        schema.percent_data.crude_ash = _to_number(parsed.get("crude_ash") or parsed.get("ash"))
        # others=100-sum(known)
        schema.percent_data.others = 100 - sum(
            filter(
                None,
                [
                    schema.percent_data.crude_protein,
                    schema.percent_data.crude_fat,
                    schema.percent_data.carbohydrates,
                    schema.percent_data.crude_fiber,
                    schema.percent_data.crude_ash,
                ],
            )
        )
    else:
        # If no structured JSON, do NOT include model's free-form text to avoid leaking reasoning.
        pass

    resp = {
        "additive": schema.additive,
        "ingredient": schema.ingredient,
        "nutrient": schema.nutrient,
        "percent_data": {
            "carbohydrates": schema.percent_data.carbohydrates,
            "crude_ash": schema.percent_data.crude_ash,
            "crude_fat": schema.percent_data.crude_fat,
            "crude_fiber": schema.percent_data.crude_fiber,
            "crude_protein": schema.percent_data.crude_protein,
            "others": schema.percent_data.others,
        },
        "percentage": schema.percentage,
        "safety": schema.safety,
        "tags": schema.tags,
    }

    return JsonResponse(resp, status=200)


# 新增的报告管理API

from django.shortcuts import get_object_or_404
from rest_framework import status as http_status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from catfood.models import CatFood

from .models import AIAnalysisReport
from .serializers import AIAnalysisReportCreateSerializer, AIAnalysisReportSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def save_report(request):
    """
    保存AI分析报告到数据库
    POST /api/ai-report/save/

    请求体示例:
    {
        "catfood_id": 1,
        "ingredients_text": "鸡肉、鱼肉...",
        "tags": ["成猫粮", "高蛋白"],
        "additives": ["牛磺酸", "维生素E"],
        "ingredients": ["粗蛋白", "粗脂肪"],
        "safety": "安全性分析...",
        "nutrient": "营养分析...",
        "percentage": true,
        "crude_protein": 40.0,
        "crude_fat": 18.0,
        "carbohydrates": 20.0,
        "crude_fiber": 3.0,
        "crude_ash": 8.0,
        "others": 11.0
    }
    """
    catfood_id = request.data.get("catfood_id")

    if not catfood_id:
        return Response({"error": "缺少 catfood_id 参数"}, status=http_status.HTTP_400_BAD_REQUEST)

    # 检查猫粮是否存在
    try:
        catfood = CatFood.objects.get(id=catfood_id)
    except CatFood.DoesNotExist:
        return Response(
            {"error": f"猫粮 ID {catfood_id} 不存在"}, status=http_status.HTTP_404_NOT_FOUND
        )

    # 准备数据
    report_data = {
        "catfood": catfood.id,
        "ingredients_text": request.data.get("ingredients_text", ""),
        "tags": request.data.get("tags", []),
        "additives": request.data.get("additives", []),
        "ingredients": request.data.get("ingredients", []),
        "safety": request.data.get("safety", ""),
        "nutrient": request.data.get("nutrient", ""),
        "percentage": request.data.get("percentage", False),
        "crude_protein": request.data.get("percent_data", {}).get("crude_protein")
        or request.data.get("crude_protein"),
        "crude_fat": request.data.get("percent_data", {}).get("crude_fat")
        or request.data.get("crude_fat"),
        "carbohydrates": request.data.get("percent_data", {}).get("carbohydrates")
        or request.data.get("carbohydrates"),
        "crude_fiber": request.data.get("percent_data", {}).get("crude_fiber")
        or request.data.get("crude_fiber"),
        "crude_ash": request.data.get("percent_data", {}).get("crude_ash")
        or request.data.get("crude_ash"),
        "others": request.data.get("percent_data", {}).get("others") or request.data.get("others"),
    }

    # 检查是否已存在报告
    try:
        existing_report = AIAnalysisReport.objects.get(catfood=catfood)
        # 更新现有报告
        serializer = AIAnalysisReportCreateSerializer(existing_report, data=report_data)
        if serializer.is_valid():
            serializer.save()
            response_serializer = AIAnalysisReportSerializer(serializer.instance)
            return Response(
                {"message": "报告更新成功", "report": response_serializer.data},
                status=http_status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=http_status.HTTP_400_BAD_REQUEST)
    except AIAnalysisReport.DoesNotExist:
        # 创建新报告
        serializer = AIAnalysisReportCreateSerializer(data=report_data)
        if serializer.is_valid():
            serializer.save()
            response_serializer = AIAnalysisReportSerializer(serializer.instance)
            return Response(
                {"message": "报告保存成功", "report": response_serializer.data},
                status=http_status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=http_status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_report(request, catfood_id):
    """
    获取指定猫粮的AI分析报告
    GET /api/ai-report/{catfood_id}/

    返回示例:
    {
        "id": 1,
        "catfood_id": 1,
        "catfood_name": "某品牌猫粮",
        "ingredients_text": "...",
        "tags": [...],
        "additives": [...],
        "ingredients": [...],
        "safety": "...",
        "nutrient": "...",
        "percentage": true,
        "percent_data": {...},
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z"
    }
    """
    # 检查猫粮是否存在
    catfood = get_object_or_404(CatFood, id=catfood_id)

    # 获取报告
    try:
        report = AIAnalysisReport.objects.get(catfood=catfood)
        serializer = AIAnalysisReportSerializer(report)
        return Response(serializer.data, status=http_status.HTTP_200_OK)
    except AIAnalysisReport.DoesNotExist:
        return Response(
            {
                "error": "该猫粮暂无AI分析报告",
                "catfood_id": catfood_id,
                "catfood_name": catfood.name,
            },
            status=http_status.HTTP_404_NOT_FOUND,
        )


@api_view(["DELETE"])
@permission_classes([AllowAny])
def delete_report(request, catfood_id):
    """
    删除指定猫粮的AI分析报告（用于重新生成）
    DELETE /api/ai-report/{catfood_id}/
    """
    catfood = get_object_or_404(CatFood, id=catfood_id)

    try:
        report = AIAnalysisReport.objects.get(catfood=catfood)
        report.delete()
        return Response({"message": "报告删除成功，可以重新生成"}, status=http_status.HTTP_200_OK)
    except AIAnalysisReport.DoesNotExist:
        return Response({"error": "该猫粮没有分析报告"}, status=http_status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@permission_classes([AllowAny])
def check_report_exists(request, catfood_id):
    """
    检查指定猫粮是否已有AI分析报告
    GET /api/ai/{catfood_id}/exists/

    返回示例:
    {
        "exists": true,
        "catfood_id": 1,
        "updated_at": "2025-01-01T00:00:00Z"
    }
    """
    # 检查猫粮是否存在
    try:
        catfood = CatFood.objects.get(id=catfood_id)
    except CatFood.DoesNotExist:
        return Response(
            {"error": f"猫粮 ID {catfood_id} 不存在", "exists": False, "catfood_id": catfood_id},
            status=http_status.HTTP_404_NOT_FOUND,
        )

    # 检查报告是否存在
    try:
        report = AIAnalysisReport.objects.get(catfood=catfood)
        return Response(
            {
                "exists": True,
                "catfood_id": catfood_id,
                "catfood_name": catfood.name,
                "report_id": report.id,
                "updated_at": report.updated_at,
            },
            status=http_status.HTTP_200_OK,
        )
    except AIAnalysisReport.DoesNotExist:
        return Response(
            {"exists": False, "catfood_id": catfood_id, "catfood_name": catfood.name},
            status=http_status.HTTP_200_OK,
        )
