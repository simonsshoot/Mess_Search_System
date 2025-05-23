#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime

def process_merged_urls():
    """
    处理merged_urls.jsonl文件，过滤损坏记录，生成新的changed_urls.jsonl文件
    """
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 输入和输出文件路径
    input_file = os.path.join(script_dir, 'merged_urls.jsonl')
    output_file = os.path.join(script_dir, 'changed_urls.jsonl')
    
    # 确保输入文件存在
    if not os.path.exists(input_file):
        print(f"错误：输入文件 {input_file} 不存在！")
        return False
    
    # 统计数据
    total_records = 0
    valid_records = 0
    damaged_records = 0
    
    valid_data = []
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                total_records += 1
                
                try:
                    record = json.loads(line.strip())
                except json.JSONDecodeError:
                    print(f"JSON解析错误，跳过第 {total_records} 行")
                    damaged_records += 1
                    continue
                
                # 检查必需的字段是否存在
                required_fields = ['title', 'url', 'post_time', 'relative_path']
                missing_fields = [field for field in required_fields if field not in record or not record[field]]
                
                if missing_fields:
                    print(f"记录 {total_records} 缺少字段: {missing_fields}")
                    damaged_records += 1
                    continue
                
                # 检查relative_path指向的文件是否存在
                relative_path = record['relative_path']
                full_path = os.path.join(script_dir, relative_path)
                
                if not os.path.exists(full_path):
                    print(f"记录 {total_records} 的图片文件不存在: {relative_path}")
                    damaged_records += 1
                    continue
                
                # 解析post_time并提取日期部分
                try:
                    post_time = record['post_time']
                    # 解析时间字符串 "2018-12-25 23:48:18 UTC"
                    if ' UTC' in post_time:
                        time_part = post_time.replace(' UTC', '')
                    else:
                        time_part = post_time
                    
                    # 提取日期部分 (YYYY-MM-DD)
                    if ' ' in time_part:
                        date_part = time_part.split(' ')[0]
                    else:
                        date_part = time_part[:10]  # 取前10个字符作为日期
                    
                    # 验证日期格式
                    datetime.strptime(date_part, '%Y-%m-%d')
                    
                except (ValueError, IndexError) as e:
                    print(f"记录 {total_records} 时间格式错误: {post_time} - {e}")
                    damaged_records += 1
                    continue
                
                # 创建新的记录格式
                new_record = {
                    "id": valid_records,
                    "title": record['title'],
                    "url": record['url'],
                    "time": date_part,
                    "relative_path": record['relative_path']
                }
                
                valid_data.append(new_record)
                valid_records += 1
        
        # 写入输出文件
        with open(output_file, 'w', encoding='utf-8') as f:
            for record in valid_data:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        print(f"\n处理完成:")
        print(f"- 总记录数: {total_records}")
        print(f"- 有效记录数: {valid_records}")
        print(f"- 损坏记录数: {damaged_records}")
        print(f"- 输出文件: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"处理文件时出错: {e}")
        return False

def verify_output():
    """
    验证输出文件的格式和内容
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, 'changed_urls.jsonl')
    
    if not os.path.exists(output_file):
        print("输出文件不存在，无法验证")
        return
    
    print(f"\n验证输出文件格式:")
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        if not lines:
            print("输出文件为空")
            return
        
        # 检查前几条记录的格式
        for i, line in enumerate(lines[:3]):
            try:
                record = json.loads(line.strip())
                expected_fields = ['id', 'title', 'url', 'time', 'relative_path']
                
                print(f"记录 {i}:")
                for field in expected_fields:
                    if field in record:
                        value = record[field]
                        if isinstance(value, str) and len(value) > 50:
                            value = value[:50] + "..."
                        print(f"  {field}: {value}")
                    else:
                        print(f"  {field}: [缺失]")
                print()
                
            except json.JSONDecodeError as e:
                print(f"记录 {i} JSON格式错误: {e}")
        
        print(f"总共 {len(lines)} 条有效记录")
        
    except Exception as e:
        print(f"验证输出文件时出错: {e}")

if __name__ == "__main__":
    success = process_merged_urls()
    if success:
        verify_output()