from paddleocr import PaddleOCR
import os
import cv2
import argparse  # 新增：支持命令行传参，不用硬改图片路径

# def preprocess_image(local_path):
#     """
#     预处理逻辑：压缩尺寸→去噪声→灰度化→增强对比度
#     输入：图片本地路径，输出：适配OCR的numpy.ndarray（BGR格式）
#     """
#     # 1. 读取本地图片（OpenCV默认BGR格式）
#     img = cv2.imread(local_path)
#     if img is None:
#         raise Exception(f"图片读取失败！请检查：1. 文件路径是否正确 2. 文件是否为有效图片格式（jpg/png等），当前路径：{local_path}")
    
#     # 2. 按比例压缩（最长边不超过1000px，减少计算量）
#     max_size = 1000
#     height, width = img.shape[:2]
#     if max(height, width) > max_size:
#         scale = max_size / max(height, width)
#         img = cv2.resize(
#             img,
#             (int(width * scale), int(height * scale)),
#             interpolation=cv2.INTER_AREA  # 压缩优先保留细节
#         )
    
#     # 3. 高斯去噪（去除杂点，避免干扰识别）
#     img = cv2.GaussianBlur(img, (3, 3), 0)
    
#     # 4. 转为灰度图（减少通道数，提速）
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
#     # 5. 自适应阈值增强（突出文本，适配光照不均场景）
#     processed_img = cv2.adaptiveThreshold(
#         gray,
#         255,
#         cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#         cv2.THRESH_BINARY_INV,
#         11,  # 块大小（奇数）
#         2    # 调整对比度的常数
#     )
    
#     # 转回BGR格式（匹配PaddleOCR输入要求）
#     return cv2.cvtColor(processed_img, cv2.COLOR_GRAY2BGR)

import cv2
import os

def preprocess_image(local_path, save_steps=True):
    """
    预处理逻辑：压缩尺寸→去噪声→灰度化→增强对比度
    输入：图片本地路径，输出：适配OCR的numpy.ndarray（BGR格式）
    save_steps: 是否保存每一步的中间结果（默认True）
    """
    # 创建保存中间结果的目录
    if save_steps:
        os.makedirs("preprocess_steps", exist_ok=True)
    
    # 1. 读取本地图片（原始图）
    img = cv2.imread(local_path)
    if img is None:
        raise Exception(f"图片读取失败！路径：{local_path}")
    # 保存原始图
    if save_steps:
        cv2.imwrite("preprocess_steps/1_original.jpg", img)
        print("已保存：1_original.jpg（原始图片）")
    

    # 4. 转为灰度图
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 保存灰度图
    if save_steps:
        cv2.imwrite("preprocess_steps/4_gray.jpg", img_gray)
        print("已保存：4_gray.jpg（转为灰度图后）")

    # 2. 按比例压缩尺寸
    max_size = 1000
    height, width = img.shape[:2]
    if max(height, width) > max_size:
        scale = max_size / max(height, width)
        img_resized = cv2.resize(
            img_gray,
            (int(width * scale), int(height * scale)),
            interpolation=cv2.INTER_AREA
        )
    else:
        img_resized = img_gray  # 无需压缩
    # 保存压缩后的图
    if save_steps:
        cv2.imwrite("preprocess_steps/2_resized.jpg", img_resized)
        print("已保存：2_resized.jpg（压缩尺寸后）")
    
    # # 3. 高斯去噪
    # img_denoised = cv2.GaussianBlur(img_resized, (3, 3), 0)
    # 保存去噪后的图
    # if save_steps:
    #     cv2.imwrite("preprocess_steps/3_denoised.jpg", img_denoised)
    #     print("已保存：3_denoised.jpg（去噪声后）")
    
    
    # 5. 自适应阈值增强
    img_threshold = cv2.adaptiveThreshold(
        img_resized,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        11,
        2
    )
    # 保存阈值增强后的图
    if save_steps:
        cv2.imwrite("preprocess_steps/5_threshold.jpg", img_threshold)
        print("已保存：5_threshold.jpg（增强对比度后）")
    
    # 6. 转回BGR格式（最终结果）
    final_img = cv2.cvtColor(img_threshold, cv2.COLOR_GRAY2BGR)
    # 保存最终预处理结果
    if save_steps:
        cv2.imwrite("preprocess_steps/6_final.jpg", final_img)
        print("已保存：6_final.jpg（最终预处理结果）")
    
    return final_img

# 测试代码（单独运行时使用）
if __name__ == "__main__":
    # 替换为你的图片路径
    image_path = "image3.png"
    try:
        preprocess_image(image_path)
        print("\n所有预处理步骤已完成，中间结果保存在 preprocess_steps 目录下")
    except Exception as e:
        print(f"处理失败：{e}")
# def test_ocr(image_path, output_dir="ocr_result"):
#     """
#     封装OCR测试逻辑：初始化→预处理→识别→结果输出
#     :param image_path: 输入图片路径（相对/绝对路径）
#     :param output_dir: 结果保存目录（默认ocr_result）
#     """
#     # 1. 初始化OCR（添加cls=False提速，关闭方向分类）
#     print("初始化PaddleOCR...")
#     ocr = PaddleOCR(
#         lang="ch",
        
#     )
    
#     # 2. 校验图片路径是否存在
#     if not os.path.exists(image_path):
#         raise FileNotFoundError(f"图片文件不存在！路径：{image_path}")
    
#     # 3. 图片预处理
#     print(f"正在预处理图片：{image_path}")
#     processed_img = preprocess_image(image_path)
    
#     # 4. 执行OCR识别
#     print("开始OCR识别...")
#     result = ocr.ocr(processed_img)  # 传入预处理后的ndarray
    
#     # 5. 处理识别结果（适配3.3.1版本格式，避免循环报错）
#     if not result or not isinstance(result[0], dict):
#         print("未识别到任何文本！")
#         return
    
#     # 提取核心结果并打印（结构化输出，更易读）
#     ocr_dict = result[0]
#     recognized_texts = ocr_dict.get("rec_texts", [])
#     confidences = ocr_dict.get("rec_scores", [])
    
#     print("\n=== 识别结果 ===")
#     for idx, (text, conf) in enumerate(zip(recognized_texts, confidences), 1):
#         print(f"{idx}. 文本：{text} | 置信度：{conf:.4f}")
    
#     # 6. 保存识别结果（图片+文本文件）
#     os.makedirs(output_dir, exist_ok=True)  # 确保目录存在
#     # 保存带标注的图片
#     ocr_dict.save_to_img(os.path.join(output_dir, "annotated_image.jpg"))
#     # 保存文本结果到txt文件
#     with open(os.path.join(output_dir, "recognized_text.txt"), "w", encoding="utf-8") as f:
#         f.write("OCR识别结果（文本+置信度）\n")
#         f.write("-" * 50 + "\n")
#         for text, conf in zip(recognized_texts, confidences):
#             f.write(f"文本：{text} | 置信度：{conf:.4f}\n")
#     print(f"\n结果已保存到：{os.path.abspath(output_dir)}")

# if __name__ == "__main__":
#     # 新增：命令行参数解析，灵活指定输入图片
#     parser = argparse.ArgumentParser(description="PaddleOCR测试脚本（带图片预处理）")
#     parser.add_argument(
#         "--image",
#         type=str,
#         required=True,
#         help="输入图片路径（例：--image ./test.png 或 --image C:/img.jpg）"
#     )
#     parser.add_argument(
#         "--output",
#         type=str,
#         default="ocr_result",
#         help="结果保存目录（默认：ocr_result）"
#     )
#     args = parser.parse_args()
    
#     try:
#         test_ocr(args.image, args.output)
#     except Exception as e:
#         print(f"\n测试失败：{str(e)}")