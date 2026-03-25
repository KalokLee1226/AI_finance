<template>
  <div class="flex h-screen bg-slate-50 font-sans text-slate-800">
    <!-- Sidebar -->
    <aside class="w-68 bg-slate-900 text-white flex flex-col shadow-2xl relative z-10">
      <div class="h-20 flex items-center justify-center px-6 border-b border-white/10 bg-black/20 backdrop-blur-sm">
        <h1 class="text-2xl font-black bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400 tracking-tight">
          AI投研终端 Pro
        </h1>
      </div>
      
      <div class="px-4 pt-6 pb-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
        全球大宗商品监控
      </div>
      
      <nav class="flex-1 px-3 space-y-2 overflow-y-auto">
        <button
          v-for="key in commodities"
          :key="key"
          @click="changeCommodity(key)"
          :class="['w-full flex items-center px-4 py-3.5 rounded-xl transition-all duration-300 font-medium group', activeComm === key ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-900/50' : 'text-gray-800 hover:bg-white/5 hover:text-white']"
        >
          <span class="w-8 h-8 rounded-lg flex items-center justify-center mr-3 transition-colors" :class="activeComm === key ? 'bg-white/20' : 'bg-white/5 group-hover:bg-white/10'">
            <span>{{ getCommodityByKey(key)?.icon || '📈' }}</span>
          </span>
          {{ getCommodityByKey(key)?.name || key }}
          <span v-if="commodities.length > 1" @click.stop="removeCommodity(key)" class="ml-auto text-xs text-slate-400 hover:text-red-400 cursor-pointer px-2">✕</span>
        </button>
        <button @click="showAddDialog = true" class="w-full flex items-center px-4 py-3.5 rounded-xl text-slate-400 hover:text-indigo-400 hover:bg-white/10 transition-all mt-2">
          <span class="w-8 h-8 rounded-lg flex items-center justify-center mr-3 bg-white/5">＋</span> 添加品种
        </button>
      </nav>
            <!-- 添加品种弹窗 -->
            <div v-if="showAddDialog" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
              <div class="bg-white rounded-xl shadow-xl p-8 w-80">
                <h2 class="text-lg font-bold mb-4 text-slate-800">添加自选品种</h2>
                <select
                  v-model="addKey"
                  class="w-full mb-4 p-2 border rounded bg-white text-slate-800"
                >
                  <option value="" disabled>请选择品种</option>
                  <option v-for="(item, idx) in allCommodityList || []" :key="idx" :value="item?.key" :disabled="commodities.includes(item?.key)">
                    {{ item?.name }}
                  </option>
                </select>
                <div class="flex justify-end space-x-2">
                  <button @click="showAddDialog = false" class="px-4 py-2 rounded bg-slate-200 text-slate-600 hover:bg-slate-300">取消</button>
                  <button @click="addCommodity" :disabled="!addKey || commodities.includes(addKey)" class="px-4 py-2 rounded bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50">添加</button>
                </div>
              </div>
            </div>
      
      <div class="p-4 border-t border-white/10 bg-black/10">
        <div class="flex items-center mb-4 px-2">
          <div class="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 mr-3 shadow-inner border border-white/20"></div>
          <div>
            <div class="text-sm font-bold text-slate-200">当前用户</div>
            <div class="text-xs text-emerald-400 flex items-center">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1.5 animate-pulse"></span>在线
            </div>
          </div>
        </div>
        <button @click="logout" class="w-full flex justify-center items-center px-4 py-2.5 rounded-lg text-sm text-slate-300 hover:text-white hover:bg-red-500/20 hover:border-red-500/30 border border-transparent transition-all">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>
          安全退出
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col overflow-hidden relative">
      <!-- Header -->
      <header class="h-20 bg-white/80 backdrop-blur-md shadow-sm border-b border-slate-200 flex items-center justify-between px-8 sticky top-0 z-20">
        <div class="flex items-center">
          <h2 class="text-2xl font-bold text-slate-800 tracking-tight">{{ getCommodityByKey(activeComm)?.name || activeComm }} <span class="font-normal text-slate-400 ml-2">深度行情分析</span></h2>
        </div>
        <div class="flex items-center space-x-4">
          <div class="bg-indigo-50 text-indigo-700 px-3 py-1.5 rounded-full text-sm font-semibold border border-indigo-100 flex items-center shadow-sm">
            <svg class="w-4 h-4 mr-1.5 text-indigo-500" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clip-rule="evenodd"></path></svg>
            DeepSeek 引擎就绪
          </div>
          <button @click="fetchData" class="p-2 text-slate-400 hover:text-indigo-600 hover:bg-slate-100 rounded-lg transition-colors" title="刷新数据">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
          </button>
        </div>
      </header>

      <!-- Dashboard Body -->
      <div class="flex-1 overflow-auto p-8 section-scroll">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          <!-- Chart Card -->
          <div class="lg:col-span-2 bg-white p-1 rounded-2xl shadow-sm border border-slate-200 relative overflow-hidden group hover:shadow-md transition-shadow">
            <div class="px-6 py-5 border-b border-slate-100 flex flex-col gap-2 bg-slate-50/50">
              <div class="flex justify-between items-center">
                <h3 class="text-lg font-bold text-slate-800 flex items-center">
                  <svg class="w-5 h-5 mr-2 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"></path></svg>
                  专业K线图及均线系统
                </h3>
                <!-- 周期切换按钮 -->
                <div class="flex space-x-2">
                  <button v-for="p in ['day','week','month']" :key="p" @click="changePeriod(p)"
                    :class="['px-3 py-1 rounded font-bold text-xs border transition', period===p ? 'bg-indigo-600 text-white border-indigo-700' : 'bg-white text-slate-600 border-slate-200 hover:bg-indigo-50']">
                    {{ p==='day'?'日K':p==='week'?'周K':'月K' }}
                  </button>
                </div>
              </div>
              <div class="flex flex-wrap items-center space-x-3 text-xs font-medium">
                <span class="flex items-center text-blue-500"><span class="w-2 h-2 rounded-full bg-blue-500 mr-1.5"></span>MA5</span>
                <span class="flex items-center text-amber-500"><span class="w-2 h-2 rounded-full bg-amber-500 mr-1.5"></span>MA10</span>
                <span class="flex items-center text-purple-500"><span class="w-2 h-2 rounded-full bg-purple-500 mr-1.5"></span>MA20</span>
                <!-- 预留多指标/对比入口 -->
                <span class="ml-4 text-slate-500">指标：</span>
                <label class="inline-flex items-center space-x-1 cursor-pointer">
                  <input type="checkbox" v-model="showBoll" class="rounded border-slate-300" />
                  <span class="text-[11px] text-slate-600">BOLL 布林带</span>
                </label>
                <span class="ml-4 text-slate-500">对比：</span>
                <select v-model="compareKey" @change="onCompareChange" class="border border-slate-300 rounded px-1 py-0.5 text-[11px] text-slate-700 bg-white">
                  <option value="">无</option>
                  <option v-for="(item, idx) in allCommodityList || []" :key="idx" :value="item?.key" v-if="item?.key !== activeComm">
                    {{ item?.name }}
                  </option>
                </select>
              </div>
            </div>
            <div class="p-4">
              <div v-if="chartLoading" class="absolute inset-0 z-10 bg-white/80 backdrop-blur-sm flex items-center justify-center">
                <div class="animate-spin rounded-full h-10 w-10 border-4 border-indigo-500 border-t-transparent"></div>
              </div>
              <div ref="chartRef" class="w-full h-[450px]"></div>
            </div>
          </div>

          <!-- News Card -->
          <div class="bg-white rounded-2xl shadow-sm border border-slate-200 flex flex-col overflow-hidden hover:shadow-md transition-shadow">
            <div class="px-6 py-5 border-b border-slate-100 bg-slate-50/50">
              <h3 class="text-lg font-bold text-slate-800 flex items-center">
                <svg class="w-5 h-5 mr-2 text-rose-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9.5a2.5 2.5 0 00-2.5-2.5H14"></path></svg>
                全球宏观异动监控
              </h3>
            </div>
            <div class="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
              <div v-if="newsLoading" class="h-full flex flex-col justify-center items-center text-slate-400">
                <div class="animate-pulse flex space-x-2 items-center">
                  <div class="h-2 w-2 bg-slate-400 rounded-full"></div>
                  <div class="h-2 w-2 bg-slate-400 rounded-full"></div>
                  <div class="h-2 w-2 bg-slate-400 rounded-full"></div>
                </div>
                <span class="text-sm mt-3">全网爬取中...</span>
              </div>
              <div v-else-if="news.length === 0" class="h-full flex items-center justify-center text-slate-400 text-sm">
                暂无最新情报
              </div>
              
              <div v-for="(item, idx) in news" :key="idx" class="p-3.5 rounded-xl border border-slate-100 bg-slate-50 hover:bg-indigo-50/50 hover:border-indigo-100 transition-colors group">
                <p class="text-sm text-slate-800 font-bold leading-relaxed mb-2 group-hover:text-indigo-900">{{ item.title }}</p>
                <div class="flex justify-between items-center mt-2">
                  <span class="text-xs font-semibold px-2 py-1 rounded bg-slate-200 text-slate-600 border border-slate-300">{{ item.source }}</span>
                  <span class="text-xs text-slate-400 flex items-center">
                    <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    实时
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- AI Report Card -->
        <div class="bg-white rounded-2xl shadow-sm border border-slate-200 hover:shadow-md transition-shadow flex flex-col relative overflow-hidden">
          <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500"></div>
          <div class="px-8 py-6 border-b border-slate-100 flex flex-col gap-4 bg-slate-50/50">
            <div class="flex justify-between items-center">
              <div>
                <h3 class="text-xl font-black text-slate-800 flex items-center tracking-tight">
                  <span class="text-2xl mr-3">🔮</span> DeepSeek 智能策略研报
                </h3>
                <p class="text-sm text-slate-500 mt-1 ml-9">聚合多维数据与宏观新闻，生成专业级行情预判与策略指导</p>
              </div>
              
              <button @click="generateReport" :disabled="reportLoading" class="relative inline-flex items-center justify-center px-6 py-3 font-bold text白 transition-all duration-200 bg-indigo-600 rounded-xl hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-600 disabled:opacity-70 shadow-lg shadow-indigo-600/30 overflow-hidden group">
              <span class="absolute inset-0 w-full h-full -mt-1 rounded-lg opacity-30 bg-gradient-to-b from-transparent via-transparent to-black"></span>
              <svg v-if="reportLoading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white relative" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              <svg v-else class="w-5 h-5 mr-2 relative" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
              <span class="relative">{{ reportLoading ? '多模型联合推理中...' : '一键生成策略研报' }}</span>
            </button>
            </div>

            <!-- 人物/风格选择 -->
            <div class="flex flex-wrap items-center gap-4 ml-9 text-xs text-slate-600">
              <div class="flex items-center gap-2">
                <span class="font-semibold text-slate-500">分析风格：</span>
                <select v-model="personaKey" class="border border-slate-300 rounded px-2 py-1 text-xs bg-white text-slate-700">
                  <option value="default">机构首席策略分析师（中性稳健）</option>
                  <option value="buffett">价值投资型股神（长期、重安全边际）</option>
                  <option value="soros">宏观对冲型高手（趋势/拐点敏感）</option>
                  <option value="dalio">全天候资产配置专家（风险平衡）</option>
                  <option value="custom">自定义人物人设</option>
                </select>
              </div>

              <div v-if="personaKey === 'custom'" class="flex flex-col sm:flex-row gap-3 flex-1">
                <input v-model="customPersonaName" type="text" placeholder="自定义人物名称，例如：XX 股神" class="flex-1 min-w-[120px] px-2 py-1 rounded border border-slate-300 bg-white text-xs" />
                <input v-model="customPersonaPrompt" type="text" placeholder="简要描述其性格、风险偏好和投资风格" class="flex-[2] min-w-[200px] px-2 py-1 rounded border border-slate-300 bg-white text-xs" />
              </div>

              <div class="flex items-center gap-2">
                <span class="font-semibold text-slate-500">生成模式：</span>
                <div class="inline-flex rounded-full bg-slate-100 p-0.5 border border-slate-200">
                  <button
                    type="button"
                    @click="reportMode = 'fast'"
                    :class="[
                      'px-3 py-1 text-[11px] rounded-full font-semibold transition-colors',
                      reportMode === 'fast'
                        ? 'bg-emerald-500 text-white shadow-sm'
                        : 'text-slate-600 hover:text-emerald-600'
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
                        ? 'bg-indigo-600 text-white shadow-sm'
                        : 'text-slate-600 hover:text-indigo-600'
                    ]"
                  >
                    📑 详尽
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <div class="p-8 min-h-[300px] relative">
            <!-- Loading State -->
            <div v-if="reportLoading" class="absolute inset-0 bg-white/80 backdrop-blur-sm flex flex-col items-center justify-center z-10">
              <div class="relative w-24 h-24 mb-6">
                <div class="absolute inset-0 rounded-full border-t-4 border-indigo-500 animate-[spin_1s_linear_infinite]"></div>
                <div class="absolute inset-2 rounded-full border-r-4 border-purple-500 animate-[spin_1.5s_linear_infinite_reverse]"></div>
                <div class="absolute inset-4 rounded-full border-b-4 border-pink-500 animate-[spin_2s_linear_infinite]"></div>
                <div class="absolute inset-0 flex items-center justify-center text-xl">🧠</div>
              </div>
              <p class="text-indigo-800 font-bold text-lg animate-pulse">DeepSeek 正在进行交叉推演...</p>
              <p class="text-slate-500 mt-2 text-sm">正在深度解析宏观关联与历史波幅</p>
            </div>
            
            <!-- Report Content -->
            <div v-else-if="reportHtml" class="prose prose-slate prose-indigo max-w-none w-full markdown-body bg-slate-50/50 p-8 rounded-xl border border-slate-100 shadow-inner" v-html="reportHtml"></div>
            
            <!-- Empty State -->
            <div v-else class="h-full flex flex-col items-center justify-center text-slate-400 py-12">
              <div class="w-24 h-24 bg-slate-100 rounded-full flex items-center justify-center mb-6 shadow-inner">
                <svg class="w-12 h-12 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
              </div>
              <p class="text-lg font-semibold text-slate-600 mb-2">等待指令生成专属分析</p>
              <p class="text-sm">点击上方按钮，基于最新行情与消息面输出深度见解</p>
            </div>
          </div>
        </div>

        <!-- 历史研报 / AI 对话 / 智能预警 -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-8">
          <!-- 历史研报 -->
          <div class="bg-white rounded-2xl shadow-sm border border-slate-200 flex flex-col overflow-hidden hover:shadow-md transition-shadow">
            <div class="px-6 py-4 border-b border-slate-100 bg-slate-50/60 flex items-center justify-between">
              <h3 class="text-sm font-bold text-slate-800 flex items-center">
                <span class="mr-2">📚</span> 历史策略研报
              </h3>
              <span class="text-xs text-slate-400">最近 5 条</span>
            </div>
            <div class="flex-1 p-4 space-y-3 custom-scrollbar max-h-80 overflow-y-auto">
              <div v-if="historyLoading" class="flex items-center justify-center text-slate-400 text-sm h-32">
                加载历史研报中...
              </div>
              <div v-else-if="!reportHistory.length" class="flex items-center justify-center text-slate-400 text-sm h-32">
                暂无历史研报，先生成一份吧
              </div>
              <div
                v-else
                v-for="item in reportHistory"
                :key="item.id"
                class="p-3 rounded-xl border border-slate-100 bg-slate-50 hover:bg-indigo-50/60 transition-colors cursor-pointer"
                @click="openHistoryReport(item)"
              >
                <div class="flex justify-between items-center mb-1">
                  <span class="text-xs font-semibold text-slate-500">{{ item.commodity }}</span>
                  <span class="text-[11px] text-slate-400">{{ item.created_at }}</span>
                </div>
                <p class="text-xs text-slate-700 leading-relaxed line-clamp-3 mb-2">
                  {{ (item.report || '').slice(0, 120) }}{{ (item.report || '').length > 120 ? '…' : '' }}
                </p>
                <div class="flex justify-between items-center mt-1 text-[11px]">
                  <button
                    class="px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 hover:bg-slate-200"
                    type="button"
                  >
                    查看完整研报
                  </button>
                  <button
                    type="button"
                    class="px-2 py-0.5 rounded-full border border-emerald-200 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 flex items-center gap-1"
                    @click.stop="sendHistoryReportEmail(item)"
                    :disabled="historyEmailSendingId === item.id"
                  >
                    <span v-if="historyEmailSendingId === item.id" class="w-3 h-3 border-2 border-emerald-600 border-t-transparent rounded-full animate-spin"></span>
                    <span v-else>发送到邮箱</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- AI 对话 -->
          <div class="bg-white rounded-2xl shadow-sm border border-slate-200 flex flex-col overflow-hidden hover:shadow-md transition-shadow">
            <div class="px-6 py-4 border-b border-slate-100 bg-slate-50/60 flex items-center justify-between">
              <h3 class="text-sm font-bold text-slate-800 flex items-center">
                <span class="mr-2">💬</span> AI 投研问答
              </h3>
              <span class="text-xs text-slate-400">围绕当前标的追问细节</span>
            </div>
            <div class="flex-1 flex flex-col">
              <div class="flex-1 p-4 space-y-2 custom-scrollbar max-h-64 overflow-y-auto">
                <div v-if="!chatMessages.length" class="h-full flex items-center justify-center text-slate-400 text-xs">
                  你可以就研报中的观点继续追问，例如“仓位怎么分层建？”
                </div>
                <div v-else v-for="(m, idx) in chatMessages" :key="idx" class="flex mb-1" :class="m.role === 'user' ? 'justify-end' : 'justify-start'">
                  <div :class="[
                    'px-3 py-2 rounded-2xl max-w-[80%] text-xs leading-relaxed',
                    m.role === 'user'
                      ? 'bg-indigo-600 text-white rounded-br-sm'
                      : 'bg-slate-100 text-slate-800 rounded-bl-sm'
                  ]">
                    {{ m.content }}
                  </div>
                </div>
              </div>
              <div class="p-3 border-t border-slate-100 bg-slate-50/80 flex items-center gap-2">
                <input
                  v-model="chatInput"
                  @keyup.enter.exact.prevent="sendChat"
                  type="text"
                  placeholder="就当前标的继续提问，例如：现在适合分批加仓吗？"
                  class="flex-1 px-3 py-2 text-xs rounded-xl border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
                <button
                  @click="sendChat"
                  :disabled="chatLoading || !chatInput.trim()"
                  class="px-3 py-2 rounded-xl text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-60 flex items-center gap-1"
                >
                  <span v-if="chatLoading" class="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                  <span v-else>发送</span>
                </button>
              </div>
            </div>
          </div>

          <!-- 智能预警 -->
          <div class="bg-white rounded-2xl shadow-sm border border-slate-200 flex flex-col overflow-hidden hover:shadow-md transition-shadow">
            <div class="px-6 py-4 border-b border-slate-100 bg-slate-50/60 flex items-center justify-between">
              <h3 class="text-sm font-bold text-slate-800 flex items-center">
                <span class="mr-2">⚠️</span> 智能技术面预警
              </h3>
              <div class="flex items-center gap-3">
                <button
                  @click="fetchAlerts"
                  class="text-[11px] text-indigo-600 hover:text-indigo-700 flex items-center"
                >
                  刷新
                </button>
                <button
                  @click="sendAlertEmail"
                  class="text-[11px] text-rose-600 hover:text-rose-700 flex items-center border border-rose-200 rounded-full px-2 py-0.5 bg-rose-50/60"
                >
                  邮件发送本次预警
                </button>
              </div>
            </div>
            <div class="flex-1 p-4 space-y-3 custom-scrollbar max-h-80 overflow-y-auto">
              <div v-if="alertsLoading" class="flex items-center justify-center text-slate-400 text-sm h-32">
                正在扫描自选品种的技术信号...
              </div>
              <div v-else-if="!alerts.length" class="flex items-center justify-center text-slate-400 text-sm h-32">
                暂无明显技术性预警
              </div>
              <div
                v-else
                v-for="(a, idx) in alerts"
                :key="idx"
                class="p-3 rounded-xl border text-xs"
                :class="a.level === 'warning' ? 'border-amber-200 bg-amber-50 text-amber-900' : 'border-emerald-200 bg-emerald-50 text-emerald-900'"
              >
                <div class="flex justify-between items-center mb-1">
                  <span class="font-semibold">{{ a.key?.toUpperCase() }}</span>
                  <span class="text-[10px] opacity-70">{{ a.time }}</span>
                </div>
                <p class="mb-1">{{ a.message }}</p>
                <div v-if="a.indicators" class="text-[10px] opacity-80">
                  指标：
                  <span v-for="(v, k) in a.indicators" :key="k" class="mr-1">
                    {{ k }}={{ v }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 量化预测与置信度仪表盘 -->
        <div class="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div class="bg-white rounded-2xl shadow-sm border border-slate-200 flex flex-col overflow-hidden hover:shadow-md transition-shadow lg:col-span-1">
            <div class="px-6 py-4 border-b border-slate-100 bg-slate-50/60 flex items-center justify-between">
              <h3 class="text-sm font-bold text-slate-800 flex items-center">
                <span class="mr-2">📈</span> 短期量化预测
              </h3>
              <button
                @click="fetchPrediction"
                class="text-[11px] text-indigo-600 hover:text-indigo-700 flex items-center border border-indigo-200 rounded-full px-2 py-0.5 bg-indigo-50/60"
              >
                生成预测
              </button>
            </div>
            <div class="p-5 space-y-4">
              <div v-if="predictLoading" class="flex items-center justify-center text-slate-400 text-sm h-24">
                正在分析近期走势与波动...
              </div>
              <div v-else-if="!predictData" class="text-xs text-slate-400 h-24 flex items-center justify-center text-center px-4">
                点击右上角“生成预测”，基于历史 K 线与技术指标给出未来 1–3 日方向与波动区间。
              </div>
              <div v-else class="space-y-4 text-xs text-slate-700">
                <div>
                  <div class="flex justify-between items-center mb-1">
                    <span class="font-semibold">短期方向（1–3 日）</span>
                    <span class="text-[11px] text-slate-500">
                      {{ predictData.short_term.direction === 'up' ? '上行概率更大' : predictData.short_term.direction === 'down' ? '下行概率更大' : '大概率区间震荡' }}
                    </span>
                  </div>
                  <div class="w-full h-2 rounded-full bg-slate-100 overflow-hidden">
                    <div
                      class="h-full rounded-full bg-gradient-to-r from-emerald-400 to-indigo-500"
                      :style="{ width: Math.round((predictData.short_term.confidence || 0) * 100) + '%' }"
                    ></div>
                  </div>
                  <div class="mt-1 text-[11px] text-slate-500">
                    置信度：{{ Math.round((predictData.short_term.confidence || 0) * 100) }}%
                  </div>
                </div>

                <div>
                  <div class="text-[11px] text-slate-500 mb-1">预期波动区间（未来 1–3 日，收益率）</div>
                  <div class="text-xs">
                    中枢：{{ (predictData.short_term.expected_return_pct_mean * 100).toFixed(2) }}%
                  </div>
                  <div class="text-xs">
                    区间：[
                    {{ (predictData.short_term.expected_return_pct_range[0] * 100).toFixed(2) }}%
                    ,
                    {{ (predictData.short_term.expected_return_pct_range[1] * 100).toFixed(2) }}%
                    ]
                  </div>
                </div>

                <div class="text-[11px] text-slate-500 leading-relaxed">
                  {{ predictData.short_term.explanation }}
                </div>

                <!-- 多模型视角对比：技术规则 vs ARIMA 计量模型 -->
                <div
                  v-if="predictData.short_term && predictData.short_term.models"
                  class="mt-3 border border-slate-200 rounded-xl bg-slate-50/80 p-3 space-y-2"
                >
                  <div class="flex items-center justify-between mb-1">
                    <span class="text-[11px] font-semibold text-slate-700 flex items-center">
                      <span class="mr-1">🧮</span> 多模型视角对比
                    </span>
                    <span class="text-[10px] text-slate-400">技术面规则引擎 vs ARIMA 计量模型</span>
                  </div>

                  <div class="grid grid-cols-2 gap-3 text-[11px] text-slate-600">
                    <!-- 技术规则视角 -->
                    <div class="border border-indigo-100 rounded-lg bg-white/80 p-2">
                      <div class="flex items-center justify-between mb-1">
                        <span class="font-semibold text-indigo-700">技术规则视角</span>
                        <span class="text-[10px] text-slate-400">权重 60%</span>
                      </div>
                      <div>
                        方向：
                        <span class="font-medium">
                          {{ predictData.short_term.models.technical?.direction === 'up'
                            ? '偏多'
                            : predictData.short_term.models.technical?.direction === 'down'
                            ? '偏空'
                            : '震荡' }}
                        </span>
                      </div>
                      <div>
                        置信度：
                        {{ Math.round((predictData.short_term.models.technical?.confidence || 0) * 100) }}%
                      </div>
                      <div>
                        区间：[
                        {{ (predictData.short_term.models.technical?.expected_return_pct_range?.[0] * 100).toFixed(2) }}%
                        ,
                        {{ (predictData.short_term.models.technical?.expected_return_pct_range?.[1] * 100).toFixed(2) }}%
                        ]
                      </div>
                    </div>

                    <!-- ARIMA 计量视角 -->
                    <div class="border border-emerald-100 rounded-lg bg-white/80 p-2">
                      <div class="flex items-center justify-between mb-1">
                        <span class="font-semibold text-emerald-700">ARIMA 计量视角</span>
                        <span class="text-[10px] text-slate-400">权重 40%</span>
                      </div>
                      <div v-if="predictData.short_term.models.arima">
                        <div>
                          方向：
                          <span class="font-medium">
                            {{ predictData.short_term.models.arima.direction === 'up'
                              ? '偏多'
                              : predictData.short_term.models.arima.direction === 'down'
                              ? '偏空'
                              : '震荡' }}
                          </span>
                        </div>
                        <div>
                          置信度：
                          {{ Math.round((predictData.short_term.models.arima.confidence || 0) * 100) }}%
                        </div>
                        <div>
                          区间：[
                          {{ (predictData.short_term.models.arima.expected_return_pct_range[0] * 100).toFixed(2) }}%
                          ,
                          {{ (predictData.short_term.models.arima.expected_return_pct_range[1] * 100).toFixed(2) }}%
                          ]
                        </div>
                      </div>
                      <div v-else class="text-[10px] text-slate-400 mt-1">
                        当前样本不足或拟合失败，ARIMA 视角暂未参与本次融合。
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-2xl shadow-sm border border-slate-200 flex flex-col overflow-hidden hover:shadow-md transition-shadow lg:col-span-2">
            <div class="px-6 py-4 border-b border-slate-100 bg-slate-50/60 flex items-center justify-between">
              <h3 class="text-sm font-bold text-slate-800 flex items-center">
                <span class="mr-2">⚡</span> 超短期波动评估（5–30 分钟）
              </h3>
            </div>
            <div class="p-5 text-xs text-slate-700">
              <div v-if="!predictData" class="text-slate-400 h-24 flex items-center justify-center text-center px-6">
                量化模块基于日频数据对 5–30 分钟的波动只给出方向性和强弱参考，需结合盘中成交与盘口自行判断，不构成交易指引。
              </div>
              <div v-else class="space-y-3">
                <div class="flex items-center justify-between">
                  <span class="font-semibold">方向判断</span>
                  <span class="text-[11px] text-slate-500">
                    {{ predictData.ultra_short_term.direction === 'up' ? '偏向短线上行' : predictData.ultra_short_term.direction === 'down' ? '偏向短线回落' : '短线更可能在窄幅内震荡' }}
                  </span>
                </div>
                <div>
                  <div class="text-[11px] text-slate-500 mb-1">置信度</div>
                  <div class="w-full h-2 rounded-full bg-slate-100 overflow-hidden">
                    <div
                      class="h-full rounded-full bg-gradient-to-r from-amber-400 to-rose-500"
                      :style="{ width: Math.round((predictData.ultra_short_term.confidence || 0) * 100) + '%' }"
                    ></div>
                  </div>
                  <div class="mt-1 text-[11px] text-slate-500">
                    置信度：{{ Math.round((predictData.ultra_short_term.confidence || 0) * 100) }}%
                  </div>
                </div>
                <div>
                  <div class="text-[11px] text-slate-500 mb-1">预期收益率区间（5–30 分钟）</div>
                  <div class="text-xs">
                    中枢：{{ (predictData.ultra_short_term.expected_return_pct_mean * 100).toFixed(3) }}%
                  </div>
                  <div class="text-xs">
                    区间：[
                    {{ (predictData.ultra_short_term.expected_return_pct_range[0] * 100).toFixed(3) }}%
                    ,
                    {{ (predictData.ultra_short_term.expected_return_pct_range[1] * 100).toFixed(3) }}%
                    ]
                  </div>
                </div>
                <div class="text-[11px] text-slate-500 leading-relaxed">
                  {{ predictData.ultra_short_term.explanation }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>

  <!-- 历史研报详情弹窗 -->
  <div
    v-if="selectedHistoryReport"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
  >
    <div class="bg-white rounded-2xl shadow-2xl w-[90%] max-w-4xl max-h-[85vh] flex flex-col overflow-hidden">
      <div class="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/80">
        <div class="flex flex-col">
          <div class="text-sm font-bold text-slate-800 flex items-center gap-2">
            <span class="text-indigo-500">📘 历史策略研报</span>
            <span class="text-slate-500 text-xs">{{ selectedHistoryReport.commodity }}</span>
          </div>
          <div class="text-[11px] text-slate-400 mt-0.5">
            生成时间：{{ selectedHistoryReport.created_at }}
          </div>
        </div>
        <div class="flex items-center gap-3">
          <button
            type="button"
            class="px-3 py-1.5 rounded-full border border-emerald-200 bg-emerald-50 text-emerald-700 text-[11px] flex items-center gap-1"
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
          class="prose prose-slate prose-indigo max-w-none w-full markdown-body bg-white p-6 rounded-xl border border-slate-100 shadow-inner"
          v-html="historyDetailHtml"
        ></div>
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
  window.addEventListener('resize', () => {
    if (chartInstance) chartInstance.resize()
  })
})
</script>

<style>
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