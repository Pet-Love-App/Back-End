"""
AI 报告相关 API
使用 Supabase 进行数据操作，集成 LLM API
"""

import json
import os
import re

import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from config.supabase_client import supabase_admin
from middleware.supabase_auth import get_current_user, require_auth
from utils import parse_json_body, safe_single

# LLM API 配置（兼容 OpenAI 格式的 API）
LLM_API_KEY = (
    os.getenv("LLM_API_KEY")
    or os.getenv("OPENAI_API_KEY")
    or "sk-b4C9_BWHAkjKhYVwq0VD1g"
)
LLM_API_URL = (
    os.getenv("LLM_API_URL")
    or os.getenv("OPENAI_API_BASE")
    or "https://llmapi.paratera.com/v1/chat/completions"
)
LLM_MODEL = os.getenv("LLM_MODEL") or os.getenv("OPENAI_MODEL") or "DeepSeek-V3.2-Exp"


def _post_json(url, headers, data, timeout=120):
    """
    发送 POST 请求到 LLM API（兼容 OpenAI 格式）
    返回: (status_code, response_text)
    """
    try:
        response = requests.post(url, headers=headers, json=data, timeout=timeout)
        return (response.status_code, response.text)
    except requests.exceptions.RequestException as e:
        return (0, str(e))


def _to_str_list(v):
    """
    将各种格式的数据转换为字符串列表

    规则:
    - None -> []
    - list -> 转换为字符串并去除空白
    - str -> 尝试 JSON 解析，或按分隔符分割
    - 其他类型 -> 单元素列表
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
        # 尝试 JSON 列表解析
        try:
            loaded = json.loads(v)
            if isinstance(loaded, list):
                return [
                    str(x).strip() for x in loaded if x is not None and str(x).strip()
                ]
        except Exception:
            pass
        # 按常见分隔符分割
        parts = [p.strip() for p in re.split(r"[;,，、\n]", v) if p.strip()]
        if parts:
            return parts
        return [v.strip()]
    # fallback
    return [str(v).strip()]


@csrf_exempt
@require_http_methods(["POST"])
def llm_chat(request):
    """
    LLM 聊天接口 - 分析猫粮成分

    POST /api/ai/llm/chat/
    Body: {
        "ingredients": "鸡肉粉, 鱼肉粉, 维生素D"
    }

    返回格式:
    {
        "additive": ["维生素D"],
        "ingredient": ["鸡肉粉", "鱼肉粉"],
        "nutrient": "营养分析详述",
        "safety": "安全评估",
        "percentage": true/false,
        "percent_data": {
            "crude_protein": 30.0,
            "crude_fat": 10.0,
            "carbohydrates": 40.0,
            "crude_fiber": 5.0,
            "crude_ash": 5.0,
            "others": 10.0
        },
        "tags": ["标签1", "标签2"]
    }
    """
    try:
        try:
            data = parse_json_body(request)
        except ValueError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        ingredients = (data.get("ingredients") or "").strip()
        if not ingredients:
            return JsonResponse({"error": "ingredients field is required"}, status=400)

        # 检查 API Key
        if not LLM_API_KEY:
            return JsonResponse(
                {
                    "ok": False,
                    "error": {
                        "message": "LLM_API_KEY not configured",
                        "type": "configuration_error",
                    },
                },
                status=502,
            )

        # 构建更强大的系统提示词
        system_instruction = (
            "你是宠物食品配方与营养专家。\n"
            "根据用户提供的猫粮配料表，只输出一个 JSON 对象。字段名必须用英文，字段内容用中文。\n"
            "严格要求：\n"
            "- 只能输出 JSON 对象本身，禁止出现任何额外文字（包括'首先'、'现在'、'需要'、'说明'、'分析'等词句）、禁止重复题目或解释步骤。\n"
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

        # 调用 LLM API（兼容 OpenAI 格式）
        headers = {
            "Authorization": f"Bearer {LLM_API_KEY}",
            "Content-Type": "application/json",
        }

        request_data = {
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": ingredients},
            ],
            "temperature": 0.0,  # 降低温度以获得更一致的输出
            "max_tokens": 2048,  # 增加 token 限制
        }

        status_code, response_text = _post_json(LLM_API_URL, headers, request_data)

        # 处理网络错误
        if status_code == 0:
            return JsonResponse(
                {
                    "ok": False,
                    "error": {"message": response_text, "type": "network_error"},
                },
                status=502,
            )

        # 尝试解析 JSON 响应
        try:
            response_json = json.loads(response_text)
        except json.JSONDecodeError:
            # 尝试提取 JSON 子串
            start = response_text.find("{")
            end = response_text.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    response_json = json.loads(response_text[start : end + 1])
                except Exception:
                    response_json = None
            else:
                response_json = None

        # 处理 API 错误
        if status_code >= 400 or response_json is None:
            print(
                f"❌ [LLM] API error: status={status_code}, response={response_text[:200]}"
            )
            return JsonResponse(
                {
                    "additive": [],
                    "ingredient": [],
                    "nutrient": "",
                    "safety": "",
                    "percentage": False,
                    "percent_data": {},
                    "tags": [],
                },
                status=200,  # 返回 200 但数据为空
            )

        # 从响应中提取 AI 生成的文本
        extracted_text = None
        if isinstance(response_json, dict):
            choices = response_json.get("choices")
            if isinstance(choices, list) and choices:
                first = choices[0]
                msg = (first or {}).get("message") or {}
                extracted_text = (
                    msg.get("content")
                    or msg.get("reasoning_content")
                    or (first or {}).get("text")
                )
            if extracted_text is None and "output" in response_json:
                out = response_json.get("output")
                extracted_text = (
                    out if isinstance(out, str) else json.dumps(out, ensure_ascii=False)
                )

        # 解析 AI 返回的 JSON
        parsed = None
        if isinstance(extracted_text, str):
            try:
                parsed = json.loads(extracted_text)
            except Exception:
                # 尝试提取 JSON 子串
                s = extracted_text.find("{")
                e = extracted_text.rfind("}")
                if s != -1 and e != -1 and e > s:
                    try:
                        parsed = json.loads(extracted_text[s : e + 1])
                    except Exception:
                        parsed = None

        print("=" * 80)
        print("🔍 [LLM] 解析结构化响应...")
        print(f"🔍 [LLM] Type of parsed: {type(parsed)}")
        print(f"🔍 [LLM] Is dict: {isinstance(parsed, dict)}")
        if isinstance(parsed, dict):
            print(f"🔍 [LLM] Keys in parsed dict: {list(parsed.keys())}")
            print("🔍 [LLM] Full parsed content:")
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
        print("=" * 80)

        # 初始化默认结构
        result = {
            "tags": [],
            "additive": [],
            "ingredient": [],
            "nutrient": "",
            "safety": "",
            "percentage": False,
            "percent_data": {},
        }

        if isinstance(parsed, dict):
            # 提取标签（带白名单验证）
            raw_tags = parsed.get("tags") or parsed.get("product_tags")
            tags_whitelist = [
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
            ]
            result["tags"] = [
                tag for tag in _to_str_list(raw_tags) if tag in tags_whitelist
            ]

            # 提取添加剂
            raw_add = (
                parsed.get("additives")
                or parsed.get("identified_additives")
                or parsed.get("additive_list")
                or parsed.get("additives_list")
            )
            result["additive"] = _to_str_list(raw_add)

            # 提取营养成分
            raw_id_nut = (
                parsed.get("identified_nutrients")
                or parsed.get("nutrients")
                or parsed.get("identified_nutrition")
                or parsed.get("nutrition_components")
            )
            result["ingredient"] = _to_str_list(raw_id_nut)

            # 提取文本分析
            result["safety"] = str(
                parsed.get("safety") or parsed.get("safety_analysis") or ""
            )
            result["nutrient"] = str(
                parsed.get("nutrient") or parsed.get("nutrition") or ""
            )

            # 提取百分比标志
            pct = (
                parsed.get("percentage")
                if parsed.get("percentage") is not None
                else parsed.get("has_percentage")
            )
            if isinstance(pct, bool):
                result["percentage"] = pct
            elif isinstance(pct, (int, float, str)):
                try:
                    iv = int(pct)
                    result["percentage"] = bool(iv)
                except Exception:
                    result["percentage"] = False

            # 提取百分比数据
            raw_percent_data = (
                parsed.get("percent_data") or parsed.get("percentage_data") or {}
            )
            print(f"🔍 [LLM Response] Raw percent_data from LLM: {raw_percent_data}")
            print(f"🔍 [LLM Response] Type: {type(raw_percent_data)}")

            if isinstance(raw_percent_data, dict):
                result["percent_data"] = raw_percent_data
            else:
                print(
                    "⚠️ [LLM Response] percent_data is not dict, converting to empty dict"
                )
                result["percent_data"] = {}

            print(
                f"🔍 [LLM Response] After validation, percent_data: {result['percent_data']}"
            )
            print(f"🔍 [LLM Response] Keys count: {len(result['percent_data'])}")

            # 确保百分比总和为 100
            if result["percentage"] and result["percent_data"]:
                total = sum(
                    v
                    for v in result["percent_data"].values()
                    if isinstance(v, (int, float))
                )
                print(f"🔍 [LLM Response] Total percentage: {total}")
                if 0 < total < 100:
                    result["percent_data"]["others"] = round(100 - total, 2)
                    print(f"✅ [LLM Response] Added 'others': {100 - total}")

            # 如果没有有效的百分比数据，设置 percentage 为 False
            if not result["percent_data"] or len(result["percent_data"]) <= 1:
                print(
                    "⚠️ [LLM Response] No valid percent_data, setting percentage to False"
                )
                result["percentage"] = False
            else:
                print(
                    f"✅ [LLM Response] Valid percent_data found with {len(result['percent_data'])} fields"
                )

        return JsonResponse(result, status=200)

    except Exception as e:
        print(f"❌ [LLM] Exception: {str(e)}")
        import traceback

        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
def save_report(request):
    """
    保存或更新 AI 分析报告（参考旧项目逻辑）

    POST /api/ai/save/
    Body: {
        "catfood_id": 123,
        "ingredients_text": "报告内容",
        "tags": [...],
        "additives": [...],
        "ingredients": [...],
        "safety": "...",
        "nutrient": "...",
        "percentage": true/false,
        "percent_data": {...}
    }

    权限说明（参考旧项目）:
    - 普通用户: 仅能为没有营养成分信息的猫粮保存报告
    - 管理员用户: 可以覆盖更新已有营养成分信息的猫粮报告
    """
    try:
        user = get_current_user(request)
        try:
            data = parse_json_body(request)
        except ValueError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        catfood_id = data.get("catfood_id")
        ingredients_text = data.get("ingredients_text") or data.get("content")

        if not catfood_id or not ingredients_text:
            return JsonResponse(
                {"error": "catfood_id and ingredients_text are required"}, status=400
            )

        # 检查猫粮是否存在
        catfood_result = (
            supabase_admin.table("catfoods").select("*").eq("id", catfood_id).execute()
        )
        catfood_data, error = safe_single(catfood_result, "Catfood not found")
        if error:
            return JsonResponse({"error": error}, status=404)

        # 检查是否已存在报告
        existing_report = (
            supabase_admin.table("ai_analysis_reports")
            .select("id")
            .eq("catfood_id", catfood_id)
            .execute()
        )

        # 检查猫粮是否已有营养成分数据
        has_nutrition_data = (
            catfood_data.get("percentage")
            or catfood_data.get("crude_protein") is not None
            or catfood_data.get("safety")
            or catfood_data.get("nutrient")
        )

        # 权限检查：只有管理员可以更新已有营养成分信息的猫粮
        is_admin = False
        if user:
            try:
                profile_result = (
                    supabase_admin.table("user_profiles")
                    .select("is_admin")
                    .eq("user_id", user.id)
                    .execute()
                )
                if profile_result.data:
                    is_admin = profile_result.data[0].get("is_admin", False)
            except Exception:
                pass

        if has_nutrition_data and not is_admin:
            return JsonResponse(
                {
                    "error": "该猫粮已有营养成分信息，只有管理员可以更新",
                    "message": "普通用户无权覆盖已有的营养成分数据。如需更新，请联系管理员。",
                    "existing_report_id": existing_report.data[0]["id"]
                    if existing_report.data
                    else None,
                },
                status=403,
            )

        # 构建报告数据
        report_data = {
            "catfood_id": catfood_id,
            "ingredients_text": ingredients_text,
            "safety": data.get("safety", ""),
            "nutrient": data.get("nutrient", ""),
            "percentage": data.get("percentage", False),
            "percent_data": data.get("percent_data", {}),
            "tags": data.get("tags", []),
            "additives": data.get("additives", []),
            "ingredients": data.get("ingredients", []),
        }

        # 保存/更新报告到 ai_analysis_reports 表
        if existing_report.data:
            result = (
                supabase_admin.table("ai_analysis_reports")
                .update(report_data)
                .eq("id", existing_report.data[0]["id"])
                .execute()
            )
            message = "报告更新成功"
        else:
            result = (
                supabase_admin.table("ai_analysis_reports")
                .insert(report_data)
                .execute()
            )
            message = "报告保存成功"

        # 同步营养成分数据到 catfoods 表（参考旧项目逻辑）
        catfood_update_data = {
            "safety": data.get("safety", ""),
            "nutrient": data.get("nutrient", ""),
            "percentage": data.get("percentage", False),
        }

        # 处理 percent_data：将其解包到各个营养成分字段
        # 需要处理字段名映射（AI 返回的简短名称 vs 数据库完整名称）
        percent_data = data.get("percent_data", {})
        if percent_data and isinstance(percent_data, dict):
            # 字段名映射表：AI返回的字段名 -> 数据库字段名
            field_mapping = {
                "protein": "crude_protein",
                "fat": "crude_fat",
                "fiber": "crude_fiber",
                "ash": "crude_ash",
                # 这些字段名相同，无需映射
                "crude_protein": "crude_protein",
                "crude_fat": "crude_fat",
                "crude_fiber": "crude_fiber",
                "crude_ash": "crude_ash",
                "carbohydrates": "carbohydrates",
                "others": "others",
                "moisture": "moisture",
            }

            for ai_key, db_key in field_mapping.items():
                if ai_key in percent_data and percent_data[ai_key] is not None:
                    catfood_update_data[db_key] = percent_data[ai_key]

        # 更新 catfoods 表
        supabase_admin.table("catfoods").update(catfood_update_data).eq(
            "id", catfood_id
        ).execute()

        return JsonResponse(
            {
                "message": message,
                "report": result.data[0] if result.data else None,
            },
            status=201,
        )

    except Exception as e:
        print(f"❌ [save_report] Error: {str(e)}")
        import traceback

        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@require_auth
def get_report(request, catfood_id):
    """
    获取猫粮的 AI 分析报告

    GET /api/ai/<catfood_id>/
    """
    try:
        user = get_current_user(request)

        # 查询报告（报告是公共的，不需要检查 user_id）
        report_result = (
            supabase_admin.table("ai_analysis_reports")
            .select("*, catfood:catfoods(*)")
            .eq("catfood_id", catfood_id)
            .execute()
        )
        report_data, error = safe_single(report_result, "Report not found")
        if error:
            return JsonResponse({"error": error}, status=404)

        return JsonResponse({"report": report_data})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@require_auth
def check_report_exists(request, catfood_id):
    """
    检查报告是否存在

    GET /api/ai/<catfood_id>/exists/
    """
    try:
        user = get_current_user(request)

        # 检查是否存在（报告是公共的）
        report = (
            supabase_admin.table("ai_analysis_reports")
            .select("id")
            .eq("catfood_id", catfood_id)
            .execute()
        )

        exists = len(report.data) > 0

        return JsonResponse({"exists": exists})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
@require_auth
def delete_report(request, catfood_id):
    """
    删除报告（用于重新生成）

    DELETE /api/ai/<catfood_id>/delete/
    """
    try:
        user = get_current_user(request)

        # 查找报告（报告是公共的）
        report_result = (
            supabase_admin.table("ai_analysis_reports")
            .select("id")
            .eq("catfood_id", catfood_id)
            .execute()
        )
        report_data, error = safe_single(report_result, "Report not found")
        if error:
            return JsonResponse({"error": error}, status=404)

        # 删除报告
        supabase_admin.table("ai_analysis_reports").delete().eq(
            "id", report_data["id"]
        ).execute()

        return JsonResponse({"message": "Report deleted successfully"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@require_auth
def get_favorite_reports(request):
    """
    获取收藏的报告列表

    GET /api/ai/favorites/
    """
    try:
        user = get_current_user(request)

        # 查询收藏，并关联报告和猫粮信息
        result = (
            supabase_admin.table("favorite_reports")
            .select("*, report:ai_analysis_reports(*, catfood:catfoods(*))")
            .eq("user_id", user.id)
            .order("created_at", desc=True)
            .execute()
        )

        return JsonResponse({"favorites": result.data})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@require_auth
def toggle_favorite_report(request):
    """
    切换报告收藏状态

    POST /api/ai/favorites/toggle/
    Body: {
        "report_id": 123
    }
    """
    try:
        user = get_current_user(request)
        try:
            data = parse_json_body(request)
        except ValueError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        report_id = data.get("report_id")
        if not report_id:
            return JsonResponse({"error": "report_id is required"}, status=400)

        # 检查是否已收藏
        existing = (
            supabase_admin.table("favorite_reports")
            .select("id")
            .eq("report_id", report_id)
            .eq("user_id", user.id)
            .execute()
        )

        if existing.data:
            # 取消收藏
            supabase_admin.table("favorite_reports").delete().eq(
                "id", existing.data[0]["id"]
            ).execute()
            return JsonResponse(
                {"message": "Unfavorited successfully", "favorited": False}
            )
        else:
            # 添加收藏
            favorite_data = {
                "report_id": report_id,
                "user_id": user.id,
            }
            supabase_admin.table("favorite_reports").insert(favorite_data).execute()
            return JsonResponse(
                {"message": "Favorited successfully", "favorited": True}
            )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
@require_auth
def delete_favorite_report(request, favorite_id):
    """
    删除收藏

    DELETE /api/ai/favorites/<favorite_id>/
    """
    try:
        user = get_current_user(request)

        # 验证收藏所有权
        favorite_result = (
            supabase_admin.table("favorite_reports")
            .select("*")
            .eq("id", favorite_id)
            .eq("user_id", user.id)
            .execute()
        )
        favorite_data, error = safe_single(favorite_result, "Favorite not found")
        if error:
            return JsonResponse({"error": error}, status=404)

        # 删除收藏
        supabase_admin.table("favorite_reports").delete().eq(
            "id", favorite_data["id"]
        ).execute()

        return JsonResponse({"message": "Favorite deleted successfully"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@require_auth
def check_favorite_report(request, report_id):
    """
    检查是否已收藏

    GET /api/ai/favorites/check/<report_id>/
    """
    try:
        user = get_current_user(request)

        # 检查是否已收藏
        favorite = (
            supabase_admin.table("favorite_reports")
            .select("id")
            .eq("report_id", report_id)
            .eq("user_id", user.id)
            .execute()
        )

        favorited = len(favorite.data) > 0

        return JsonResponse({"favorited": favorited})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
