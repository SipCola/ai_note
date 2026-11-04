import asyncio, base64, json
import httpx
from websockets.asyncio.client import connect

async def main():
    async with httpx.AsyncClient() as client:
        health = await client.get('http://127.0.0.1:5173/api/health')
        assert health.json()['status'] == 'ok'
    async with connect('ws://127.0.0.1:5173/ws/call', origin='http://localhost:5173') as ws:
        assert json.loads(await ws.recv())['type'] == 'connected'
        for payload in ({'type':'text','text':'联通测试'}, {'type':'audio','audio':base64.b64encode(b'mock audio payload').decode(),'mime':'audio/webm'}):
            await ws.send(json.dumps(payload))
            events=[]
            while True:
                e=json.loads(await ws.recv());events.append(e)
                if e['type']=='status' and e['status']=='listening': break
            assert any(e['type']=='reply' for e in events), events
            assert not any(e['type']=='error' for e in events), events
        await ws.send(json.dumps({'type':'hangup'}))
    print('PASS: Vite proxy -> WebSocket gateway -> integrated AI module, text + audio mock, hangup')
asyncio.run(main())
