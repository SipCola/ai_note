"""薄 API：启动图、读取检查点、提交人工输入。"""
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from langgraph.types import Command
from .workflow import build_workflow


class CreateRun(BaseModel):
    model_config = ConfigDict(extra='forbid')
    direction: str = Field(default='AI 应用开发', min_length=1)
    audience: str = Field(default='AI 编程初学者', min_length=1)
    image_count: int = Field(default=4, ge=3, le=5)


class ResumeRun(BaseModel):
    model_config = ConfigDict(extra='forbid')
    topic_index: int | None = None
    decision: str | None = None
    feedback: str = ''


def create_app(graph=None):
    app = FastAPI(title='LangGraph 内容工作流框架')
    graph = graph if graph is not None else build_workflow()
    app.state.graph = graph

    def config(run_id):
        return {'configurable': {'thread_id': run_id}}

    def snapshot(run_id):
        state = graph.get_state(config(run_id))
        if not state.values:
            raise HTTPException(404, '流程不存在')
        pauses = [item.value for task in state.tasks for item in task.interrupts]
        return {'run_id': run_id, 'status': 'waiting' if pauses else 'completed' if not state.next else 'running',
                'state': state.values, 'next': state.next, 'interrupts': pauses}

    @app.post('/runs', status_code=201)
    def start(body: CreateRun):
        run_id = uuid4().hex
        graph.invoke(body.model_dump(), config(run_id))
        return snapshot(run_id)

    @app.get('/runs/{run_id}')
    def read(run_id: str):
        return snapshot(run_id)

    @app.post('/runs/{run_id}/resume')
    def resume(run_id: str, body: ResumeRun):
        current = snapshot(run_id)
        if not current['interrupts']:
            raise HTTPException(409, '当前没有等待人工输入的节点')
        answer = body.model_dump(exclude_none=True)
        stage = current['interrupts'][0]['stage']
        if stage == 'topic_selection':
            index = body.topic_index
            if index is None or not 0 <= index < len(current['state']['topics']):
                raise HTTPException(422, 'topic_index 必须是有效选题序号')
        elif body.decision not in ('approve', 'revise') or (body.decision == 'revise' and not body.feedback.strip()):
            raise HTTPException(422, '请选择 approve，或 revise 并填写 feedback')
        graph.invoke(Command(resume=answer), config(run_id))
        return snapshot(run_id)

    return app
