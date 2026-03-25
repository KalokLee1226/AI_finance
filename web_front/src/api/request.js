import axios from 'axios'

const request = axios.create({
  baseURL: '/api', // Proxied to backend
  // 延长超时时间，避免 DeepSeek 大模型生成较长研报时前端过早超时
  timeout: 120000
})

request.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  res => res.data,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default request