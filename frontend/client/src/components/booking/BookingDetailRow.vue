<template>
  <AppBlock class="booking-detail-row" compact>
    <div class="booking-detail-row__inner">
      <div class="booking-detail-row__identity">
        <div
          v-if="avatar"
          class="booking-detail-row__avatar"
          :style="{ background: avatarColor }"
          aria-hidden="true"
        />
        <div v-else class="booking-detail-row__icon-wrap" aria-hidden="true">
          <img
            class="booking-detail-row__icon"
            :src="icon"
            alt=""
            :width="iconWidth"
            :height="iconHeight"
          />
        </div>
        <div class="booking-detail-row__meta">
          <p class="booking-detail-row__title">{{ title }}</p>
          <p class="booking-detail-row__subtitle">{{ subtitle }}</p>
          <p v-if="price" class="booking-detail-row__price">{{ price }}</p>
        </div>
      </div>
      <button
        type="button"
        class="booking-detail-row__edit"
        :aria-label="editLabel"
        @click="emit('edit')"
      >
        <img src="/client/icons/record/edit.svg" alt="" width="20" height="20" />
      </button>
    </div>
  </AppBlock>
</template>

<script setup>
import AppBlock from '@/components/ui/AppBlock.vue'

defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  },
  price: {
    type: String,
    default: ''
  },
  avatar: {
    type: Boolean,
    default: false
  },
  avatarColor: {
    type: String,
    default: 'var(--dvijok-accent-coral)'
  },
  icon: {
    type: String,
    default: ''
  },
  iconWidth: {
    type: [Number, String],
    default: 23
  },
  iconHeight: {
    type: [Number, String],
    default: 25
  },
  editLabel: {
    type: String,
    default: 'Изменить'
  }
})

const emit = defineEmits(['edit'])
</script>

<style scoped lang="scss">
.booking-detail-row {
  padding: 15px 20px;
}

.booking-detail-row__inner {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.booking-detail-row__identity {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.booking-detail-row__avatar {
  flex-shrink: 0;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: var(--dvijok-accent-coral);
}

.booking-detail-row__icon-wrap {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
}

.booking-detail-row__icon {
  display: block;
}

.booking-detail-row__meta {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
}

.booking-detail-row__title {
  margin: 0;
  font-weight: 700;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-text-primary);
}

.booking-detail-row__subtitle {
  margin: 0;
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-text-secondary);
}

.booking-detail-row__price {
  margin: 0;
  font-weight: 700;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-text-primary);
}

.booking-detail-row__edit {
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
}
</style>
