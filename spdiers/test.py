import requests

proxies = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
}

try:
    response = requests.get("https://www.reddit.com", proxies=proxies)
    print("连接成功！状态码:", response.status_code)
except Exception as e:
    print("连接失败:", e)