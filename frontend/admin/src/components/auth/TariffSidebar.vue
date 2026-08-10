<template>
  <aside class="tariff-sidebar">
    <div class="tariff-sidebar__rounds" aria-hidden="true">
      <img class="tariff-sidebar__round tariff-sidebar__round--1" src="/admin/round.svg" alt="" />
      <img class="tariff-sidebar__round tariff-sidebar__round--2" src="/admin/round.svg" alt="" />
    </div>

    <div class="tariff-sidebar__brand">
      <img class="tariff-sidebar__logo" :src="plan.logoNoStar" :alt="plan.logoAlt" />
    </div>

    <div class="tariff-sidebar__features-wrap">
      <ul v-if="plan.includedFrom" class="tariff-sidebar__features">
        <li class="tariff-sidebar__feature">
          <img class="tariff-sidebar__feature-icon" :src="plan.includedFrom.icon" alt="" />
          <div class="tariff-sidebar__feature-body">
            <p class="tariff-sidebar__feature-title">{{ plan.includedFrom.title }}</p>
          </div>
        </li>
      </ul>

      <div v-if="plan.includedFrom" class="tariff-sidebar__divider" aria-hidden="true">
        <span class="tariff-sidebar__divider-line" />
        <span class="tariff-sidebar__divider-text">а также</span>
        <span class="tariff-sidebar__divider-line" />
      </div>

      <ul class="tariff-sidebar__features">
        <li v-for="feature in plan.features" :key="feature.title" class="tariff-sidebar__feature">
          <img class="tariff-sidebar__feature-icon" :src="feature.icon" alt="" />
          <div class="tariff-sidebar__feature-body">
            <p class="tariff-sidebar__feature-title">{{ feature.title }}</p>
            <p v-if="feature.text" class="tariff-sidebar__feature-text">{{ feature.text }}</p>
          </div>
        </li>
      </ul>
    </div>
  </aside>
</template>

<script setup>
defineProps({
  plan: {
    type: Object,
    required: true
  }
})
</script>

<style scoped lang="scss">
.tariff-sidebar {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 30px;
  width: 446px;
  flex-shrink: 0;
  padding: 50px 30px;
  background-color: var(--dvijok-bg-dark);
  overflow: hidden;
}

.tariff-sidebar__rounds {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 0;
}

.tariff-sidebar__round {
  position: absolute;
  pointer-events: none;
  width: auto;
  height: auto;
  object-fit: contain;
}

.tariff-sidebar__round--1 {
  width: 412px;
  height: 412px;
  top: 0;
  right: 0;
  transform: translate(45%, -25%);
}

.tariff-sidebar__round--2 {
  width: 389px;
  height: 389px;
  bottom: 0;
  left: 0;
  transform: translate(-20%, 50%);
}

.tariff-sidebar__brand,
.tariff-sidebar__features-wrap {
  position: relative;
  z-index: 1;
  width: 100%;
}

.tariff-sidebar__brand {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.tariff-sidebar__logo {
  display: block;
  width: 100%;
  max-width: 316px;
  height: auto;
}

.tariff-sidebar__features-wrap {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.tariff-sidebar__features {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.tariff-sidebar__feature {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 20px;
  padding: 10px 20px;
  background-image: url('/admin/icons/auth/background.svg');
  background-size: 100% 100%;
  background-repeat: no-repeat;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

.tariff-sidebar__feature-icon {
  flex-shrink: 0;
  width: 30px;
  height: 30px;
  object-fit: contain;
}

.tariff-sidebar__feature-body {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
}

.tariff-sidebar__feature-title {
  margin: 0;
  color: var(--dvijok-white);
  font-size: 16px;
  font-weight: 600;
  line-height: 24px;
}

.tariff-sidebar__feature-text {
  margin: 0;
  color: var(--dvijok-muted);
  font-size: 12px;
  font-weight: 400;
  line-height: normal;
}

.tariff-sidebar__divider {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  width: 100%;
}

.tariff-sidebar__divider-line {
  flex: 1;
  height: 1px;
  background-color: var(--dvijok-tab-inactive);
  opacity: 0.5;
}

.tariff-sidebar__divider-text {
  color: var(--dvijok-tab-inactive);
  font-size: 16px;
  font-weight: 400;
  line-height: 19px;
  white-space: nowrap;
}
</style>
