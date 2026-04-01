<template>
  <div class="dash-root min-h-screen font-sans bg-white text-slate-900 flex flex-col dashboard-shell">
    <!-- Main Content -->
    <main class="flex-1 flex flex-col overflow-hidden relative">
      <!-- Header -->
      <header
        class="h-28 bg-white/95 backdrop-blur-md border-b border-black/5 flex items-center justify-between px-10 sticky top-0 z-20"
      >
        <div class="flex flex-col space-y-3 max-w-[60%]">
          <div class="flex items-center">
            <h2 class="text-xl font-bold tracking-tight text-slate-900">
              {{ getCommodityByKey(activeComm)?.name || activeComm }}
              <span
                class="font-normal text-slate-400 ml-3 text-sm uppercase tracking-[0.25em]"
              >
                {{ lang === 'en' ? 'Market Intelligence' : '市场智能洞察' }}
              </span>
            </h2>
          </div>
          <!-- Commodities selector -->
          <div class="flex flex-wrap items-center gap-2 mt-3">
            <button
              v-for="key in commodities"
              :key="key"
              type="button"
              @click="changeCommodity(key)"
              :class="[
                'btn-tag flex items-center gap-2',
                activeComm === key
                  ? 'btn-tag-active'
                  : 'btn-tag-idle'
              ]"
            >
              <span>{{ getCommodityByKey(key)?.name || key }}</span>
              <span
                v-if="commodities.length > 1"
                class="text-[10px] opacity-70"
                @click.stop="removeCommodity(key)"
              >
                ✕
              </span>
            </button>
            <button
              type="button"
              class="btn-tag btn-tag-outline"
              @click="showAddDialog = true"
            >
              {{ lang === 'en' ? 'Add' : '添加品种' }}
            </button>
          </div>
        </div>

        <div class="flex items-center gap-4">
          <div
            class="inline-flex rounded-full border border-black/10 bg-white overflow-hidden text-xs shadow-xs"
          >
            <button
              type="button"
              class="px-3 py-1 transition-colors"
              :class="
                lang === 'en'
                  ? 'bg-slate-900 text-white'
                  : 'text-slate-600 hover:bg-slate-100'
              "
              @click="setLang('en')"
            >
              EN
            </button>
            <button
              type="button"
              class="px-3 py-1 transition-colors"
              :class="
                lang === 'zh'
                  ? 'bg-slate-900 text-white'
                  : 'text-slate-600 hover:bg-slate-100'
              "
              @click="setLang('zh')"
            >
              中
            </button>
          </div>
          <button
            type="button"
            class="btn-ghost text-xs"
            @click="fetchData"
          >
            {{ lang === 'en' ? 'Refresh Data' : '刷新数据' }}
          </button>
          <button
            type="button"
            class="btn-ghost text-xs"
            @click="logout"
          >
            {{ lang === 'en' ? 'Logout' : '退出登录' }}
          </button>
        </div>
      </header>

      <!-- Dashboard Body -->
      <div class="flex-1 overflow-auto p-8 section-scroll bg-white space-y-8">
        <!-- 第一行：K线图 + AI 研报（K 线占比 > 70%） -->
        <div class="grid grid-cols-1 lg:grid-cols-[7fr_3fr] gap-10 items-start">
          <!-- Chart Card -->
          <div
            class="card-main kline-card relative overflow-hidden group hover:shadow-lg transition-all"
          >
            <div class="px-6 py-5 flex flex-col gap-2 bg-white">
              <div class="flex justify-between items-center">
                <h3
                  class="text-sm font-semibold text-slate-900 tracking-[0.18em] uppercase flex items-center"
                >
                  <span
                    class="inline-block w-1.5 h-1.5 rounded-full bg-black mr-3"
                  ></span>
                  {{ lang === 'en' ? 'Price Action & MA System' : '价格行为与均线系统' }}
                </h3>
                <!-- 周期切换按钮 -->
                <div class="flex space-x-2 text-[11px]">
                  <button
                    v-for="p in ['day', 'week', 'month']"
                    :key="p"
                    @click="changePeriod(p)"
                    :class="[
                      'px-3 py-1 rounded-full font-semibold border transition',
                      period === p
                        ? 'bg-black text-white border-black'
                        : 'bg-white text-slate-600 border-slate-300 hover:bg-slate-900 hover:text-white'
                    ]"
                  >
                    {{
                      p === 'day'
                        ? lang === 'en'
                          ? 'Daily'
                          : '日K'
                        : p === 'week'
                        ? lang === 'en'
                          ? 'Weekly'
                          : '周K'
                        : lang === 'en'
                        ? 'Monthly'
                        : '月K'
                    }}
                  </button>
                </div>
              </div>
              <div class="flex flex-wrap items-center space-x-3 text-[11px] font-medium text-slate-700">
                <span class="flex items-center text-slate-700">
                  <span class="w-2 h-2 rounded-full bg-slate-900 mr-1.5"></span>MA5
                </span>
                <span class="flex items-center text-slate-500">
                  <span class="w-2 h-2 rounded-full bg-slate-500 mr-1.5"></span>MA10
                </span>
                <span class="flex items-center text-slate-400">
                  <span class="w-2 h-2 rounded-full bg-slate-300 mr-1.5"></span>MA20
                </span>
                <span
                  class="ml-4 text-slate-500 uppercase text-[10px] tracking-[0.18em]"
                  >Indicators</span
                >
                <label class="inline-flex items-center space-x-1 cursor-pointer">
                  <input type="checkbox" v-model="showBoll" class="rounded border-slate-300" />
                  <span class="text-[11px] text-slate-600">BOLL 布林带</span>
                </label>
                <span
                  class="ml-4 text-slate-500 uppercase text-[10px] tracking-[0.18em]"
                  >Compare</span
                >
                <select
                  v-model="compareKey"
                  @change="onCompareChange"
                  class="border border-slate-300 rounded-full px-2 py-0.5 text-[11px] text-slate-700 bg-white"
                >
                  <option value="">无</option>
                  <option
                    v-for="(item, idx) in allCommodityList || []"
                    :key="idx"
                    :value="item?.key"
                    v-if="item?.key !== activeComm"
                  >
                    {{ item?.name }}
                  </option>
                </select>
              </div>
            </div>
            <div class="p-4 pt-3">
              <div
                v-if="chartLoading"
                class="absolute inset-0 z-10 bg-white/80 backdrop-blur-sm flex items-center justify-center"
              >
                <div
                  class="animate-spin rounded-full h-10 w-10 border-4 border-indigo-500 border-t-transparent"
                ></div>
              </div>
              <div ref="chartRef" class="w-full h-[450px]"></div>
            </div>
          </div>

          <!-- AI Report Card（右侧 AI 分析） -->
          <div
            class="card-main ai-panel flex flex-col relative overflow-hidden hover:shadow-xl transition-all"
          >
            <div class="absolute inset-0 bg-gradient-to-br from-black via-black to-zinc-900 opacity-95"></div>
            <div class="relative px-8 py-6 flex flex-col gap-4">
              <div class="flex justify-between items-center">
                <div>
                  <h3 class="text-xl font-black text-white flex items-center tracking-tight">
                    <span class="text-2xl mr-3">🔮</span>
                    <span>
                      {{
                        lang === 'en'
                          ? 'DeepSeek AI Strategy Report'
                          : 'DeepSeek 智能策略研报'
                      }}
                    </span>
                  </h3>
                  <p class="text-xs text-zinc-300 mt-1 ml-9 leading-relaxed max-w-[90%]">
                    {{
                      lang === 'en'
                        ? 'Aggregate multi-dimensional data and macro news to generate professional-grade market forecasts and strategy guidance.'
                        : '聚合多维数据与宏观新闻，生成专业级行情预判与策略指导'
                    }}
                  </p>
                </div>

                <button
                  @click="generateReport"
                  :disabled="reportLoading"
                  class="btn-primary btn-primary-lg relative overflow-hidden"
                >
                  <span
                    class="absolute inset-0 w-full h-full -mt-1 rounded-lg opacity-30 bg-gradient-to-b from-transparent via-transparent to-black"
                  ></span>
                  <svg
                    v-if="reportLoading"
                    class="animate-spin -ml-1 mr-3 h-5 w-5 text-white relative"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      class="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      stroke-width="4"
                    ></circle>
                    <path
                      class="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  <svg
                    v-else
                    class="w-5 h-5 mr-2 relative"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M13 10V3L4 14h7v7l9-11h-7z"
                    ></path>
                  </svg>
                  <span class="relative">
                    {{
                      reportLoading
                        ? lang === 'en'
                          ? 'Multi-model reasoning in progress...'
                          : '多模型联合推理中...'
                        : lang === 'en'
                        ? 'Generate Strategy Report'
                        : '一键生成策略研报'
                    }}
                  </span>
                </button>
              </div>

              <!-- 人物/风格选择 -->
              <div class="flex flex-wrap items-center gap-4 ml-9 text-[11px] text-zinc-300">
                <div class="flex items-center gap-2">
                  <span class="font-semibold text-slate-600 text-xs uppercase tracking-[0.18em]">
                    {{ lang === 'en' ? 'Persona' : '人物画像' }}
                  </span>
                  <select
                    v-model="personaKey"
                    class="px-2 py-1 rounded bg-zinc-900/70 border border-white/10 text-[11px] text-zinc-100 focus:outline-none"
                  >
                    <option value="default">
                      {{
                        lang === 'en'
                          ? 'Chief institutional strategist (neutral & balanced)'
                          : '机构首席策略分析师（中性稳健）'
                      }}
                    </option>
                    <option value="buffett">
                      {{
                        lang === 'en'
                          ? 'Value-investing legend (long-term, safety margin)'
                          : '价值投资型股神（长期、重安全边际）'
                      }}
                    </option>
                    <option value="soros">
                      {{
                        lang === 'en'
                          ? 'Macro hedge master (trend & inflection sensitive)'
                          : '宏观对冲型高手（趋势/拐点敏感）'
                      }}
                    </option>
                    <option value="dalio">
                      {{
                        lang === 'en'
                          ? 'All-weather asset allocation expert (risk parity)'
                          : '全天候资产配置专家（风险平衡）'
                      }}
                    </option>
                    <option value="custom">
                      {{ lang === 'en' ? 'Custom persona' : '自定义人物人设' }}
                    </option>
                  </select>
                </div>

                <div v-if="personaKey === 'custom'" class="flex flex-col sm:flex-row gap-3 flex-1">
                  <input
                    v-model="customPersonaName"
                    type="text"
                    :placeholder="
                      lang === 'en'
                        ? 'Custom persona name, e.g. Emerging Market Guru'
                        : '自定义人物名称，例如：XX 股神'
                    "
                    class="flex-1 min-w-[120px] px-2 py-1 rounded bg-zinc-900/70 border border-white/10 text-[11px] text-zinc-100 placeholder-zinc-500 focus:outline-none"
                  />
                  <input
                    v-model="customPersonaPrompt"
                    type="text"
                    :placeholder="
                      lang === 'en'
                        ? 'Briefly describe personality, risk preference and style'
                        : '简要描述其性格、风险偏好和投资风格'
                    "
                    class="flex-[2] min-w-[200px] px-2 py-1 rounded bg-zinc-900/70 border border-white/10 text-[11px] text-zinc-100 placeholder-zinc-500 focus:outline-none"
                  />
                </div>

                <div class="flex items-center gap-2">
                  <span class="font-semibold text-zinc-200 text-[11px] uppercase tracking-[0.18em]">
                    Mode
                  </span>
                  <div class="inline-flex rounded-full bg-zinc-900/60 p-0.5 border border-white/10">
                    <button
                      type="button"
                      @click="reportMode = 'fast'"
                      :class="[
                        'px-3 py-1 text-[11px] rounded-full font-semibold transition-colors',
                        reportMode === 'fast'
                          ? 'bg-white text-black shadow-sm'
                          : 'text-zinc-300 hover:text-white'
                      ]"
                    >
                      ⚡ 快速
                    </button>
                    <button
                      type="button"
                      @click="reportMode = 'detailed'"
                      :class="[
                        'px-3 py-1 text-[11px] rounded-full font-semibold transition-colors',
                        reportMode === 'detailed'
                          ? 'bg-white text-black shadow-sm'
                          : 'text-zinc-300 hover:text-white'
                      ]"
                    >
                      📑 详尽
                    </button>
                  </div>
                </div>
              </div>

              <!-- 短期趋势走向条 -->
              <div
                v-if="predictData && predictData.short_term"
                class="mt-2 ml-9 flex items-center gap-3 text-[11px] text-zinc-300"
              >
                <span class="uppercase tracking-[0.18em] text-zinc-500">
                  {{ lang === 'en' ? 'Trend' : '短期趋势' }}
                </span>
                <div class="flex-1 h-1.5 rounded-full overflow-hidden bg-zinc-800">
                  <div
                    class="h-full transition-all duration-500"
                    :class="{
                      'bg-emerald-400': predictData.short_term.direction === 'up',
                      'bg-rose-400': predictData.short_term.direction === 'down',
                      'bg-zinc-400': predictData.short_term.direction === 'range'
                    }"
                    :style="{ width: (40 + (predictData.short_term.confidence || 0) * 50) + '%' }"
                  ></div>
                </div>
                <span class="text-[11px] font-medium">
                  {{
                    predictData.short_term.direction === 'up'
                      ? (lang === 'en' ? 'Bullish' : '偏多')
                      : predictData.short_term.direction === 'down'
                      ? (lang === 'en' ? 'Bearish' : '偏空')
                      : (lang === 'en' ? 'Range' : '震荡')
                  }}
                </span>
              </div>
            </div>

            <div class="relative p-8 min-h-[300px]">
              <!-- Loading State -->
              <div
                v-if="reportLoading"
                class="absolute inset-0 bg-black/60 backdrop-blur-sm flex flex-col items-center justify-center z-10"
              >
                <div class="relative w-24 h-24 mb-6">
                  <div
                    class="absolute inset-0 rounded-full border-t-4 border-white animate-[spin_1s_linear_infinite]"
                  ></div>
                  <div
                    class="absolute inset-2 rounded-full border-r-4 border-zinc-500 animate-[spin_1.5s_linear_infinite_reverse]"
                  ></div>
                  <div
                    class="absolute inset-4 rounded-full border-b-4 border-zinc-700 animate-[spin_2s_linear_infinite]"
                  ></div>
                  <div class="absolute inset-0 flex items-center justify-center text-xl">
                    🧠
                  </div>
                </div>
                <p class="text-white font-bold text-lg animate-pulse">
                  DeepSeek 正在进行交叉推演...
                </p>
                <p class="text-zinc-300 mt-2 text-sm">正在深度解析宏观关联与历史波幅</p>
              </div>

              <!-- Report Content -->
              <div
                v-else-if="reportHtml"
                class="prose prose-slate max-w-none w-full markdown-body bg-zinc-900/60 p-6 rounded-xl border border-white/5 text-zinc-100"
                v-html="reportHtml"
              ></div>

              <!-- Empty State -->
              <div
                v-else
                class="h-full flex flex-col items-center justify-center text-zinc-300 py-12"
              >
                <div
                  class="w-24 h-24 bg-zinc-900/70 border border-white/10 rounded-full flex items-center justify-center mb-6 shadow-inner"
                >
                  <svg
                    class="w-12 h-12 text-zinc-500"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="1.5"
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    ></path>
                  </svg>
                </div>
                <p class="text-lg font-semibold text-zinc-100 mb-2">
                  等待指令生成专属分析
                </p>
                <p class="text-sm">点击上方按钮，基于最新行情与消息面输出深度见解</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 第二行：Latest News + 专家观点（均具备翻译与展开功能） -->
        <div class="grid grid-cols-1 lg:grid-cols-[11fr_9fr] gap-10 mt-10 items-start">
          <!-- Latest News 卡片（左侧 55%） -->
          <div
            class="card-main flex flex-col overflow-hidden hover:shadow-lg transition-all"
          >
            <div
              class="px-6 py-5 border-b border-slate-100 bg-white flex items-center justify-between"
            >
              <h3
                class="text-sm font-semibold text-slate-900 tracking-[0.18em] uppercase flex items-center"
              >
                <span class="inline-block w-1.5 h-1.5 rounded-full bg-black mr-3"></span>
                <span>
                  {{ lang === 'en' ? 'Latest News' : '最新资讯' }}
                </span>
              </h3>
            </div>
            <div class="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
              <div
                v-if="newsLoading"
                class="h-full flex flex-col justify-center items-center text-slate-400"
              >
                <div class="animate-pulse flex space-x-2 items-center">
                  <div class="h-2 w-2 bg-slate-400 rounded-full"></div>
                  <div class="h-2 w-2 bg-slate-400 rounded-full"></div>
                  <div class="h-2 w-2 bg-slate-400 rounded-full"></div>
                </div>
                <span class="text-sm mt-3">
                  {{
                    lang === 'en'
                      ? 'Crawling latest market news...'
                      : '全网爬取中...'
                  }}
                </span>
              </div>
              <div
                v-else-if="news.length === 0"
                class="h-full flex items-center justify-center text-slate-400 text-sm"
              >
                {{ lang === 'en' ? 'No latest news yet' : '暂无最新资讯' }}
              </div>

              <div
                v-else
                v-for="(item, idx) in news"
                :key="idx"
                class="p-3.5 rounded-xl bg-white/80 hover:bg-black hover:text-white transition-colors group shadow-xs"
              >
                <div class="flex justify-between items-start mb-1">
                  <p
                    class="text-sm text-slate-900 font-semibold leading-relaxed group-hover:text-white flex-1 mr-2"
                  >
                    {{ item.title }}
                  </p>
                  <button
                    type="button"
                    class="text-[10px] px-2 py-0.5 rounded-full bg-black text-white hover:bg-white hover:text-black shrink-0 transition-colors"
                    @click.stop="translateNewsItem(item, idx)"
                  >
                    {{
                      newsTranslatingIndex === idx
                        ? lang === 'en'
                          ? 'Translating...'
                          : '翻译中...'
                        : lang === 'en'
                        ? 'Translate'
                        : '翻译'
                    }}
                  </button>
                </div>
                <p
                  v-if="item.summary"
                  :class="[
                    'mt-1 text-[11px] text-slate-500 group-hover:text-slate-200 leading-relaxed',
                    !expandedNews[idx] && 'line-clamp-3'
                  ]"
                >
                  {{ item.summary.replace(/<[^>]+>/g, '') }}
                </p>
                <p
                  v-if="newsTranslations[idx]"
                  class="mt-1 text-[11px] text-slate-700 group-hover:text-slate-100 leading-relaxed"
                >
                  {{ newsTranslations[idx] }}
                </p>
                <div class="flex justify-between items-center mt-2">
                  <span
                    class="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-white/90 text-slate-800 border border-black/5 uppercase tracking-[0.16em]"
                  >
                    {{ item.source }}
                  </span>
                  <div class="flex items-center gap-3">
                    <button
                      v-if="item.summary && item.summary.length > 60"
                      type="button"
                      class="text-[11px] text-slate-500 hover:text-slate-900 group-hover:text-white underline-offset-2 hover:underline"
                      @click.stop="expandedNews[idx] = !expandedNews[idx]"
                    >
                      {{
                        expandedNews[idx]
                          ? (lang === 'en' ? 'Collapse' : '收起')
                          : (lang === 'en' ? 'Expand' : '展开')
                      }}
                    </button>
                    <span class="text-[11px] text-slate-400 flex items-center">
                      <svg
                        class="w-3 h-3 mr-1"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                        ></path>
                      </svg>
                      {{ lang === 'en' ? 'Live' : '实时' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 专家观点（右侧 45%） -->
          <div
            class="card-main flex flex-col overflow-hidden hover:shadow-lg transition-all"
          >
            <div
              class="px-6 py-5 border-b border-slate-100 bg-white flex items-center justify-between"
            >
              <h3
                class="text-sm font-semibold text-slate-900 tracking-[0.18em] uppercase flex items-center"
              >
                <span class="inline-block w-1.5 h-1.5 rounded-full bg-black mr-3"></span>
                <span>
                  {{ lang === 'en' ? 'Global Expert Views' : '全球专家观点' }}
                </span>
              </h3>
              <button
                type="button"
                @click="fetchExpertViews"
                class="text-[11px] px-3 py-1 rounded-full border border-slate-300 bg-white text-slate-600 hover:bg-slate-900 hover:text-white"
              >
                {{ lang === 'en' ? 'Refresh' : '刷新观点' }}
              </button>
            </div>
            <div class="flex-1 p-4 space-y-3 custom-scrollbar max-h-80 overflow-y-auto">
              <div
                v-if="expertLoading"
                class="flex items-center justify-center text-slate-400 text-sm h-32"
              >
                {{
                  lang === 'en'
                    ? 'Loading global expert views...'
                    : '正在抓取全球大宗商品专家观点...'
                }}
              </div>
              <div
                v-else-if="!expertOpinions.length"
                class="flex items-center justify-center text-slate-400 text-sm h-32 text-center px-4"
              >
                {{
                  lang === 'en'
                    ? 'No expert views available. Try again later or check RSS sources.'
                    : '暂无可用专家观点，稍后再试或检查后端 RSS 源。'
                }}
              </div>
              <div
                v-else
                v-for="(op, idx) in expertOpinions"
                :key="idx"
                class="p-3 rounded-xl bg-white/80 hover:bg-black hover:text-white transition-colors cursor-pointer group shadow-xs"
                @click="op.link && window.open(op.link, '_blank')"
              >
                <div class="flex justify-between items-center mb-1">
                  <span class="text-[11px] font-semibold text-slate-500 group-hover:text-slate-200">
                    {{ op.source }}
                  </span>
                  <span class="text-[10px] text-slate-400 group-hover:text-slate-300">
                    {{ op.published || '' }}
                  </span>
                </div>
                <div class="flex justify-between items-center mb-1">
                  <p
                      class="text-sm font-semibold text-slate-900 group-hover:text-white leading-snug line-clamp-2 flex-1 mr-2"
                  >
                    {{ expertTitleTranslations[idx] || op.title || '未命名观点' }}
                  </p>
                  <button
                    type="button"
                    class="text-[10px] px-2 py-0.5 rounded-full bg-black text-white hover:bg-white hover:text-black transition-colors"
                    @click.stop="translateExpertItem(op, idx)"
                  >
                    {{
                      expertTranslatingIndex === idx
                        ? lang === 'en'
                          ? 'Translating...'
                          : '翻译中...'
                        : lang === 'en'
                        ? 'Translate'
                        : '翻译'
                    }}
                  </button>
                </div>
                <p
                  v-if="op.summary"
                  :class="[
                    'text-[11px] text-slate-500 group-hover:text-slate-200 leading-relaxed',
                    !expandedExperts[idx] && 'line-clamp-3'
                  ]"
                >
                  {{ op.summary.replace(/<[^>]+>/g, '') }}
                </p>
                <p
                  v-if="expertBodyTranslations[idx]"
                  class="mt-1 text-[11px] text-slate-700 group-hover:text-slate-100 leading-relaxed"
                >
                  {{ expertBodyTranslations[idx] }}
                </p>
                <p
                  v-else-if="op.error"
                  class="text-[11px] text-rose-500 group-hover:text-rose-200 leading-relaxed"
                >
                  {{ lang === 'en' ? 'Error fetching this source: ' : '抓取该源时出现错误：' }}{{
                    op.error
                  }}
                </p>
                <div
                  v-if="op.summary && op.summary.length > 60"
                  class="mt-2 flex justify-end"
                >
                  <button
                    type="button"
                    class="text-[11px] text-slate-500 hover:text-slate-900 group-hover:text-white underline-offset-2 hover:underline"
                    @click.stop="expandedExperts[idx] = !expandedExperts[idx]"
                  >
                    {{
                      expandedExperts[idx]
                        ? (lang === 'en' ? 'Collapse' : '收起')
                        : (lang === 'en' ? 'Expand' : '展开')
                    }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 添加品种弹窗（全局） -->
    <div
      v-if="showAddDialog"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
    >
      <div class="bg-white rounded-xl shadow-xl p-8 w-80">
        <h2 class="text-lg font-bold mb-4 text-slate-800">
          {{ lang === 'en' ? 'Add Instrument' : '添加自选品种' }}
        </h2>
        <select
          v-model="addKey"
          class="w-full mb-4 p-2 border rounded bg-white text-slate-800"
        >
          <option value="" disabled>
            {{ lang === 'en' ? 'Please select' : '请选择品种' }}
          </option>
          <option
            v-for="(item, idx) in allCommodityList || []"
            :key="idx"
            :value="item?.key"
            :disabled="commodities.includes(item?.key)"
          >
            {{ item?.name }}
          </option>
        </select>
        <div class="flex justify-end space-x-2">
          <button
            @click="showAddDialog = false"
            class="px-4 py-2 rounded bg-slate-200 text-slate-600 hover:bg-slate-300"
          >
            {{ lang === 'en' ? 'Cancel' : '取消' }}
          </button>
          <button
            @click="addCommodity"
            :disabled="!addKey || commodities.includes(addKey)"
            class="px-4 py-2 rounded bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            {{ lang === 'en' ? 'Add' : '添加' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 历史研报详情弹窗 -->
    <div
      v-if="selectedHistoryReport"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
    >
      <div
        class="bg-white rounded-2xl shadow-2xl w-[90%] max-w-4xl max-h-[85vh] flex flex-col overflow-hidden"
      >
        <div
          class="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/80"
        >
          <div class="flex flex-col">
            <div class="text-sm font-bold text-slate-800 flex items-center gap-2">
              <span class="text-slate-900">📘 历史策略研报</span>
              <span class="text-slate-500 text-xs">
                {{ selectedHistoryReport.commodity }}
              </span>
            </div>
            <div class="text-[11px] text-slate-400 mt-0.5">
              生成时间：{{ selectedHistoryReport.created_at }}
            </div>
          </div>
          <div class="flex items-center gap-3">
            <button
              type="button"
              class="px-3 py-1.5 rounded-full border border-slate-300 bg-white text-[11px] text-slate-700 hover:bg-slate-900 hover:text-white flex items-center gap-1"
              @click="sendHistoryReportEmail(selectedHistoryReport)"
              :disabled="historyEmailSendingId === selectedHistoryReport.id"
            >
              <span
                v-if="historyEmailSendingId === selectedHistoryReport.id"
                class="w-3 h-3 border-2 border-emerald-600 border-t-transparent rounded-full animate-spin"
              ></span>
              <span v-else>发送到邮箱</span>
            </button>
            <button
              type="button"
              class="w-7 h-7 rounded-full flex items-center justify-center bg-slate-100 text-slate-500 hover:bg-slate-200"
              @click="closeHistoryReport"
            >
              ✕
            </button>
          </div>
        </div>
        <div class="flex-1 overflow-auto p-6 bg-slate-50/60">
          <div
            class="prose prose-slate max-w-none w-full markdown-body bg-white p-6 rounded-xl border border-slate-200"
            v-html="historyDetailHtml"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { marked } from 'marked'
import request from '../api/request'

const router = useRouter()
const chartRef = ref(null)
let chartInstance = null

// 语言状态：默认英文，可记忆到本地
const lang = ref(localStorage.getItem('lang') === 'zh' ? 'zh' : 'en')
const setLang = (value) => {
  lang.value = value === 'zh' ? 'zh' : 'en'
  localStorage.setItem('lang', lang.value)
}

// 商品基础信息（可扩展）
const allCommodityList = [
  { key: 'gold', name: '国际黄金 (XAU/USD)', icon: '🥇' },
  { key: 'oil', name: 'WTI原油 (CL=F)', icon: '🛢️' },
  { key: 'silver', name: '国际白银 (XAG/USD)', icon: '🥈' },
  { key: 'copper', name: '国际铜 (HG=F)', icon: '🟫' },
  { key: 'aluminum', name: '国际铝 (ALI=F)', icon: '⬜' },
  { key: 'corn', name: '美玉米 (ZC=F)', icon: '🌽' },
  { key: 'soybean', name: '美大豆 (ZS=F)', icon: '🌱' },
  // { key: 'btc', name: '比特币 (BTC-USD)', icon: '₿' },
  // { key: 'eth', name: '以太坊 (ETH-USD)', icon: 'Ξ' },
  // { key: 'usdindex', name: '美元指数 (DX-Y.NYB)', icon: '💵' },
  // { key: 'eurusd', name: '欧元/美元 (EURUSD=X)', icon: '💶' },
  // { key: 'ndx', name: '纳指100 (^NDX)', icon: '💹' },
  // { key: 'sp500', name: '标普500 (^GSPC)', icon: '📈' },
  // { key: 'hsi', name: '恒生指数 (^HSI)', icon: '🇭🇰' }
]
const getCommodityByKey = (key) => allCommodityList.find(c => c.key === key)

const localKey = 'my_commodities'
const getDefaultKeys = () => ['gold', 'oil', 'silver']
const getLocalCommodities = () => {
  try {
    const arr = JSON.parse(localStorage.getItem(localKey))
    if (Array.isArray(arr) && arr.length > 0) {
      const validKeys = allCommodityList.map(c => c.key)
      const filtered = arr.filter(k => validKeys.includes(k))
      if (filtered.length !== arr.length) {
        localStorage.setItem(localKey, JSON.stringify(filtered.length > 0 ? filtered : getDefaultKeys()))
      }
      return filtered.length > 0 ? filtered : getDefaultKeys()
    }
  } catch {}
  return getDefaultKeys()
}
const setLocalCommodities = (arr) => {
  localStorage.setItem(localKey, JSON.stringify(arr))
}

const commodities = ref(getLocalCommodities())
const activeComm = ref(commodities.value[0] || 'gold')

const period = ref('day')

const showBoll = ref(false)
const compareKey = ref('')

const news = ref([])
const newsLoading = ref(false)
const newsTranslations = ref({})
const newsTranslatingIndex = ref(null)
const reportHtml = ref('')
const reportLoading = ref(false)
const chartLoading = ref(false)

// AI 人物/风格配置
const personaKey = ref('default')
const customPersonaName = ref('')
const customPersonaPrompt = ref('')
// 研报生成模式：detailed（默认）/ fast
const reportMode = ref('detailed')

// 研报历史 / AI 对话 / 智能预警
const reportHistory = ref([])
const historyLoading = ref(false)
const selectedHistoryReport = ref(null)
const historyDetailHtml = ref('')
const historyEmailSendingId = ref(null)

const chatMessages = ref([])
const chatInput = ref('')
const chatLoading = ref(false)

const alerts = ref([])
const alertsLoading = ref(false)

// 量化预测
const predictData = ref(null)
const predictLoading = ref(false)

// 专家观点
const expertOpinions = ref([])
const expertLoading = ref(false)
// 标题翻译 + 正文翻译分开存，便于完整展示
const expertTitleTranslations = ref({})
const expertBodyTranslations = ref({})
const expertTranslatingIndex = ref(null)

// 展开/收起状态
const expandedNews = ref({})
const expandedExperts = ref({})

// 翻译助手
const translateInput = ref('')
const translateFrom = ref('auto')
const translateTo = ref('zh')
const translateResult = ref('')
const translateLoading = ref(false)

// 顶部用户菜单
const userMenuOpen = ref(false)


const showAddDialog = ref(false)
const addKey = ref('')
const addCommodity = () => {
  if (!addKey.value) return
  if (!commodities.value.includes(addKey.value)) {
    commodities.value.push(addKey.value)
    setLocalCommodities(commodities.value)
    saveUserCommodities()
  }
  showAddDialog.value = false
  addKey.value = ''
}
const removeCommodity = (key) => {
  if (commodities.value.length <= 1) return
  commodities.value = commodities.value.filter(k => k !== key)
  setLocalCommodities(commodities.value)
  saveUserCommodities()
  if (activeComm.value === key) {
    activeComm.value = commodities.value[0]
    fetchData()
  }
}
const changeCommodity = (key) => {
  activeComm.value = key
  reportHtml.value = ''
  fetchData()
  fetchReportHistory()
  fetchAlerts()
}
const changePeriod = (p) => {
  if (period.value !== p) {
    period.value = p
    fetchData()
  }
}

const onCompareChange = () => {
  fetchData()
}

const loadUserCommodities = async () => {
  try {
    const res = await request.get('/user-commodities')
    if (Array.isArray(res.commodities) && res.commodities.length > 0) {
      commodities.value = res.commodities
      activeComm.value = commodities.value[0] || 'gold'
      setLocalCommodities(commodities.value)
    }
  } catch (err) {
    console.error('Load user commodities failed:', err)
  }
}

const saveUserCommodities = async () => {
  try {
    await request.post('/user-commodities', { commodities: commodities.value })
  } catch (err) {
    console.error('Save user commodities failed:', err)
  }
}

const fetchData = async () => {
  chartLoading.value = true
  try {
    const res = await request.get(`/market-data/${activeComm.value.toUpperCase()}?period=${period.value}`)

    let compareData = null
    if (compareKey.value) {
      try {
        compareData = await request.get(`/market-data/${compareKey.value.toUpperCase()}?period=${period.value}`)
      } catch (e) {
        console.error('Fetch compare data failed:', e)
      }
    }

    renderChart(res, compareData)
  } catch (err) {
    console.error('Fetch data failed:', err)
  } finally {
    chartLoading.value = false
  }
}

const fetchNews = async () => {
  newsLoading.value = true
  try {
    const res = await request.get('/news')
    news.value = res.news || []
  } catch (err) {
    console.error('Fetch news failed:', err)
    news.value = []
  } finally {
    newsLoading.value = false
  }
}

const getCurrentCommodityLabel = () => {
  const current = getCommodityByKey(activeComm.value)
  return current ? current.name : activeComm.value
}

const fetchReportHistory = async () => {
  historyLoading.value = true
  try {
    const commodityLabel = getCurrentCommodityLabel()
    const res = await request.get('/user-reports', { params: { commodity: commodityLabel, limit: 5 } })
    reportHistory.value = Array.isArray(res.items) ? res.items : []
  } catch (err) {
    console.error('Fetch report history failed:', err)
    reportHistory.value = []
  } finally {
    historyLoading.value = false
  }
}

const openHistoryReport = (item) => {
  selectedHistoryReport.value = item
  historyDetailHtml.value = marked.parse(item.report || '')
}

const closeHistoryReport = () => {
  selectedHistoryReport.value = null
  historyDetailHtml.value = ''
}

const sendHistoryReportEmail = async (item) => {
  if (!item || !item.id) return
  historyEmailSendingId.value = item.id
  try {
    const res = await request.post(`/user-reports/${item.id}/send-email`)
    const status = res?.status
    if (status === 'sent') {
      alert('该策略研报已发送到您的邮箱。')
    } else if (status === 'no_email') {
      alert('当前账号未设置邮箱，无法发送策略研报。')
    } else if (status === 'failed') {
      alert('研报邮件发送失败，请检查 SMTP 配置或稍后重试。')
    } else {
      alert('本次研报邮件发送已处理，如有异常请查看后端日志。')
    }
  } catch (err) {
    console.error('Send history report email failed:', err)
    const msg = err?.response?.data?.detail || '研报邮件发送失败，请稍后重试或检查后端日志。'
    alert(msg)
  } finally {
    historyEmailSendingId.value = null
  }
}

const generateReport = async () => {
  reportLoading.value = true
  try {
    const current = getCommodityByKey(activeComm.value)
    const payload = {
      commodity: current ? current.name : activeComm.value,
      persona: personaKey.value,
      mode: reportMode.value,
    }
    if (personaKey.value === 'custom') {
      payload.custom_persona_name = customPersonaName.value || undefined
      payload.custom_persona_prompt = customPersonaPrompt.value || undefined
    }
    const res = await request.post('/generate-report', payload)
    reportHtml.value = marked.parse(res.report)
    // 刷新当前品种的历史研报
    fetchReportHistory()
    // 同步更新量化趋势视图
    fetchPrediction()
  } catch (err) {
    console.error('Generate report failed:', err)
    const msg = err?.response?.data?.detail || 'AI 调用失败，请稍后重试或检查后端日志。'
    alert(msg)
  } finally {
    reportLoading.value = false
  }
}

const sendChat = async () => {
  if (!chatInput.value.trim()) return
  const question = chatInput.value.trim()
  chatInput.value = ''

  chatMessages.value.push({ role: 'user', content: question })
  chatLoading.value = true
  try {
    const commodityLabel = getCurrentCommodityLabel()
    const historyPayload = chatMessages.value.map(m => ({ role: m.role, content: m.content }))

    const payload = {
      commodity: commodityLabel,
      question,
      persona: personaKey.value,
      history: historyPayload
    }
    if (personaKey.value === 'custom') {
      payload.custom_persona_name = customPersonaName.value || undefined
      payload.custom_persona_prompt = customPersonaPrompt.value || undefined
    }

    const res = await request.post('/ai-chat', payload)
    if (res && res.answer) {
      chatMessages.value.push({ role: 'assistant', content: res.answer })
    }
  } catch (err) {
    console.error('AI chat failed:', err)
    const msg = err?.response?.data?.detail || 'AI 对话调用失败，请稍后重试或检查后端日志。'
    alert(msg)
  } finally {
    chatLoading.value = false
  }
}

const fetchAlerts = async () => {
  alertsLoading.value = true
  try {
    const res = await request.get('/alerts')
    alerts.value = Array.isArray(res.alerts) ? res.alerts : []
  } catch (err) {
    console.error('Fetch alerts failed:', err)
    alerts.value = []
  } finally {
    alertsLoading.value = false
  }
}

const fetchPrediction = async () => {
  predictLoading.value = true
  try {
    const res = await request.get(`/predict-price/${activeComm.value.toUpperCase()}`)
    predictData.value = res
  } catch (err) {
    console.error('Fetch prediction failed:', err)
    const msg = err?.response?.data?.detail || '量化预测失败，请稍后重试或检查后端日志。'
    alert(msg)
  } finally {
    predictLoading.value = false
  }
}

const fetchExpertViews = async () => {
  expertLoading.value = true
  try {
    const res = await request.get('/expert/latest', { params: { limit: 10 } })
    expertOpinions.value = Array.isArray(res.opinions) ? res.opinions : []
  } catch (err) {
    console.error('Fetch expert views failed:', err)
    expertOpinions.value = []
  } finally {
    expertLoading.value = false
  }
}

const translateNewsItem = async (item, idx) => {
  if (!item || (!item.title && !item.summary)) return
  newsTranslatingIndex.value = idx
  try {
    const rawTitle = item.title || ''
    const rawSummary = item.summary ? item.summary.replace(/<[^>]+>/g, '') : ''
    const parts = []
    if (rawTitle) parts.push(`${lang.value === 'zh' ? '标题：' : 'Title: '} ${rawTitle}`)
    if (rawSummary) parts.push(`${lang.value === 'zh' ? '内容：' : 'Body: '} ${rawSummary}`)
    const text = parts.join('\n\n') || rawTitle

    const res = await request.get('/translate', {
      params: {
        q: text,
        from_lang: 'auto',
        to_lang: lang.value === 'zh' ? 'zh' : 'en'
      }
    })
    if (res?.translated) {
      newsTranslations.value = { ...newsTranslations.value, [idx]: res.translated }
    }
  } catch (err) {
    console.error('Translate news failed:', err)
    const msg = err?.response?.data?.detail || '新闻翻译失败，请稍后重试。'
    alert(msg)
  } finally {
    newsTranslatingIndex.value = null
  }
}

const translateExpertItem = async (op, idx) => {
  if (!op || (!op.title && !op.summary)) return
  expertTranslatingIndex.value = idx
  try {
    const tasks = []

    const rawTitle = op.title || ''
    if (rawTitle) {
      tasks.push(
        request
          .get('/translate', {
            params: {
              q: rawTitle,
              from_lang: 'auto',
              to_lang: lang.value === 'zh' ? 'zh' : 'en'
            }
          })
          .then((res) => {
            if (res?.translated) {
              expertTitleTranslations.value = {
                ...expertTitleTranslations.value,
                [idx]: res.translated
              }
            }
          })
      )
    }

    const rawSummary = op.summary ? op.summary.replace(/<[^>]+>/g, '') : ''
    if (rawSummary) {
      tasks.push(
        request
          .get('/translate', {
            params: {
              q: rawSummary,
              from_lang: 'auto',
              to_lang: lang.value === 'zh' ? 'zh' : 'en'
            }
          })
          .then((res) => {
            if (res?.translated) {
              expertBodyTranslations.value = {
                ...expertBodyTranslations.value,
                [idx]: res.translated
              }
            }
          })
      )
    }

    if (tasks.length) {
      await Promise.all(tasks)
    }
  } catch (err) {
    console.error('Translate expert view failed:', err)
    const msg = err?.response?.data?.detail || '专家观点翻译失败，请稍后重试。'
    alert(msg)
  } finally {
    expertTranslatingIndex.value = null
  }
}

// 保留翻译接口逻辑供新闻/专家观点调用（顶部 Translate Helper UI 已精简移除）

const sendAlertEmail = async () => {
  try {
    const res = await request.get('/alerts', { params: { send_email: true } })
    // 同时刷新一次当前告警列表
    alerts.value = Array.isArray(res.alerts) ? res.alerts : []
    const status = res.email_status
    if (status === 'sent') {
      alert('已将本次重要预警通过邮件发送给您。')
    } else if (status === 'no_important_alerts') {
      alert('当前没有需要邮件提醒的高等级预警。')
    } else if (status === 'no_email') {
      alert('当前账号未设置邮箱，无法发送邮件预警。')
    } else if (status === 'failed') {
      alert('邮件发送失败，请检查 SMTP 配置或稍后重试。')
    } else {
      alert('本次预警扫描已完成，如有重要信号会尝试邮件推送。')
    }
  } catch (err) {
    console.error('Send alert email failed:', err)
    const msg = err?.response?.data?.detail || '预警邮件发送失败，请稍后重试或检查后端日志。'
    alert(msg)
  }
}

const renderChart = (data, compareData = null) => {
  nextTick(() => {
    if (!chartInstance) {
      chartInstance = echarts.init(chartRef.value)
    }
    const upColor = '#ef4444';
    const downColor = '#10b981';

    // 主数据
    let dates = data.dates || []
    let kline = data.kline || []
    let volumes = data.volumes || []
    const ma5 = data.ma5 || []
    const ma10 = data.ma10 || []
    const ma20 = data.ma20 || []

    // 若存在对比标的，按较短长度对齐
    let compareSeriesData = null
    if (compareData && compareData.dates && compareData.kline && compareData.kline.length > 0) {
      const len = Math.min(dates.length, compareData.dates.length)
      if (len > 0) {
        dates = dates.slice(-len)
        kline = kline.slice(-len)
        volumes = volumes.slice(-len)

        const closeMain = kline.map(k => k[1])
        const closeCmp = compareData.kline.slice(-len).map(k => k[1])
        const mainMin = Math.min(...closeMain)
        const mainMax = Math.max(...closeMain)
        const cmpMin = Math.min(...closeCmp)
        const cmpMax = Math.max(...closeCmp)
        const spanMain = mainMax - mainMin || 1
        const spanCmp = cmpMax - cmpMin || 1
        compareSeriesData = closeCmp.map(v => (v - cmpMin) / spanCmp * spanMain + mainMin)
      }
    }

    const option = {
      animation: true,
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross', lineStyle: { color: '#94a3b8', type: 'dashed' } },
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        borderColor: '#e2e8f0',
        textStyle: { color: '#1e293b' },
        extraCssText: 'box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);'
      },
      legend: {
        data: ['K线', 'MA5', 'MA10', 'MA20', '成交量'],
        top: 0,
        textStyle: { color: '#64748b' }
      },
      grid: [
        { left: '8%', right: '4%', height: '60%', top: '10%' },
        { left: '8%', right: '4%', top: '75%', height: '16%' }
      ],
      xAxis: [
        {
          type: 'category',
          data: dates,
          boundaryGap: false,
          axisLine: { onZero: false, lineStyle: { color: '#cbd5e1' } },
          axisLabel: { color: '#64748b' },
          splitLine: { show: false }
        },
        {
          type: 'category',
          gridIndex: 1,
          data: dates,
          boundaryGap: false,
          axisLine: { onZero: false },
          axisTick: { show: false },
          splitLine: { show: false },
          axisLabel: { show: false }
        }
      ],
      yAxis: [
        {
          scale: true,
          splitArea: { show: true, areaStyle: { color: ['rgba(250,250,250,0.3)', 'rgba(200,200,200,0.1)'] } },
          axisLine: { show: false },
          axisTick: { show: false },
          splitLine: { lineStyle: { color: '#e2e8f0', type: 'dashed' } },
          axisLabel: { color: '#64748b' }
        },
        {
          scale: true,
          gridIndex: 1,
          splitNumber: 2,
          axisLabel: { show: false },
          axisLine: { show: false },
          axisTick: { show: false },
          splitLine: { show: false }
        }
      ],
      dataZoom: [
        { type: 'inside', xAxisIndex: [0, 1], start: 30, end: 100 },
        { show: true, xAxisIndex: [0, 1], type: 'slider', top: '95%', bottom: '0', borderColor: '#e2e8f0', textStyle: { color: '#64748b' } }
      ],
      series: [
        {
          name: 'K线',
          type: 'candlestick',
          data: kline,
          itemStyle: { color: upColor, color0: downColor, borderColor: upColor, borderColor0: downColor },
        },
        { name: 'MA5', type: 'line', data: ma5, smooth: true, showSymbol: false, lineStyle: { opacity: 0.8, color: '#3b82f6', width: 2 } },
        { name: 'MA10', type: 'line', data: ma10, smooth: true, showSymbol: false, lineStyle: { opacity: 0.8, color: '#f59e0b', width: 2 } },
        { name: 'MA20', type: 'line', data: ma20, smooth: true, showSymbol: false, lineStyle: { opacity: 0.8, color: '#8b5cf6', width: 2 } },
        // BOLL 布林带（可选）
        ...(showBoll.value ? [
          { name: 'BOLL 上轨', type: 'line', data: data.boll_upper || [], smooth: true, showSymbol: false, lineStyle: { opacity: 0.6, color: '#38bdf8', width: 1 } },
          { name: 'BOLL 下轨', type: 'line', data: data.boll_lower || [], smooth: true, showSymbol: false, lineStyle: { opacity: 0.6, color: '#38bdf8', width: 1, type: 'dashed' } }
        ] : []),
        // 对比标的（价格形态归一后映射到主轴）
        ...(compareSeriesData ? [
          {
            name: `对比: ${getCommodityByKey(compareKey.value)?.name || compareKey.value}`,
            type: 'line',
            data: compareSeriesData,
            smooth: true,
            showSymbol: false,
            lineStyle: { opacity: 0.8, color: '#0ea5e9', width: 1.5, type: 'dotted' }
          }
        ] : []),
        {
          name: '成交量',
          type: 'bar',
          xAxisIndex: 1,
          yAxisIndex: 1,
          data: volumes.map((vol, idx) => {
             const k = kline[idx];
             // color volume bar conditionally
             const color = (k && k[1] > k[0]) ? upColor : downColor;
             return { value: vol, itemStyle: { color: color, opacity: 0.7 } };
          })
        }
      ]
    }
    chartInstance.setOption(option, true)
  })
}

const logout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}

onMounted(async () => {
  await loadUserCommodities()
  fetchData()
  fetchNews()
  fetchReportHistory()
  fetchAlerts()
   fetchExpertViews()
  window.addEventListener('resize', () => {
    if (chartInstance) chartInstance.resize()
  })
})
</script>

<style>
/* 页面淡入与整体呼吸感 */
.dashboard-shell {
  animation: dash-fade-in 0.6s ease-out;
}

@keyframes dash-fade-in {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 统一卡片风格：弱边框，轻阴影，大留白 */
.card-main {
  border-radius: 22px;
  background: #ffffff;
  box-shadow: 0 14px 40px rgba(0, 0, 0, 0.03);
}

.kline-card {
  border-radius: 26px;
  background: #ffffff;
}

.ai-panel {
  border-radius: 26px;
}

/* Nike 风按钮体系 */
.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.9rem 1.9rem;
  border-radius: 999px;
  background: #000000;
  color: #ffffff;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 11px;
  border: none;
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease, background-color 0.18s ease, color 0.18s ease;
  box-shadow: 0 18px 45px rgba(0, 0, 0, 0.35);
}

.btn-primary-lg {
  border-radius: 999px;
}

.btn-primary:hover:not(:disabled) {
  background: #ffffff;
  color: #000000;
  transform: translateY(-1px) scale(1.03);
  box-shadow: 0 22px 60px rgba(0, 0, 0, 0.45);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0) scale(0.97);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: default;
}

.btn-ghost {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.55rem 1.2rem;
  border-radius: 999px;
  background: #ffffff;
  color: #111111;
  border: 1px solid rgba(0, 0, 0, 0.12);
  cursor: pointer;
  transition: transform 0.18s ease, background-color 0.18s ease, color 0.18s ease, box-shadow 0.18s ease;
}

.btn-ghost:hover:not(:disabled) {
  background: #000000;
  color: #ffffff;
  transform: translateY(-1px) scale(1.03);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.25);
}

.btn-ghost:active:not(:disabled) {
  transform: translateY(0) scale(0.97);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.18);
}

.btn-tag {
  padding: 0.35rem 0.9rem;
  border-radius: 999px;
  font-size: 11px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  border: none;
  cursor: pointer;
  transition: transform 0.18s ease, background-color 0.18s ease, color 0.18s ease, box-shadow 0.18s ease;
}

.btn-tag-active {
  background: #000000;
  color: #ffffff;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
}

.btn-tag-idle {
  background: #f5f5f5;
  color: #222222;
}

.btn-tag-outline {
  background: #ffffff;
  color: #111111;
  border: 1px dashed rgba(0, 0, 0, 0.25);
}

.btn-tag:hover {
  transform: translateY(-1px) scale(1.03);
}

.btn-tag:active {
  transform: translateY(0) scale(0.97);
}

.shadow-xs {
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
}

/* Custom Scrollbar for modern look */
.custom-scrollbar::-webkit-scrollbar, .section-scroll::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track, .section-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb, .section-scroll::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 20px;
}
.custom-scrollbar:hover::-webkit-scrollbar-thumb, .section-scroll:hover::-webkit-scrollbar-thumb {
  background-color: #94a3b8;
}

/* Base styles for Markdown output from AI */
.markdown-body {
  color: #334155;
  line-height: 1.7;
}
.markdown-body h1, .markdown-body h2, .markdown-body h3 {
  color: #1e293b;
  font-weight: 700;
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 0.3em;
}
.markdown-body p { margin-bottom: 1em; }
.markdown-body ul, .markdown-body ol { padding-left: 1.5em; margin-bottom: 1em; }
.markdown-body li { margin-bottom: 0.25em; }
.markdown-body strong { color: #0f172a; }
.markdown-body blockquote {
  border-left: 4px solid #indigo-500;
  padding-left: 1em;
  color: #64748b;
  background-color: #f8fafc;
  padding: 0.5em 1em;
  border-radius: 0 0.5rem 0.5rem 0;
}
</style>