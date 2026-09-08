<template>
  <div class="site-header" :class="{ 'site-header--open': menuOpen }" aria-label="Шапка сайта">
    <div class="site-header__bar">
      <router-link :to="{ name: 'home' }" class="site-header__logo" aria-label="На главную">
        <img class="site-header__logo-desktop" src="/site/icons/logo.png" alt="DVIJOK" />
        <img class="site-header__logo-mobile" src="/site/icons/logo-mobile.png" alt="DVIJOK" />
      </router-link>

      <div class="site-header__actions">
        <nav class="site-header__tabs" aria-label="Основная навигация">
          <template v-for="item in siteNavigation" :key="item.label">
            <router-link v-if="item.to" :to="item.to" class="site-header__tab">
              {{ item.label }}
            </router-link>
            <span v-else class="site-header__tab">{{ item.label }}</span>
          </template>
        </nav>

        <q-btn
          class="site-header__cta site-header__cta--desktop"
          unelevated
          no-caps
          label="Начать"
        />
      </div>

      <button
        type="button"
        class="site-header__burger"
        aria-label="Открыть меню"
        :aria-expanded="menuOpen"
        @click="menuOpen = true"
      >
        <img src="/site/icons/lines.svg" alt="" width="46" height="36" />
      </button>
    </div>

    <div class="site-header__panel" :aria-hidden="!menuOpen">
      <div class="site-header__panel-inner">
        <div class="site-header__panel-top">
          <p class="site-header__menu-title">Меню</p>
          <button
            type="button"
            class="site-header__close"
            aria-label="Закрыть меню"
            @click="menuOpen = false"
          >
            <img src="/site/icons/close.svg" alt="" width="36" height="36" />
          </button>
        </div>

        <div class="site-header__panel-nav">
          <nav class="site-header__mobile-tabs" aria-label="Мобильная навигация">
            <template v-for="item in siteNavigation" :key="`mobile-${item.label}`">
              <router-link
                v-if="item.to"
                :to="item.to"
                class="site-header__tab"
                @click="menuOpen = false"
              >
                {{ item.label }}
              </router-link>
              <span v-else class="site-header__tab">{{ item.label }}</span>
            </template>
          </nav>

          <q-btn
            class="site-header__cta site-header__cta--mobile"
            unelevated
            no-caps
            label="Начать"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { siteNavigation } from '@/constants/navigation.js'

const route = useRoute()
const menuOpen = ref(false)

watch(
  () => route.fullPath,
  () => {
    menuOpen.value = false
  }
)
</script>

<style scoped>
.site-header {
  --site-header-duration: 0.35s;
  --site-header-ease: ease;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 30px 40px;
}

.site-header__bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.site-header__logo {
  display: block;
  flex: 0 0 25%;
  width: 25%;
  max-width: 280px;
  line-height: 0;
}

.site-header__logo-desktop {
  display: block;
  width: 100%;
  height: auto;
}

.site-header__logo-mobile {
  display: none;
  width: auto;
  height: auto;
}

.site-header__actions {
  display: flex;
  flex-direction: row;
  align-items: center;
  flex-shrink: 0;
  gap: 100px;
}

.site-header__tabs {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.site-header__tab {
  box-sizing: border-box;
  padding: 5px 10px;
  border: 1px solid transparent;
  font-weight: 600;
  font-size: 16px;
  line-height: 19px;
  color: var(--dvijok-white);
  text-decoration: none;
}

.site-header__tab.router-link-active {
  padding: 4px 9px;
  border-color: var(--dvijok-white);
}

.site-header__cta {
  min-height: 0;
  padding: 15px 30px;
  border-radius: 0;
  background: var(--dvijok-blue-bright);
  font-weight: 600;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-white);
}

.site-header__burger,
.site-header__close {
  display: none;
  padding: 0;
  border: none;
  background: transparent;
  line-height: 0;
  cursor: pointer;
}

.site-header__burger img,
.site-header__close img {
  display: block;
}

.site-header__panel {
  display: none;
}

.site-header__panel-inner {
  min-height: 0;
}

.site-header__panel-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.site-header__menu-title {
  margin: 0;
  padding: 0 10px;
  font-family: var(--dvijok-font-display);
  font-weight: 400;
  font-size: 24px;
  line-height: 35px;
  color: var(--dvijok-white);
}

.site-header__panel-nav {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.site-header__mobile-tabs {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.site-header__cta--mobile {
  display: none;
  width: 100%;
  padding: 15px;
}

@media (max-width: 1023px) {
  .site-header {
    padding: 20px 40px 12px;
    transition: padding-bottom var(--site-header-duration) var(--site-header-ease);
  }

  .site-header--open {
    padding-bottom: 20px;
  }

  .site-header--open .site-header__bar {
    display: none;
  }

  .site-header__logo {
    flex: 0 0 13%;
    width: 13%;
    max-width: none;
  }

  .site-header__logo-desktop {
    display: none;
  }

  .site-header__logo-mobile {
    display: block;
    width: 100%;
    height: auto;
  }

  .site-header__actions {
    display: none;
  }

  .site-header__burger,
  .site-header__close {
    display: block;
  }

  .site-header__panel {
    display: grid;
    grid-template-rows: 0fr;
    transition: grid-template-rows var(--site-header-duration) var(--site-header-ease);
  }

  .site-header--open .site-header__panel {
    grid-template-rows: 1fr;
  }

  .site-header__panel-inner {
    display: flex;
    flex-direction: column;
    gap: 48px;
    overflow: hidden;
    opacity: 0;
    transition: opacity calc(var(--site-header-duration) * 0.7) var(--site-header-ease);
  }

  .site-header--open .site-header__panel-inner {
    opacity: 1;
  }

  .site-header__cta--mobile {
    display: flex;
  }
}
</style>
