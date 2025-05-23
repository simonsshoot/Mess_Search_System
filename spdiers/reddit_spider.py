import praw
import jsonlines
import requests
import time
import os
import urllib.request
print("系统级代理配置:", urllib.request.getproxies())
print("当前代理环境变量:", os.environ.get('https_proxy'))
reddit_read_only = praw.Reddit(
    client_id="2VYEF43NKc5Fgy4tyVrpRA",
    client_secret="5G89AoMDmT4tkHC2e1i2M316YM_Sjg",
    user_agent="simonsshoot",  # 按规范格式修改
    proxies={
        "http": "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890"
    }
)

subreddit = reddit_read_only.subreddit("pics")
count=0
# 打开 jsonl 文件以写入数据
with jsonlines.open("urls.jsonl", mode="w") as writer:
    # 遍历热帖并写入 URL
    for post in subreddit.top(limit=1):
        count+=1
        print("start^")
        if count%40==0:
            time.sleep(3)
            print("sleep 3s")
        data = {
            "title": post.title,  # 帖子标题
            "url": post.url       # 帖子详细 URL
        }
        print("fetch post: ",post.title)
        writer.write(data)  # 写入 JSONL 文件

print("爬取完成，数据已写入文件中。")
