# 工作流实现

## 核心机制

- `ContentState` 是整个流程的共享状态，各节点返回局部字段更新。
- `build_workflow()` 注册节点和连接，compile 后返回可独立调用的图。
- 选题和文案审核通过 `interrupt()` 暂停，调用方使用相同 thread_id 和 `Command(resume=...)` 继续。
- 审核节点通过 `Command(goto=...)` 选择重写文章或规划卡片；因此退回循环直接表达在图中。
- 人工节点恢复时会从头运行，中断前不调用模型、不写文件。
- 检查点是流程状态的唯一来源，没有额外业务状态机或任务仓储。

## 脱离 HTTP 使用

```python
from langgraph.types import Command
from media_ops.workflow import build_workflow

graph = build_workflow()
config = {"configurable": {"thread_id": "demo"}}
graph.invoke({"direction": "AI 编程", "audience": "新手", "image_count": 3}, config)
graph.invoke(Command(resume={"topic_index": 0}), config)
graph.invoke(Command(resume={"decision": "revise", "feedback": "加入案例"}), config)
graph.invoke(Command(resume={"decision": "approve"}), config)
print(graph.get_state(config).values)
print(graph.get_graph().draw_mermaid())
```

直接调用图时应传入完整初始字段；API 会补默认值并校验输入。无效人工输入会报错，可用正确输入重试。示例 API 不支持同一流程的并发恢复。

## 扩展点

1. 实现 `ContentProvider`，通过 `build_workflow(provider=...)` 注入真实模型。
2. 在 plan_cards 后增加独立图片渲染节点，避免把文件副作用放入人工中断节点。
3. 在创建图时注入官方 PostgreSQL checkpointer，生命周期由启动入口管理，保持稳定 thread_id。
4. 需要图片审核时增加 interrupt 节点及回退边；先扩展图，再暴露输入接口。

参考：[LangGraph interrupt 官方 API](https://reference.langchain.com/python/langgraph/types/interrupt)。
