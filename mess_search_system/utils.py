# import json
# def add_id_to_jsonl(input_file_path, output_file_path):
#     with open(input_file_path, 'r', encoding='utf-8') as infile, \
#          open(output_file_path, 'w', encoding='utf-8') as outfile:
#         for index, line in enumerate(infile):
#             # 将每行解析为 JSON 对象
#             data = json.loads(line)
#             # 添加 id 字段，从 0 开始
#             data['id'] = index
#             # 将更新后的 JSON 对象写入新文件
#             outfile.write(json.dumps(data, ensure_ascii=False) + '\n')

# # 示例用法
# input_file_path = r'G:\大三上试题笔记合集\python_finalwork\reddit_spider\reddit_detailed.jsonl'  # 替换为你的输入文件路径
# output_file_path = r'G:\大三上试题笔记合集\python_finalwork\reddit_spider\reddit_detailed_id.jsonl'  # 替换为你的输出文件路径
# add_id_to_jsonl(input_file_path, output_file_path)



import json

# 输入和输出文件路径
input_file = 'input.jsonl'  # 假设原始JSONL文件名为input.jsonl
output_file = 'output.jsonl'  # 假设输出文件名为output.jsonl

try:
    # 打开输入和输出文件
    with open(input_file, 'r', encoding='utf-8') as fin, \
         open(output_file, 'w', encoding='utf-8') as fout:
        
        id_counter = 0  # 用于生成id
        
        for line in fin:
            try:
                # 解析每一行JSON
                data = json.loads(line.strip())
                
                # 提取需要的字段
                new_data = {
                    "id": id_counter,
                    "title": data.get("title", ""),
                    "url": data.get("url", ""),
                    "time": data.get("post_time", "")[:10],
                    "relative_path":data.get("relative_path", ""),
                }
                
                # 写入新的JSONL文件
                fout.write(json.dumps(new_data, ensure_ascii=False) + '\n')
                
                id_counter += 1  # id递增
                
            except json.JSONDecodeError as e:
                print(f"警告：无法解析JSON行 - {e}")
                continue
            except Exception as e:
                print(f"警告：处理行时出错 - {e}")
                continue

    print(f"处理完成，共处理 {id_counter} 条记录，结果已写入 {output_file}")

except FileNotFoundError:
    print(f"错误：文件 {input_file} 不存在")
except Exception as e:
    print(f"错误：处理文件时出错 - {e}")