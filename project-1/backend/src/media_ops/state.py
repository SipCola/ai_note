"""图中共享的数据；节点只返回自己修改的字段。"""
from typing import TypedDict


class ContentState(TypedDict, total=False):
    direction: str
    audience: str
    image_count: int
    topics: list[str]
    selected_topic: str
    feedback: str
    article: str
    cards: list[dict]
    materials: dict[str, str]
