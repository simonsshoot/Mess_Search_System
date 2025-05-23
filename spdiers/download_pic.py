import jsonlines
import requests
import os
from urllib.parse import unquote

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

def process_jsonl(input_file, output_dir="images"):
    os.makedirs(output_dir, exist_ok=True)
    
    with jsonlines.open(input_file) as reader:
        for idx, item in enumerate(reader):
            if 'url' not in item:
                continue
            
            # 生成安全文件名
            title = unquote(item.get('title', f'image_{idx}'))[:100]  # 限制文件名长度
            title = "".join([c if c.isalnum() else "_" for c in title])  # 去除特殊字符
            ext = item['url'].split('.')[-1].split('?')[0][:4]  # 提取扩展名
            filename = f"{title}_{idx}.{ext}"
            
            save_path = os.path.join(output_dir, filename)
            
            # 跳过已存在的文件
            if os.path.exists(save_path):
                print(f"跳过已存在: {filename}")
                continue
            
            # 执行下载
            print(f"正在下载: {item['url']}")
            success = download_image(item['url'], save_path)
            
            if success:
                print(f"保存成功: {filename} ({os.path.getsize(save_path)/1024:.1f}KB)")
            else:
                print(f"保存失败: {filename}")

if __name__ == "__main__":
    process_jsonl("urls-1.jsonl", output_dir="images")