"""Business gateway. One cancellable conversation task per WebSocket."""
import asyncio
import json
import os
import uuid
from pathlib import Path
from dotenv import dotenv_values, load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import ValidationError
from backend.ai_service import Turn, health as ai_health, router as ai_router, turn

load_dotenv(Path(__file__).resolve().parents[1] / '.env')
app = FastAPI(title='Voice customer service')
app.include_router(ai_router, prefix='/api/ai', tags=['AI'])
ENV_PATH = Path(__file__).resolve().parents[1] / '.env'

def allowed_origins():
    # Read the local configuration for each handshake; reload must not retain
    # a stale value inherited from the parent process's dotenv environment.
    configured = dotenv_values(ENV_PATH).get('ALLOWED_ORIGINS')
    if configured is None:
        configured = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173')
    return {origin.strip().rstrip('/') for origin in configured.split(',') if origin.strip()}


@app.get('/api/health')
async def health():
    return ai_health()

@app.websocket('/ws/call')
async def call(ws: WebSocket):
    if ws.headers.get('origin') not in allowed_origins():
        await ws.close(code=1008)
        return
    await ws.accept()
    history = []
    task = None
    async def process(data):
        try:
            await ws.send_json({'type':'status', 'status':'thinking'})
            result = await turn(Turn(**data, history=history[-20:]))
            await ws.send_json({'type':'transcript', 'text':result['text']})
            # Incremental bubble rendering; model response is obtained per completed turn.
            for start in range(0, len(result['reply']), 6):
                await ws.send_json({'type':'delta', 'text':result['reply'][start:start+6]})
                await asyncio.sleep(0.025)
            await ws.send_json({'type':'reply', **result})
            history.extend([{'role':'user','content':result['text']}, {'role':'assistant','content':result['reply']}])
            del history[:-20]
        except HTTPException as exc:
            await ws.send_json({'type':'error', 'message':str(exc.detail)})
        except ValidationError:
            await ws.send_json({'type':'error', 'message':'请求数据格式不正确'})
        except (ValueError, KeyError, TypeError):
            await ws.send_json({'type':'error','message':'AI 处理失败，请检查服务配置'})
        finally:
            if not asyncio.current_task().cancelling():
                await ws.send_json({'type':'status','status':'listening'})
    try:
        await ws.send_json({'type':'connected','session_id':uuid.uuid4().hex})
        while True:
            raw = await ws.receive_text()
            if len(raw) > 5_600_000:
                await ws.close(code=1009)
                break
            try:
                data = json.loads(raw)
                if not isinstance(data, dict):
                    raise ValueError()
            except (ValueError, TypeError):
                await ws.send_json({'type':'error','message':'无效消息'})
                continue
            if data.get('type') == 'hangup':
                await ws.close(code=1000)
                break
            if data.get('type') not in ('text','audio'):
                await ws.send_json({'type':'error','message':'不支持的消息类型'})
                continue
            if task and not task.done():
                await ws.send_json({'type':'error','message':'正在回复，请稍后再说'})
                continue
            payload = {k:data[k] for k in ('text','audio','mime') if k in data}
            task = asyncio.create_task(process(payload))
    except WebSocketDisconnect:
        pass
    finally:
        if task:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
