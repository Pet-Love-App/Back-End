"""
测试辅助工具

提供测试中常用的 Mock 对象和辅助函数。
"""

from unittest.mock import Mock


class FakeSupabaseResponse:
    """
    模拟 Supabase 查询响应。

    用于 mock Supabase 的 execute() 方法返回值。

    Args:
        data: 查询返回的数据列表
        count: 查询结果总数
        error: 错误信息（如有）

    Example:
        >>> response = FakeSupabaseResponse(data=[{"id": 1, "name": "Test"}])
        >>> response.data
        [{"id": 1, "name": "Test"}]
        >>> response.count
        1
    """

    def __init__(self, data=None, count=None, error=None):
        self.data = data if data is not None else []
        self.count = (
            count if count is not None else (len(self.data) if self.data else 0)
        )
        self.error = error


class FakeUser:
    """
    模拟 Supabase 认证用户。

    用于 mock get_current_user() 返回值。

    Args:
        user_id: 用户 UUID
        email: 用户邮箱

    Example:
        >>> user = FakeUser()
        >>> user.id
        'test-uuid'
    """

    def __init__(self, user_id="test-uuid", email="test@example.com"):
        self.id = user_id
        self.email = email


def create_mock_session(
    access_token="test-access-token", refresh_token="test-refresh-token"
):
    """
    创建模拟的 Supabase Session。

    Args:
        access_token: 访问令牌
        refresh_token: 刷新令牌

    Returns:
        Mock: 模拟的 Session 对象

    Example:
        >>> session = create_mock_session()
        >>> session.access_token
        'test-access-token'
    """
    mock_session = Mock()
    mock_session.access_token = access_token
    mock_session.refresh_token = refresh_token
    return mock_session


def create_mock_auth_response(user=None, session=None):
    """
    创建模拟的 Supabase 认证响应。

    Args:
        user: 用户对象（默认创建 FakeUser）
        session: Session 对象（默认创建 mock session）

    Returns:
        Mock: 模拟的认证响应对象

    Example:
        >>> response = create_mock_auth_response()
        >>> response.user.id
        'test-uuid'
    """
    mock_response = Mock()
    mock_response.user = user if user is not None else FakeUser()
    mock_response.session = session if session is not None else create_mock_session()
    return mock_response
