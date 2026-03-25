# 更新日志

## [2026-03-25] - v0.3

### 新增功能
1. **百度翻译集成**
   - 新增 `/translate` 接口，支持中英文及多语言互译，基于百度云新版 API Key 实现。  
   - 封装 `BaiduTranslator` 类，自动获取 access_token 并调用翻译接口，支持单条文本翻译。  
   - FastAPI 路由集成，可直接通过 GET 参数 `q`, `from_lang`, `to_lang` 使用。  

2. **专家观点抓取**
   - 新增 `/expert/latest` 接口，抓取 OilPrice 等稳定 RSS 源的专家观点。  
   - 支持异步抓取，返回字段包含 `source`, `title`, `link`, `summary`, `published`。  
   - 可通过查询参数 `limit` 控制每个 RSS 源抓取条数，前端可直接展示最新观点。  

---

### 优化
1. **统一配置与安全**
   - 后端启动时自动加载 `backend/.env`，集中管理 DeepSeek、AI_FINANCE_SECRET、NewsAPI、GNEWS、SMTP、百度翻译 API Key 等敏感配置，避免在代码中硬编码密钥。  

2. **日志与稳定性**
   - 降低 yfinance / investpy / akshare 以及 HTML 新闻抓取失败的日志级别，压制非致命的“上游数据源失败”刷屏，仅在真正不可恢复时输出错误日志。  
   - 市场数据、新闻、翻译、专家观点接口在部分数据源失败时自动尝试其他源或返回友好提示，提高整体鲁棒性和用户体验。  

3. **接口体验优化**
   - 翻译接口提供完整调试信息，方便排查 API Key 或网络问题。  
   - 专家观点接口异步抓取，多源并行返回，提高响应速度。  