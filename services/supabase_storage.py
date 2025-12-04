"""
Supabase Storage 服务
处理文件上传、删除等操作
"""

import mimetypes
import os
from typing import Optional

from config.supabase_client import supabase_admin


class SupabaseStorageService:
    """Supabase Storage 服务类"""

    # 存储桶配置
    BUCKETS = {
        "avatars": "avatars",  # 用户头像
        "pets": "pets",  # 宠物照片
        "posts": "posts",  # 帖子图片/视频
        "catfoods": "catfoods",  # 猫粮图片
    }

    @classmethod
    def upload_file(
        cls,
        bucket: str,
        file_path: str,
        file_data: bytes,
        content_type: str | None = None,
    ) -> str:
        """
        上传文件到 Supabase Storage

        Args:
            bucket: 存储桶名称
            file_path: 文件路径 (如: user_123/avatar.jpg)
            file_data: 文件二进制数据
            content_type: 文件 MIME 类型

        Returns:
            文件的公开 URL
        """
        # 自动检测 content_type
        if not content_type:
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                content_type = "application/octet-stream"

        try:
            # 上传文件
            result = supabase_admin.storage.from_(bucket).upload(
                file_path, file_data, {"content-type": content_type}
            )

            # 获取公开 URL
            public_url = supabase_admin.storage.from_(bucket).get_public_url(file_path)

            return public_url

        except Exception as e:
            raise Exception(f"Failed to upload file: {str(e)}")

    @classmethod
    def delete_file(cls, bucket: str, file_path: str) -> bool:
        """
        删除文件

        Args:
            bucket: 存储桶名称
            file_path: 文件路径

        Returns:
            是否删除成功
        """
        try:
            supabase_admin.storage.from_(bucket).remove([file_path])
            return True
        except Exception as e:
            print(f"Failed to delete file: {str(e)}")
            return False

    @classmethod
    def delete_file_from_url(cls, file_url: str) -> bool:
        """
        从完整 URL 中提取路径并删除文件

        Args:
            file_url: 完整的文件 URL

        Returns:
            是否删除成功
        """
        if not file_url:
            return False

        try:
            # 从 URL 中提取 bucket 和 file_path
            # URL 格式: https://xxx.supabase.co/storage/v1/object/public/{bucket}/{file_path}
            parts = file_url.split("/storage/v1/object/public/")
            if len(parts) != 2:
                print(f"Invalid URL format: {file_url}")
                return False

            path_parts = parts[1].split("/", 1)
            if len(path_parts) != 2:
                print(f"Invalid path format: {parts[1]}")
                return False

            bucket = path_parts[0]
            file_path = path_parts[1]

            return cls.delete_file(bucket, file_path)

        except Exception as e:
            print(f"Failed to parse and delete file from URL: {str(e)}")
            return False

    @classmethod
    def get_public_url(cls, bucket: str, file_path: str) -> str:
        """
        获取文件的公开 URL

        Args:
            bucket: 存储桶名称
            file_path: 文件路径

        Returns:
            公开 URL
        """
        return supabase_admin.storage.from_(bucket).get_public_url(file_path)

    @classmethod
    def upload_avatar(cls, user_id: str, file_data: bytes, file_extension: str) -> str:
        """
        上传用户头像

        Args:
            user_id: 用户 ID
            file_data: 文件数据
            file_extension: 文件扩展名 (如: jpg, png)

        Returns:
            头像 URL
        """
        file_path = f"{user_id}/avatar.{file_extension}"
        return cls.upload_file(cls.BUCKETS["avatars"], file_path, file_data)

    @classmethod
    def upload_pet_photo(
        cls, user_id: str, pet_id: int, file_data: bytes, file_extension: str
    ) -> str:
        """
        上传宠物照片

        Args:
            user_id: 用户 ID
            pet_id: 宠物 ID
            file_data: 文件数据
            file_extension: 文件扩展名

        Returns:
            照片 URL
        """
        file_path = f"{user_id}/pet_{pet_id}.{file_extension}"
        return cls.upload_file(cls.BUCKETS["pets"], file_path, file_data)

    @classmethod
    def upload_post_media(
        cls, user_id: str, post_id: int, media_index: int, file_data: bytes, file_extension: str
    ) -> str:
        """
        上传帖子媒体文件

        Args:
            user_id: 用户 ID
            post_id: 帖子 ID
            media_index: 媒体索引
            file_data: 文件数据
            file_extension: 文件扩展名

        Returns:
            媒体 URL
        """
        file_path = f"{user_id}/post_{post_id}_{media_index}.{file_extension}"
        return cls.upload_file(cls.BUCKETS["posts"], file_path, file_data)

    @classmethod
    def upload_catfood_image(cls, catfood_id: int, file_data: bytes, file_extension: str) -> str:
        """
        上传猫粮图片

        Args:
            catfood_id: 猫粮 ID
            file_data: 文件数据
            file_extension: 文件扩展名

        Returns:
            图片 URL
        """
        file_path = f"catfood_{catfood_id}.{file_extension}"
        return cls.upload_file(cls.BUCKETS["catfoods"], file_path, file_data)


# 便捷实例
storage_service = SupabaseStorageService()
