<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-900 via-indigo-900 to-purple-900">
    <div class="bg-white/10 backdrop-blur-lg p-8 rounded-2xl shadow-2xl w-96 border border-white/20">
      <div class="mb-8 text-center">
        <h2 class="text-3xl font-extrabold text-white tracking-wider mb-2">
          {{ isLogin ? '系统登录' : '创建账号' }}
        </h2>
        <p class="text-sm text-gray-300">
          {{ isLogin ? '全球大宗商品智能分析终端' : '加入并体验AI前沿分析' }}
        </p>
      </div>

      <!-- Tabs -->
      <div class="flex mb-6 bg-black/20 rounded-lg p-1">
        <button 
          @click="isLogin = true; error = ''; successMsg=''" 
          :class="['flex-1 py-2 text-sm font-semibold rounded-md transition-all', isLogin ? 'bg-blue-600 text-white shadow' : 'text-gray-400 hover:text-white']"
        >
          登录
        </button>
        <button 
          @click="isLogin = false; error = ''; successMsg=''" 
          :class="['flex-1 py-2 text-sm font-semibold rounded-md transition-all', !isLogin ? 'bg-blue-600 text-white shadow' : 'text-gray-400 hover:text-white']"
        >
          注册
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-5">
        <div>
          <label class="block text-sm font-medium text-gray-200 mb-1">用户名</label>
          <div class="relative">
            <span class="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">
              <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
            </span>
            <input v-model="form.username" type="text" required placeholder="请输入您的用户名" class="pl-10 block w-full rounded-lg bg-black/20 border-white/10 text-white placeholder-gray-400 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2.5 transition-colors">
          </div>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-200 mb-1">密码</label>
          <div class="relative">
            <span class="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">
              <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
            </span>
            <input v-model="form.password" type="password" required placeholder="请输入密码" class="pl-10 block w-full rounded-lg bg-black/20 border-white/10 text-white placeholder-gray-400 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2.5 transition-colors">
          </div>
        </div>

        <!-- 邮箱，仅注册时必填，用于接收智能告警邮件 -->
        <div v-if="!isLogin">
          <label class="block text-sm font-medium text-gray-200 mb-1">邮箱</label>
          <div class="relative">
            <span class="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">
              <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12H8m8-4H8m9-7H7a2 2 0 00-2 2v14a2 2 0 002 2h10a2 2 0 002-2V3a2 2 0 00-2-2z" /></svg>
            </span>
            <input v-model="form.email" type="email" required placeholder="用于接收智能告警邮件" class="pl-10 block w-full rounded-lg bg-black/20 border-white/10 text-white placeholder-gray-400 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2.5 transition-colors">
          </div>
        </div>

        <div v-if="error" class="bg-red-500/20 text-red-200 text-sm p-3 rounded-lg border border-red-500/50 flex items-center">
          <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path></svg>
          {{ error }}
        </div>
        
        <div v-if="successMsg" class="bg-green-500/20 text-green-200 text-sm p-3 rounded-lg border border-green-500/50 flex items-center">
          <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>
          {{ successMsg }}
        </div>

        <button type="submit" :disabled="loading" class="w-full flex justify-center py-3 px-4 rounded-lg shadow-lg text-sm font-bold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 focus:ring-offset-gray-900 disabled:opacity-50 transition-all transform hover:scale-[1.02]">
          <svg v-if="loading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          {{ loading ? '处理中...' : (isLogin ? '立即登录' : '立即注册') }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import request from '../api/request'

const router = useRouter()
const isLogin = ref(true)
const form = ref({ username: 'admin', password: 'admin123', email: '' })
const error = ref('')
const successMsg = ref('')
const loading = ref(false)

const handleSubmit = async () => {
  loading.value = true
  error.value = ''
  successMsg.value = ''
  
  if (isLogin.value) {
    try {
      const res = await request.post('/login', form.value)
      if (res.status === 'success') {
        localStorage.setItem('token', res.token)
        router.push('/')
      }
    } catch (err) {
      error.value = err.response?.data?.detail || '用户名或密码错误'
    }
  } else {
    try {
      const payload = { username: form.value.username, password: form.value.password, email: form.value.email }
      const res = await request.post('/register', payload)
      if (res.status === 'success') {
        successMsg.value = res.message
        setTimeout(() => {
          isLogin.value = true
          successMsg.value = ''
        }, 1500)
      }
    } catch (err) {
      error.value = err.response?.data?.detail || '注册失败，请检查输入'
    }
  }
  loading.value = false
}
</script>