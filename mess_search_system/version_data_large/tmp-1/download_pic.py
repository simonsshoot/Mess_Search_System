#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import jsonlines
import requests
import os
import json
from urllib.parse import unquote
import time
import shutil

def download_image(url, save_path, timeout=5):
    """下载单张图片"""
    try:
        response = requests.get(url, stream=True, timeout=timeout)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return True
        return False
    except Exception as e:
        print(f"下载失败: {url} - {str(e)}")
        return False

def process_jsonl(input_file, output_dir="images", record_file="image_record.jsonl", output_jsonl="merged_urls.jsonl"):
    """
    处理JSONL文件，下载图片，对图片编号并重命名，生成记录文件
    
    参数:
    - input_file: 输入的JSONL文件路径
    - output_dir: 图片保存目录
    - record_file: 图片编号记录文件路径
    - output_jsonl: 输出的合并JSONL文件路径
    """
    # 创建保存目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 临时目录，用于存储下载的图片（使用原始文件名）
    temp_dir = "temp_images"
    os.makedirs(temp_dir, exist_ok=True)
    
    # 读取输入JSONL并准备处理
    all_items = []
    image_mapping = []  # 存储图片名称和编号的映射
    
    with jsonlines.open(input_file) as reader:
        all_items = list(reader)
    
    # 第一步：下载所有图片到临时目录
    successful_downloads = []
    for idx, item in enumerate(all_items):
        if 'url' not in item:
            continue
        
        # 生成安全文件名
        title = unquote(item.get('title', f'image_{idx}'))[:100]  # 限制文件名长度
        title = "".join([c if c.isalnum() else "_" for c in title])  # 去除特殊字符
        ext = item['url'].split('.')[-1].split('?')[0][:4].lower()  # 提取扩展名
        
        # 确保扩展名是图片格式
        if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp']:
            ext = 'jpg'  # 默认扩展名
        
        # 生成文件名和保存路径
        filename = f"{title}_{idx}.{ext}"
        save_path = os.path.join(temp_dir, filename)
        
        # 跳过已存在的文件
        if os.path.exists(save_path):
            print(f"跳过已存在: {filename}")
            successful_downloads.append((item, filename, ext))
            continue
        
        # 执行下载
        print(f"正在下载: {item['url']}")
        success = download_image(item['url'], save_path)
        
        if success:
            file_size = os.path.getsize(save_path)
            print(f"保存成功: {filename} ({file_size/1024:.1f}KB)")
            successful_downloads.append((item, filename, ext))
        else:
            print(f"保存失败: {filename}")
    
    # 第二步：对成功下载的图片进行编号和重命名
    for number, (item, filename, ext) in enumerate(successful_downloads, 1):
        # 源文件路径和目标文件路径
        src_path = os.path.join(temp_dir, filename)
        dst_path = os.path.join(output_dir, f"{number}.{ext}")
        
        # 复制文件并重命名
        try:
            shutil.copy2(src_path, dst_path)
            print(f"重命名: {filename} -> {number}.{ext}")
            
            # 记录映射关系
            image_mapping.append({
                "image_name": filename,
                "number": number
            })
            
            # 更新原始记录中的信息
            item["image_name"] = filename
            item["number"] = number
            item["relative_path"] = f"{output_dir}/{number}.{ext}"
            
        except Exception as e:
            print(f"重命名失败: {filename} - {str(e)}")
    
    # 第三步：保存图片编号记录
    with open(record_file, 'w', encoding='utf-8') as f:
        for mapping in image_mapping:
            f.write(json.dumps(mapping, ensure_ascii=False) + '\n')
    
    # 第四步：输出合并后的JSONL文件
    with jsonlines.open(output_jsonl, 'w') as writer:
        for item in all_items:
            writer.write(item)
    
    print(f"\n处理完成:")
    print(f"- 总共处理 URL: {len(all_items)} 条")
    print(f"- 成功下载图片: {len(successful_downloads)} 张")
    print(f"- 图片编号记录已保存至: {record_file}")
    print(f"- 合并 JSONL 已保存至: {output_jsonl}")
    
    # 清理临时目录
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        print(f"- 已清理临时目录: {temp_dir}")

if __name__ == "__main__":
    process_jsonl("urls-1.jsonl", output_dir="images", record_file="image_record.jsonl", output_jsonl="merged_urls.jsonl")