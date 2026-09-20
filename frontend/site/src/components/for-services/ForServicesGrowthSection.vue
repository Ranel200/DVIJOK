<template>
  <section class="growth-section">
    <h2 class="growth-section__title">Рост с ДВИЖКОМ</h2>

    <div class="growth-section__grid">
      <article
        v-for="stat in growthStats"
        :key="stat.percent"
        class="growth-section__card"
        :class="`growth-section__card--${stat.size}`"
        :style="{ background: stat.bg }"
      >
        <div class="growth-section__copy">
          <p class="growth-section__percent">{{ stat.percent }}</p>
          <p class="growth-section__desc">{{ stat.description }}</p>
        </div>
        <div class="growth-section__icon-wrap">
          <img class="growth-section__icon" :src="stat.icon" :alt="stat.alt" />
        </div>
      </article>
    </div>

    <div class="growth-section__divider" aria-hidden="true" />
  </section>
</template>

<script setup>
const growthStats = [
  {
    percent: '27%',
    description: 'На 27% более эффективная\nпроизводительность',
    bg: '#8AABFF',
    size: 'sm',
    icon: '/site/icons/for-services/arrow.png',
    alt: 'Рост производительности'
  },
  {
    percent: '51%',
    description: 'Внедрение на 51% быстрее',
    bg: '#2E68FF',
    size: 'md',
    icon: '/site/icons/for-services/clock.png',
    alt: 'Быстрое внедрение'
  },
  {
    percent: '75%',
    description: 'Рост дохода на 75%',
    bg: '#001240',
    size: 'lg',
    icon: '/site/icons/for-services/ruble.png',
    alt: 'Рост дохода'
  }
]
</script>

<style scoped>
.growth-section {
  display: flex;
  flex-direction: column;
  gap: 40px;
  padding: 45px 60px;
  background: var(--dvijok-white);
}

.growth-section__title {
  margin: 0;
  font-family: var(--dvijok-font-display);
  font-weight: 400;
  font-size: 32px;
  line-height: 46px;
  text-align: center;
  text-transform: uppercase;
  color: #000;
}

.growth-section__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 50px;
  align-items: end;
}

.growth-section__card {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 50px;
  padding: 24px;
  box-shadow: 4px 4px 4px 0 #00000040;
}

.growth-section__card--sm {
  aspect-ratio: 407 / 407;
}

.growth-section__card--md {
  aspect-ratio: 407 / 538;
}

.growth-section__card--lg {
  aspect-ratio: 407 / 735;
}

.growth-section__copy {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.growth-section__percent {
  margin: 0;
  font-family: var(--dvijok-font-display);
  font-weight: 400;
  font-size: 32px;
  line-height: 46px;
  color: #fff;
}

.growth-section__desc {
  margin: 0;
  font-family: Inter, sans-serif;
  font-weight: 500;
  font-size: 20px;
  line-height: 24px;
  white-space: pre-line;
  color: #fff;
}

.growth-section__icon-wrap {
  display: flex;
  justify-content: center;
}

.growth-section__icon {
  display: block;
  height: auto;
}

.growth-section__divider {
  width: 100%;
  height: 4px;
  background: #7a82a0;
}
</style>
