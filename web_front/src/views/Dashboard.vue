<template>
  <div class="auth-shell">
    <!-- 全屏粒子背景画布 -->
    <canvas ref="bgCanvas" class="bg-canvas"></canvas>
    <!-- 顶部导航 -->
    <nav class="nav">
      <a class="nav-logo" href="javascript:void(0)">
        <svg viewBox="0 0 32 32" fill="none">
          <rect width="32" height="32" rx="6" fill="#0a0a0a" />
          <path
            d="M10 8L16 24L22 8"
            stroke="white"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
            fill="none"
          />
          <circle cx="16" cy="16" r="2" fill="white" opacity="0.5" />
        </svg>
        <span class="nav-logo-text">Global Commodity AI Analyzer Pro</span>
      </a>
    </nav>

    <!-- 右下角产品优势文案 -->
    <div class="feat-float">
      <div class="feat-tag"><span class="feat-dot"></span> 全球大宗商品一站式监控</div>
      <div class="feat-tag"><span class="feat-dot"></span> AI 驱动多因子量化研判</div>
      <div class="feat-tag"><span class="feat-dot"></span> 实时风险告警与交易洞察</div>
    </div>

    <div class="footer">© 2026 Vitality AI · All Rights Reserved</div>

    <!-- 主内容 -->
    <main class="page">
      <!-- 左侧宣传文案 -->
      <section class="hero-text">
        <div class="hero-tagline">NEXT GENERATION AI PLATFORM</div>
        <h1 class="hero-title">
          JUST
          <em>CREATE</em>
          IT.
        </h1>
        <p class="hero-desc">
          用 AI 赋能每一位交易与研究者，让灵感不再受限，让每一个想法都能被量化与验证。
        </p>
        <div class="hero-line"></div>
      </section>

      <!-- 中间黑色登录卡片 -->
      <section class="card">
        <div class="card-top">
          <div class="card-logo">
            <div class="card-logo-mark">
              <svg viewBox="0 0 32 32" fill="none">
                <rect width="32" height="32" rx="10" fill="#0a0a0a" />
                <path
                  d="M11 9L16 23L21 9"
                  stroke="white"
                  stroke-width="2.3"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  fill="none"
                />
              </svg>
            </div>
            <div class="card-logo-name">GLOBAL COMMODITY AI ANALYZER PRO</div>
          </div>
          <div class="card-badge">SECURE</div>
        </div>

        <!-- Tab 切换 -->
        <div class="tabs">
          <button
            type="button"
            class="tab"
            :class="{ active: isLogin }"
            @click="switchMode(true)"
          >
            登录
          </button>
          <button
            type="button"
            class="tab"
            :class="{ active: !isLogin }"
            @click="switchMode(false)"
          >
            注册
          </button>
        </div>

        <!-- 步骤条（注册时亮更多步） -->
        <div class="steps">
          <div class="step-seg" :class="{ on: true }"></div>
          <div class="step-seg" :class="{ on: !isLogin }"></div>
          <div class="step-seg" :class="{ on: !isLogin }"></div>
        </div>

        <!-- 表单 -->
        <form class="form show" @submit.prevent="handleSubmit">
          <div class="field">
            <label class="field-label">账号</label>
            <input
              v-model="form.username"
              type="text"
              required
              :placeholder="isLogin ? '手机号 / 邮箱 / 用户名' : '为你的账号取一个名字'"
            />
            <span class="field-icon">👤</span>
          </div>

          <div class="field">
            <label class="field-label">密码</label>
            <input
              :type="showPassword ? 'text' : 'password'"
              v-model="form.password"
              required
              placeholder="请输入密码"
            />
            <span class="field-icon">🔒</span>
            <button
              type="button"
              class="eye-toggle"
              @click="showPassword = !showPassword"
            >
              {{ showPassword ? 'HIDE' : 'SHOW' }}
            </button>
          </div>

          <div v-if="!isLogin" class="field">
            <label class="field-label">邮箱</label>
            <input
              v-model="form.email"
              type="email"
              required
              placeholder="用于接收智能告警与通知"
            />
            <span class="field-icon">✉️</span>
          </div>

          <div class="quick">
            <label class="check-label">
              <input type="checkbox" v-model="remember" />
              <span>记住我</span>
            </label>
            <button type="button" class="link-gray">忘记密码？</button>
          </div>

          <div v-if="error" class="msg msg-error">{{ error }}</div>
          <div v-if="successMsg" class="msg msg-success">{{ successMsg }}</div>

          <button type="submit" class="btn-main" :disabled="loading">
            <span v-if="!loading">{{ isLogin ? 'LOG IN' : 'CREATE ACCOUNT' }}</span>
            <span v-else>处理中…</span>
          </button>
          <div class="agree">
            登录/注册即表示同意
            <a href="javascript:void(0)">用户服务协议</a>
            与
            <a href="javascript:void(0)">隐私政策</a>
          </div>
        </form>
      </section>

      <div></div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import request from '../api/request'

const router = useRouter()
const isLogin = ref(true)
const form = ref({ username: 'admin', password: 'admin123', email: '' })
const error = ref('')
const successMsg = ref('')
const loading = ref(false)
const showPassword = ref(false)
const remember = ref(false)
const bgCanvas = ref(null)

const switchMode = (loginMode) => {
  if (isLogin.value === loginMode) return
  isLogin.value = loginMode
  error.value = ''
  successMsg.value = ''
}

const handleSubmit = async () => {
  if (loading.value) return
  loading.value = true
  error.value = ''
  successMsg.value = ''

  try {
    if (isLogin.value) {
      const res = await request.post('/login', form.value)
      if (res.status === 'success') {
        localStorage.setItem('token', res.token)
        if (remember.value) {
          localStorage.setItem('remember_username', form.value.username)
        } else {
          localStorage.removeItem('remember_username')
        }
        router.push('/')
      }
    } else {
      const payload = {
        username: form.value.username,
        password: form.value.password,
        email: form.value.email
      }
      const res = await request.post('/register', payload)
      if (res.status === 'success') {
        successMsg.value = res.message || '注册成功，请使用账号登录'
        setTimeout(() => {
          isLogin.value = true
          successMsg.value = ''
        }, 1500)
      }
    }
  } catch (err) {
    if (isLogin.value) {
      error.value = err?.response?.data?.detail || '用户名或密码错误'
    } else {
      error.value = err?.response?.data?.detail || '注册失败，请检查输入'
    }
  } finally {
    loading.value = false
  }
}

// 读取记住的用户名（如有）
const savedName = localStorage.getItem('remember_username')
if (savedName) {
  form.value.username = savedName
  remember.value = true
}

// 粒子背景动画（改写自静态 login.html）
let ctx
let W = 0
let H = 0
let pts = []
let blobs = []
let ripples = []
let bursts = []
let frameId
let mx = -9999
let my = -9999
let lastAutoBurst = 0

const PAL = [
  [10, 10, 10],
  [80, 80, 80],
  [140, 140, 140],
  [200, 200, 200],
  [0, 180, 200],
  [100, 160, 255]
]

const rc = () => PAL[Math.floor(Math.random() * PAL.length)]

class P {
  constructor () {
    this.init(true)
  }

  init (first = false) {
    this.x = first ? Math.random() * W : (Math.random() < 0.5 ? -2 : W + 2)
    this.y = first ? Math.random() * H : Math.random() * H
    this.r = Math.random() * 1.8 + 0.4
    this.vx = (Math.random() - 0.5) * 0.7
    this.vy = (Math.random() - 0.5) * 0.7
    this.col = rc()
    this.maxA = Math.random() * 0.55 + 0.1
    this.a = 0
    this.life = Math.random() * 350 + 120
    this.age = 0
    this.trail = []
  }

  update () {
    if (this.x < 0 || this.x > W) this.vx *= -1
    if (this.y < 0 || this.y > H) this.vy *= -1
    const spd = Math.sqrt(this.vx * this.vx + this.vy * this.vy)
    if (spd > 1.2) {
      this.vx *= 0.95
      this.vy *= 0.95
    }
    this.x += this.vx
    this.y += this.vy
    this.age++
    const t = this.age / this.life
    this.a = t < 0.1 ? this.maxA * (t / 0.1) : t > 0.8 ? this.maxA * ((1 - t) / 0.2) : this.maxA
    if (spd > 0.4) {
      this.trail.push({ x: this.x, y: this.y })
      if (this.trail.length > 10) this.trail.shift()
    }
    if (this.age > this.life) this.init()
  }

  draw () {
    const [r, g, b] = this.col
    this.trail.forEach((t, i) => {
      const fa = this.a * (i / this.trail.length) * 0.4
      if (fa < 0.01) return
      ctx.save()
      ctx.globalAlpha = fa
      ctx.fillStyle = `rgb(${r},${g},${b})`
      ctx.beginPath()
      ctx.arc(t.x, t.y, this.r * 0.5, 0, Math.PI * 2)
      ctx.fill()
      ctx.restore()
    })

    ctx.save()
    ctx.globalAlpha = this.a
    ctx.shadowColor = `rgba(${r},${g},${b},.6)`
    ctx.shadowBlur = this.r * 5
    ctx.fillStyle = `rgb(${r},${g},${b})`
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2)
    ctx.fill()
    ctx.restore()
  }
}

class Blob {
  constructor () {
    this.reset()
  }

  reset () {
    this.x = Math.random() * W
    this.y = Math.random() * H
    this.r = Math.random() * 220 + 80
    this.c = PAL[Math.floor(Math.random() * 3)]
    this.a = Math.random() * 0.025 + 0.008
    this.vx = (Math.random() - 0.5) * 0.35
    this.vy = (Math.random() - 0.5) * 0.35
    this.life = Math.random() * 500 + 200
    this.age = 0
  }

  update () {
    this.x += this.vx
    this.y += this.vy
    this.age++
    if (this.x < -this.r || this.x > W + this.r) this.vx *= -1
    if (this.y < -this.r || this.y > H + this.r) this.vy *= -1
    if (this.age > this.life) this.reset()
  }

  draw () {
    const [r, g, b] = this.c
    const gd = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.r)
    gd.addColorStop(0, `rgba(${r},${g},${b},${this.a})`)
    gd.addColorStop(1, `rgba(${r},${g},${b},0)`)
    ctx.save()
    ctx.fillStyle = gd
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2)
    ctx.fill()
    ctx.restore()
  }
}

class Ripple {
  constructor (x, y) {
    this.x = x
    this.y = y
    this.r = 0
    this.maxR = Math.random() * 80 + 40
    this.life = 40
    this.age = 0
  }

  update () {
    this.r = this.maxR * (this.age / this.life)
    this.age++
  }

  draw () {
    const a = (1 - this.age / this.life) * 0.5
    ctx.save()
    ctx.globalAlpha = a
    ctx.strokeStyle = 'rgba(0,0,0,0.6)'
    ctx.lineWidth = 1
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2)
    ctx.stroke()
    ctx.restore()
  }
}

class Burst {
  constructor (x, y) {
    this.x = x
    this.y = y
    const a = Math.random() * Math.PI * 2
    const s = Math.random() * 5 + 1.5
    this.vx = Math.cos(a) * s
    this.vy = Math.sin(a) * s
    this.r = Math.random() * 2 + 0.5
    this.col = rc()
    this.a = 1
    this.life = 50
    this.age = 0
  }

  update () {
    this.x += this.vx
    this.y += this.vy
    this.vx *= 0.93
    this.vy *= 0.93
    this.age++
    this.a = 1 - this.age / this.life
  }

  draw () {
    const [r, g, b] = this.col
    ctx.save()
    ctx.globalAlpha = this.a
    ctx.shadowColor = `rgba(${r},${g},${b},.8)`
    ctx.shadowBlur = 8
    ctx.fillStyle = `rgb(${r},${g},${b})`
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2)
    ctx.fill()
    ctx.restore()
  }
}

function drawWeb (points) {
  for (let i = 0; i < points.length; i++) {
    for (let j = i + 1; j < points.length; j++) {
      const dx = points[i].x - points[j].x
      const dy = points[i].y - points[j].y
      const d = Math.sqrt(dx * dx + dy * dy)
      if (d > 110) continue
      const a = (1 - d / 110) * 0.12
      ctx.save()
      ctx.globalAlpha = a
      const gd = ctx.createLinearGradient(points[i].x, points[i].y, points[j].x, points[j].y)
      const [r1, g1, b1] = points[i].col
      const [r2, g2, b2] = points[j].col
      gd.addColorStop(0, `rgb(${r1},${g1},${b1})`)
      gd.addColorStop(1, `rgb(${r2},${g2},${b2})`)
      ctx.strokeStyle = gd
      ctx.lineWidth = 0.6
      ctx.beginPath()
      ctx.moveTo(points[i].x, points[i].y)
      ctx.lineTo(points[j].x, points[j].y)
      ctx.stroke()
      ctx.restore()
    }
  }
}

const resize = () => {
  if (!bgCanvas.value || !ctx) return
  W = bgCanvas.value.width = window.innerWidth
  H = bgCanvas.value.height = window.innerHeight
}

const handleMouseMove = (e) => {
  mx = e.clientX
  my = e.clientY
  pts.forEach(p => {
    const dx = p.x - mx
    const dy = p.y - my
    const d = Math.sqrt(dx * dx + dy * dy)
    if (d < 100 && d > 0) {
      p.vx += (dx / d) * 0.1
      p.vy += (dy / d) * 0.1
    }
  })
}

const handleClick = (e) => {
  for (let i = 0; i < 3; i++) ripples.push(new Ripple(e.clientX, e.clientY))
  for (let i = 0; i < 24; i++) bursts.push(new Burst(e.clientX, e.clientY))
}

const loop = () => {
  frameId = requestAnimationFrame(loop)
  if (!ctx) return
  ctx.clearRect(0, 0, W, H)

  blobs.forEach(b => { b.update(); b.draw() })
  drawWeb(pts)
  pts.forEach(p => { p.update(); p.draw() })

  // 周期性自动轻微爆散，让画面始终有细腻流动感
  const now = Date.now()
  if (!lastAutoBurst) {
    lastAutoBurst = now
  } else if (now - lastAutoBurst > 4500) {
    const cx = W * (0.3 + Math.random() * 0.4)
    const cy = H * (0.3 + Math.random() * 0.4)
    for (let i = 0; i < 2; i++) ripples.push(new Ripple(cx, cy))
    for (let i = 0; i < 14; i++) bursts.push(new Burst(cx, cy))
    lastAutoBurst = now
  }

  if (mx > -100) {
    const gd = ctx.createRadialGradient(mx, my, 0, mx, my, 70)
    gd.addColorStop(0, 'rgba(0,0,0,0.05)')
    gd.addColorStop(1, 'rgba(0,0,0,0)')
    ctx.save()
    ctx.fillStyle = gd
    ctx.beginPath()
    ctx.arc(mx, my, 70, 0, Math.PI * 2)
    ctx.fill()
    ctx.restore()
  }

  ripples = ripples.filter(r => r.age < r.life)
  ripples.forEach(r => { r.update(); r.draw() })
  bursts = bursts.filter(b => b.age < b.life)
  bursts.forEach(b => { b.update(); b.draw() })
}

onMounted(() => {
  const canvas = bgCanvas.value
  if (!canvas) return
  ctx = canvas.getContext('2d')
  resize()

  pts = Array.from({ length: 130 }, () => new P())
  blobs = Array.from({ length: 6 }, () => new Blob())
  ripples = []
  bursts = []

  window.addEventListener('resize', resize)
  window.addEventListener('mousemove', handleMouseMove)
  window.addEventListener('click', handleClick)
  loop()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  window.removeEventListener('mousemove', handleMouseMove)
  window.removeEventListener('click', handleClick)
  if (frameId) cancelAnimationFrame(frameId)
})
</script>

<style scoped>
.auth-shell {
  min-height: 100vh;
  background: #ffffff;
  font-family: 'Helvetica Neue', 'Microsoft Yahei', Arial, sans-serif;
  color: #0a0a0a;
  position: relative;
}

.auth-shell {
  --white: #ffffff;
  --black: #0a0a0a;
  --gray1: #f5f5f5;
  --gray2: #e8e8e8;
  --gray3: #999999;
  --gray4: #555555;
  --accent: #111111;
}

.bg-canvas {
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
  z-index: 0;
}

.nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 48px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--gray2);
  z-index: 10;
}

.nav-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
}

.nav-logo svg {
  width: 32px;
  height: 32px;
}

.nav-logo-text {
  font-size: 15px;
  font-weight: 800;
  color: var(--black);
  letter-spacing: 2px;
  text-transform: uppercase;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 32px;
}

.nav-links a {
  font-size: 12px;
  font-weight: 600;
  color: var(--gray3);
  text-decoration: none;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  transition: color 0.2s;
}

.nav-links a:hover {
  color: var(--black);
}

.nav-badge {
  font-size: 11px;
  font-weight: 700;
  color: var(--gray3);
  border: 1px solid var(--gray2);
  border-radius: 20px;
  padding: 5px 14px;
  letter-spacing: 1px;
}

.stat-float {
  position: fixed;
  left: 40px;
  bottom: 40px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 5;
}

.stat-item {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.stat-num {
  font-size: 26px;
  font-weight: 900;
  color: var(--black);
  line-height: 1;
  letter-spacing: -1px;
}

.stat-label {
  font-size: 11px;
  color: var(--gray3);
  letter-spacing: 1px;
  text-transform: uppercase;
}

.feat-float {
  position: fixed;
  right: 40px;
  bottom: 40px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  z-index: 5;
  align-items: flex-end;
}

.feat-tag {
  font-size: 11px;
  font-weight: 600;
  color: var(--gray4);
  letter-spacing: 1.5px;
  text-transform: uppercase;
  display: flex;
  align-items: center;
  gap: 7px;
}

.feat-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--black);
}

.footer {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 11px;
  color: var(--gray2);
  letter-spacing: 2px;
  text-transform: uppercase;
  white-space: nowrap;
}

.page {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr 480px 1fr;
  align-items: center;
  padding-top: 64px;
}

.hero-text {
  padding: 0 0 0 80px;
}

.hero-tagline {
  font-size: 11px;
  font-weight: 700;
  color: var(--gray3);
  letter-spacing: 4px;
  text-transform: uppercase;
  margin-bottom: 18px;
}

.hero-title {
  font-size: clamp(36px, 4vw, 64px);
  font-weight: 900;
  color: var(--black);
  line-height: 1.05;
  letter-spacing: -2px;
  text-transform: uppercase;
}

.hero-title em {
  font-style: normal;
  display: block;
  color: var(--gray3);
  font-weight: 300;
}

.hero-desc {
  margin-top: 20px;
  font-size: 13px;
  color: var(--gray3);
  line-height: 1.8;
  max-width: 320px;
  letter-spacing: 0.3px;
}

.hero-line {
  width: 40px;
  height: 2px;
  background: var(--black);
  margin-top: 30px;
}

.card {
  background: var(--black);
  border-radius: 0;
  padding: 52px 48px 44px;
  position: relative;
  box-shadow: 0 40px 80px rgba(0, 0, 0, 0.18), 0 8px 24px rgba(0, 0, 0, 0.12);
  overflow: hidden;
  color: #ffffff;
}

.card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.15), transparent);
}

.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 36px;
}

.card-logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-logo-mark {
  width: 36px;
  height: 36px;
  border: 1.5px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.card-logo-mark svg {
  width: 18px;
  height: 18px;
}

.card-logo-name {
  font-size: 12px;
  font-weight: 800;
  color: rgba(255, 255, 255, 1);
  letter-spacing: 2.5px;
  text-transform: uppercase;
}

.card-badge {
  font-size: 10px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 4px;
  padding: 3px 8px;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.tabs {
  display: flex;
  gap: 0;
  margin-bottom: 32px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.18);
}

.tab {
  flex: 1;
  background: none;
  border: none;
  cursor: pointer;
  padding: 12px 0;
  font-size: 12px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.5);
  letter-spacing: 2px;
  text-transform: uppercase;
  position: relative;
  transition: color 0.3s;
}

.tab::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--white);
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.tab.active {
  color: var(--white);
}

.tab.active::after {
  transform: scaleX(1);
}

.steps {
  display: flex;
  gap: 4px;
  margin-bottom: 24px;
}

.step-seg {
  flex: 1;
  height: 2px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
  transition: background 0.4s ease;
}

.step-seg.on {
  background: var(--white);
}

.field {
  margin-bottom: 14px;
  position: relative;
}

.field-label {
  display: block;
  font-size: 10px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.65);
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-bottom: 7px;
}

.field input {
  width: 100%;
  padding: 14px 16px 14px 42px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 4px;
  color: #ffffff;
  font-size: 14px;
  outline: none;
  transition: border-color 0.25s, background 0.25s;
}

.field input::placeholder {
  color: rgba(255, 255, 255, 0.4);
  font-size: 13px;
}

.field input:focus {
  border-color: rgba(255, 255, 255, 0.7);
  background: rgba(255, 255, 255, 0.15);
}

.field input:not(:placeholder-shown) {
  color: rgba(255, 255, 255, 0.96);
}

.field-icon {
  position: absolute;
  left: 14px;
  bottom: 14px;
  opacity: 0.6;
  font-size: 14px;
}

.eye-toggle {
  position: absolute;
  right: 14px;
  bottom: 12px;
  background: none;
  border: none;
  cursor: pointer;
  opacity: 0.5;
  padding: 2px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.8);
}

.eye-toggle:hover {
  opacity: 0.9;
}

.quick {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
  margin-top: 4px;
}

.check-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
}

.check-label input[type='checkbox'] {
  width: 13px;
  height: 13px;
}

.link-gray {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  background: none;
  border: none;
  cursor: pointer;
}

.link-gray:hover {
  color: rgba(255, 255, 255, 0.95);
}

.msg {
  font-size: 12px;
  padding: 10px 12px;
  border-radius: 4px;
  margin-bottom: 12px;
}

.msg-error {
  background: rgba(255, 64, 64, 0.16);
  border: 1px solid rgba(255, 64, 64, 0.4);
  color: #ff8a8a;
}

.msg-success {
  background: rgba(76, 209, 149, 0.16);
  border: 1px solid rgba(76, 209, 149, 0.4);
  color: #9cf2c8;
}

.btn-main {
  display: block;
  width: 100%;
  padding: 16px 0;
  background: var(--white);
  border: none;
  border-radius: 4px;
  color: var(--black);
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 3px;
  text-transform: uppercase;
  cursor: pointer;
  margin-bottom: 24px;
  position: relative;
  overflow: hidden;
}

.btn-main[disabled] {
  opacity: 0.6;
  cursor: default;
}

.btn-main::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(0, 0, 0, 0.12), transparent);
  transform: translateX(-100%);
  transition: transform 0.5s ease;
}

.btn-main:hover:not([disabled])::before {
  transform: translateX(100%);
}

.sep {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
}

.sep::before,
.sep::after {
  content: '';
  flex: 1;
  height: 1px;
  background: rgba(255, 255, 255, 0.18);
}

.sep span {
  font-size: 10px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.5);
  letter-spacing: 2px;
  text-transform: uppercase;
}

.socials {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-bottom: 24px;
}

.soc-btn {
  width: 44px;
  height: 44px;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.22);
  background: rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #ffffff;
  font-size: 14px;
}

.soc-btn:hover {
  border-color: rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.16);
}

.agree {
  text-align: center;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.45);
  line-height: 1.8;
}

.agree a {
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
}

.agree a:hover {
  color: rgba(255, 255, 255, 0.95);
}

/* 取消点击时默认白色聚焦描边，避免出现突兀白框 */
button,
button:focus,
button:focus-visible,
input:focus,
input:focus-visible {
  outline: none;
}

@media (max-width: 960px) {
  .page {
    grid-template-columns: 0 1fr 0;
  }

  .hero-text {
    display: none;
  }

  .stat-float,
  .feat-float {
    display: none;
  }

  .card {
    margin: 80px 20px 20px;
  }
}
</style>
