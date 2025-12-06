"""
API 测试包

精简后的测试模块（只测试保留在后端的服务）：

活跃测试：
- test_ai_report.py: AI 报告生成测试（LLM API 调用）
- test_ocr.py: OCR 识别测试（阿里云 OCR）
- test_search.py: 搜索服务测试（百度百科 API）
- helpers.py: 测试辅助工具

已归档测试（功能已迁移到 Supabase）：
- archived/test_auth.py: 认证相关测试 → Supabase Auth
- archived/test_catfood.py: 猫粮 CRUD 测试 → Supabase Tables
- archived/test_additive.py: 添加剂搜索测试 → Supabase Tables
- archived/test_comment.py: 评论功能测试 → Supabase Tables
- archived/test_pet.py: 宠物管理测试 → Supabase Tables
- archived/test_forum.py: 论坛功能测试 → Supabase Tables
- archived/test_notification.py: 通知系统测试 → Supabase Tables
- archived/test_reputation.py: 声望系统测试 → Supabase Functions

运行所有测试：
    python manage.py test api.tests

运行特定模块测试：
    python manage.py test api.tests.test_ai_report
    python manage.py test api.tests.test_ocr
    python manage.py test api.tests.test_search

运行特定测试类：
    python manage.py test api.tests.test_ai_report.AIReportAPITests

运行特定测试方法：
    python manage.py test api.tests.test_ai_report.AIReportAPITests.test_llm_chat_success

架构说明：
- 核心数据操作已迁移到 Supabase（前端直接调用）
- 后端只保留需要保护 API 密钥的服务（AI、OCR、搜索）
- 这些服务作为代理层，前端通过后端调用第三方 API
"""
