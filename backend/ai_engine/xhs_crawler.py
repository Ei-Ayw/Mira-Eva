import json
import os
from pathlib import Path
from typing import List, Dict

try:
    from hyperbrowser import Hyperbrowser
    from hyperbrowser.models import (
        ScrapeOptions,
        StartScrapeJobParams,
        CreateSessionParams,
    )
    HYPERBROWSER_AVAILABLE = True
except ImportError:
    HYPERBROWSER_AVAILABLE = False

EXEMPLAR_DIR = Path(__file__).resolve().parent / 'exemplars'
EXEMPLAR_DIR.mkdir(parents=True, exist_ok=True)
EXEMPLAR_FILE = EXEMPLAR_DIR / 'xhs_examples.json'


def get_mock_examples() -> List[Dict[str, str]]:
    """提供模拟的高情商对话示例"""
    return [
        {
            'text': '今天遇到一个特别暖心的事情，在地铁上有个小姐姐主动给我让座，虽然我其实不需要，但她的善意真的让我一整天心情都很好。这种小小的温暖真的能传递很久呢！'
        },
        {
            'text': '朋友最近工作压力很大，我约她出来喝咖啡聊天。她说谢谢我陪她，其实我觉得朋友之间互相陪伴是很自然的事情，不需要说谢谢的。'
        },
        {
            'text': '昨天和室友因为一点小事有点小摩擦，今天主动和她道歉了。她也很理解，我们很快就和好了。有时候主动一点真的能避免很多误会。'
        },
        {
            'text': '今天看到一个老奶奶在超市里很迷茫地找东西，我主动过去问她需要什么帮助。她特别感动，一直说现在的年轻人真好。其实帮助别人真的能让自己也感到快乐。'
        },
        {
            'text': '朋友失恋了，我陪她聊了很久。虽然我不能替她解决问题，但至少能让她知道有人陪着她，有人理解她的感受。有时候陪伴就是最好的安慰。'
        },
        {
            'text': '今天在餐厅吃饭，服务员不小心把汤洒了一点在我衣服上。她特别紧张地道歉，我笑着说没关系，衣服洗洗就好了。她的表情从紧张变成了感激，我觉得这样处理挺好的。'
        },
        {
            'text': '同事今天心情不好，我主动关心她，问她怎么了。她说谢谢我的关心，其实我觉得同事之间互相关心是很正常的事情，希望我们都能在困难的时候得到支持。'
        },
        {
            'text': '今天在公交车上看到一个孕妇站着，我主动给她让座。她特别感谢我，其实我觉得这是应该做的事情。希望我们都能在生活中多一份善意和关怀。'
        }
    ]


def fetch_xhs_examples(query: str = '高情商 对话 示例', limit: int = 10) -> List[Dict[str, str]]:
    """
    通过 hyperbrowser Python 库抓取小红书的高情商对话示例。
    如果抓取失败，则使用模拟示例。
    依赖：hyperbrowser 库，环境变量 HYPERBROWSER_API_KEY。
    """
    if not HYPERBROWSER_AVAILABLE:
        print("hyperbrowser 库未安装，使用模拟示例")
        return get_mock_examples()[:limit]
    
    api_key = os.getenv('HYPERBROWSER_API_KEY', '').strip()
    if not api_key:
        print("HYPERBROWSER_API_KEY 环境变量未设置，使用模拟示例")
        return get_mock_examples()[:limit]
    
    try:
        client = Hyperbrowser(api_key=api_key)
        
        # 尝试抓取小红书内容
        scrape_result = client.scrape.start_and_wait(
            StartScrapeJobParams(
                url="https://www.xiaohongshu.com/",
                session_options=CreateSessionParams(
                    accept_cookies=True,
                    use_stealth=False,  # 关闭 stealth 模式
                    use_proxy=False,
                    solve_captchas=False,
                ),
                scrape_options=ScrapeOptions(
                    formats=["markdown", "html"],
                    only_main_content=False,  # 关闭内容过滤
                ),
            )
        )
        
        print(f"抓取状态: {scrape_result.status}")
        
        # 处理抓取结果
        items: List[Dict[str, str]] = []
        
        if scrape_result.status == "completed" and hasattr(scrape_result, 'data'):
            # 尝试从 markdown 格式提取内容
            if hasattr(scrape_result.data, 'markdown') and scrape_result.data.markdown:
                markdown_content = str(scrape_result.data.markdown)
                print(f"Markdown 内容长度: {len(markdown_content)}")
                
                # 分割成段落
                paragraphs = [p.strip() for p in markdown_content.split('\n') if p.strip() and len(p.strip()) > 10]
                
                for para in paragraphs[:limit]:
                    if len(para) > 20:  # 过滤太短的内容
                        items.append({'text': para[:500]})
            
            # 如果没有 markdown，尝试从 html 提取
            elif hasattr(scrape_result.data, 'html') and scrape_result.data.html:
                html_content = str(scrape_result.data.html)
                print(f"HTML 内容长度: {len(html_content)}")
                
                # 简单提取文本（去除HTML标签）
                import re
                text_content = re.sub(r'<[^>]+>', '', html_content)
                paragraphs = [p.strip() for p in text_content.split('\n') if p.strip() and len(p.strip()) > 10]
                
                for para in paragraphs[:limit]:
                    if len(para) > 20:
                        items.append({'text': para[:500]})
            
            # 如果都没有，尝试从 metadata 提取
            elif hasattr(scrape_result.data, 'metadata') and scrape_result.data.metadata:
                metadata = scrape_result.data.metadata
                print(f"Metadata: {metadata}")
                # 这里可以根据需要处理 metadata
        else:
            print(f"抓取失败或状态异常: {scrape_result.status}")
            if hasattr(scrape_result, 'error'):
                print(f"错误信息: {scrape_result.error}")
        
        # 如果抓取成功且获得了内容，返回抓取的内容
        if items:
            print(f"抓取到 {len(items)} 个示例")
            return items
        else:
            print("抓取未获得有效内容，使用模拟示例")
            return get_mock_examples()[:limit]
        
    except Exception as e:
        print(f"抓取失败: {e}")
        print("使用模拟示例作为备选")
        return get_mock_examples()[:limit]


def save_exemplars(examples: List[Dict[str, str]]) -> None:
    """保存示例到本地文件"""
    try:
        with open(EXEMPLAR_FILE, 'w', encoding='utf-8') as f:
            json.dump({'examples': examples}, f, ensure_ascii=False, indent=2)
        print(f"已保存 {len(examples)} 个示例到 {EXEMPLAR_FILE}")
    except Exception as e:
        print(f"保存示例失败: {e}")


def load_exemplars() -> List[str]:
    """从本地文件加载示例"""
    try:
        if not EXEMPLAR_FILE.exists():
            return []
        data = json.loads(EXEMPLAR_FILE.read_text(encoding='utf-8'))
        examples = data.get('examples') or []
        result = [e.get('text', '') for e in examples if isinstance(e, dict) and e.get('text')]
        print(f"从缓存加载了 {len(result)} 个示例")
        return result
    except Exception as e:
        print(f"加载示例失败: {e}")
        return []


