<template>
  <AppBlock compact>
    <div class="service-card__top">
      <div class="service-card__logo" aria-hidden="true">
        <img v-if="logo" class="service-card__logo-image" :src="logo" alt="" />
        <span v-else>Лого 110х60</span>
      </div>
      <div class="service-card__meta">
        <p class="service-card__name">Автосервис “{{ name }}”</p>
        <p class="service-card__address">{{ address }}</p>
        <p class="service-card__hours">{{ hours }}</p>
      </div>
    </div>

    <p class="service-card__description">{{ description }}</p>

    <div class="service-card__footer">
      <div class="service-card__stats">
        <div class="service-card__rating-row">
          <div class="service-card__rating">
            <img
              class="service-card__star"
              src="/client/icons/record/star.svg"
              alt=""
              width="17"
              height="16"
            />
            <span class="service-card__score">{{ rating }}</span>
          </div>
          <span class="service-card__reviews">{{ reviewsLabel }}</span>
        </div>
        <p v-if="lastVisit" class="service-card__visit">Последний визит: {{ lastVisit }}</p>
      </div>

      <BaseButton color="blue1" size="sm" @click="emit('book')">Записаться</BaseButton>
    </div>
  </AppBlock>
</template>

<script setup>
import { computed } from 'vue'
import AppBlock from '@/components/ui/AppBlock.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

const props = defineProps({
  logo: {
    type: String,
    default: ''
  },
  name: {
    type: String,
    required: true
  },
  address: {
    type: String,
    required: true
  },
  hours: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  rating: {
    type: [Number, String],
    required: true
  },
  reviews: {
    type: Number,
    required: true
  },
  lastVisit: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['book'])

const reviewsLabel = computed(() => {
  const count = props.reviews
  const mod10 = count % 10
  const mod100 = count % 100
  let word = 'отзывов'
  if (mod10 === 1 && mod100 !== 11) word = 'отзыв'
  else if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) word = 'отзыва'
  return `${count} ${word}`
})
</script>

<style scoped lang="scss">
.service-card__top {
  display: flex;
  flex-direction: row;
  gap: 20px;
}

.service-card__logo {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 110px;
  height: 60px;
  border-radius: 5px;
  background: var(--dvijok-text-secondary);
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-white);
  text-align: center;
}

.service-card__logo-image {
  display: block;
  width: 100%;
  height: 100%;
  border-radius: inherit;
  object-fit: contain;
}

.service-card__meta {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 3px;
  min-width: 0;
}

.service-card__name {
  margin: 0;
  font-weight: 600;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-bg-dark);
}

.service-card__address {
  margin: 0;
  font-weight: 400;
  font-size: 11px;
  line-height: 13px;
  color: var(--dvijok-text-secondary);
}

.service-card__hours {
  margin: 0;
  font-weight: 400;
  font-size: 11px;
  line-height: 13px;
  color: var(--dvijok-workday);
}

.service-card__description {
  margin: 0;
  font-weight: 400;
  font-size: 13px;
  line-height: 16px;
  color: var(--dvijok-text-secondary);
}

.service-card__footer {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  justify-content: space-between;
  gap: 10px;
}

.service-card__stats {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
}

.service-card__rating-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 15px;
}

.service-card__rating {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 5px;
}

.service-card__star {
  display: block;
  flex-shrink: 0;
}

.service-card__score {
  font-weight: 600;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-bg-dark);
}

.service-card__reviews {
  font-weight: 400;
  font-size: 13px;
  line-height: 16px;
  color: var(--dvijok-text-secondary);
}

.service-card__visit {
  margin: 0;
  font-weight: 400;
  font-size: 11px;
  line-height: 13px;
  color: var(--dvijok-text-secondary);
}
</style>
