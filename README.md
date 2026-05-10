# 🎯 模拟面试官 Agent

基于 DeepSeek AI 的专业面试练习助手，可以根据你输入的岗位 JD 进行连环追问，帮助你提升面试技巧。

## ✨ 功能特性

- 📋 **JD 分析**：智能分析岗位要求，提取关键技能点
- 🎙️ **连环追问**：针对你的回答进行深度追问，挖掘真实能力
- 💬 **多轮对话**：支持完整的面试对话记忆
- 🔄 **话题转换**：自然衔接不同面试话题
- 📊 **专业反馈**：给出改进建议和评价
- 🌐 **网站集成**：提供 HTTP API，可快速集成到你的网站

---

## 🚀 快速开始

### 本地运行

```bash
# 启动 HTTP 服务
bash scripts/http_run.sh -m http -p 5000

# 服务运行在 http://localhost:5000
```

### 测试 Agent

直接在浏览器打开 `examples/interview-demo.html`，或使用 curl 测试：

```bash
curl -X POST http://localhost:5000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "interview-assistant",
    "messages": [
      {"role": "user", "content": "我想面试Python后端开发，有3年经验"}
    ]
  }'
```

---

## 🖥️ 部署到服务器

### 方式一：一键部署脚本

```bash
# 1. 上传项目到服务器
scp -r ./projects root@your-server:/root/

# 2. SSH 登录服务器
ssh root@your-server

# 3. 进入项目目录
cd /root/projects

# 4. 安装依赖
pip install -r requirements.txt

# 5. 启动服务（后台运行）
nohup python src/main.py -m http -p 5000 > app.log 2>&1 &

# 6. 验证服务
curl http://localhost:5000/health
```

### 方式二：使用 systemd 服务（推荐）

创建服务文件 `/etc/systemd/system/interview-agent.service`：

```ini
[Unit]
Description=Interview Agent Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/projects
ExecStart=/root/projects/.venv/bin/python src/main.py -m http -p 5000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start interview-agent

# 设置开机自启
sudo systemctl enable interview-agent

# 查看状态
sudo systemctl status interview-agent
```

### 方式三：Docker 部署

#### 3.1 创建 Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目
COPY . .

# 暴露端口
EXPOSE 5000

# 启动服务
CMD ["python", "src/main.py", "-m", "http", "-p", "5000"]
```

#### 3.2 构建和运行

```bash
# 构建镜像
docker build -t interview-agent .

# 运行容器
docker run -d \
  --name interview-agent \
  -p 5000:5000 \
  interview-agent

# 查看日志
docker logs -f interview-agent
```

#### 3.3 Docker Compose（推荐）

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  interview-agent:
    build: .
    container_name: interview-agent
    ports:
      - "5000:5000"
    restart: unless-stopped
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - ./logs:/app/logs
```

启动：

```bash
docker-compose up -d
docker-compose logs -f
```

---

## 🌐 网站集成

### API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/v1/chat/completions` | POST | OpenAI 兼容接口（推荐） |
| `/stream_run` | POST | SSE 流式接口 |
| `/run` | POST | 非流式接口 |
| `/health` | GET | 健康检查 |

### 方式一：直接嵌入 HTML

将 `examples/interview-demo.html` 中的代码复制到你的网页即可。

核心调用示例：

```javascript
const response = await fetch('http://your-server:5000/v1/chat/completions', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    model: 'interview-assistant',
    messages: [
      { role: 'user', content: '我想面试Python后端开发' }
    ],
    stream: true  // 流式输出
  })
});

// 处理流式响应
const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  console.log(decoder.decode(value));  // 逐步输出
}
```

### 方式二：React 组件

```jsx
import { useState, useRef, useEffect } from 'react';

function InterviewChat({ apiUrl = 'http://localhost:5000/v1/chat/completions' }) {
  const [messages, setMessages] = useState([]);
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
      const response = await fetch(apiUrl, {
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
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="输入你的回答..."
        />
        <button 
          onClick={sendMessage}
          disabled={loading}
          className="bg-blue-500 text-white px-6 rounded-lg"
        >
          {loading ? '发送中...' : '发送'}
        </button>
      </div>
    </div>
  );
}

export default InterviewChat;
```

### Nginx 反向代理配置

如果需要域名访问，配置 Nginx：

```nginx
server {
    listen 80;
    server_name interview.your-domain.com;

    # SSL 配置（生产环境必须）
    # ssl_certificate /path/to/cert.pem;
    # ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
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

### CORS 跨域配置

如果前端和 API 不在同一域名，在 `src/main.py` 中添加：

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-website.com"],  # 允许的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## ⚙️ 配置说明

### 模型配置

编辑 `config/agent_llm_config.json`：

```json
{
    "config": {
        "model": "deepseek-chat",
        "temperature": 0.7,
        "top_p": 0.9,
        "max_completion_tokens": 10000,
        "timeout": 600
    },
    "sp": "# 面试官 System Prompt",
    "tools": []
}
```

### API Key 配置

编辑 `src/agents/agent.py` 中的配置：

```python
DEEPSEEK_API_KEY = "sk-your-api-key"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"
```

---

## 📁 项目结构

```
.
├── config/
│   └── agent_llm_config.json    # Agent 配置
├── examples/
│   └── interview-demo.html      # 前端集成示例
├── scripts/
│   ├── http_run.sh              # HTTP 服务启动脚本
│   └── local_run.sh             # 本地运行脚本
├── src/
│   ├── agents/
│   │   └── agent.py             # Agent 核心逻辑
│   ├── storage/
│   │   └── memory/              # 对话记忆存储
│   └── main.py                  # HTTP 服务入口
├── INTEGRATION_GUIDE.md         # 完整集成文档
├── requirements.txt
└── README.md
```

---

## 🔧 常见问题

### Q: 服务启动失败？

检查依赖是否安装完整：
```bash
pip install -r requirements.txt
```

### Q: API 调用超时？

增加超时时间或检查网络连接：
```json
{
    "config": {
        "timeout": 120
    }
}
```

### Q: 如何更换模型？

修改 `src/agents/agent.py` 中的模型配置，支持 DeepSeek、OpenAI 兼容接口。

### Q: 如何实现多用户隔离？

在请求中传递 `thread_id` 参数，用于区分不同用户的对话：
```bash
curl -X POST http://localhost:5000/run \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"type": "human", "content": "你好"}],
    "configurable": {"thread_id": "user_123"}
  }'
```

---

## 📜 License

MIT License
