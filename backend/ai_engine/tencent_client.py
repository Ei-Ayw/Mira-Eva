# -*- coding: utf-8 -*-
import os
import json
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv

try:
    from tencentcloud.common.common_client import CommonClient
    from tencentcloud.common import credential
    from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
    from tencentcloud.common.profile.client_profile import ClientProfile
    from tencentcloud.common.profile.http_profile import HttpProfile
    TENCENT_AVAILABLE = True
except Exception:  # SDK 未安装或环境不满足
    TENCENT_AVAILABLE = False

load_dotenv()  # 读取 .env

class NonStreamResponse(object):
    def __init__(self):
        self.response = ""
    def _deserialize(self, obj):
        self.response = json.dumps(obj, ensure_ascii=False)

class TencentDeepSeekClient:
    def __init__(self, region: str = None, endpoint: str = None):
        self.secret_id = os.getenv("TENCENTCLOUD_SECRET_ID")
        self.secret_key = os.getenv("TENCENTCLOUD_SECRET_KEY")
        self.region = region or os.getenv("TENCENTCLOUD_REGION", "ap-guangzhou")
        self.endpoint = endpoint or os.getenv("TENCENTCLOUD_LKE_ENDPOINT", "lkeap.tencentcloudapi.com")
        self.model = os.getenv("TENCENTCLOUD_DEEPSEEK_MODEL", "deepseek-r1")

    def _build_client(self):
        if not TENCENT_AVAILABLE:
            raise RuntimeError("tencentcloud-sdk-python 未安装或不可用")
        if not self.secret_id or not self.secret_key:
            raise RuntimeError("缺少 TENCENTCLOUD_SECRET_ID 或 TENCENTCLOUD_SECRET_KEY")
        cred = credential.Credential(self.secret_id, self.secret_key)
        http_profile = HttpProfile()
        http_profile.endpoint = self.endpoint
        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile
        return CommonClient("lkeap", "2024-05-22", cred, self.region, profile=client_profile)

    def chat(self, messages: List[Dict[str, str]], stream: bool = False) -> Dict[str, Any]:
        """调用DeepSeek R1对话。
        messages: [{"Role": "user"|"assistant", "Content": "..."}, ...]
        返回统一字典：{"success": bool, "text": str, "raw": any}
        """
        # 若缺少密钥或SDK，不报错中断，回退到本地模拟
        if not (TENCENT_AVAILABLE and self.secret_id and self.secret_key):
            return self._mock_chat(messages)
        try:
            common_client = self._build_client()
            params = json.dumps({
                "Model": self.model,
                "Messages": messages,
                "Stream": stream,
            }, ensure_ascii=False)
            resp = common_client._call_and_deserialize("ChatCompletions", json.loads(params), NonStreamResponse)
            if isinstance(resp, NonStreamResponse):
                raw = json.loads(resp.response)
                text = self._extract_text(raw)
                return {"success": True, "text": text, "raw": raw}
            else:
                parts = []
                for event in resp:
                    try:
                        data = json.loads(event)
                        parts.append(self._extract_text(data))
                    except Exception:
                        continue
                return {"success": True, "text": "".join(parts), "raw": parts}
        except TencentCloudSDKException as e:
            return {"success": False, "text": "", "raw": {"error": str(e)}}
        except Exception as e:
            # 兜底为本地模拟
            return self._mock_chat(messages, error=str(e))

    @staticmethod
    def _extract_text(raw: Dict[str, Any]) -> str:
        """从Tencent返回中尽量抽取纯文本内容。"""
        try:
            if not isinstance(raw, dict):
                return str(raw)
            # 1) 新版/常见结构：Choices[0].Message.Content
            choices = raw.get("Choices") or raw.get("choices")
            if isinstance(choices, list) and choices:
                msg = choices[0].get("Message") or choices[0].get("message") or {}
                content = msg.get("Content") or msg.get("content")
                if isinstance(content, str) and content.strip():
                    return content.strip()
            # 2) 另一种结构：Output.Text
            out = raw.get("Output") or raw.get("output") or {}
            text = out.get("Text") or out.get("text")
            if isinstance(text, str) and text.strip():
                return text.strip()
            # 3) 备用字段
            for key in ("content", "message", "Message", "answer", "text"):
                v = raw.get(key)
                if isinstance(v, str) and v.strip():
                    return v.strip()
            return ""
        except Exception:
            return ""

    @staticmethod
    def _mock_chat(messages: List[Dict[str, str]], error: Optional[str] = None) -> Dict[str, Any]:
        user_last = ""
        for m in reversed(messages or []):
            if m.get("Role") == "user":
                user_last = m.get("Content", "")
                break
        prefix = "[Mock DeepSeek R1] "
        if error:
            prefix += f"(fallback due to: {error}) "
        reply = prefix + ("我已收到你的消息：" + user_last[:60] if user_last else "你好，我在～")
        return {"success": True, "text": reply, "raw": {"mock": True}}
