# Global Commodity AI Analyzer Pro
# 全球商品智能投研终端 Pro

这是一个由大语言模型 (DeepSeek) 驱动的现代化金融投研终端全栈项目，专为监控并分析国际大宗商品（黄金、原油、白银）设计，并提供极具科技感的 UI 交互体验。项目包含一套完整的用户授权、实时行情监测、均线分析以及 AI 智能策略生成工作流。


## 🎯 系统核心功能详解
1. **真实 Auth 认证体系**
   - 基于 `sqlite3` + `hashlib` 加密，构建持久化账号系统，支持注册/登录切换，保障数据安全。
2. **多层级金融图表与指标分析**
   - 后端实时拉取多源金融历史行情（yfinance / investpy / akshare 三级兜底），利用 `pandas` 计算 MA5/MA10/MA20、RSI14、MACD、BOLL 等核心技术指标。
   - 前端采用 `ECharts`，双 Y 轴混合展示 K 线、均线与成交量，支持指标开关与对比标的叠加，交互体验专业。
3. **全球 + 国内多源财经新闻聚合**
   - 通过 `httpx` + `asyncio` 并发抓取 BBC、Reuters、CNBC、Yahoo Finance、CoinDesk 以及新浪财经、东方财富等站点标题，并可选接入 NewsAPI / GNews 免费 API。
   - 针对不同网站自动适配主标题标签，支持相对链接补全、去重与按时间排序；当全部外部源不可用时自动返回系统提示，保证接口高可用。
4. **AI 智能行情分析与研报生成**
   - 后端自动将最新新闻与行情拼装成 Prompt，调用 DeepSeek 大模型生成专业级行情分析、投资建议与风险提示，并支持多种分析人设（首席策略、价值投资、宏观对冲等）。
   - 支持用户自定义人设与 AI 对话追问，以及当前标的的历史研报列表回看。
   - 前端采用 Markdown + Tailwind Typography 优雅排版，支持一键生成和阅读 AI 投资报告。
5. **现代化极客风 UI 体验**
   - 前端采用卡片式透明模糊、渐变、发光阴影等 Glassmorphism 设计理念，滚动条、交互细节高度定制。
   - 支持移动端与桌面端自适应，体验流畅。
6. **智能技术预警与邮件告警**
   - 后端根据 RSI、MACD、BOLL 等技术指标对用户自选品种生成“提示 / 预警”级别信号，通过 `/api/alerts` 提供统一接口。
   - 前端 Dashboard 的“智能技术面预警”卡片支持一键刷新与“邮件发送本次预警”，仅在你主动点击时通过 SMTP 发送邮件，避免骚扰。
7. **量化价格预测与可解释性仪表盘**
   - 后端 `/api/predict-price/{symbol}` 结合规则引擎与 ARIMA 模型，对未来 1–3 日和 5–30 分钟给出方向、收益率区间和置信度，并同时返回各单模型视角及多模型融合结果。
   - 前端提供“短期量化预测”“超短期波动评估”卡片，配套置信度进度条、中文解释文字，以及“技术规则 vs ARIMA”模型对比小面板，突出可解释性。

---

## 🆕 近期重大升级亮点（v0.3）
- 新增基于技术指标的智能预警模块与 `/api/alerts` 接口，支持自选品种预警列表与一键邮件告警。
- 新增短期/超短期量化价格预测模块 `/api/predict-price`，采用规则引擎 + ARIMA 多模型融合，并配套前端可视化仪表盘与模型对比面板。
- 新闻源扩展至 NewsAPI / GNews 以及新浪财经、东方财富等国内站点，加入 `/api/news-debug` 连通性体检接口与 `NEWS_VERIFY_SSL` 配置，提升在受限网络环境下的可用性。
- 后端统一通过 `backend/.env` 加载 DeepSeek、AI_FINANCE_SECRET、NewsAPI、GNEWS、SMTP 等敏感配置，部署更安全可控。
- 调整 yfinance / investpy / akshare 与新闻抓取的日志级别，压制非致命错误日志，提升整体可观测性与稳定性。

---

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
在前端终端看到 `http://localhost:5173/` （具体端口视终端而定）字样后，**按住 Ctrl/Cmd 点击该地址** 在浏览器中打开应用，即可注册登录、选择标的并体验完整的行情监控 + 新闻聚合 + AI 研报 + 智能预警 + 量化预测工作流。

确保您的电脑上已经安装最新版的 **Python (>= 3.8)** 与 **Node.js (>= 18)** 环境。

所有敏感配置（DeepSeek Key、AI_FINANCE_SECRET、NewsAPI/GNEWS Key、SMTP 等）均通过 `backend/.env` 管理，请参考文件内注释填写为你自己的密钥；本仓库不再在代码中硬编码任何真实密钥。

当前推荐的前端入口为 Vite + Vue 3 应用 `web_front`；根目录下的 `frontend/` 目录仅保留为早期静态 Demo，不再维护。

---

## 📌 操作使用流程
1. 打开浏览器呈现的页面，输入平台通用测试账号（账号：`admin`，密码：`admin123`）验证进入系统。
2. 左滑菜单选择想要研判的标的物（如：**国际黄金 (XAU)**）。
3. 界面中部K线会基于Python服务端自动拉取生成最近3个月金融K线（支持滑轮放大缩小、鼠标跨越悬浮看当日OHLC明细）。
4. 界面右侧“全球政经爬虫头条”将快速更新国际政治新闻。
5. 点击 **[生成最新走势研报]** 按钮，触发DeepSeek智能体运行，等待数秒推理完成后渲染出一份精美深入的 Markdown AI投资报告。