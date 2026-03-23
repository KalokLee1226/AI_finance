# Global Commodity AI Analyzer Pro
# 全球商品智能投研终端 Pro

这是一个由大语言模型 (DeepSeek) 驱动的现代化金融投研终端全栈项目，专为监控并分析国际大宗商品（黄金、原油、白银）设计，并提供极具科技感的 UI 交互体验。项目包含一套完整的用户授权、实时行情监测、均线分析以及 AI 智能策略生成工作流。

## 🎯 核心功能与实现机制
1. **真实 Auth 认证体系**：基于 `sqlite3` 以及 `hashlib` 加密构建的一站式真实持久化账号系统，内置 `users.db`。支持前端无缝原位切换注册和登录形态，告别曾经硬编码极简登录的阶段。
2. **专业级多层图表与指标运算**：
   - 接入真实的金融历史行情，后端采用 `pandas` 高阶运算功能实时预计算 **MA5/MA10/MA20 移动平均线** 以及处理格式化每日**真实交易量（Volume）**。
   - 前端集成高端 `ECharts` 配置逻辑，采用了双 Y 轴分布设计支持同图混合展示（带有彩色判断的柱状体积图及多重均线线条图）。
3. **宏观新闻多维自动采集**：基于 `requests`+`BeautifulSoup` 实时聚合外媒经济及地缘政治事件（如果遭到拦截则启用本地 Mock 数据进行策略补救保证使用连贯）。
4. **DeepSeek AI 推理研报系统**：后端根据抓取的情报和商品走势拼装 Prompt 输入 DeepSeek 云模型，输出极高逻辑性的行情指导预判。前端特制 Markdown 及 Tailwind Typography `Prose` 样式进行优质阅读级排版。
5. **极具质感的现代客户端体验**：前台已全面升级为包含卡片式透明模糊、渐变过渡与发光阴影等具有前沿极客感风格（Glassmorphism等理念）的系统级平台，包括高度定制化的专属滚动条设计。

---

## 🛠️ 技术选型与架构
- **系统架构**：全栈前后端分离
- **前端工具链 (Frontend - Web_Front)**：
  - 基于 Vite + Vue 3 (Composition API `setup`)
  - Tailwind CSS 深度排版
  - ECharts 金融图形化及 Marked.js / Vue-Router / Axios。
- **后端服务端 (Backend)**：
  - Python FastAPI (高并发接口构建)
  - Pandas + yFinance (专业量化历史和指标计算)
  - Python 标准 SQLite3 / hashlib 认证引擎
  - OpenAI-Python-SDK（官方对接 DeepSeek）

---

## 🚀 运行指南在本地

本项目采用前后端分离的现代化架构，需要在不同的终端内分别启动它们。

### 第一步：后端启动（FastAPI 服务）
1. 打开你的终端（比如在 VS Code 里），先进入到你项目里的后端目录：
```bash
cd backend
```
2. 为了防止环境干扰，请安装项目要求的全部 Python 依赖包：
```bash
pip install -r requirements.txt
# 或者手动安装依赖: pip install fastapi uvicorn yfinance requests beautifulsoup4 openai pandas
```
3. 运行主服务程序：
```bash
python main.py
```
> 控制台输出并保活后，后端服务将运行在 `http://127.0.0.1:8000`。并且在首次运行项目或产生注册时会自动新建出库文件 `users.db`。

### 第二步：前端启动（Vite 打包式项目）
1. 打开**独立的一个新的终端**（一定要保留住后端服务正在跑的终端别关掉它），进入到前端 Vite 文件夹：
```bash
cd web_front
```
2. 由于采用 Node.js 最新生态链设计，你需要装载依赖节点包资源：
```bash
npm install
```
3. 启动开发态服务器：
```bash
npm run dev
```

### 第三步：体验产品
在前端终端看到 `http://localhost:5173/` （具体端口视终端而定）字样后，**长按 `Ctrl` (`Cmd`) 键点击这个网址** 在浏览器上打通应用即可开启前沿的 AI 金融大数据库探索之旅。首先注册你自己的专属账户后进入后台！

确保您的电脑上已经安装最新版的 **Python (>= 3.8)**环境。

### 步骤一：拉取并配置后端
1. 进入项目后端目录，并安装依赖：
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
2. （*可选进阶*）：在`backend/main.py`文件中，配置了您的专属**DeepSeek Key** `sk-0a2b77e7cb9f469eaa2c585e1013a2df`，可根据需要随时修改或配置系统环境变量。

### 步骤二：运行系统服务
1. 启动FastAPI异步后端服务器：
   ```bash
   python main.py
   ```
   > 启动成功后，控制台会显示 `Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)`。API服务现在已经就绪。

### 步骤三：启动前端管理仪表盘
由于前端采用了非常纯粹免编译的 `CDN`模式：
可以直接**双击使用浏览器打开** `frontend/index.html` 文件即可！（也可以把它丢入 VS Code Live Server 插件进行开启）。

---

## 📌 操作使用流程
1. 打开浏览器呈现的页面，输入平台通用测试账号（账号：`admin`，密码：`admin123`）验证进入系统。
2. 左滑菜单选择想要研判的标的物（如：**国际黄金 (XAU)**）。
3. 界面中部K线会基于Python服务端自动拉取生成最近3个月金融K线（支持滑轮放大缩小、鼠标跨越悬浮看当日OHLC明细）。
4. 界面右侧“全球政经爬虫头条”将快速更新国际政治新闻。
5. 点击 **[生成最新走势研报]** 按钮，触发DeepSeek智能体运行，等待数秒推理完成后渲染出一份精美深入的 Markdown AI投资报告。