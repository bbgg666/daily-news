import requests
import feedparser
import os

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_KEY")
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID")

RSS_SOURCES = [
    "https://www.reuters.com/rssFeed/worldNews",
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "https://apnews.com/rss/apf-topnews",
    "http://www.xinhuanet.com/world/news_world.xml"
]

def get_global_news():
    all_news = []
    for url in RSS_SOURCES:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:8]:
                summary = entry.summary if hasattr(entry, 'summary') else entry.title
                all_news.append(f"标题：{entry.title}\n摘要：{summary}\n链接：{entry.link}")
        except Exception as e:
            print(f"抓取源失败 {url}: {e}")
            continue
    return "\n\n".join(all_news)

def summarize_news(raw_news):
    prompt = f"""
基于下面的真实新闻素材，精选10条过去24小时全球重要新闻，按重要性排序。
严格按照以下格式输出，不要任何额外说明：
1. 开头固定三行：
──────────
<b>       📰 全球早报</b>
──────────
2. 每条新闻固定格式：
<b>序号. 新闻核心标题</b>
一句话核心事实内容
<small>来源：<a href="原文链接">查看原文</a></small>
3. 序号从1开始连续编号，每条新闻之间空一行
4. 所有信息完全来自素材，严禁编造内容，原文链接必须对应每条新闻的真实链接

新闻素材：
{raw_news}
"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "stream": False
    }
    resp = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=data)
    resp_json = resp.json()
    if "choices" not in resp_json:
        raise Exception(f"API调用失败: {resp_json}")
    return resp_json["choices"][0]["message"]["content"]

def push_telegram(content):
    api_url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": content,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    resp = requests.post(api_url, json=payload)
    resp.raise_for_status()

if __name__ == "__main__":
    print("开始抓取新闻...")
    raw_news = get_global_news()
    print("开始AI总结...")
    result = summarize_news(raw_news)
    print("总结完成，开始推送...")
    push_telegram(result)
    print("全球早报推送完成")
