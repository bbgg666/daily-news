import requests
import feedparser
import os

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_KEY")
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID")

RSS_SOURCES = [
    "https://www.reuters.com/rssFeed/worldNews",
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "https://apnews.com/rss/apf-topnews/world-news",
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
        except:
            continue
    return "\n\n".join(all_news)

def summarize_news(raw_news):
    prompt = f"""
基于下面的真实新闻素材，精选10条过去24小时全球重要新闻，按重要性排序。
严格格式规则：
1. 开头只写「📰 全球早报」
2. 每条新闻第一行是加粗的核心标题：**标题内容**
3. 标题下空一行，再写一句话核心事实
4. 每条完整新闻之间空两行
5. 所有信息完全来自素材，严禁编造任何内容

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
    return resp.json()["choices"][0]["message"]["content"]

def push_telegram(content):
    api_url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": content,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    requests.post(api_url, json=payload)

if __name__ == "__main__":
    raw_news = get_global_news()
    result = summarize_news(raw_news)
    push_telegram(result)
    print("全球早报推送完成")
