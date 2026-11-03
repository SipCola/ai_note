"""替换此接口即可接入 LLM，节点和边无需改变。"""
from typing import Protocol
from .state import ContentState


class ContentProvider(Protocol):
    def topics(self, state: ContentState) -> list[str]: ...
    def article(self, state: ContentState) -> str: ...
    def cards(self, state: ContentState) -> list[dict]: ...


class MockProvider:
    def topics(self, state):
        return [f"{state['direction']}：{angle}" for angle in
                ['入门实践', '常见误区', '项目拆解']]

    def article(self, state):
        text = (f"# {state['selected_topic']}\n\n"
                f"面向{state['audience']}的 mock 技术分享。\n\n"
                "## 实践步骤\n明确目标，搭建最小案例，检查结果。")
        if state.get('feedback'):
            text += f"\n\n本轮修改意见：{state['feedback']}"
        return text

    def cards(self, state):
        return [{'page': i + 1, 'title': state['selected_topic'],
                 'text': state['article'], 'image_prompt': f'第 {i + 1} 页技术知识卡片'}
                for i in range(state['image_count'])]
