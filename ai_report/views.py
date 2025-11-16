import json
import os
import re
import urllib.error
import urllib.request
import urllib.parse

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from bs4 import BeautifulSoup

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

def extract_summary(html_text: str) -> str:
    soup = BeautifulSoup(html_text, "html.parser")
    node = soup.select_one("#J-lemma-main-wrapper > div.contentWrapper_IZKqz > div > div.mainContent_V_Z7A > div > div.lemmaSummary_LOb9D.J-summary")
    if not node:
        return "未找到简介"

    text = node.get_text(separator="", strip=True)
    import re
    text = re.sub(r"\[\d+\]", "", text)
    return text

def _fetch_text(title: str, timeout: int = 10) -> tuple[int, object]:
    """Fetch a concise page summary from Baidu Baike.

    Returns (status_code, data) where data is a dict parsed from JSON on success,
    or a string error message on network failure.
    """
    safe_title = urllib.parse.quote(title.strip())
    url = f"https://baike.baidu.com/item/{safe_title}"
    headers = {
        "User-Agent": "pet_love/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive"
    }
    # headers = {"Accept": "application/json", "User-Agent": "pet_love/1.0"}
    if requests is not None:
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            try:
                return resp.status_code, resp.json()
            except Exception:
                return resp.status_code, resp.text
        except Exception as e:  # pragma: no cover
            return 0, str(e)

    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec B310
            status = resp.status
            text = resp.read().decode("utf-8", errors="replace")
            try:
                return status, json.loads(text)
            except Exception:
                return status, text
    except urllib.error.HTTPError as e:  # pragma: no cover
        return e.code, e.read().decode("utf-8", errors="replace")
    except Exception as e:  # pragma: no cover
        return 0, str(e)


def _to_simplified(text: str) -> str:
    """Convert Chinese text to Simplified Chinese if a converter is available.

    Tries the following libraries in order: opencc, zhconv, hanziconv. If none are
    available the original text is returned unchanged. This keeps the change
    optional and avoids adding a hard dependency.
    """
    if not text:
        return text
    # opencc (fast, reliable) - pip package name: opencc
    try:
        from opencc import OpenCC

        cc = OpenCC("t2s")
        return cc.convert(text)
    except Exception:
        pass

    # zhconv - pip package name: zhconv
    try:
        import zhconv

        return zhconv.convert(text, "zh-cn")
    except Exception:
        pass

    # hanziconv - pip package name: hanziconv
    try:
        from hanziconv import HanziConv

        return HanziConv.toSimplified(text)
    except Exception:
        pass

    return text


@csrf_exempt
@require_http_methods(["GET", "POST"])
def ingredient_info(request: HttpRequest) -> JsonResponse:
    """Return a short summary for a given ingredient name.

    GET params: q (ingredient name)
    POST JSON: {"ingredient": "维生素D"}

    Response JSON: { ok: bool, title, extract, url}
    """
    if request.method == "GET":
        q = (request.GET.get("q") or "").strip()
    else:
        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return JsonResponse({"ok": False, "error": {"code": "bad_json", "message": "Invalid JSON"}}, status=400, json_dumps_params={"ensure_ascii": False})
        q = (payload.get("ingredient") or payload.get("q") or "").strip()

    if not q:
        return JsonResponse({"ok": False, "error": {"code": "missing_ingredient", "message": "Provide 'q' or 'ingredient'"}}, status=400, json_dumps_params={"ensure_ascii": False})

    status, data = _fetch_text(q)
    data=extract_summary(data)
    if status == 0:
        return JsonResponse({"ok": False, "error": {"code": "network", "message": "request failed", "detail": data}}, status=502, json_dumps_params={"ensure_ascii": False})

    if isinstance(data, dict):
        title = data.get("title") or q
        extract = data.get("extract") or data.get("description") or ""
        # Prefer returning Simplified Chinese when possible
        try:
            title = _to_simplified(title)
        except Exception:
            pass
        try:
            extract = _to_simplified(extract)
        except Exception:
            pass
        page_url = None
        cu = data.get("content_urls") or {}
        if isinstance(cu, dict):
            desktop = cu.get("desktop") or {}
            if isinstance(desktop, dict):
                page_url = desktop.get("page")
        if not page_url:
            page_url = f"https://baike.baidu.com/item/{urllib.parse.quote(title)}"

        return JsonResponse({"ok": True, "title": title, "extract": extract, "url": page_url}, status=200, json_dumps_params={"ensure_ascii": False})

    return JsonResponse({"ok": False, "error": {"code": "invalid_response", "detail": str(data)}}, status=502, json_dumps_params={"ensure_ascii": False})

from typing import Optional, List


class PercentData:
    """百分比数据"""
    carbohydrates: Optional[float]
    crude_ash: Optional[float]
    crude_fat: Optional[float]
    crude_fiber: Optional[float]
    crude_protein: Optional[float]
    others: Optional[float]

    def __init__(self, carbohydrates: Optional[float], crude_ash: Optional[float], crude_fat: Optional[float], crude_fiber: Optional[float], crude_protein: Optional[float], others: Optional[float]) -> None:
        self.carbohydrates = carbohydrates
        self.crude_ash = crude_ash
        self.crude_fat = crude_fat
        self.crude_fiber = crude_fiber
        self.crude_protein = crude_protein
        self.others = others


class Request:
    """Request"""
    additive: List[str]
    ingredient: List[str]
    """营养分析"""
    nutrient: str
    """百分比数据"""
    percent_data: PercentData
    """是否支持百分比分析"""
    percentage: bool
    """安全性分析"""
    safety: str
    """标签"""
    tags: List[str]

    def __init__(self, additive: List[str], ingredient: List[str], nutrient: str, percent_data: PercentData, percentage: bool, safety: str, tags: List[str]) -> None:
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
        resp={
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
        raw_tags = (
            parsed.get("tags")
            or parsed.get("product_tags")
        )
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

        schema.percent_data.crude_protein = _to_number(parsed.get("crude_protein") or parsed.get("protein"))
        schema.percent_data.crude_fat = _to_number(parsed.get("crude_fat") or parsed.get("fat"))
        schema.percent_data.carbohydrates = _to_number(parsed.get("carbohydrates") or parsed.get("carb"))
        schema.percent_data.crude_fiber = _to_number(parsed.get("crude_fiber") or parsed.get("fiber"))
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

    resp={
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