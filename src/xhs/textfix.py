"""文字整理：中文与英文、数字之间不留空格。"""
import re

CJK = r"[\u3000-\u303f\u4e00-\u9fff\uff00-\uffef“”‘’・]"


def nospace(t: str) -> str:
    t = re.sub(rf"(?<={CJK})[ ]+(?=[A-Za-z0-9$#(])", "", t)
    t = re.sub(rf"(?<=[A-Za-z0-9$%)'])[ ]+(?={CJK})", "", t)
    return t


def clean(obj):
    """递归处理稿件数据里的所有文字，路径和链接不动。"""
    if isinstance(obj, str):
        return obj if obj.startswith(("data/", "/", "http")) else nospace(obj)
    if isinstance(obj, list):
        return [clean(x) for x in obj]
    if isinstance(obj, dict):
        return {k: clean(v) for k, v in obj.items()}
    return obj
