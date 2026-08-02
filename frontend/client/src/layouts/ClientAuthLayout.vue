<template>
  <q-layout view="lHh Lpr lFf" class="client-auth-layout">
    <div class="client-auth-layout__scroll">
      <header class="auth-header">
        <div class="auth-header__rounds" aria-hidden="true">
          <img class="auth-header__round auth-header__round--1" src="/client/round.svg" alt="" />
          <img class="auth-header__round auth-header__round--2" src="/client/round.svg" alt="" />
        </div>

        <p class="auth-header__welcome">Добро пожаловать!</p>
        <img class="auth-header__logo" src="/client/icons/logo.svg" alt="DVIJOK" />
      </header>

      <q-page-container class="client-auth-layout__content">
        <router-view />
      </q-page-container>
    </div>
  </q-layout>
</template>

<script setup></script>

<style scoped lang="scss">
.client-auth-layout {
  height: 100%;
  overflow: hidden;
}

.client-auth-layout__scroll {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: auto;
  background-color: var(--dvijok-muted);
}

.client-auth-layout__content {
  flex: 1;
  min-height: 0;
}

.auth-header {
  position: relative;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 50px 30px;
  overflow: hidden;
  background: var(--dvijok-gradient-brand);
}

.auth-header__rounds {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 0;
}

.auth-header__round {
  position: absolute;
  pointer-events: none;
  object-fit: contain;
}

.auth-header__round--1 {
  width: 50%;
  aspect-ratio: 1;
  top: 0;
  right: 0;
  transform: translate(40%, -50%);
}

.auth-header__round--2 {
  width: 30%;
  aspect-ratio: 1;
  bottom: 0;
  left: 0;
  transform: translate(-30%, 50%);
}

.auth-header__welcome {
  position: relative;
  z-index: 1;
  margin: 0;
  font-weight: 400;
  font-size: 13px;
  line-height: 16px;
  color: var(--dvijok-white);
}

.auth-header__logo {
  position: relative;
  z-index: 1;
  display: block;
  max-width: 100%;
  height: auto;
}
</style>
