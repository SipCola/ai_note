import base64
import os
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.main import app as ai_app
from backend.main import app as gateway_app

class VoiceFlowTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {f'{s}_{k}':'' for s in ('ASR','LLM','TTS') for k in ('BASE_URL','API_KEY','MODEL')})
        self.env.start()
        self.ai = TestClient(ai_app)
    def tearDown(self):
        self.env.stop()
    def test_mock_text_and_audio(self):
        result = self.ai.post('/api/ai/turn', json={'text':'你好'}).json()
        self.assertIn('你好', result['reply'])
        self.assertIsNone(result['audio'])
        result = self.ai.post('/api/ai/turn', json={'audio':base64.b64encode(b'example audio').decode()})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()['modes']['asr'], 'mock')
    def test_reject_invalid_inputs(self):
        for payload in ({}, {'audio':'!!!'}, {'text':'a'*2001}):
            self.assertIn(self.ai.post('/api/ai/turn', json=payload).status_code, (400,422))
    def test_live_provider_adapters(self):
        import httpx
        from unittest.mock import AsyncMock
        response = httpx.Response(200, json={'choices':[{'message':{'content':'真实回复'}}]}, request=httpx.Request('POST','https://example.com'))
        with patch.dict(os.environ, {'LLM_BASE_URL':'https://example.com/v1','LLM_API_KEY':'test','LLM_MODEL':'test'}), patch('backend.ai_service.request', new=AsyncMock(return_value=response)) as req:
            result = self.ai.post('/api/ai/turn',json={'text':'你好','history':[{'role':'system','content':'untrusted'}]}).json()
            self.assertEqual(result['reply'],'真实回复')
            self.assertEqual(len(req.call_args.kwargs['json']['messages']),2)
    def test_websocket_protocol(self):
        from unittest.mock import AsyncMock
        import httpx
        result = {'text':'你好','reply':'您好，请问有什么可以帮助您？','audio':None,'modes':{'asr':'mock','llm':'mock','tts':'mock'}}
        with patch('backend.main.turn',new=AsyncMock(return_value=result)):
            with TestClient(gateway_app).websocket_connect('/ws/call', headers={'origin':'http://localhost:5173'}) as socket:
                self.assertEqual(socket.receive_json()['type'],'connected')
                socket.send_text('bad json')
                self.assertEqual(socket.receive_json()['type'],'error')
                socket.send_json({'type':'text','text':'你好'})
                events=[]
                while True:
                    event=socket.receive_json(); events.append(event)
                    if event['type']=='status' and event['status']=='listening': break
                self.assertTrue(any(e['type']=='transcript' for e in events))
                self.assertEqual(''.join(e['text'] for e in events if e['type']=='delta'),result['reply'])
                socket.send_json({'type':'hangup'})
    def test_combined_websocket_flow(self):
        with TestClient(gateway_app) as client:
            self.assertEqual(client.get('/api/health').json()['status'], 'ok')
            with client.websocket_connect('/ws/call', headers={'origin':'http://localhost:5173'}) as socket:
                socket.receive_json()
                for payload in ({'type':'text','text':'合并测试'}, {'type':'audio','audio':base64.b64encode(b'example audio').decode()}, {'type':'text','text':''}):
                    socket.send_json(payload)
                    events=[]
                    while True:
                        event=socket.receive_json(); events.append(event)
                        if event['type']=='status' and event['status']=='listening': break
                    expected = 'reply' if payload.get('text') or payload.get('audio') else 'error'
                    self.assertTrue(any(e['type']==expected for e in events))
                socket.send_json({'type':'hangup'})
    def test_origin_config_refresh(self):
        from tempfile import TemporaryDirectory
        from pathlib import Path
        with TemporaryDirectory() as folder:
            env = Path(folder) / '.env'
            with patch('backend.main.ENV_PATH', env), patch.dict(os.environ, {'ALLOWED_ORIGINS':'http://localhost:5173'}):
                env.write_text('ALLOWED_ORIGINS=http://localhost:5173', encoding='utf-8')
                from backend.main import allowed_origins
                self.assertNotIn('http://10.253.255.121:5173', allowed_origins())
                env.write_text('ALLOWED_ORIGINS=http://localhost:5173, http://10.253.255.121:5173/ ', encoding='utf-8')
                with TestClient(gateway_app).websocket_connect('/ws/call', headers={'origin':'http://10.253.255.121:5173'}) as socket:
                    self.assertEqual(socket.receive_json()['type'], 'connected')
                    socket.send_json({'type':'hangup'})
    def test_origin_rejected(self):
        from starlette.websockets import WebSocketDisconnect
        with self.assertRaises(WebSocketDisconnect):
            with TestClient(gateway_app).websocket_connect('/ws/call',headers={'origin':'https://untrusted.example'}): pass

if __name__ == '__main__': unittest.main()
