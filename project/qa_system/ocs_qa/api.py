"""DeepSeek generation and a separately configured embeddings endpoint."""
import json
import math
import httpx


class APIError(RuntimeError):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


class ModelClient:
    def __init__(self, settings, transport=None):
        self.settings = settings
        self.transport = transport

    def _post(self, base, endpoint, key, payload):
        if not key: raise APIError("missing_key", "未配置相应 API Key，请在本机 .env 中填写。")
        if not base.startswith("https://") and not base.startswith(("http://localhost:", "http://127.0.0.1:")):
            raise APIError("invalid_endpoint", "API 地址须使用 HTTPS，本机测试地址除外。")
        try:
            with httpx.Client(timeout=self.settings.timeout, transport=self.transport, follow_redirects=False) as client:
                response = client.post(base.rstrip("/")+endpoint, headers={"Authorization": f"Bearer {key}"}, json=payload)
            if response.status_code != 200:
                code = response.status_code
                message = {401: "密钥无效或未授权", 402: "账户余额不足", 403: "接口无访问权限", 404: "模型或接口不存在", 429: "请求受到限流"}.get(code, "模型服务请求失败")
                # Never expose raw response bodies, URLs with credentials, or prompts.
                raise APIError(f"http_{code}", f"{message}（HTTP {code}）。")
            result = response.json()
            if not isinstance(result, dict): raise ValueError("not an object")
            return result
        except httpx.TimeoutException as exc:
            raise APIError("timeout", "模型服务超时，请稍后重试。") from exc
        except httpx.RequestError as exc:
            raise APIError("network", "无法连接模型服务，请检查网络和接口地址。") from exc
        except (ValueError, TypeError) as exc:
            raise APIError("invalid_response", "模型服务返回了无效 JSON。") from exc

    def chat(self, system, prompt):
        data = self._post(self.settings.chat_url, "/chat/completions", self.settings.chat_key, {
            "model": self.settings.chat_model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            "thinking": {"type": "disabled"}, "temperature": 0, "max_tokens": 2400,
            "response_format": {"type": "json_object"}, "stream": False,
        })
        try:
            choice = data["choices"][0]
            if choice.get("finish_reason") == "length": raise ValueError("truncated")
            content = choice["message"]["content"]
            if not isinstance(content, str) or not content.strip(): raise ValueError("empty")
            answer = json.loads(content)
            if not isinstance(answer, dict): raise ValueError("not object")
            return answer, data.get("usage", {})
        except (KeyError, IndexError, ValueError, TypeError) as exc:
            raise APIError("invalid_response", "模型输出为空、截断或不符合 JSON 结构，未作为正常答案展示。") from exc

    def embed(self, texts):
        if not self.settings.embedding_url or not self.settings.embedding_model:
            raise APIError("embedding_not_configured", "尚未配置独立的 Embedding 服务；可先使用 BM25。")
        if not texts: return []
        data = self._post(self.settings.embedding_url, "/embeddings", self.settings.embedding_key,
                          {"model": self.settings.embedding_model, "input": texts})
        try:
            items = sorted(data["data"], key=lambda x: x["index"])
            if [x["index"] for x in items] != list(range(len(texts))): raise ValueError("indices")
            vectors = [x["embedding"] for x in items]
            dimensions = {len(v) for v in vectors}
            if len(dimensions) != 1 or not next(iter(dimensions)): raise ValueError("dimensions")
            for vector in vectors:
                if any(not isinstance(v, (int, float)) or not math.isfinite(v) for v in vector) or sum(v*v for v in vector) == 0:
                    raise ValueError("invalid vector")
            return vectors
        except (KeyError, TypeError, ValueError) as exc:
            raise APIError("invalid_embedding", "向量服务返回数量、顺序或维度异常。") from exc
