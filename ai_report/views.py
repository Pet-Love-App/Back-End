import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

from django.contrib.auth.models import AnonymousUser, User
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


class Request:
    """Request"""

    additive: list[str]
    ingredient: list[str]
    """营养分析"""
    nutrient: str
    """百分比数据"""
    percent_data: None
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
        percent_data: None,
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
        '  - percent_data（dict,以营养成分英文名作为字段名，例如"carbohydrates"，值为number,各相应成分百分比。如果能分析占比，percentage=True。如果percentage=True，一定要有一个字段是others，代表其他成分的百分比。所有含量之和应为100）\n'
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
            percent_data=None,
        )
        resp = {
            "additive": result.additive,
            "ingredient": result.ingredient,
            "nutrient": result.nutrient,
            "percent_data": result.percent_data,
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
        percent_data=None,
    )

    print("=" * 80)
    print("🔍 [LLM] Parsing structured response...")
    print(f"🔍 [LLM] Type of parsed: {type(parsed)}")
    print(f"🔍 [LLM] Is dict: {isinstance(parsed, dict)}")
    if isinstance(parsed, dict):
        print(f"🔍 [LLM] Keys in parsed dict: {list(parsed.keys())}")
        print("🔍 [LLM] Full parsed content:")
        print(json.dumps(parsed, indent=2, ensure_ascii=False))
    print("=" * 80)

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

        # percent_data
        raw_percent_data = parsed.get("percent_data") or parsed.get("percentage_data") or {}
        print(f"🔍 [LLM Response] Raw percent_data from LLM: {raw_percent_data}")
        print(f"🔍 [LLM Response] Type: {type(raw_percent_data)}")

        schema.percent_data = raw_percent_data
        # make sure percent_data has correct form
        if not isinstance(schema.percent_data, dict):
            print("⚠️ [LLM Response] percent_data is not dict, converting to empty dict")
            schema.percent_data = {}

        print(f"🔍 [LLM Response] After validation, percent_data: {schema.percent_data}")
        print(f"🔍 [LLM Response] Keys count: {len(schema.percent_data)}")

        # make sure sum=100
        if schema.percentage and schema.percent_data:
            total = sum(v for v in schema.percent_data.values() if isinstance(v, (int, float)))
            print(f"🔍 [LLM Response] Total percentage: {total}")
            if 0 < total < 100:
                schema.percent_data["others"] = 100 - total
                print(f"✅ [LLM Response] Added 'others': {100 - total}")

        # make sure "percentage" is False if there is no percent_data(only has others=100)
        if not schema.percent_data or len(schema.percent_data) <= 1:
            print("⚠️ [LLM Response] No valid percent_data, setting percentage to False")
            print(f"   - percent_data empty: {not schema.percent_data}")
            print(
                f"   - percent_data keys: {list(schema.percent_data.keys()) if schema.percent_data else []}"
            )
            schema.percentage = False
        else:
            print(
                f"✅ [LLM Response] Valid percent_data found with {len(schema.percent_data)} fields"
            )
    else:
        # If no structured JSON, do NOT include model's free-form text to avoid leaking reasoning.
        pass

    resp = {
        "additive": schema.additive,
        "ingredient": schema.ingredient,
        "nutrient": schema.nutrient,
        "percent_data": schema.percent_data,
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

from .models import AIAnalysisReport, FavoriteReport
from .serializers import (
    AIAnalysisReportCreateSerializer,
    AIAnalysisReportSerializer,
    FavoriteReportSerializer,
)


@api_view(["POST"])
@permission_classes([AllowAny])
def save_report(request):
    """
    保存AI分析报告到数据库
    POST /api/ai/save/

    权限说明:
    - 普通用户: 仅能为没有营养成分信息的猫粮保存报告
    - 管理员用户: 可以覆盖更新已有营养成分信息的猫粮报告

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
        "percent_data": {
            "protein": 40.0,
            "fat": 18.0,
            "carbohydrates": 20.0,
            "fiber": 3.0,
            "ash": 8.0,
            "others": 11.0
        }
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
        "percent_data": request.data.get("percent_data", {}),
    }

    # 检查是否已存在报告
    try:
        existing_report = AIAnalysisReport.objects.get(catfood=catfood)

        # 权限检查：只有管理员可以更新已有报告
        is_admin = False
        if request.user and not isinstance(request.user, AnonymousUser):
            try:
                is_admin = request.user.profile.is_admin
            except Exception:
                is_admin = False

        if not is_admin:
            return Response(
                {
                    "error": "该猫粮已有营养成分信息，只有管理员可以更新",
                    "message": "普通用户无权覆盖已有的营养成分数据。如需更新，请联系管理员。",
                    "existing_report_id": existing_report.id,
                },
                status=http_status.HTTP_403_FORBIDDEN,
            )

        # 管理员更新现有报告
        serializer = AIAnalysisReportCreateSerializer(existing_report, data=report_data)
        if serializer.is_valid():
            serializer.save()
            response_serializer = AIAnalysisReportSerializer(serializer.instance)
            return Response(
                {
                    "message": "报告更新成功（管理员权限）",
                    "report": response_serializer.data,
                },
                status=http_status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=http_status.HTTP_400_BAD_REQUEST)
    except AIAnalysisReport.DoesNotExist:
        # 创建新报告（所有用户均可）
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
    GET /api/ai/{catfood_id}/

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
        "percent_data": {"protein": 40, "fat": 18, ...},
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
    DELETE /api/ai/{catfood_id}/delete/
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
        "report_id": 1,
        "updated_at": "2025-01-01T00:00:00Z"
    }
    """
    catfood = get_object_or_404(CatFood, id=catfood_id)

    try:
        report = AIAnalysisReport.objects.get(catfood=catfood)
        return Response(
            {
                "exists": True,
                "catfood_id": catfood_id,
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


# ========== 报告收藏相关API ==========


@api_view(["GET"])
@permission_classes([AllowAny])
def get_favorite_reports(request: HttpRequest) -> Response:
    """
    获取用户收藏的AI报告列表
    """
    # 临时用户处理（后续需要改为真实用户认证）
    if isinstance(request.user, AnonymousUser):
        # 使用默认用户（ID=1）或返回空列表
        try:
            user = User.objects.get(id=1)
        except User.DoesNotExist:
            return Response({"results": [], "count": 0}, status=http_status.HTTP_200_OK)
    else:
        user = request.user

    # 获取收藏列表
    favorites = FavoriteReport.objects.filter(user=user).select_related("report", "report__catfood")

    serializer = FavoriteReportSerializer(favorites, many=True)

    return Response(
        {"results": serializer.data, "count": favorites.count()}, status=http_status.HTTP_200_OK
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def toggle_favorite_report(request: HttpRequest) -> Response:
    """
    切换AI报告收藏状态
    请求体: {"report_id": 123}
    """
    report_id = request.data.get("report_id")

    if not report_id:
        return Response({"error": "缺少 report_id 参数"}, status=http_status.HTTP_400_BAD_REQUEST)

    # 临时用户处理
    if isinstance(request.user, AnonymousUser):
        try:
            user = User.objects.get(id=1)
        except User.DoesNotExist:
            return Response(
                {"error": "用户不存在，请先登录"}, status=http_status.HTTP_401_UNAUTHORIZED
            )
    else:
        user = request.user

    # 检查报告是否存在
    try:
        report = AIAnalysisReport.objects.get(id=report_id)
    except AIAnalysisReport.DoesNotExist:
        return Response(
            {"error": f"AI报告 ID {report_id} 不存在"}, status=http_status.HTTP_404_NOT_FOUND
        )

    # 检查是否已收藏
    favorite = FavoriteReport.objects.filter(user=user, report=report).first()

    if favorite:
        # 已收藏，取消收藏
        favorite.delete()
        return Response(
            {
                "detail": "已取消收藏",
                "is_favorited": False,
                "report_id": report_id,
            },
            status=http_status.HTTP_200_OK,
        )
    else:
        # 未收藏，添加收藏
        favorite = FavoriteReport.objects.create(user=user, report=report)
        serializer = FavoriteReportSerializer(favorite)
        return Response(
            {
                "detail": "收藏成功",
                "is_favorited": True,
                "favorite": serializer.data,
            },
            status=http_status.HTTP_201_CREATED,
        )


@api_view(["DELETE"])
@permission_classes([AllowAny])
def delete_favorite_report(request: HttpRequest, favorite_id: int) -> Response:
    """
    删除AI报告收藏
    """
    # 临时用户处理
    if isinstance(request.user, AnonymousUser):
        try:
            user = User.objects.get(id=1)
        except User.DoesNotExist:
            return Response(
                {"error": "用户不存在，请先登录"}, status=http_status.HTTP_401_UNAUTHORIZED
            )
    else:
        user = request.user

    # 查找收藏记录
    try:
        favorite = FavoriteReport.objects.get(id=favorite_id, user=user)
    except FavoriteReport.DoesNotExist:
        return Response({"error": "收藏记录不存在"}, status=http_status.HTTP_404_NOT_FOUND)

    favorite.delete()

    return Response({"detail": "删除成功"}, status=http_status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
def check_favorite_report(request: HttpRequest, report_id: int) -> Response:
    """
    检查AI报告是否已收藏
    """
    # 临时用户处理
    if isinstance(request.user, AnonymousUser):
        try:
            user = User.objects.get(id=1)
        except User.DoesNotExist:
            return Response({"is_favorited": False}, status=http_status.HTTP_200_OK)
    else:
        user = request.user

    # 检查是否已收藏
    is_favorited = FavoriteReport.objects.filter(user=user, report_id=report_id).exists()

    return Response({"is_favorited": is_favorited}, status=http_status.HTTP_200_OK)
