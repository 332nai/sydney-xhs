"""调用 Claude 并解析 JSON。需要环境变量 ANTHROPIC_API_KEY。"""
import json, os, re

from . import config


class LLMError(RuntimeError):
    pass


def ask_json(prompt: str, model_key: str = "write_model") -> dict:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise LLMError("没有设置 ANTHROPIC_API_KEY，无法调用模型。")
    import anthropic
    s = config.settings()["llm"]
    client = anthropic.Anthropic()
    msg = client.messages.create(model=s[model_key], max_tokens=s["max_tokens"],
                                 messages=[{"role": "user", "content": prompt}])
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    return parse_json(text)


def parse_json(text: str) -> dict:
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if m:
        text = m.group(1)
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < 0:
        raise LLMError("模型没有返回 JSON：" + text[:200])
    return json.loads(text[start:end + 1])
