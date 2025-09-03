import os
import json

from ai_engine.hunyuan_client import HunyuanClient
from ai_engine.prompt_library import get_system_prompt, get_style_notes


def main():
    print("Testing Hunyuan ChatCompletions...")
    print("Region:", os.getenv("TENCENT_REGION", "ap-guangzhou"))
    model = os.getenv("HUNYUAN_MODEL", "hunyuan-turbo")
    print("Model:", model)

    try:
        client = HunyuanClient()
    except Exception as e:
        print("[INIT ERROR]", str(e))
        return

    messages = [
        {"Role": "system", "Content": get_system_prompt()},
        {"Role": "user", "Content": "用两句话、口语化打个招呼，然后问我今天过得咋样？\n" + get_style_notes()},
    ]

    resp = client.chat(messages, stream=False)
    print("success=", resp.get("success"))
    if resp.get("success"):
        print("text=", resp.get("text", "").strip())
    else:
        print("error=", resp.get("error"))
        raw = resp.get("raw")
        if raw:
            try:
                print(json.dumps(json.loads(raw), ensure_ascii=False, indent=2))
            except Exception:
                print(raw)


if __name__ == "__main__":
    main()


