<template>
  <aside class="cookies-banner" role="dialog" aria-label="Уведомление о cookies" aria-modal="false">
    <p class="cookies-banner__text">
      Мы используем cookies для корректной работы сайта, аналитики и улучшения сервиса. Продолжая
      пользоваться сайтом, вы соглашаетесь с использованием cookies.
    </p>

    <a
      class="cookies-banner__link"
      href="/docs/cookies-policy.html"
      target="_blank"
      rel="noopener noreferrer"
    >
      Подробнее о Политике cookies
    </a>

    <BaseButton color="blue2" size="sm" block @click="emit('accept')"> Принять </BaseButton>
  </aside>
</template>

<script setup>
import BaseButton from '@/components/ui/BaseButton.vue'

const emit = defineEmits(['accept'])
</script>

<style scoped lang="scss">
@use '../../css/glass' as glass;

.cookies-banner {
  @include glass.glass-surface(
    $background: #00124080,
    $inset: rgba(255, 255, 255, 0.14),
    $edge-start: rgba(255, 255, 255, 0.5),
    $edge-end: rgba(255, 255, 255, 0.4)
  );
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 20px 30px;
  border-radius: 10px;
  box-sizing: border-box;
}

.cookies-banner__text {
  margin: 0;
  font-weight: 400;
  font-size: 13px;
  line-height: 16px;
  color: var(--dvijok-white);
}

.cookies-banner__link {
  font-weight: 400;
  font-size: 14px;
  line-height: 17px;
  text-decoration: underline;
  color: var(--dvijok-tab-inactive);
}
</style>
