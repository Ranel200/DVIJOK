<template>
  <q-drawer :width="233" :breakpoint="0" :model-value="true" class="admin-sidebar-drawer">
    <div class="admin-sidebar">
      <div class="admin-sidebar__logo">
        <img src="/admin/icons/auth/logo.png" alt="DVIJOK" />
      </div>

      <nav class="admin-sidebar__nav">
        <ul ref="listEl" class="admin-sidebar__list">
          <li class="admin-sidebar__indicator" :style="indicatorStyle" aria-hidden="true"></li>
          <li
            v-for="item in visibleNavigation"
            :key="item.label"
            :ref="el => setItemRef(el, item)"
            :class="[
              'admin-sidebar__item',
              { 'admin-sidebar__item--active': isActive(item) },
              { 'admin-sidebar__item--pin': item.pinBottom }
            ]"
          >
            <router-link :to="item.to" class="admin-sidebar__link">
              <span class="admin-sidebar__icon">
                <img :src="item.icon" alt="" />
              </span>
              <span class="admin-sidebar__label">{{ item.label }}</span>
            </router-link>
          </li>
        </ul>
      </nav>

      <button
        type="button"
        class="admin-sidebar__logout"
        :disabled="logoutLoading"
        @click="onLogout"
      >
        {{ logoutLoading ? 'Выход...' : 'Выйти' }}
      </button>

      <div class="admin-sidebar__user">
        <div class="admin-sidebar__avatar">{{ initials }}</div>
        <p class="admin-sidebar__user-text">{{ userText }}</p>
      </div>
    </div>
  </q-drawer>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth.js'
import { adminNavigation } from '@/constants/navigation.js'
import { STAFF_ACCESS_KEYS } from '@/constants/staff.js'
import { getInitials, getShortName } from '@/utils/name.js'

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()

const { user } = storeToRefs(authStore)
const logoutLoading = ref(false)

const visibleNavigation = computed(() =>
  adminNavigation.filter(item => {
    const routeName = item.to?.name
    if (STAFF_ACCESS_KEYS.includes(routeName)) return authStore.canAccess(routeName)
    return true
  })
)

const initials = computed(() => getInitials(user.value?.name))
const userText = computed(() => {
  if (!user.value) return ''
  const short = getShortName(user.value.name)
  return user.value.role ? `${short} — ${user.value.role}` : short
})

const itemRefs = {}
const indicator = reactive({ y: 0, h: 0, ready: false })
const listEl = ref(null)

function setItemRef(el, item) {
  if (el) itemRefs[item.to.name] = el
  else delete itemRefs[item.to.name]
}

function isActive(item) {
  return route.name === item.to.name
}

function updateIndicator() {
  const el = itemRefs[route.name]
  if (!el) {
    indicator.ready = false
    return
  }
  indicator.y = el.offsetTop
  indicator.h = el.offsetHeight
  indicator.ready = true
}

const indicatorStyle = computed(() => ({
  transform: `translateY(${indicator.y}px)`,
  height: `${indicator.h}px`,
  opacity: indicator.ready ? 1 : 0
}))

async function onLogout() {
  if (logoutLoading.value) return
  logoutLoading.value = true
  try {
    await authStore.logout()
  } finally {
    logoutLoading.value = false
    await router.replace({ name: 'login' })
  }
}

watch(
  () => [route.name, visibleNavigation.value],
  () => nextTick(updateIndicator)
)

let resizeObserver
onMounted(() => {
  nextTick(updateIndicator)
  resizeObserver = new ResizeObserver(() => updateIndicator())
  if (listEl.value) resizeObserver.observe(listEl.value)
})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
})
</script>

<style scoped lang="scss">
.admin-sidebar-drawer {
  background-color: var(--dvijok-bg-dark);
  border-right: none;
  box-shadow: none;
}

.admin-sidebar {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 30px;
  height: 100%;
  padding: 44px 15px 20px;
  background-color: var(--dvijok-bg-dark);
}

.admin-sidebar__logo {
  width: 100%;

  img {
    display: block;
    max-width: 100%;
    height: auto;
  }
}

.admin-sidebar__nav {
  flex: 1;
  width: 100%;
  min-height: 0;
}

.admin-sidebar__list {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 10px;
  height: 100%;
  margin: 0;
  padding: 55px 0 0;
  list-style: none;
}

.admin-sidebar__indicator {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  border-radius: 6px;
  background-color: rgba(9, 48, 149, 0.4);
  background-image: url('/admin/icons/sidebar/background.png');
  background-size: 100% 100%;
  background-repeat: no-repeat;
  pointer-events: none;
  z-index: 0;
  transition:
    transform 0.3s ease,
    height 0.3s ease,
    opacity 0.2s ease;
}

.admin-sidebar__item {
  position: relative;
  z-index: 1;
  border-radius: 6px;

  &--pin {
    margin-top: auto;
  }
}

.admin-sidebar__link {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 20px;
  padding: 10px 15px;
  color: inherit;
  text-decoration: none;
  border-radius: 6px;
  outline: none;

  &:focus-visible {
    box-shadow: 0 0 0 2px var(--dvijok-blue-primary);
  }
}

.admin-sidebar__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 26px;
  height: 26px;

  img {
    width: 100%;
    height: 100%;
    object-fit: contain;
  }
}

.admin-sidebar__label {
  color: var(--dvijok-white);
  font-size: 14px;
  font-weight: 400;
  line-height: 17px;
}

.admin-sidebar__user {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding-left: 15px;
}

.admin-sidebar__avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 18px;
  background-color: var(--dvijok-blue-primary);
  color: var(--dvijok-bg-dark);
  font-size: 12px;
  font-weight: 600;
  line-height: 15px;
}

.admin-sidebar__user-text {
  margin: 0;
  color: var(--dvijok-white);
  font-size: 12px;
  font-weight: 400;
  line-height: 16px;
}

.admin-sidebar__logout {
  width: 100%;
  padding: 9px 15px;
  border: none;
  border-radius: 8px;
  background: #e5242a;
  color: var(--dvijok-white);
  font: inherit;
  font-size: 12px;
  font-weight: 600;
  line-height: 15px;
  cursor: pointer;
  transition: filter 0.18s ease;

  &:hover:not(:disabled) {
    filter: brightness(1.08);
  }

  &:focus-visible {
    outline: 2px solid var(--dvijok-white);
    outline-offset: 2px;
  }

  &:disabled {
    cursor: wait;
    opacity: 0.7;
  }
}
</style>
