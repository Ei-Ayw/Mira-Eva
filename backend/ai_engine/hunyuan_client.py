"""
腾讯混元大模型（ChatCompletions）最小封装。

参考文档：`https://cloud.tencent.com/document/api/1729/105701`

环境变量：
- TENCENT_SECRET_ID
- TENCENT_SECRET_KEY
- TENCENT_REGION（可选，默认 ap-guangzhou）
- HUNYUAN_MODEL（可选，默认 hunyuan-turbo）
"""

from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

try:
    from tencentcloud.common import credential
    from tencentcloud.common.profile.client_profile import ClientProfile
    from tencentcloud.common.profile.http_profile import HttpProfile
    from tencentcloud.hunyuan.v20230901 import hunyuan_client, models
except Exception:  # 环境缺少 SDK 时，调用方会自动回退
    credential = None
    ClientProfile = None
    HttpProfile = None
    hunyuan_client = None
    models = None


class HunyuanClient:
    def __init__(self) -> None:
        load_dotenv()
        # 优先支持标准云 API 变量名，其次兼容旧命名
        self.secret_id = (
            os.getenv('TENCENTCLOUD_SECRET_ID')
            or os.getenv('TENCENT_SECRET_ID')
            or ''
        ).strip()
        self.secret_key = (
            os.getenv('TENCENTCLOUD_SECRET_KEY')
            or os.getenv('TENCENT_SECRET_KEY')
            or ''
        ).strip()
        self.region = (
            os.getenv('TENCENTCLOUD_REGION')
            or os.getenv('TENCENT_REGION')
            or 'ap-guangzhou'
        ).strip()
        self.model = os.getenv('HUNYUAN_MODEL', 'hunyuan-turbo').strip()

        if not (self.secret_id and self.secret_key):
            raise RuntimeError('Missing TENCENT_SECRET_ID or TENCENT_SECRET_KEY')

        if credential is None:
            raise RuntimeError('tencentcloud-sdk-python not available')

        cred = credential.Credential(self.secret_id, self.secret_key)
        http_profile = HttpProfile()
        http_profile.endpoint = 'hunyuan.tencentcloudapi.com'
        client_profile = ClientProfile(httpProfile=http_profile)
        self.client = hunyuan_client.HunyuanClient(cred, self.region, client_profile)

    def chat(self, messages: List[Dict[str, str]], stream: bool = False, temperature: float = 0.9) -> Dict[str, Any]:
        """
        messages: [{"Role": "system|user|assistant", "Content": "..."}, ...]
        返回：{"success": bool, "text": str, "raw": dict}
        """
        req = models.ChatCompletionsRequest()
        req.Model = self.model
        req.Stream = bool(stream)
        req.Temperature = float(temperature)
        req.Messages = []
        for m in messages:
            item: Dict[str, Any] = {
                "Role": m.get("Role") or m.get("role") or "user",
                "Content": m.get("Content") or m.get("content") or "",
            }
            # 可选的多模态图片输入：传入 m["Images"] = [ {"Url": "..."}, ... ]
            images = m.get("Images") or m.get("images")
            if images:
                # SDK 结构体允许设置 Images 字段用于图像理解
                item["Images"] = [
                    {"Url": img.get("Url") or img.get("url")} if isinstance(img, dict) else {"Url": str(img)}
                    for img in images
                    if img
                ]
            req.Messages.append(item)

        try:
            resp = self.client.ChatCompletions(req)
            # 非流式：取第一条 Choice 的 Content
            text = ""
            if hasattr(resp, 'Choices') and resp.Choices:
                first = resp.Choices[0]
                # SDK 将 Content 放在 first.Delta/first.Message，两者择一
                content = getattr(first, 'Message', None) or getattr(first, 'Delta', None)
                if content and getattr(content, 'Content', None):
                    text = content.Content
            return {"success": True, "text": text or "", "raw": resp.to_json_string()}
        except Exception as e:
            return {"success": False, "text": "", "error": str(e), "raw": None}


