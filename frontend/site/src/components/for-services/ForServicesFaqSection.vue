<template>
  <section class="faq-section">
    <div class="faq-section__headings">
      <p class="faq-section__eyebrow">FAQ</p>
      <h2 class="faq-section__title">Ответы на ваши вопросы</h2>
    </div>

    <div class="faq-section__list">
      <div v-for="item in items" :key="item.id" class="faq-section__item">
        <img
          class="faq-section__icon"
          src="/site/icons/question.png"
          alt=""
          width="48"
          height="48"
        />

        <span class="faq-section__line" aria-hidden="true" />

        <div class="faq-section__body">
          <div class="faq-section__copy">
            <h3 class="faq-section__question">{{ item.question }}</h3>
            <div
              class="faq-section__answer-wrap"
              :class="{ 'faq-section__answer-wrap--open': isOpen(item.id) }"
            >
              <div class="faq-section__answer-inner">
                <div class="faq-section__answer">{{ item.answer }}</div>
              </div>
            </div>
          </div>

          <button
            class="faq-section__toggle"
            type="button"
            :aria-expanded="isOpen(item.id)"
            :aria-label="isOpen(item.id) ? 'Свернуть ответ' : 'Показать ответ'"
            @click="toggle(item.id)"
          >
            <ArrowDiagIcon
              :color="isOpen(item.id) ? '#fff' : '#2E68FF'"
              :direction="isOpen(item.id) ? 'up-left' : 'down-right'"
            />
          </button>
        </div>
      </div>
    </div>

    <div class="faq-section__cta">
      <SiteBtn :width="350" type="button">Посмотреть все вопросы и ответы</SiteBtn>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import ArrowDiagIcon from '@/components/ui/ArrowDiagIcon.vue'
import SiteBtn from '@/components/ui/SiteBtn.vue'

defineProps({
  items: {
    type: Array,
    default: () => []
  }
})

const openedIds = ref(new Set())

function toggle(id) {
  const next = new Set(openedIds.value)
  if (next.has(id)) {
    next.delete(id)
  } else {
    next.add(id)
  }
  openedIds.value = next
}

function isOpen(id) {
  return openedIds.value.has(id)
}
</script>

<style scoped>
.faq-section {
  display: flex;
  flex-direction: column;
  gap: 50px;
  padding: 80px;
  background: var(--dvijok-navy);
}

.faq-section__headings {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.faq-section__eyebrow {
  margin: 0;
  font-weight: 500;
  font-size: 20px;
  line-height: 24px;
  text-transform: uppercase;
  color: var(--dvijok-blue-bright);
}

.faq-section__title {
  margin: 0;
  font-family: var(--dvijok-font-display);
  font-weight: 400;
  font-size: 32px;
  line-height: 48px;
  text-transform: uppercase;
  color: #fff;
}

.faq-section__list {
  display: flex;
  flex-direction: column;
}

.faq-section__item {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  gap: 40px;
  padding: 20px;
}

.faq-section__icon {
  display: block;
  flex: none;
  width: 48px;
  height: 48px;
  object-fit: contain;
  align-self: flex-start;
}

.faq-section__line {
  flex: 1 1 auto;
  min-width: 0;
  height: 2px;
  margin-top: 23px;
  background: #2e68ff;
}

.faq-section__body {
  display: flex;
  flex: 0 1 auto;
  flex-direction: row;
  align-items: flex-start;
  gap: 50px;
  min-width: 0;
}

.faq-section__copy {
  display: flex;
  flex: none;
  flex-direction: column;
  width: fit-content;
  max-width: 100%;
}

.faq-section__question {
  margin: 0;
  font-family: var(--dvijok-font-display);
  font-weight: 400;
  font-size: 20px;
  line-height: 29px;
  color: #fff;
}

.faq-section__answer-wrap {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 0.3s ease;
}

.faq-section__answer-wrap--open {
  grid-template-rows: 1fr;
}

.faq-section__answer-inner {
  overflow: hidden;
  min-height: 0;
}

.faq-section__answer {
  box-sizing: border-box;
  width: 0;
  min-width: 100%;
  padding-top: 25px;
  font-family: Inter, sans-serif;
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  color: #fff;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.faq-section__answer-wrap--open .faq-section__answer {
  opacity: 1;
}

.faq-section__toggle {
  display: flex;
  flex: none;
  align-items: center;
  justify-content: center;
  margin: 0;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
}

.faq-section__cta {
  display: flex;
  justify-content: flex-end;
}

@media (prefers-reduced-motion: reduce) {
  .faq-section__answer-wrap,
  .faq-section__answer {
    transition: none;
  }
}
</style>
