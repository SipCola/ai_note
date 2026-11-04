import React, { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

function App() {
  const [state, setState] = useState('idle');
  const [messages, setMessages] = useState([]);
  const [draft, setDraft] = useState('');
  const [error, setError] = useState('');
  const [modes, setModes] = useState(null);
  const [recording, setRecording] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [caption, setCaption] = useState('每一次对话，都有回应。');
  const [muted, setMuted] = useState(false);
  const ws = useRef(null), stream = useRef(null), recorder = useRef(null), audio = useRef(null);
  const timer = useRef(null), generation = useRef(0), end = useRef(null), partial = useRef('');
  const silent = useRef(false), busy = useRef(false), recordTimer = useRef(null);
  const active = !['idle', 'connecting'].includes(state);
  const labels = {idle:'等待接通', connecting:'正在连接', listening:'正在聆听', thinking:'正在思考', speaking:'正在回复'};
  useEffect(() => { fetch('/api/health').then(r => r.json()).then(d => setModes(d.modes || null)).catch(() => {}); return () => cleanup(); }, []);
  useEffect(() => { end.current?.scrollIntoView({behavior:'smooth'}); }, [messages]);
  useEffect(() => { if (active) timer.current = setInterval(() => setSeconds(v => v+1), 1000); return () => clearInterval(timer.current); }, [active]);
  function stopPlayback() {
    window.speechSynthesis?.cancel();
    if (audio.current) { audio.current.pause(); audio.current = null; }
  }
  function cleanup() {
    generation.current++;
    clearTimeout(recordTimer.current);
    if (recorder.current?.state === 'recording') recorder.current.stop();
    recorder.current = null;
    stream.current?.getTracks().forEach(t => t.stop()); stream.current = null;
    ws.current?.close(); ws.current = null;
    stopPlayback(); busy.current = false;
  }
  function hangup() { cleanup(); setRecording(false); setState('idle'); setCaption('通话已结束，期待再次与你相遇。'); }
  function playback(data, token) {
    if (silent.current) { busy.current = false; setState('listening'); return; }
    const finish = () => { if (generation.current === token) {busy.current = false; setState('listening');} };
    setState('speaking');
    if (data.audio) {
      const player = new Audio(`data:${data.audio_mime};base64,${data.audio}`);
      audio.current = player; player.onended = finish;
      player.onerror = () => { setError('语音播放失败，回复文字已保留'); finish(); };
      player.play().catch(() => {setError('浏览器阻止了语音播放，请允许此页面播放声音'); finish();});
    } else if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(data.reply); utterance.lang = 'zh-CN'; utterance.rate = 1.05;
      utterance.onend = finish; utterance.onerror = finish;
      window.speechSynthesis.speak(utterance);
    } else { setError('浏览器不支持本地语音合成，可阅读文字回复'); finish(); }
  }
  async function dial() {
    if (state !== 'idle') return;
    setError(''); setState('connecting'); setMessages([]); setSeconds(0); partial.current = '';
    const token = ++generation.current;
    const socket = new WebSocket(`${location.protocol === 'https:' ? 'wss':'ws'}://${location.host}/ws/call`); ws.current = socket;
    const timeout = setTimeout(() => {if (socket.readyState !== WebSocket.OPEN) {setError('连接超时，请检查业务后台'); hangup();}}, 8000);
    socket.onopen = () => { clearTimeout(timeout); if (token !== generation.current) return; setState('listening'); setCaption('你好，我是小声。很高兴为你服务。'); };
    socket.onmessage = event => {
      if (token !== generation.current) return;
      const data = JSON.parse(event.data);
      if (data.type === 'status' && data.status === 'thinking') setState('thinking');
      if (data.type === 'transcript') {
        partial.current = '';
        setMessages(m => [...m, {role:'user', text:data.text}, {role:'assistant', text:'', pending:true}]);
      }
      if (data.type === 'delta') {
        partial.current += data.text; const text = partial.current; setCaption(text);
        setMessages(m => m.map((v,i) => i === m.length-1 && v.pending ? {...v, text} : v));
      }
      if (data.type === 'reply') {
        setModes(data.modes); setMessages(m => m.map(v => v.pending ? {...v, text:data.reply, pending:false} : v)); playback(data, token);
      }
      if (data.type === 'error') { setError(data.message); busy.current = false; setState('listening'); }
    };
    socket.onerror = () => setError('无法连接业务后台，请确认 8000 端口已启动');
    socket.onclose = () => { clearTimeout(timeout); if (token === generation.current) { cleanup(); setRecording(false); setState('idle'); } };
    fetch('/api/health').then(r => r.json()).then(d => {if (token === generation.current) setModes(d.modes || null);}).catch(() => {});
  }
  function send(payload) {
    if (ws.current?.readyState !== WebSocket.OPEN || busy.current) return;
    busy.current = true; setError(''); setState('thinking'); ws.current.send(JSON.stringify(payload));
  }
  async function toggleRecord() {
    if (recording) { clearTimeout(recordTimer.current); recorder.current?.stop(); return; }
    if (!active || busy.current) return;
    const token = generation.current;
    try {
      if (!window.isSecureContext) throw new Error('当前 HTTP 地址无法使用麦克风，请先安装本项目证书，再通过 HTTPS 地址访问。');
      if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) throw new Error('当前浏览器缺少录音功能，请尝试更新浏览器或使用 Chrome / Edge。');
      const media = await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true, noiseSuppression:true}, video:false});
      if (token !== generation.current || busy.current) {media.getTracks().forEach(t=>t.stop()); return;}
      stream.current = media;
      const mime = ['audio/webm;codecs=opus','audio/mp4','audio/ogg;codecs=opus'].find(t=>MediaRecorder.isTypeSupported(t));
      const rec = new MediaRecorder(media, mime ? {mimeType:mime}:undefined); recorder.current = rec;
      const chunks = []; let size = 0;
      rec.ondataavailable = e => {if(e.data.size) {chunks.push(e.data); size += e.data.size; if(size > 4*1024*1024 && rec.state === 'recording') rec.stop();}};
      rec.onstop = async () => {
        media.getTracks().forEach(t=>t.stop());
        if (token !== generation.current) return;
        setRecording(false); setCaption('正在识别你刚才说的话…');
        if (size > 4*1024*1024) {setError('录音超过 4 MB，请缩短后重试'); return;}
        const blob = new Blob(chunks, {type:rec.mimeType});
        if (blob.size < 100) {setError('录音太短，请重试'); return;}
        const reader = new FileReader();
        reader.onloadend = () => {if(token === generation.current) send({type:'audio', audio:String(reader.result).split(',')[1], mime:rec.mimeType});};
        reader.readAsDataURL(blob);
      };
      rec.start(250); setRecording(true); setCaption('正在录音，说完后点击「发送语音」');
      recordTimer.current = setTimeout(()=>{if(rec.state === 'recording') rec.stop();}, 20000);
    } catch (e) {setError(e.name === 'NotAllowedError' ? '麦克风权限被拒绝，请在浏览器地址栏允许访问，或使用文字对话。' : e.message);}
  }
  const clock = `${String(Math.floor(seconds/60)).padStart(2,'0')}:${String(seconds%60).padStart(2,'0')}`;
  return <div className="shell">
    <header className="app-header"><a className="brand" href="/">✦ <span>AI 实时语音对话</span></a><span className="header-caption">智能客服体验</span></header>
    <main>
      {!window.isSecureContext && <section className="certificate-notice" aria-label="平板录音设置">
        <div><strong>在平板上录音？请先安装证书</strong><p>当前为 HTTP 访问，麦克风暂不可用。文字对话可以正常使用。</p></div>
        <a className="certificate-download" href="/voice-link-ca.cer" download="voice-link-ca.cer">下载 CA 证书 ↓</a>
        <details><summary>下载后如何使用？</summary><ol><li>在平板设置中搜索“安装证书”，选择“CA 证书”，安装下载的 voice-link-ca.cer。</li><li>电脑停止当前前端，在 frontend 目录运行 npm run dev:https，后台保持运行。</li><li>然后打开 <a href={`https://${location.host}/`}>HTTPS 语音页面</a>，允许麦克风权限。</li></ol><p>证书需要在系统设置中手动安装。安装后设备会信任本项目 CA 签发的证书，测试结束可移除。</p></details>
      </section>}

      <div className="workspace">
        <section className={'session-panel '+(active?'in-call':'')}>
          <div className="card-top"><span>实时对话</span><span className={'connection '+(active?'on':'')}>● {labels[state]} {active && clock}</span></div>
          <div className="agent-scene"><div className={'orb-wrap '+(active?'alive':'')}><div className="orbit"/><div className="orb"><span>✦</span></div><div className="orb-tag">AI</div></div><h1>小声 · 智能客服</h1><p>随时开口，自然交流</p><div className={'wave '+(recording || state==='speaking'?'moving':'')}>{Array.from({length:15},(_,i)=><i key={i} style={{height:`${8+Math.sin(i*1.7)**2*22}px`,animationDelay:`${i*0.06}s`}}/>)}</div><div className="caption" aria-live="polite">{caption}</div></div>
      <section className="chat-card"><div className="card-top"><span>对话记录 <small>LIVE TRANSCRIPT</small></span><span className="count">{messages.filter(m=>m.role==='user').length} 轮</span></div><div className="messages" role="log" aria-live="polite">{!messages.length ? <div className="empty"><span>☏</span><h3>好对话，从一句你好开始</h3><p>接通后，你们的对话会显示在这里。<br/>支持语音，也可以直接输入文字。</p><div className="suggestions">{['你好，介绍一下你的服务','我想咨询一个问题'].map(t=><button key={t} disabled={!active} onClick={()=>send({type:'text',text:t})}>{t} ↗</button>)}</div></div> : messages.map((m,i)=><div className={'message '+m.role} key={i}><div className="message-name">{m.role==='user'?'你':'✦ 小声'}</div><div className="bubble">{m.text || '正在准备回复…'}{m.pending&&<span className="cursor">▍</span>}</div></div>)}<div ref={end}/></div><form onSubmit={e=>{e.preventDefault();if(draft.trim()){send({type:'text',text:draft.trim()});setDraft('');}}}><input aria-label="输入消息" placeholder={active?'输入消息，按 Enter 发送…':'接通后，即可发送消息'} value={draft} maxLength={2000} disabled={!active || recording || busy.current} onChange={e=>setDraft(e.target.value)}/><button aria-label="发送消息" disabled={!active||!draft.trim()||recording||busy.current}>↑</button></form><div className="chat-foot">AI 生成内容，请结合实际情况确认</div></section>
<div className="call-actions"><button className={'round '+(muted?'muted':'')} onClick={()=>{silent.current=!muted;setMuted(!muted);if(!muted){stopPlayback();if(state==='speaking'){busy.current=false;setState('listening');}}}} aria-label={muted?'开启回复语音':'静音回复'} title="回复语音">{muted?'◌':'♫'}</button><button className={'call-button '+(active?'hangup':'')} disabled={state==='connecting'} onClick={active?hangup:dial}>☎ <span>{active?'挂断通话':state==='connecting'?'连接中…':'拨打客服'}</span></button><button className={'round '+(recording?'recording':'')} onClick={toggleRecord} disabled={!active || busy.current} aria-label={recording?'发送语音':'开始录音'} title={recording?'发送语音':'开始录音'}>●</button></div><p className="call-hint">{active ? (recording?'录音最长 20 秒 · 点击右侧按钮发送':'点击右侧录音按钮说话，说完再次点击发送') : '点击拨打，随时开启一段对话'}</p><div className="privacy">♧ 仅在主动录音时使用麦克风 · 挂断即释放设备</div>
        </section>
        <aside className="operation-area">
          <section className="info-box"><h2>AI 人设</h2><div className="persona"><span>✦</span><div><strong>小声</strong><p>通用智能客服</p></div></div><p>认真聆听你的问题，提供及时、清晰的回答。</p><span className="scene-tag">语音对话</span><span className="scene-tag">文字交流</span></section>
          <section className="info-box"><h2>对话设置</h2><label className="setting-row">回复语音<button className={'switch '+(!muted?'enabled':'')} role="switch" aria-checked={!muted} aria-label="回复语音" onClick={()=>{silent.current=!muted;setMuted(!muted);if(!muted){stopPlayback();if(state==='speaking'){busy.current=false;setState('listening');}}}}><span/></button></label><div className="setting-row">会话状态<span>{labels[state]}</span></div><div className="setting-row">通话时长<span>{clock}</span></div></section>
          <section className="info-box"><h2>服务状态</h2>      <div className="mode-list">{['asr','llm','tts'].map((key,i)=><span key={key}><i className={modes?.[key]==='live'?'live':''}/>{['语音识别','大模型','语音合成'][i]}<b>{modes ? modes[key]==='live'?'已接入':key==='tts'?'浏览器合成':'Mock 演示':'未连接'}</b></span>)}</div><p>演示模式中的语音识别返回固定样例，不代表真实识别结果。</p>
</section>
          <section className="info-box instructions"><h2>使用说明</h2><p>1. 点击下方按钮拨打客服</p><p>2. 点击麦克风开始录音</p><p>3. 说完再次点击发送语音</p><p>也可以直接输入文字进行对话。</p></section>
        </aside>
      </div>
      {error&&<div className="error" role="alert">{error}<button onClick={()=>setError('')} aria-label="关闭提示">×</button></div>}
    </main></div>;
}
createRoot(document.getElementById('root')).render(<App/>);
