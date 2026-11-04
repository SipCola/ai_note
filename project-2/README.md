# 声连 · 实时语音智能客服

React 前端 + 一个 Python FastAPI 后台（内含业务与 AI 模块）。原有 `rtc_basic/` 保留作参考，新项目不需要购买 RTC 服务。

## 启动（Windows PowerShell）

在项目根目录安装一次依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
Copy-Item .env.example .env
cd frontend
npm install
```

打开两个终端，分别执行（均从项目根目录开始）：

```powershell
# 终端 1：统一后台（业务 + ASR / LLM / TTS）
.\.venv\Scripts\python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload --ws-max-size 6000000
```

```powershell
# 终端 2：React 前端
cd frontend
npm run dev
```

后台只需一个终端、一个进程，使用 8000 端口；不再需要启动 8001。停止时在对应终端按 Ctrl+C。

访问 http://localhost:5173 。支持 Node.js 20.19+ / 22.12+，Python 3.11+。无需激活虚拟环境，也无需更改 PowerShell 执行策略。

## 局域网访问

前端 `npm run dev` 已监听 `0.0.0.0:5173` 并固定端口；后台继续监听 `127.0.0.1:8000`，由前端代理转发。

同一局域网设备访问 http://10.253.255.121:5173 。`.env` 中已允许此地址的 WebSocket Origin。电脑 IP 变化后，请同步更新 `.env` 的 `ALLOWED_ORIGINS`，然后重启后台。

局域网 HTTP 支持文字对话；手机或其他设备的麦克风录音需要受设备信任的 HTTPS。防火墙需要允许 TCP 5173 入站，建议仅限专用网络和本地子网。

## 安卓 / HarmonyOS 平板录音（HTTPS）

已为当前电脑 `10.253.255.121` 生成本地开发 CA 和服务器证书，私钥存放在被 Git 忽略的 `.certs/`，仅公开 CA 证书放在 `frontend/public/voice-link-ca.cer`。这些文件不提交 Git，复制项目到其他机器时需重新签发。服务器证书有效期 180 天，IP 变化后需要重新签发。

局域网 HTTP 首页会自动显示证书下载提示和“下载 CA 证书”按钮，展开后可查看安装步骤；不会自动安装证书。

1. 保持前端使用 `npm run dev`，在平板访问 http://10.253.255.121:5173/voice-link-ca.cer 下载公开 CA 证书。
2. 在平板设置中搜索“安装证书”，选择“CA 证书”，安装下载的 `voice-link-ca.cer`。常见路径为“安全 → 更多安全设置 → 加密与凭据 → 安装证书 → CA 证书”；不同品牌名称可能不同。选择 CA，不要选择 Wi-Fi 或 VPN 用户证书。
3. 电脑上停止前端（Ctrl+C），然后在 `frontend` 目录运行 `npm run dev:https`。后台启动命令保持不变。
4. 平板打开 https://10.253.255.121:5173 ，允许麦克风后录音。若仍显示证书错误，应检查证书是否安装为 CA、设备日期和访问 IP；不要通过忽略证书错误代替安装信任。

安装此 CA 会让平板信任该 CA 签发的证书；仅安装本项目生成的证书，勿分享 `.certs/ca-key.pem` 和服务器私钥。测试完成后可在“受信任的凭据 / 用户凭据”中移除 VoiceLink Local Development CA。无需在电脑上安装证书即可供平板访问，但电脑浏览器通过 HTTPS 访问也需要信任该 CA。

## 使用

1. 点击「拨打客服」建立 WebSocket 会话。
2. 点击右侧圆形录音按钮并允许麦克风，说完再次点击发送；单句最长 20 秒。也可直接输入文字。
3. 后端完成 ASR → LLM → TTS，前端展示对话气泡、逐字字幕并播放语音。
4. 点击音符按钮可静音；点击「挂断通话」关闭连接、取消后台任务、停止播放并释放麦克风。

没有配置时可直接演示：ASR 返回 `.env` 中的固定样例（并非真实语音识别），LLM 返回演示回复，TTS 使用浏览器 speechSynthesis 中文语音。操作系统需要安装中文语音；没有可用声音时仍可查看文字。录音需要 localhost 或 HTTPS。

## 配置真实服务

复制 `.env.example` 为 `.env`，分别填写 ASR / LLM / TTS 的 `BASE_URL`、`API_KEY`、`MODEL`，例如服务地址包含 `/v1`。三项均填写时对应阶段切换到真实服务，可以分别混合使用。密钥只保存在 Python 后台，不发送到浏览器。修改配置后重启统一后台。旧 `.env` 中的 `AI_SERVICE_URL` 已不再使用，可以删除。

兼容接口：

- ASR：`POST {ASR_BASE_URL}/audio/transcriptions`，multipart 文件和 model，返回 `{ "text": "识别文本" }`。
- LLM：`POST {LLM_BASE_URL}/chat/completions`，messages 多轮上下文，读取 choices[0].message.content。
- TTS：`POST {TTS_BASE_URL}/audio/speech`，input/model/voice/response_format，返回 MP3 二进制。

其他厂商协议在 `backend/ai_service.py` 的适配层替换，不需要修改前端通信。未配置时使用 mock，已配置但服务报错时显示错误，不会悄悄回退为假结果。

## 目录与协议

- `frontend/`：React + Vite，开发代理转发 `/api` 和 `/ws`。
- `backend/main.py`：统一 FastAPI 入口，WebSocket 会话、20 条上下文、连接释放和任务取消。
- `backend/ai_service.py`：同进程内的 ASR / LLM / TTS 适配与环境配置，由业务层直接调用，无内部 HTTP 请求。
- `tests/`：mock、输入校验、真实适配调用、WebSocket 生命周期测试。

浏览器发送 `{type:"text", text}` 或 `{type:"audio", audio:"base64", mime}`；服务器返回 connected、status、transcript、delta、reply、error。reply 含 MP3 base64（真实 TTS）或 null（浏览器合成）。

当前采用**完整单句识别**，不是逐音频帧流式识别；WebSocket 实时传输事件，模型返回后分片展示文字，不宣称模型 token 流式生成。录音期间文字输入禁用，回复和播放期间不能发起下一轮，避免重叠。没有实现 RAG、知识库、多模态或音色克隆。

本地开发版后台仅绑定 loopback，前端开发服务器允许局域网访问，未实现登录鉴权、持久化、生产部署或公网限流。若部署到其他域名，应同时配置 HTTPS/WSS、反向代理和 ALLOWED_ORIGINS，并补充认证；不要直接公开未鉴权的 AI 接口。浏览器合成可能使用系统语音服务，真实模式下音频和文字发送到配置的供应商。

## 验证与构建

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
cd frontend
npm run build
```

统一接口文档：http://127.0.0.1:8000/docs。健康检查 `/api/health`，AI 接口 `/api/ai/health`、`/api/ai/turn`，WebSocket `/ws/call`。

接口格式参考：[FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)、[音频转写接口](https://developers.openai.com/api/reference/resources/audio/subresources/transcriptions/methods/create)。
`requirements.lock.txt` 记录了本次验证使用的完整 Python 版本；需要复现时可运行 `python -m pip install -r requirements.lock.txt`。前端与统一后台启动后，可在项目根目录运行 `.\.venv\Scripts\python tests/smoke_live.py` 验证实际前后端链路。
