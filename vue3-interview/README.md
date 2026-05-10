# AI Interview Assistant - Vue3 Frontend

AI智能面试助手移动端应用，基于Vue3构建，支持语音对话面试。

## 功能特性

### 核心功能
- 🎤 **实时语音通话** - 麦克风输入，AI面试官实时语音回答
- 📄 **简历智能分析** - 上传简历，AI定制面试问题
- 📊 **面试评估报告** - 多维度评分，改进建议
- 💬 **对话文本显隐** - 一键切换"电话面试"模式

### 面试管理
- 📋 **岗位化面试** - Java、Python、前端、产品经理等
- 📈 **历史记录** - 保存面试记录，方便复盘
- ⭐ **收藏错题** - 标记高频问题，反复练习

### 个性化设置
- 🎙️ **语音音色** - 女声/男声/专业音色
- ⚡ **语速调节** - 0.5x - 2.0x
- 🎨 **主题切换** - 多种配色方案

## 快速开始

### 安装依赖
```bash
npm install
```

### 开发模式
```bash
npm run dev
```

### 构建生产版本
```bash
npm run build
```

### 预览构建结果
```bash
npm run preview
```

## 项目结构

```
src/
├── api/              # API接口
├── assets/           # 静态资源
├── components/       # 通用组件
├── router/           # 路由配置
├── stores/           # Pinia状态管理
├── styles/           # 全局样式
├── views/            # 页面组件
│   ├── HomePage.vue      # 首页
│   ├── InterviewPage.vue  # 面试通话页
│   ├── ResumePage.vue    # 简历分析页
│   ├── HistoryPage.vue    # 历史记录页
│   ├── ReportPage.vue     # 评估报告页
│   └── SettingsPage.vue   # 设置页
├── App.vue           # 根组件
└── main.js          # 入口文件
```

## 配置说明

### API地址配置
创建 `.env` 文件：
```env
VITE_API_BASE_URL=http://localhost:5000
```

### 后端服务
确保后端Agent服务运行在配置的地址上。

## 技术栈

- Vue 3.4+
- Vue Router 4
- Pinia 2
- Axios
- Vite 5
- SCSS

## License

MIT
