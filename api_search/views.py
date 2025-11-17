import json
import os
import re
import urllib.error
import urllib.request
import urllib.parse

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

try:
    # Prefer requests if available for simplicity
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # fall back to urllib at runtime


#baidu baike api_key
key="bce-v3/ALTAK-6xqmhDYUBdfEIXPQNrvVb/b87bd21e8dc6b6081288c489b369845a3a31ef37"

def _fetch_summary(title: str, timeout: int = 20) -> tuple[int, object]:
    """Fetch a concise page summary from Wikipedia REST API.

    Returns (status_code, data) where data is a dict parsed from JSON on success,
    or a string error message on network failure.
    """
    safe_title = urllib.parse.quote(title.strip())
    url = f"https://appbuilder.baidu.com/v2/baike/lemma/get_content?search_type=lemmaTitle&search_key={safe_title}"
    print("Fetching URL:", url)
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

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

@csrf_exempt
@require_http_methods(["POST"])
def ingredient_info(request: HttpRequest) -> JsonResponse:
    """Return a short summary for a given ingredient name.

    GET params: q (ingredient name)
    POST JSON: {"ingredient": "维生素D"}

    Response JSON: { ok: bool, title, extract}
    """
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": {"code": "bad_json", "message": "Invalid JSON"}}, status=400, json_dumps_params={"ensure_ascii": False})

    q = (payload.get("ingredient") or payload.get("q") or "").strip()
    if not q:
        return JsonResponse({"ok": False, "error": {"code": "missing_ingredient", "message": "Provide 'q' or 'ingredient'"}}, status=400, json_dumps_params={"ensure_ascii": False})

    status, data = _fetch_summary(q)
    if status == 0:
        return JsonResponse({"ok": False, "error": {"code": "network", "message": "request failed", "detail": data}}, status=502, json_dumps_params={"ensure_ascii": False})

    if isinstance(data, dict):
        title = data.get("title") or q
        result = data.get("result")
        extract = result.get("summary")

        return JsonResponse({"ok": True, "title": title, "extract": extract}, status=200, json_dumps_params={"ensure_ascii": False})

    return JsonResponse({"ok": False, "error": {"code": "invalid_response", "detail": str(data)}}, status=502, json_dumps_params={"ensure_ascii": False})
