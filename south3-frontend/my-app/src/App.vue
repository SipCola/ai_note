<template>
  <div class="app">
    <!-- ==================== 侧边栏：对话历史 ==================== -->
    <aside class="sidebar" :class="{ open: sidebarOpen }">
      <div class="sidebar-head">
        <button class="new-chat-btn" @click="newChat">＋ 新对话</button>
      </div>
      <div class="conv-list">
        <div v-if="!conversations.length" class="conv-empty">暂无对话</div>
        <div
          v-for="c in conversations"
          :key="c.id"
          class="conv-item"
          :class="{ active: c.id === activeId }"
          @click="switchConversation(c.id)"
        >
          <span class="conv-title">{{ c.title || '新对话' }}</span>
          <button class="conv-del" title="删除" @click.stop="deleteConversation(c.id)">×</button>
        </div>
      </div>
    </aside>
    <div v-if="sidebarOpen" class="sidebar-mask" @click="sidebarOpen = false"></div>

    <!-- ==================== 主区 ==================== -->
    <div class="main">
      <header class="nav">
        <div class="nav-left">
          <button class="icon-btn hamburger" title="历史对话" @click="sidebarOpen = !sidebarOpen">☰</button>
          <span class="title">🤖 AI 助手</span>
        </div>
        <div class="nav-right">
          <button class="icon-btn" title="切换主题" @click="toggleTheme">
            {{ theme === 'dark' ? '☀️' : '🌙' }}
          </button>
          <button
            class="icon-btn"
            title="导出当前对话"
            :disabled="!currentConvo || !currentConvo.messages.length"
            @click="exportChat"
          >
            ⬇️
          </button>
          <button class="avatar-btn" title="设置我的头像" @click="avatarPickerOpen = true">
            {{ userAvatar }}
          </button>
        </div>
      </header>

      <div ref="chatEl" class="chat" @click="onChatClick">
        <div v-if="!currentMessages.length" class="empty">
          <div class="empty-icon">💬</div>
          <p>问点什么吧～</p>
        </div>

        <div v-for="(m, i) in currentMessages" :key="i" class="row" :class="m.role">
          <div class="avatar">{{ m.role === 'user' ? userAvatar : '🤖' }}</div>
          <div class="bubble">
            <span v-if="m.role === 'user'" class="plain">{{ m.content }}</span>

            <template v-else>
              <span v-if="!m.content" class="thinking">思考中…</span>
              <template v-else>
                <div class="md" v-html="render(m.content)"></div>
                <span v-if="typing && i === currentMessages.length - 1" class="cursor"></span>
              </template>
            </template>
          </div>
        </div>
      </div>

      <div class="input-bar">
        <textarea
          v-model="text"
          rows="1"
          placeholder="Enter 发送，Shift + Enter 换行"
          :disabled="loading"
          @keydown.enter.exact.prevent="onEnter"
        ></textarea>
        <button class="send" :disabled="loading || !text.trim()" @click="send">
          {{ loading ? '生成中' : '发送' }}
        </button>
      </div>
    </div>

    <!-- ==================== 头像选择弹窗 ==================== -->
    <div v-if="avatarPickerOpen" class="modal-mask" @click.self="avatarPickerOpen = false">
      <div class="modal">
        <div class="modal-title">选择你的头像</div>
        <div class="avatar-grid">
          <button
            v-for="e in AVATARS"
            :key="e"
            class="avatar-opt"
            :class="{ active: e === userAvatar }"
            @click="pickAvatar(e)"
          >{{ e }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
// 依赖：npm install marked marked-highlight highlight.js
import { marked } from 'marked'
import { markedHighlight } from 'marked-highlight'
import hljs from 'highlight.js'
// ?inline 让 Vite 把 CSS 文件内容作为字符串返回，而不是自动注入 <style>。
// 这样可以根据当前主题动态切换 highlight.js 的配色。
import hljsLightCss from 'highlight.js/styles/github.css?inline'
import hljsDarkCss from 'highlight.js/styles/github-dark.css?inline'

/* ---------- 配置 ---------- */
const API_URL = 'https://api.deepseek.com/chat/completions'
const API_KEY = 'sk-765903c8a50d44f6a6851466a6807667'
const MODEL = 'deepseek-flash'
const TYPE_SPEED = 25
const AVATARS = ['🧑', '👩', '👨', '🧔', '👱', '🧓', '👧', '👦', '😎', '🤓', '🐱', '🐶', '🦊', '🐼', '🐨', '🦁']

/* ---------- Markdown + 高亮 ---------- */
marked.use(markedHighlight({
  langPrefix: 'hljs language-',
  highlight(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try { return hljs.highlight(code, { language: lang }).value } catch {}
    }
    return hljs.highlightAuto(code).value
  }
}))
marked.setOptions({ gfm: true, breaks: true })

/* ============================================================
 * 一、对话历史状态
 * conversations: [{ id, title, messages: [], createdAt }]
 * ========================================================== */
const conversations = ref(loadConversations())
const activeId = ref(localStorage.getItem('active-conv-id') || null)

// 首次使用 / 旧版数据迁移 / 当前 id 失效时，保证至少有一个对话
;(function bootstrap() {
  // 从旧版单对话数据迁移（旧版 localStorage 键是 chat-messages）
  const legacy = localStorage.getItem('chat-messages')
  if (legacy && !conversations.value.length) {
    try {
      const msgs = JSON.parse(legacy)
      if (Array.isArray(msgs) && msgs.length) {
        conversations.value = [{
          id: genId(),
          title: msgs.find(m => m.role === 'user')?.content?.slice(0, 20) || '旧对话',
          messages: msgs,
          createdAt: Date.now()
        }]
      }
      localStorage.removeItem('chat-messages')
    } catch {}
  }

  if (!conversations.value.length) {
    createConversation()
  } else if (!conversations.value.find(c => c.id === activeId.value)) {
    activeId.value = conversations.value[0].id
  }
})()

const currentConvo = computed(() => conversations.value.find(c => c.id === activeId.value) || null)
const currentMessages = computed(() => currentConvo.value?.messages || [])

function loadConversations() {
  try {
    const v = JSON.parse(localStorage.getItem('conversations'))
    return Array.isArray(v) ? v : []
  } catch { return [] }
}
function genId() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 6)
}
function createConversation() {
  const c = { id: genId(), title: '', messages: [], createdAt: Date.now() }
  conversations.value.unshift(c) // 最新的排最前
  activeId.value = c.id
  return c
}

// 持久化（防抖 300ms，流式输出时不会频繁写盘）
let saveTimer
watch(conversations, v => {
  clearTimeout(saveTimer)
  saveTimer = setTimeout(() => {
    localStorage.setItem('conversations', JSON.stringify(v))
  }, 300)
}, { deep: true })
watch(activeId, v => { if (v) localStorage.setItem('active-conv-id', v) })

/* ============================================================
 * 二、主题切换
 * CSS 变量定义在 :root[data-theme] 上，切换时只需改 html 属性。
 * highlight.js 的样式通过 ?inline 动态替换 <style> 内容。
 * ========================================================== */
const theme = ref(localStorage.getItem('theme') || 'light')

function applyHljsTheme(dark) {
  let el = document.getElementById('hljs-theme-style')
  if (!el) {
    el = document.createElement('style')
    el.id = 'hljs-theme-style'
    document.head.appendChild(el)
  }
  el.textContent = dark ? hljsDarkCss : hljsLightCss
}
function applyTheme(t) {
  document.documentElement.setAttribute('data-theme', t)
  applyHljsTheme(t === 'dark')
}
watch(theme, t => {
  localStorage.setItem('theme', t)
  applyTheme(t)
})
function toggleTheme() { theme.value = theme.value === 'dark' ? 'light' : 'dark' }
applyTheme(theme.value) // 首屏立即生效，避免闪烁

/* ============================================================
 * 三、头像自定义
 * ========================================================== */
const userAvatar = ref(localStorage.getItem('user-avatar') || '🧑')
const avatarPickerOpen = ref(false)
function pickAvatar(e) {
  userAvatar.value = e
  localStorage.setItem('user-avatar', e)
  avatarPickerOpen.value = false
}

/* ============================================================
 * 四、其它 UI 状态
 * ========================================================== */
const loading = ref(false)
const typing = ref(false)
const text = ref('')
const chatEl = ref(null)
const sidebarOpen = ref(false)

/* ============================================================
 * 五、渲染（Markdown + 代码块复制按钮）
 * ========================================================== */
function escHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))
}
function render(s) {
  if (!s) return ''
  const tpl = document.createElement('template')
  tpl.innerHTML = marked.parse(s)
  tpl.content.querySelectorAll('pre').forEach(pre => {
    if (pre.parentElement?.classList.contains('code-block')) return
    const code = pre.querySelector('code')
    const m = code?.className.match(/language-([\w+#.-]+)/)
    const lang = m ? m[1] : 'text'
    const wrap = document.createElement('div')
    wrap.className = 'code-block'
    wrap.innerHTML =
      `<div class="code-header"><span class="code-lang">${escHtml(lang)}</span>` +
      `<button class="copy-btn" type="button">复制</button></div>`
    pre.replaceWith(wrap)
    wrap.appendChild(pre)
  })
  return tpl.innerHTML
}
function scroll() {
  nextTick(() => { if (chatEl.value) chatEl.value.scrollTop = chatEl.value.scrollHeight })
}

/* ============================================================
 * 六、复制代码（事件委托）
 * ========================================================== */
async function copyText(t) {
  try {
    await navigator.clipboard.writeText(t)
    return true
  } catch {
    const ta = document.createElement('textarea')
    ta.value = t
    ta.style.cssText = 'position:fixed;left:-9999px;top:0;opacity:0'
    document.body.appendChild(ta)
    ta.select()
    let ok = false
    try { ok = document.execCommand('copy') } catch {}
    document.body.removeChild(ta)
    return ok
  }
}
async function onChatClick(e) {
  const btn = e.target.closest?.('.copy-btn')
  if (!btn) return
  const codeEl = btn.closest('.code-block')?.querySelector('pre code')
  if (!codeEl) return
  const ok = await copyText(codeEl.textContent || '')
  const old = btn.textContent
  btn.textContent = ok ? '已复制' : '复制失败'
  btn.classList.add('copied')
  setTimeout(() => {
    btn.textContent = old
    btn.classList.remove('copied')
  }, 1500)
}

/* ============================================================
 * 七、流式请求（SSE）
 * ========================================================== */
async function stream(history, onDelta) {
  const res = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${API_KEY}` },
    body: JSON.stringify({ model: MODEL, messages: history, stream: true })
  })
  if (!res.ok) throw new Error(`请求失败：${res.status}`)

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buf = ''
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buf += decoder.decode(value, { stream: true })
    const lines = buf.split('\n')
    buf = lines.pop() || ''
    for (const line of lines) {
      const s = line.trim()
      if (!s.startsWith('data:')) continue
      const p = s.slice(5).trim()
      if (!p || p === '[DONE]') continue
      try {
        const c = JSON.parse(p).choices?.[0]?.delta?.content
        if (c) onDelta(c)
      } catch {}
    }
  }
}

/* ============================================================
 * 八、发送（关键：在开始时锁定 convo 引用，
 *     后续所有异步写入都针对这个引用，不受切换对话影响）
 * ========================================================== */
async function send() {
  const t = text.value.trim()
  if (!t || loading.value) return

  // 极端兜底：没有任何对话就自动建一个
  if (!currentConvo.value) createConversation()
  const convo = currentConvo.value // ← 锁定

  text.value = ''
  convo.messages.push({ role: 'user', content: t })

  // 首条消息自动生成标题
  if (!convo.title) {
    convo.title = t.length > 20 ? t.slice(0, 20) + '…' : t
  }
  scroll()

  // 构建发给 API 的历史（在 push 空 AI 占位之前）
  const history = convo.messages.map(m => ({ role: m.role, content: m.content }))

  convo.messages.push({ role: 'assistant', content: '' })
  const idx = convo.messages.length - 1
  loading.value = true
  typing.value = true

  // 逐字队列
  let queue = ''
  let finished = false
  const typer = setInterval(() => {
    const msg = convo.messages[idx]
    if (!msg) { clearInterval(typer); typing.value = false; return }
    if (queue.length) {
      msg.content += queue[0]
      queue = queue.slice(1)
      if (convo.id === activeId.value) scroll()
    } else if (finished) {
      clearInterval(typer)
      typing.value = false
    }
  }, TYPE_SPEED)

  try {
    await stream(history, d => { queue += d })
  } catch (e) {
    convo.messages[idx].content = `❌ 出错了：${e.message}`
    queue = ''
  } finally {
    finished = true
    loading.value = false
    if (!convo.messages[idx].content) convo.messages[idx].content = '（无回复）'
  }
}
function onEnter(e) { if (!e.isComposing) send() }

/* ============================================================
 * 九、对话操作
 * ========================================================== */
function newChat() {
  if (loading.value) return
  // 当前已是空对话就不重复创建，只清空输入框
  if (currentConvo.value && !currentConvo.value.messages.length) {
    text.value = ''
  } else {
    createConversation()
    text.value = ''
  }
  sidebarOpen.value = false
  scroll()
}
function switchConversation(id) {
  if (loading.value || id === activeId.value) { sidebarOpen.value = false; return }
  activeId.value = id
  sidebarOpen.value = false
  scroll()
}
function deleteConversation(id) {
  if (loading.value) return
  const idx = conversations.value.findIndex(c => c.id === id)
  if (idx < 0) return
  conversations.value.splice(idx, 1)
  if (activeId.value === id) {
    if (conversations.value.length) {
      activeId.value = conversations.value[0].id
    } else {
      createConversation()
    }
  }
}

/* ============================================================
 * 十、导出聊天记录
 * 生成纯文本 .txt，通过 Blob + <a download> 触发下载。
 * 文件名里过滤掉 Windows 非法字符。
 * ========================================================== */
function exportChat() {
  const convo = currentConvo.value
  if (!convo || !convo.messages.length) return

  const now = new Date()
  const pad = n => String(n).padStart(2, '0')
  const ts = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ` +
             `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`

  const lines = []
  lines.push('AI 对话记录')
  lines.push(`标题：${convo.title || '新对话'}`)
  lines.push(`导出时间：${ts}`)
  lines.push(`消息数：${convo.messages.length}`)
  lines.push('')
  for (const m of convo.messages) {
    lines.push('─'.repeat(50))
    lines.push(m.role === 'user' ? '[用户]' : '[AI]')
    lines.push(m.content)
    lines.push('')
  }

  const blob = new Blob([lines.join('\n')], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  const safeTitle = (convo.title || '对话').replace(/[\\/:*?"<>|]/g, '_').slice(0, 30)
  a.href = url
  a.download = `${safeTitle}_${Date.now()}.txt`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

onMounted(scroll)
</script>

<style>
/* ==================== 主题变量 ==================== */
:root {
  --bg-app: #f0f2f5;
  --bg-panel: #ffffff;
  --bg-input: #f7f7f7;
  --bg-hover: #f3f4f6;
  --bg-active: #eef4ff;
  --text-main: #333333;
  --text-secondary: #666666;
  --text-muted: #999999;
  --border: #e8e8e8;
  --border-soft: #e5e7eb;
  --bubble-ai: #ffffff;
  --bubble-user-bg: #95ec69;
  --bubble-user-text: #1a1a1a;
  --primary: #1677ff;
  --primary-hover: #0f5fd6;
  --code-bg: #f6f8fa;
  --code-header: #eef1f4;
  --mask: rgba(0, 0, 0, 0.4);
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.08);
  --shadow-lg: 0 0 20px rgba(0, 0, 0, 0.1);
  --scrollbar: #cccccc;
  --scrollbar-hover: #aaaaaa;
}

:root[data-theme="dark"] {
  --bg-app: #0d1117;
  --bg-panel: #161b22;
  --bg-input: #21262d;
  --bg-hover: #30363d;
  --bg-active: #1f2937;
  --text-main: #e6edf3;
  --text-secondary: #c9d1d9;
  --text-muted: #8b949e;
  --border: #30363d;
  --border-soft: #30363d;
  --bubble-ai: #161b22;
  --bubble-user-bg: #238636;
  --bubble-user-text: #ffffff;
  --primary: #58a6ff;
  --primary-hover: #79b8ff;
  --code-bg: #0d1117;
  --code-header: #21262d;
  --mask: rgba(0, 0, 0, 0.6);
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.5);
  --shadow-lg: 0 0 20px rgba(0, 0, 0, 0.5);
  --scrollbar: #30363d;
  --scrollbar-hover: #484f58;
}

* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
  background: var(--bg-app);
  color: var(--text-main);
  transition: background .25s, color .25s;
}

/* ==================== 整体布局 ==================== */
.app {
  display: flex;
  height: 100vh;
  max-width: 1200px;
  margin: 0 auto;
  background: var(--bg-app);
  box-shadow: var(--shadow-lg);
}

/* ==================== 侧边栏 ==================== */
.sidebar {
  width: 240px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background: var(--bg-panel);
  border-right: 1px solid var(--border);
  transition: background .25s, border-color .25s;
}
.sidebar-head { padding: 14px; border-bottom: 1px solid var(--border); }
.new-chat-btn {
  width: 100%;
  padding: 9px 0;
  font-size: 14px;
  font-weight: 500;
  color: var(--primary);
  background: transparent;
  border: 1px solid var(--primary);
  border-radius: 8px;
  cursor: pointer;
  transition: all .2s;
}
.new-chat-btn:hover { background: var(--primary); color: #fff; }

.conv-list { flex: 1; overflow-y: auto; padding: 8px; }
.conv-list::-webkit-scrollbar { width: 4px; }
.conv-list::-webkit-scrollbar-thumb { background: var(--scrollbar); border-radius: 2px; }
.conv-empty { padding: 20px 10px; text-align: center; font-size: 13px; color: var(--text-muted); }

.conv-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
  padding: 9px 10px;
  margin-bottom: 4px;
  font-size: 13px;
  color: var(--text-secondary);
  border-radius: 7px;
  cursor: pointer;
  transition: background .15s;
}
.conv-item:hover { background: var(--bg-hover); }
.conv-item.active { background: var(--bg-active); color: var(--primary); font-weight: 500; }

.conv-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.conv-del {
  width: 20px;
  height: 20px;
  line-height: 1;
  font-size: 16px;
  color: var(--text-muted);
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  opacity: 0;
  transition: all .15s;
}
.conv-item:hover .conv-del { opacity: 1; }
.conv-del:hover { background: rgba(220, 38, 38, 0.15); color: #dc2626; }

.sidebar-mask { display: none; }

/* ==================== 主区 ==================== */
.main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

/* 顶栏 */
.nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--bg-panel);
  border-bottom: 1px solid var(--border);
  transition: background .25s, border-color .25s;
}
.nav-left, .nav-right { display: flex; align-items: center; gap: 8px; }
.title { font-size: 16px; font-weight: 600; color: var(--text-main); }

.icon-btn {
  width: 34px;
  height: 34px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  color: var(--text-main);
  background: transparent;
  border: 1px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all .15s;
}
.icon-btn:hover:not(:disabled) { background: var(--bg-hover); }
.icon-btn:disabled { opacity: .35; cursor: not-allowed; }

.avatar-btn {
  width: 34px;
  height: 34px;
  font-size: 18px;
  background: var(--bg-hover);
  border: 1px solid var(--border-soft);
  border-radius: 50%;
  cursor: pointer;
  transition: all .15s;
}
.avatar-btn:hover { transform: scale(1.06); }

/* 聊天区 */
.chat { flex: 1; overflow-y: auto; padding: 18px; }
.chat::-webkit-scrollbar { width: 6px; }
.chat::-webkit-scrollbar-thumb { background: var(--scrollbar); border-radius: 3px; }
.chat::-webkit-scrollbar-thumb:hover { background: var(--scrollbar-hover); }

.empty { text-align: center; color: var(--text-muted); margin-top: 25vh; }
.empty-icon { font-size: 42px; margin-bottom: 10px; }

/* 消息 */
.row { display: flex; gap: 10px; margin-bottom: 16px; align-items: flex-start; }
.row.user { flex-direction: row-reverse; }
.avatar {
  width: 34px; height: 34px;
  border-radius: 50%;
  background: var(--bg-panel);
  display: flex; align-items: center; justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
  box-shadow: var(--shadow-sm);
}
.bubble {
  max-width: 74%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 15px;
  line-height: 1.65;
  word-break: break-word;
  background: var(--bubble-ai);
  color: var(--text-main);
  box-shadow: var(--shadow-sm);
}
.row.user .bubble { background: var(--bubble-user-bg); color: var(--bubble-user-text); }
.plain { white-space: pre-wrap; }
.thinking { color: var(--text-muted); font-size: 14px; }

/* 流式光标 */
.cursor {
  display: inline-block;
  width: 2px; height: 15px;
  margin-left: 2px;
  background: var(--primary);
  vertical-align: -2px;
  animation: blink 1s steps(1) infinite;
}
@keyframes blink { 50% { opacity: 0; } }

/* Markdown */
.md > *:first-child { margin-top: 0; }
.md > *:last-child { margin-bottom: 0; }
.md p { margin: 0 0 8px; }
.md h1, .md h2, .md h3, .md h4 { font-size: 16px; margin: 12px 0 6px; font-weight: 600; }
.md ul, .md ol { padding-left: 22px; margin: 6px 0; }
.md li { margin: 2px 0; }
.md code {
  font-family: ui-monospace, Menlo, Consolas, monospace;
  font-size: 13px;
  background: rgba(127, 127, 127, .15);
  padding: 1px 5px;
  border-radius: 4px;
}
.md blockquote {
  border-left: 3px solid var(--border);
  padding-left: 10px;
  color: var(--text-secondary);
  margin: 8px 0;
}
.md table { border-collapse: collapse; margin: 8px 0; font-size: 14px; }
.md th, .md td { border: 1px solid var(--border); padding: 5px 10px; }
.md th { background: var(--bg-hover); }
.md a { color: var(--primary); text-decoration: none; }

/* 代码块 */
.md .code-block {
  margin: 8px 0;
  border-radius: 8px;
  overflow: hidden;
  background: var(--code-bg);
  border: 1px solid var(--border-soft);
}
.md .code-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 12px;
  background: var(--code-header);
  border-bottom: 1px solid var(--border-soft);
  font-size: 12px;
  color: var(--text-secondary);
}
.md .code-lang {
  font-family: ui-monospace, Menlo, Consolas, monospace;
  text-transform: uppercase;
  letter-spacing: .5px;
}
.md .copy-btn {
  font-size: 12px;
  color: var(--text-secondary);
  background: var(--bg-panel);
  border: 1px solid var(--border-soft);
  border-radius: 5px;
  padding: 2px 10px;
  cursor: pointer;
  transition: all .15s;
}
.md .copy-btn:hover { color: var(--primary); border-color: var(--primary); }
.md .copy-btn.copied { color: #16a34a; border-color: #16a34a; }

.md .code-block pre {
  margin: 0;
  padding: 10px 12px;
  background: transparent;
  border-radius: 0;
  overflow-x: auto;
}
.md .code-block pre code,
.md .code-block pre code.hljs {
  background: transparent;
  padding: 0;
  font-size: 13px;
  line-height: 1.55;
}

/* 输入栏 */
.input-bar {
  display: flex;
  gap: 10px;
  padding: 12px 16px;
  background: var(--bg-panel);
  border-top: 1px solid var(--border);
  transition: background .25s, border-color .25s;
}
.input-bar textarea {
  flex: 1;
  height: 44px;
  padding: 11px 14px;
  font-size: 15px;
  font-family: inherit;
  line-height: 1.4;
  color: var(--text-main);
  background: var(--bg-input);
  border: 1px solid transparent;
  border-radius: 10px;
  outline: none;
  resize: none;
  transition: all .2s;
}
.input-bar textarea:focus { background: var(--bg-panel); border-color: var(--primary); }
.input-bar textarea:disabled { opacity: .6; }
.input-bar textarea::placeholder { color: var(--text-muted); }

.send {
  width: 74px;
  height: 44px;
  font-size: 15px;
  color: #fff;
  background: var(--primary);
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: background .2s, opacity .2s;
}
.send:hover:not(:disabled) { background: var(--primary-hover); }
.send:disabled { opacity: .5; cursor: not-allowed; }

/* ==================== 头像选择弹窗 ==================== */
.modal-mask {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--mask);
  z-index: 200;
  animation: fadeIn .18s;
}
@keyframes fadeIn { from { opacity: 0; } }
.modal {
  width: min(90vw, 360px);
  padding: 20px;
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: 14px;
  box-shadow: var(--shadow-lg);
}
.modal-title { font-size: 15px; font-weight: 600; color: var(--text-main); margin-bottom: 14px; }
.avatar-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}
.avatar-opt {
  aspect-ratio: 1;
  font-size: 24px;
  background: var(--bg-input);
  border: 2px solid transparent;
  border-radius: 10px;
  cursor: pointer;
  transition: all .15s;
}
.avatar-opt:hover { background: var(--bg-hover); }
.avatar-opt.active { border-color: var(--primary); background: var(--bg-active); }

/* ==================== 移动端 ==================== */
@media (max-width: 800px) {
  .app { box-shadow: none; }

  .sidebar {
    position: fixed;
    top: 0; left: 0; bottom: 0;
    z-index: 150;
    width: 260px;
    transform: translateX(-100%);
    transition: transform .25s ease;
    box-shadow: 2px 0 12px rgba(0, 0, 0, .2);
  }
  .sidebar.open { transform: translateX(0); }

  .sidebar-mask {
    display: block;
    position: fixed;
    inset: 0;
    background: var(--mask);
    z-index: 140;
  }

  .bubble { max-width: 82%; }
}
</style>