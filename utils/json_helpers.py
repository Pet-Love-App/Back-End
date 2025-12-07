import json


def snake_to_camel(snake_str):
    """
    将 snake_case 字符串转换为 camelCase

    Args:
        snake_str: snake_case 格式的字符串

    Returns:
        camelCase 格式的字符串

    Example:
        >>> snake_to_camel("user_name")
        "userName"
        >>> snake_to_camel("created_at")
        "createdAt"
    """
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def convert_keys_to_camel(data):
    """
    递归地将字典或列表中的所有 snake_case 键转换为 camelCase

    Args:
        data: 字典、列表或其他数据类型

    Returns:
        转换后的数据（保持原始数据结构）

    Example:
        >>> convert_keys_to_camel({"user_name": "John", "created_at": "2024-01-01"})
        {"userName": "John", "createdAt": "2024-01-01"}
        >>> convert_keys_to_camel([{"user_id": 1}, {"user_id": 2}])
        [{"userId": 1}, {"userId": 2}]
    """
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            # 转换键名
            new_key = snake_to_camel(key) if "_" in key else key
            # 递归处理值
            new_dict[new_key] = convert_keys_to_camel(value)
        return new_dict
    elif isinstance(data, list):
        return [convert_keys_to_camel(item) for item in data]
    else:
        return data


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
