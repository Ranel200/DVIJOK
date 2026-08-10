import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

const MODES = ['waiting', 'loading', 'error']

export const useStatusOverlayStore = defineStore('statusOverlay', () => {
  const mode = ref(null)

  const isOpen = computed(() => Boolean(mode.value))

  function show(nextMode) {
    if (!MODES.includes(nextMode)) return
    mode.value = nextMode
  }

  function showWaiting() {
    show('waiting')
  }

  function showLoading() {
    show('loading')
  }

  function showError() {
    show('error')
  }

  function hide() {
    mode.value = null
  }

  function toggle(nextMode) {
    if (!MODES.includes(nextMode)) return
    mode.value = mode.value === nextMode ? null : nextMode
  }

  return {
    mode,
    isOpen,
    show,
    showWaiting,
    showLoading,
    showError,
    hide,
    toggle
  }
})
