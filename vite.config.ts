import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  base: process.env.GITHUB_ACTIONS ? '/financial_crisis_observer/' : '/',
})
