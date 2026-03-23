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
          v-for="(title, key) in commodities" 
          :key="key"
          @click="changeCommodity(key)"
          :class="['w-full flex items-center px-4 py-3.5 rounded-xl transition-all duration-300 font-medium group', activeComm === key ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-900/50' : 'text-slate-300 hover:bg-white/5 hover:text-white']"
        >
          <span class="w-8 h-8 rounded-lg flex items-center justify-center mr-3 transition-colors" :class="activeComm === key ? 'bg-white/20' : 'bg-white/5 group-hover:bg-white/10'">
            <span v-if="key === 'gold'">🥇</span>
            <span v-if="key === 'oil'">🛢️</span>
            <span v-if="key === 'silver'">🥈</span>
          </span>
          {{ title }}
        </button>
      </nav>
      
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
          <h2 class="text-2xl font-bold text-slate-800 tracking-tight">{{ commodities[activeComm] }} <span class="font-normal text-slate-400 ml-2">深度行情分析</span></h2>
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
            <div class="px-6 py-5 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
              <h3 class="text-lg font-bold text-slate-800 flex items-center">
                <svg class="w-5 h-5 mr-2 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"></path></svg>
                专业K线图及均线系统
              </h3>
              <div class="flex space-x-3 text-xs font-medium">
                <span class="flex items-center text-blue-500"><span class="w-2 h-2 rounded-full bg-blue-500 mr-1.5"></span>MA5</span>
                <span class="flex items-center text-amber-500"><span class="w-2 h-2 rounded-full bg-amber-500 mr-1.5"></span>MA10</span>
                <span class="flex items-center text-purple-500"><span class="w-2 h-2 rounded-full bg-purple-500 mr-1.5"></span>MA20</span>
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
          <div class="px-8 py-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
            <div>
              <h3 class="text-xl font-black text-slate-800 flex items-center tracking-tight">
                <span class="text-2xl mr-3">🔮</span> DeepSeek 智能策略研报
              </h3>
              <p class="text-sm text-slate-500 mt-1 ml-9">聚合多维数据与宏观新闻，生成专业级行情预判与策略指导</p>
            </div>
            
            <button @click="generateReport" :disabled="reportLoading" class="relative inline-flex items-center justify-center px-6 py-3 font-bold text-white transition-all duration-200 bg-indigo-600 rounded-xl hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-600 disabled:opacity-70 shadow-lg shadow-indigo-600/30 overflow-hidden group">
              <span class="absolute inset-0 w-full h-full -mt-1 rounded-lg opacity-30 bg-gradient-to-b from-transparent via-transparent to-black"></span>
              <svg v-if="reportLoading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white relative" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              <svg v-else class="w-5 h-5 mr-2 relative" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
              <span class="relative">{{ reportLoading ? '多模型联合推理中...' : '一键生成策略研报' }}</span>
            </button>
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
      </div>
    </main>
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

const commodities = {
  gold: '国际黄金 (XAU/USD)',
  oil: 'WTI原油 (CL=F)',
  silver: '国际白银 (XAG/USD)'
}
const activeComm = ref('gold')

const news = ref([])
const newsLoading = ref(false)
const reportHtml = ref('')
const reportLoading = ref(false)
const chartLoading = ref(false)

const changeCommodity = (key) => {
  activeComm.value = key
  reportHtml.value = ''
  fetchData()
}

const fetchData = async () => {
  chartLoading.value = true
  try {
    const res = await request.get(`/market-data/${activeComm.value}`)
    renderChart(res)
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
    news.value = res.news
  } catch (err) {
    console.error(err)
  } finally {
    newsLoading.value = false
  }
}

const generateReport = async () => {
  reportLoading.value = true
  try {
    const res = await request.post('/generate-report', { commodity: commodities[activeComm.value] })
    reportHtml.value = marked.parse(res.report)
  } catch (err) {
    console.error(err)
    alert('AI 调用失败。请确保后端DeepSeek Key正确。')
  } finally {
    reportLoading.value = false
  }
}

const renderChart = (data) => {
  nextTick(() => {
    if (!chartInstance) {
      chartInstance = echarts.init(chartRef.value)
    }
    const upColor = '#ef4444';
    const downColor = '#10b981';

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
          data: data.dates,
          boundaryGap: false,
          axisLine: { onZero: false, lineStyle: { color: '#cbd5e1' } },
          axisLabel: { color: '#64748b' },
          splitLine: { show: false }
        },
        {
          type: 'category',
          gridIndex: 1,
          data: data.dates,
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
          data: data.kline,
          itemStyle: { color: upColor, color0: downColor, borderColor: upColor, borderColor0: downColor },
        },
        { name: 'MA5', type: 'line', data: data.ma5, smooth: true, showSymbol: false, lineStyle: { opacity: 0.8, color: '#3b82f6', width: 2 } },
        { name: 'MA10', type: 'line', data: data.ma10, smooth: true, showSymbol: false, lineStyle: { opacity: 0.8, color: '#f59e0b', width: 2 } },
        { name: 'MA20', type: 'line', data: data.ma20, smooth: true, showSymbol: false, lineStyle: { opacity: 0.8, color: '#8b5cf6', width: 2 } },
        {
          name: '成交量',
          type: 'bar',
          xAxisIndex: 1,
          yAxisIndex: 1,
          data: data.volumes.map((vol, idx) => {
             const k = data.kline[idx];
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

onMounted(() => {
  fetchData()
  fetchNews()
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