import praw
import jsonlines
import time
from datetime import datetime

# 初始化 Reddit API 客户端
reddit_read_only = praw.Reddit(
    client_id="2VYEF43NKc5Fgy4tyVrpRA",
    client_secret="5G89AoMDmT4tkHC2e1i2M316YM_Sjg",
    user_agent="simonsshoot"
)

subreddit = reddit_read_only.subreddit("pics")
count = 0

# 打开 jsonl 文件以写入数据
with jsonlines.open("urls-1.jsonl", mode="w") as writer:
    # 遍历热帖并写入 URL
    for post in subreddit.top(limit=2000):
        count += 1
        print("start^")
        if count % 40 == 0:
            time.sleep(3)
            print("sleep 3s")
            
        # 获取发帖时间（UTC 时间戳转换为可读格式）
        post_time = datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        
        # 获取当前爬取时间
        crawl_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        data = {
            "title": post.title,            # 帖子标题
            "url": post.url,                # 帖子详细 URL
            "post_time": post_time,         # 发帖时间
            "crawl_time": crawl_time        # 爬取时间
        }
        print(f"fetch post: {post.title}")
        writer.write(data)  # 写入 JSONL 文件

print("爬取完成，数据已写入文件中。")