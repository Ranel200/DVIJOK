<template>
  <section class="support-section">
    <SiteSectionHeadings eyebrow="Поддержка" title="Наша команда всегда поможет" />

    <div class="support-section__row">
      <div class="support-section__info">
        <div v-for="item in items" :key="item.title" class="support-section__item">
          <h3 class="support-section__item-title">{{ item.title }}</h3>
          <p class="support-section__item-desc">{{ item.description }}</p>
        </div>

        <SiteTextLink>Написать техподдержке</SiteTextLink>
      </div>

      <div class="support-section__chat">
        <SmsBubble
          side="right"
          color="blue"
          class="support-section__sms support-section__sms--right"
        >
          <strong>{{ clientLabel }}</strong
          >{{ clientMessage }}
        </SmsBubble>
        <SmsBubble side="left" color="gray" class="support-section__sms support-section__sms--left">
          <strong>{{ agentLabel }}</strong
          >{{ agentMessage }}
        </SmsBubble>
      </div>
    </div>
  </section>
</template>

<script setup>
import SiteSectionHeadings from '@/components/ui/SiteSectionHeadings.vue'
import SiteTextLink from '@/components/ui/SiteTextLink.vue'
import SmsBubble from '@/components/ui/SmsBubble.vue'

defineProps({
  items: {
    type: Array,
    default: () => []
  },
  clientLabel: {
    type: String,
    required: true
  },
  clientMessage: {
    type: String,
    required: true
  },
  agentLabel: {
    type: String,
    default: 'Специалист поддержки Алексей К.'
  },
  agentMessage: {
    type: String,
    required: true
  }
})
</script>

<style scoped>
.support-section {
  position: relative;
  z-index: 1;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 50px;
  padding: 80px;
  background: var(--dvijok-white);
}

.support-section__row {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: stretch;
}

.support-section__info {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 33%;
}

.support-section__item {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.support-section__item-title {
  margin: 0;
  font-family: Inter, sans-serif;
  font-weight: 600;
  font-size: 24px;
  line-height: 29px;
  color: #000;
}

.support-section__item-desc {
  margin: 0;
  font-family: Inter, sans-serif;
  font-weight: 400;
  font-size: 16px;
  line-height: 19px;
  white-space: pre-line;
  color: #7a82a0;
}

.support-section__chat {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 40px;
  width: 50%;
}

.support-section__sms {
  width: 60%;
}

.support-section__sms :deep(strong) {
  font-weight: 700;
}

.support-section__sms--right {
  align-self: flex-end;
}

.support-section__sms--left {
  align-self: flex-start;
}

@media (max-width: 1023px) {
  .support-section {
    padding: 80px 20px;
  }

  .support-section__row {
    flex-direction: column;
    gap: 30px;
  }

  .support-section__info,
  .support-section__chat {
    width: 100%;
  }

  .support-section__item-title {
    font-size: 20px;
    line-height: 24px;
  }

  .support-section__sms {
    width: 95%;
  }
}
</style>
