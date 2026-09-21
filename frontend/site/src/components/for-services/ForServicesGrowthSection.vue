<template>
  <section class="growth-section">
    <h2 class="growth-section__title">Рост с ДВИЖКОМ</h2>

    <div class="growth-section__grid">
      <div v-for="stat in growthStats" :key="stat.percent" class="growth-section__col">
        <p class="growth-section__desc growth-section__desc--above">{{ stat.description }}</p>

        <article
          class="growth-section__card"
          :class="`growth-section__card--${stat.size}`"
          :style="{ background: stat.bg }"
        >
          <div class="growth-section__copy">
            <p class="growth-section__percent">{{ stat.percent }}</p>
            <p class="growth-section__desc growth-section__desc--in-card">{{ stat.description }}</p>
          </div>
          <div class="growth-section__icon-wrap">
            <img class="growth-section__icon" :src="stat.icon" :alt="stat.alt" />
          </div>
        </article>
      </div>
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
    description: '75% экономии на сторонних сервисах',
    bg: '#001240',
    size: 'lg',
    icon: '/site/icons/for-services/ruble.png',
    alt: 'Экономия на сторонних сервисах'
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

.growth-section__col {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.growth-section__desc--above {
  display: none;
}

.growth-section__card {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
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

@media (max-width: 1023px) {
  .growth-section {
    gap: 20px;
    padding: 30px 20px 40px;
  }

  .growth-section__title {
    margin: 0 -10px;
  }

  .growth-section__grid {
    gap: 15px;
    align-items: end;
  }

  .growth-section__col {
    gap: 6px;
  }

  .growth-section__desc--above {
    display: block;
    font-family: Inter, sans-serif;
    font-weight: 500;
    font-size: 11px;
    line-height: 13px;
    color: #000;
  }

  .growth-section__desc--in-card {
    display: none;
  }

  .growth-section__card {
    width: 100%;
    min-width: 0;
    gap: 20px;
    padding: 16px;
  }

  .growth-section__card--sm,
  .growth-section__card--md,
  .growth-section__card--lg {
    aspect-ratio: auto;
  }

  .growth-section__card--sm {
    height: 240px;
  }

  .growth-section__card--md {
    height: calc(240px * 538 / 407);
  }

  .growth-section__card--lg {
    height: calc(240px * 735 / 407);
  }

  .growth-section__percent {
    text-align: center;
  }

  .growth-section__icon {
    max-width: 100%;
  }
}
</style>
