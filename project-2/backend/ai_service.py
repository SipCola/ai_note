"""AI adapters: OpenAI-compatible HTTP endpoints, with independent mock fallbacks."""
import base64
import binascii
import os
from pathlib import Path
import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

load_dotenv(Path(__file__).resolve().parents[1] / '.env')
router = APIRouter()
MAX_AUDIO = 4 * 1024 * 1024

def config(stage):
    return tuple(os.getenv(f'{stage}_{key}', '').strip() for key in ('BASE_URL', 'API_KEY', 'MODEL'))

def modes():
    return {s.lower(): 'live' if all(config(s)) else 'mock' for s in ('ASR', 'LLM', 'TTS')}

class Turn(BaseModel):
    text: str = Field(default='', max_length=2000)
    audio: str = Field(default='', max_length=MAX_AUDIO * 4 // 3 + 4)
    mime: str = 'audio/webm'
    history: list[dict[str, str]] = Field(default_factory=list, max_length=20)

async def request(stage, path, **kwargs):
    url, key, _ = config(stage)
    async with httpx.AsyncClient(timeout=45) as client:
        response = await client.post(url.rstrip('/') + path, headers={'Authorization': f'Bearer {key}'}, **kwargs)
        response.raise_for_status()
        return response

@router.get('/health')
def health():
    return {'status': 'ok', 'modes': modes()}

@router.post('/turn')
async def turn(body: Turn):
    mode = modes()
    text = body.text.strip()
    try:
        if body.audio:
            try:
                audio = base64.b64decode(body.audio, validate=True)
            except (ValueError, binascii.Error):
                raise HTTPException(400, '无效的音频编码')
            if not audio or len(audio) > MAX_AUDIO:
                raise HTTPException(400, '音频为空或超过 4 MB')
            if mode['asr'] == 'mock':
                text = os.getenv('MOCK_TRANSCRIPT', '你好，我想了解一下你们的服务。')
            else:
                mime = body.mime.split(';')[0]
                ext = {'audio/webm':'webm', 'audio/ogg':'ogg', 'audio/mp4':'mp4', 'audio/wav':'wav'}.get(mime)
                if not ext:
                    raise HTTPException(400, '不支持的音频格式')
                result = await request('ASR', '/audio/transcriptions', data={'model':config('ASR')[2]}, files={'file':(f'speech.{ext}', audio, mime)})
                text = result.json().get('text', '').strip()
        if not text:
            raise HTTPException(400, '未识别到文字，请重新说话')
        if mode['llm'] == 'mock':
            reply = f'收到，您说的是“{text}”。我是演示客服，目前尚未连接真实大模型。您可以继续介绍您的需求，接入服务后我会为您提供具体解答。'
        else:
            history = [{'role':h['role'], 'content':h['content'][:2000]} for h in body.history if h.get('role') in ('user','assistant') and isinstance(h.get('content'), str)]
            result = await request('LLM', '/chat/completions', json={'model':config('LLM')[2], 'messages':[{'role':'system','content':os.getenv('SYSTEM_PROMPT','你是简洁友好的中文客服。')}, *history, {'role':'user','content':text}], 'max_tokens':500})
            reply = result.json()['choices'][0]['message']['content']
        speech = None
        if mode['tts'] == 'live':
            result = await request('TTS', '/audio/speech', json={'model':config('TTS')[2], 'voice':os.getenv('TTS_VOICE','alloy'), 'input':reply, 'response_format':'mp3'})
            speech = base64.b64encode(result.content).decode()
        return {'text':text, 'reply':reply, 'audio':speech, 'audio_mime':'audio/mpeg', 'modes':mode}
    except httpx.HTTPError:
        raise HTTPException(502, 'AI 服务请求失败，请检查服务地址、密钥、额度或网络')
    except (KeyError, IndexError, TypeError, ValueError):
        raise HTTPException(502, 'AI 服务返回格式不符合兼容协议')
