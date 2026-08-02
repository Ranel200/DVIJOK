<template>
  <header class="client-header">
    <div class="client-header__rounds" aria-hidden="true">
      <img class="client-header__round client-header__round--1" src="/client/round.svg" alt="" />
      <img class="client-header__round client-header__round--2" src="/client/round.svg" alt="" />
    </div>

    <div class="client-header__text">
      <p class="client-header__subtitle">{{ subtitle || '\u00A0' }}</p>
      <h1 class="client-header__title">{{ title }}</h1>
    </div>
  </header>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  }
})
</script>

<style scoped lang="scss">
.client-header {
  position: relative;
  flex-shrink: 0;
  padding: 20px 30px;
  overflow: hidden;
  background: var(--dvijok-gradient-brand);
}

.client-header__rounds {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 0;
}

.client-header__round {
  position: absolute;
  pointer-events: none;
  object-fit: contain;
}

.client-header__round--1 {
  width: 50%;
  aspect-ratio: 1;
  top: 0;
  right: 0;
  transform: translate(40%, -50%);
}

.client-header__round--2 {
  width: 30%;
  aspect-ratio: 1;
  bottom: 0;
  left: 0;
  transform: translate(-30%, 50%);
}

.client-header__text {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.client-header__subtitle {
  margin: 0;
  min-height: 16px;
  font-weight: 400;
  font-size: 13px;
  line-height: 16px;
  color: var(--dvijok-tab-inactive);
}

.client-header__title {
  margin: 0;
  font-weight: 600;
  font-size: 20px;
  line-height: 30px;
  color: var(--dvijok-white);
}
</style>
