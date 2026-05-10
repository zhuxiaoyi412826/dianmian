# 模拟面试官 Agent 网站集成指南

## 快速启动

```bash
# 在项目目录启动服务
cd /workspace/projects
python src/main.py -m http -p 5000
```

服务运行在 `http://localhost:5000`

---

## API 接口

### 1. OpenAI 兼容接口（推荐）

完全兼容 OpenAI Chat API，可直接替换你的 OpenAI 调用地址。

**接口**: `POST /v1/chat/completions`

**请求示例**:
```javascript
const response = await fetch('http://localhost:5000/v1/chat/completions', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer your-api-key'  // 可选
  },
  body: JSON.stringify({
    model: 'interview-assistant',
    messages: [
      { role: 'system', content: '你是一个专业的面试官' },
      { role: 'user', content: '我想面试Python后端开发岗位' }
    ],
    stream: true  // 流式输出
  })
});
```

### 2. 流式 SSE 接口

适合需要实时显示面试官回答的场景。

**接口**: `POST /stream_run`

**请求体**:
```json
{
  "messages": [
    {"type": "human", "content": "我想面试Python后端开发岗位"}
  ]
}
```

---

## 前端集成示例（HTML + JavaScript）

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>模拟面试助手</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
    .chat-container { border: 1px solid #ddd; border-radius: 8px; height: 500px; overflow-y: auto; padding: 20px; }
    .message { margin-bottom: 15px; padding: 10px 15px; border-radius: 8px; }
    .message.user { background: #e3f2fd; margin-left: 50px; }
    .message.assistant { background: #f5f5f5; margin-right: 50px; }
    .input-area { display: flex; margin-top: 20px; }
    .input-area textarea { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 8px; resize: none; }
    .input-area button { margin-left: 10px; padding: 10px 20px; background: #1976d2; color: white; border: none; border-radius: 8px; cursor: pointer; }
    .typing { color: #666; font-style: italic; }
  </style>
</head>
<body>
  <h1>🎯 模拟面试官</h1>
  <div id="chat" class="chat-container"></div>
  <div class="input-area">
    <textarea id="input" rows="3" placeholder="输入你的回答..."></textarea>
    <button onclick="sendMessage()">发送</button>
  </div>

  <script>
    const chat = document.getElementById('chat');
    const input = document.getElementById('input');
    const API_URL = 'http://localhost:5000/v1/chat/completions';

    function addMessage(content, role) {
      const div = document.createElement('div');
      div.className = `message ${role}`;
      div.textContent = content;
      chat.appendChild(div);
      chat.scrollTop = chat.scrollHeight;
    }

    function showTyping() {
      const div = document.createElement('div');
      div.id = 'typing';
      div.className = 'message assistant typing';
      div.textContent = '面试官正在思考...';
      chat.appendChild(div);
    }

    function removeTyping() {
      const typing = document.getElementById('typing');
      if (typing) typing.remove();
    }

    async function sendMessage() {
      const text = input.value.trim();
      if (!text) return;

      addMessage(text, 'user');
      input.value = '';
      showTyping();

      try {
        const response = await fetch(API_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            model: 'interview-assistant',
            messages: [{ role: 'user', content: text }],
            stream: true
          })
        });

        removeTyping();
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let answer = '';

        const div = document.createElement('div');
        div.className = 'message assistant';
        chat.appendChild(div);

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          
          const chunk = decoder.decode(value);
          answer += chunk;
          div.textContent = answer;
          chat.scrollTop = chat.scrollHeight;
        }
      } catch (error) {
        removeTyping();
        addMessage('抱歉，服务暂时不可用，请稍后重试。', 'assistant');
        console.error(error);
      }
    }

    // 回车发送
    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });

    // 初始欢迎消息
    addMessage('你好！我是你的模拟面试官。请告诉我你想面试的岗位，我就可以开始面试了。', 'assistant');
  </script>
</body>
</html>
```

---

## React 集成示例

```jsx
import { useState, useRef, useEffect } from 'react';

function InterviewAssistant() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: '你好！我是你的模拟面试官。请告诉我你想面试的岗位。' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:5000/v1/chat/completions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: 'interview-assistant',
          messages: [...messages, userMessage],
          stream: true
        })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantMessage = '';

      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        assistantMessage += decoder.decode(value);
        setMessages(prev => {
          const updated = [...prev];
          updated[updated.length - 1] = { role: 'assistant', content: assistantMessage };
          return updated;
        });
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <div className="border rounded-lg h-96 overflow-y-auto p-4 mb-4">
        {messages.map((msg, i) => (
          <div key={i} className={`mb-3 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
            <span className={`inline-block p-3 rounded-lg ${
              msg.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200'
            }`}>
              {msg.content}
            </span>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <div className="flex gap-2">
        <textarea
          className="flex-1 border rounded-lg p-2"
          rows={2}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), sendMessage())}
          placeholder="输入你的回答..."
        />
        <button 
          onClick={sendMessage}
          disabled={loading}
          className="bg-blue-500 text-white px-6 rounded-lg disabled:opacity-50"
        >
          {loading ? '发送中...' : '发送'}
        </button>
      </div>
    </div>
  );
}

export default InterviewAssistant;
```

---

## Vue 3 集成示例

```vue
<template>
  <div class="max-w-2xl mx-auto p-4">
    <div class="border rounded-lg h-96 overflow-y-auto p-4 mb-4">
      <div v-for="(msg, i) in messages" :key="i" class="mb-3" :class="msg.role === 'user' ? 'text-right' : 'text-left'">
        <span 
          class="inline-block p-3 rounded-lg"
          :class="msg.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200'"
        >
          {{ msg.content }}
        </span>
      </div>
      <div ref="messagesEnd"></div>
    </div>
    <div class="flex gap-2">
      <textarea
        v-model="input"
        class="flex-1 border rounded-lg p-2"
        rows="2"
        @keyup.enter.exact="sendMessage"
        placeholder="输入你的回答..."
      ></textarea>
      <button 
        @click="sendMessage"
        :disabled="loading"
        class="bg-blue-500 text-white px-6 rounded-lg disabled:opacity-50"
      >
        {{ loading ? '发送中...' : '发送' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue';

const messages = ref([
  { role: 'assistant', content: '你好！我是你的模拟面试官。请告诉我你想面试的岗位。' }
]);
const input = ref('');
const loading = ref(false);
const messagesEnd = ref(null);

const scrollToBottom = () => {
  nextTick(() => {
    messagesEnd.value?.scrollIntoView({ behavior: 'smooth' });
  });
};

const sendMessage = async () => {
  if (!input.value.trim() || loading.value) return;

  const userMessage = { role: 'user', content: input.value };
  messages.value.push(userMessage);
  input.value = '';
  loading.value = true;

  try {
    const response = await fetch('http://localhost:5000/v1/chat/completions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'interview-assistant',
        messages: messages.value,
        stream: true
      })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let assistantMessage = '';

    messages.value.push({ role: 'assistant', content: '' });

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      assistantMessage += decoder.decode(value);
      messages.value[messages.value.length - 1].content = assistantMessage;
      scrollToBottom();
    }
  } catch (error) {
    console.error('Error:', error);
  } finally {
    loading.value = false;
  }
};
</script>
```

---

## 多轮对话支持

如果需要支持多轮面试对话（用户中途刷新页面不丢上下文），需要传递 `thread_id`：

```javascript
// 生成或获取 thread_id
let threadId = localStorage.getItem('interview_thread_id');
if (!threadId) {
  threadId = 'interview_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  localStorage.setItem('interview_thread_id', threadId);
}

// 在每次请求中传递 thread_id
await fetch('http://localhost:5000/run', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    messages: [{ type: 'human', content: input }],
    configurable: { thread_id: threadId }
  })
});
```

---

## 部署注意事项

### 1. CORS 跨域配置

如果前端和后端不在同一域名，需要配置 CORS：

```python
# 在 main.py 中添加 CORS 中间件
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-website.com"],  # 你的网站域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Docker 部署

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "src/main.py", "-m", "http", "-p", "5000"]
```

### 3. Nginx 反向代理

```nginx
server {
    listen 80;
    server_name interview.your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        
        # SSE 流式响应支持
        proxy_buffering off;
        proxy_cache off;
    }
}
```

---

## 接口文档

- **健康检查**: `GET /health`
- **流式调用**: `POST /stream_run`
- **非流式调用**: `POST /run`
- **取消任务**: `POST /cancel/{run_id}`
- **OpenAI兼容**: `POST /v1/chat/completions`
