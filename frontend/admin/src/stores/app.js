import { defineStore } from 'pinia'
import { ref } from 'vue'

// UI-состояние приложения (например, открытие бокового меню).
export const useAppStore = defineStore('app', () => {
  const sidebarOpen = ref(true)

  function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value
  }

  function setSidebar(value) {
    sidebarOpen.value = value
  }

  return {
    sidebarOpen,
    toggleSidebar,
    setSidebar
  }
})
