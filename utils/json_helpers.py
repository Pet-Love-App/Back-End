import json


def parse_json_body(request, default=None):
    """
    安全地解析请求体中的 JSON 数据

    Args:
        request: Django 请求对象
        default: 解析失败时的默认值。如果为 None 且解析失败，抛出 ValueError

    Returns:
        解析后的字典或列表

    Raises:
        ValueError: 当 JSON 格式错误且没有提供默认值时
    """
    try:
        body = request.body.decode("utf-8")
        if not body:
            return default if default is not None else {}
        return json.loads(body)
    except json.JSONDecodeError:
        if default is not None:
            return default
        raise ValueError("Invalid JSON format")


def parse_json_field(json_str, default=None):
    """
    安全地解析 JSON 字符串字段
    """
    try:
        if not json_str:
            return default if default is not None else []
        return json.loads(json_str)
    except (TypeError, json.JSONDecodeError):
        return default if default is not None else []
