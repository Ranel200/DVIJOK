<template>
  <div class="specialist-step">
    <BookingStepHead :name="branchName" :address="branchAddress" @back="emit('back')" />

    <h2 class="booking-step-title">Выбрать специалиста</h2>

    <GlassActionRow
      icon="/client/icons/record/man.svg"
      label="Любой специалист"
      @click="emit('update:modelValue', 'any')"
    >
      <template #trailing>
        <Radio
          :filled="modelValue === 'any'"
          :color="radioColor(modelValue === 'any')"
          :size="20"
        />
      </template>
    </GlassActionRow>

    <AppBlock
      v-for="person in specialists"
      :key="person.id"
      class="specialist-step__card"
      role="button"
      tabindex="0"
      @click="emit('update:modelValue', person.id)"
      @keydown.enter.prevent="emit('update:modelValue', person.id)"
    >
      <div class="specialist-step__top">
        <div class="specialist-step__identity">
          <div
            class="specialist-step__avatar"
            :style="{ background: person.avatarColor }"
            aria-hidden="true"
          />
          <div class="specialist-step__meta">
            <p class="specialist-step__name">{{ person.name }}</p>
            <p class="specialist-step__role">{{ person.role }}</p>
          </div>
        </div>
        <Radio
          :filled="modelValue === person.id"
          :color="radioColor(modelValue === person.id)"
          :size="20"
        />
      </div>

      <div class="specialist-step__rating-row">
        <div class="specialist-step__rating">
          <img
            class="specialist-step__star"
            src="/client/icons/record/star.svg"
            alt=""
            width="17"
            height="16"
          />
          <span class="specialist-step__score">{{ person.rating }}</span>
        </div>
        <span class="specialist-step__reviews">{{ reviewsLabel(person.reviews) }}</span>
      </div>

      <p class="specialist-step__price">{{ formatPrice(person.price) }}</p>

      <p class="specialist-step__nearest">
        Ближайшее время для записи:
        <span class="specialist-step__nearest-date">{{ person.nearestDate }}</span>
      </p>

      <div class="specialist-step__slots">
        <span v-for="slot in person.slots" :key="slot" class="specialist-step__slot">
          {{ slot }}
        </span>
      </div>
    </AppBlock>

    <BaseButton color="blue1" size="sm" block @click="emit('next')">Далее</BaseButton>
  </div>
</template>

<script setup>
import { formatPrice, radioColor, reviewsLabel } from '@/utils/booking.js'
import AppBlock from '@/components/ui/AppBlock.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BookingStepHead from '@/components/booking/BookingStepHead.vue'
import GlassActionRow from '@/components/booking/GlassActionRow.vue'
import Radio from '@/components/ui/Radio.vue'

defineProps({
  modelValue: {
    type: String,
    default: 'any'
  },
  specialists: {
    type: Array,
    default: () => []
  },
  branchName: {
    type: String,
    default: ''
  },
  branchAddress: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'back', 'next'])
</script>

<style scoped lang="scss">
.specialist-step {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.specialist-step__card {
  gap: 10px;
  padding: 15px 20px;
  cursor: pointer;
}

.specialist-step__top {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.specialist-step__identity {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.specialist-step__avatar {
  flex-shrink: 0;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: var(--dvijok-accent-coral);
}

.specialist-step__meta {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
}

.specialist-step__name {
  margin: 0;
  font-weight: 700;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-text-primary);
}

.specialist-step__role {
  margin: 0;
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-text-secondary);
}

.specialist-step__rating-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 15px;
}

.specialist-step__rating {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 5px;
}

.specialist-step__star {
  display: block;
  flex-shrink: 0;
}

.specialist-step__score {
  font-weight: 600;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-bg-dark);
}

.specialist-step__reviews {
  font-weight: 400;
  font-size: 13px;
  line-height: 16px;
  color: var(--dvijok-text-secondary);
}

.specialist-step__price {
  margin: 0;
  font-weight: 700;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-text-primary);
}

.specialist-step__nearest {
  margin: 0;
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-text-secondary);
}

.specialist-step__nearest-date {
  font-weight: 700;
}

.specialist-step__slots {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 5px;
}

.specialist-step__slot {
  padding: 5px;
  border-radius: 5px;
  background: var(--dvijok-choice-active);
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-blue-primary);
}
</style>
