import requests
import pandas as pd
import time
import os
from datetime import datetime, timedelta, timezone  # 引入时区处理

def get_beijing_time():
    """获取当前的北京时间串"""
    # 创建 UTC+8 时区
    tz_beijing = timezone(timedelta(hours=8))
    # 返回格式化后的北京时间
    return datetime.now(tz_beijing).strftime("%m-%d %H:%M")

def get_bili_data(keyword):
    """抓取B站指定关键词播放量最高的Top 10"""
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
        "Referer": "https://www.bilibili.com"
    }
    url = f"https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={keyword}&order=click"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        res_json = response.json()
        items = res_json['data']['result'][:10]
        
        results = []
        bj_time = get_beijing_time() # 获取统一的北京时间
        for v in items:
            results.append({
                "标题": v['title'].replace('<em class="keyword">', '').replace('</em>', ''),
                "播放量": v['play'],
                "UP主": v['author'],
                "链接": f"https://www.bilibili.com/video/{v['bvid']}",
                "时间": bj_time
            })
        return results
    except Exception as e:
        print(f"抓取 {keyword} 出错: {e}")
        return []

def generate_dashboard(data_list):
    """生成高级感、极简深色模式手机端监控看板（大字优化版）"""
    html_items = ""
    for item in data_list:
        play_count = str(item['播放量'])
        if play_count.isdigit() and int(play_count) > 10000:
            play_count = f"{round(int(play_count)/10000, 1)}万"

        html_items += f"""
        <div class="card">
            <div class="card-body">
                <div class="title">{item['标题']}</div>
                <div class="stats">
                    <span class="stat-item"><span class="icon">📈</span> {play_count}</span>
                    <span class="stat-item"><span class="icon">👤</span> {item['UP主']}</span>
                </div>
            </div>
            <div class="card-footer">
                <span class="time">⏰ {item['时间']}</span>
                <a href="{item['链接']}" class="btn">WATCH</a>
            </div>
        </div>
        """

    current_bj_time = get_beijing_time()

    full_html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
        <meta http-equiv="refresh" content="600">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <title>Bili Monitor Pro</title>
        <style>
            :root {{ 
                --bg: #121212; 
                --card-bg: #1E1E1E; 
                --bili-blue: #00A1D6; 
                --text-main: #E0E0E0; 
                --text-sub: #A0A0A0; 
                --border: #333;
            }}
            body {{ 
                background: var(--bg); color: var(--text-main); 
                margin: 0; padding: 0; 
                font-family: -apple-system, "SF Pro Text", "Helvetica Neue", sans-serif; 
                -webkit-font-smoothing: antialiased;
            }}
            .header {{ 
                position: sticky; top: 0; 
                background: rgba(18, 18, 18, 0.7);
                backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
                padding: 15px; text-align: center;
                border-bottom: 1px solid var(--border); z-index: 100;
                padding-top: calc(15px + env(safe-area-inset-top)); 
            }}
            .header h2 {{ margin: 0; font-size: 16px; font-weight: 700; color: #fff; letter-spacing: 0.5px; }}
            
            /* 顶部同步时间：17px */
            .header p {{ margin: 6px 0 0; font-size: 17px; color: var(--text-sub); text-transform: uppercase; letter-spacing: 1px; }}
            
            .container {{ padding: 12px; max-width: 600px; margin: 0 auto; padding-bottom: calc(12px + env(safe-area-inset-bottom)); }}
            .card {{ background: var(--card-bg); border-radius: 12px; margin-bottom: 12px; border: 1px solid var(--border); transition: background 0.2s; }}
            .card:active {{ background: #252525; }}
            .card-body {{ padding: 16px; }}
            
            /* 标题：19px 粗体 */
            .title {{ font-size: 19px; font-weight: 700; color: var(--text-main); line-height: 1.5; margin-bottom: 12px; }}
            
            .stats {{ display: flex; gap: 15px; }}
            .stat-item {{ font-size: 14px; color: var(--text-sub); display: flex; align-items: center; background: rgba(255,255,255,0.05); padding: 4px 8px; border-radius: 4px; }}
            .icon {{ margin-right: 5px; opacity: 0.7; font-size: 10px; }}
            .card-footer {{ display: flex; justify-content: space-between; align-items: center; padding: 10px 16px; border-top: 1px solid var(--border); background: rgba(0,0,0,0.1); border-radius: 0 0 12px 12px; }}
            
            /* 卡片时间：17px */
            .time {{ font-size: 17px; color: #888; font-family: "Courier New", monospace; }}
            
            /* 按钮：微调 padding 让它在 17px 字体旁不显瘦小 */
            .btn {{ background: transparent; color: var(--bili-blue); text-decoration: none; padding: 8px 18px; border-radius: 6px; font-size: 13px; font-weight: 800; border: 1px solid var(--bili-blue); letter-spacing: 1px; transition: all 0.2s; }}
            .btn:active {{ background: var(--bili-blue); color: #fff; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>Bili Monitor Pro</h2>
            <p>Synced: {current_bj_time}</p>
        </div>
        <div class="container">
            {html_items}
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

if __name__ == "__main__":
    # 你设定的关键词
    keywords = ["全栈开发", "GitHub", "白帽黑客", "DIY"]
    all_data = []
    for kw in keywords:
        all_data.extend(get_bili_data(kw))
    
    if all_data:
        df = pd.DataFrame(all_data)
        df.to_csv("data.csv", index=False, encoding="utf-8-sig")
        generate_dashboard(all_data)
        print("数据已按北京时间更新，大字版网页已生成。")
