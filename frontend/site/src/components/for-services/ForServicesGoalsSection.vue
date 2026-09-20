<template>
  <section class="goals-section">
    <h2 class="goals-section__title">ДВИЖОК поможет достичь любых бизнес-целей</h2>

    <div class="goals-section__grid">
      <div
        v-for="card in goalCards"
        :key="card.id"
        class="goals-section__card"
        :class="[
          `goals-section__card--${card.variant}`,
          `goals-section__card--span-${card.span}`,
          `goals-section__card--${card.id}`
        ]"
      >
        <h3 class="goals-section__card-title">{{ card.title }}</h3>
        <p class="goals-section__card-desc">{{ card.description }}</p>

        <div
          v-if="card.id === 'online'"
          class="goals-section__visual goals-section__visual--online"
        >
          <div class="goals-section__online-details">
            <img
              class="goals-section__online-details-img"
              src="/site/icons/for-services/details.webp"
              alt=""
            />
          </div>
          <div class="goals-section__online-icons">
            <img
              class="goals-section__online-icon goals-section__online-icon--ydx"
              src="/site/icons/for-services/ydx.webp"
              alt=""
            />
            <img
              class="goals-section__online-icon goals-section__online-icon--max"
              src="/site/icons/for-services/max.webp"
              alt=""
            />
            <img
              class="goals-section__online-icon goals-section__online-icon--vk"
              src="/site/icons/for-services/vk.webp"
              alt=""
            />
            <img
              class="goals-section__online-icon goals-section__online-icon--2gis"
              src="/site/icons/for-services/2gis.webp"
              alt=""
            />
          </div>
        </div>

        <div
          v-else-if="card.id === 'routine'"
          class="goals-section__visual goals-section__visual--routine"
        >
          <div class="goals-section__routine-side">
            <img
              class="goals-section__routine-success"
              src="/site/icons/for-services/success.svg"
              alt=""
            />
            <ul class="goals-section__routine-list">
              <li v-for="item in routineItems" :key="item">{{ item }}</li>
            </ul>
          </div>
          <div class="goals-section__routine-preview">
            <img
              class="goals-section__routine-record"
              src="/site/icons/for-services/first-record.png"
              alt=""
            />
          </div>
        </div>

        <div
          v-else-if="card.id === 'earn'"
          class="goals-section__visual goals-section__visual--earn"
        >
          <img class="goals-section__earn-cards" src="/site/icons/for-services/cards.png" alt="" />
        </div>

        <template v-else-if="card.id === 'retain'">
          <div class="goals-section__retain-corner">
            <img
              class="goals-section__retain-arrow"
              src="/site/icons/for-services/arrow.svg"
              alt=""
            />
            <img
              class="goals-section__retain-max"
              src="/site/icons/for-services/max+1.png"
              alt=""
            />
          </div>
          <div class="goals-section__retain-sms">
            <SmsBubble side="left" color="blue" class="goals-section__sms">
              {{ retainSms }}
            </SmsBubble>
          </div>
        </template>

        <div
          v-else-if="card.id === 'realtime'"
          class="goals-section__visual goals-section__visual--realtime"
        >
          <img class="goals-section__traffic" src="/site/icons/for-services/traffic.svg" alt="" />
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import SmsBubble from '@/components/ui/SmsBubble.vue'

const routineItems = ['CRM-система', 'Задачник', 'Сотрудники', 'Аналитика']

const retainSms =
  'Добрый день!\n\nНапоминание о записи\n22 августа в 14:00, диагностика.\nАдрес мастерской: ул. Пушкина, 26'

const goalCards = [
  {
    id: 'online',
    variant: 'light',
    span: 3,
    title: 'Записывайте клиентов онлайн',
    description:
      'Позвольте клиентам записываться в автосервис в любое удобное для них время. Система покажет доступные окна, поможет выбрать подходящее время и автоматически зафиксирует запись в расписании'
  },
  {
    id: 'routine',
    variant: 'dark',
    span: 3,
    title: 'Не тратьте время на рутину',
    description:
      'Доверьте управление автоматизированной системе. Ставьте задачи, следите за исполнением, контролируйте процессы'
  },
  {
    id: 'earn',
    variant: 'light',
    span: 2,
    title: 'Зарабатывайте\nбольше',
    description:
      'Оценивайте доходность онлайн. Информируйте о скидках и акциях своих клиентов вовремя'
  },
  {
    id: 'retain',
    variant: 'light',
    span: 2,
    title: 'Не отпускайте клиентов\nк конкурентам',
    description:
      'Автоматически отправляйте уведомления о статусе автомобиля, завершении работ и напоминайте о плановом ТО, замене масла и других необходимых работах'
  },
  {
    id: 'realtime',
    variant: 'light',
    span: 2,
    title: 'Управляйте бизнесом\nв реальном времени',
    description: 'Используйте цифровизацию на максимум для своей свободы и новых достижений'
  }
]
</script>

<style scoped>
.goals-section {
  display: flex;
  flex-direction: column;
  gap: 50px;
  padding: 80px;
  background: var(--dvijok-white);
}

.goals-section__title {
  margin: 0;
  font-family: var(--dvijok-font-display);
  font-weight: 400;
  font-size: 32px;
  line-height: 46px;
  text-align: center;
  text-transform: uppercase;
  color: #000;
}

.goals-section__grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 20px;
}

.goals-section__card {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow: hidden;
}

.goals-section__card--span-3 {
  grid-column: span 3;
}

.goals-section__card--span-2 {
  grid-column: span 2;
}

.goals-section__card--dark {
  padding: 20px;
  background: var(--dvijok-navy);
  color: var(--dvijok-white);
}

.goals-section__card--light {
  padding: 19px;
  border: 1px solid var(--dvijok-text-secondary);
  background: transparent;
  color: var(--dvijok-text-primary);
}

.goals-section__card-title {
  margin: 0;
  font-weight: 600;
  font-size: 24px;
  line-height: 29px;
  white-space: pre-line;
  color: inherit;
}

.goals-section__card-desc {
  margin: 0;
  font-weight: 400;
  font-size: 18px;
  line-height: 22px;
  color: inherit;
}

.goals-section__visual {
  position: relative;
  flex: 1;
  min-height: 220px;
}

.goals-section__visual--online {
  display: flex;
  flex-direction: row;
  align-items: stretch;
}

.goals-section__online-details,
.goals-section__online-icons {
  position: relative;
  flex: 1;
  min-width: 0;
}

.goals-section__online-details {
  display: flex;
  align-items: flex-end;
  justify-content: flex-start;
}

.goals-section__online-details-img {
  display: block;
  max-width: 100%;
  height: auto;
}

.goals-section__online-icon {
  position: absolute;
  display: block;
  width: 66px;
  height: 66px;
  object-fit: contain;
}

.goals-section__online-icon--ydx {
  top: 20%;
  left: 15%;
}

.goals-section__online-icon--max {
  bottom: 15%;
  left: 20%;
}

.goals-section__online-icon--vk {
  top: 0;
  right: 30%;
}

.goals-section__online-icon--2gis {
  right: 20%;
  bottom: 35%;
}

.goals-section__visual--routine {
  display: flex;
  flex-direction: row;
  align-items: stretch;
}

.goals-section__routine-side {
  display: flex;
  flex-direction: column;
  gap: 30px;
  width: 30%;
}

.goals-section__routine-success {
  display: block;
  align-self: center;
  width: 71px;
  height: 71px;
}

.goals-section__routine-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin: 0;
  padding: 0;
  list-style: none;
  font-family: Inter, sans-serif;
  font-weight: 600;
  font-size: 20px;
  line-height: 24px;
  color: #8aabff;
}

.goals-section__routine-preview {
  position: relative;
  width: 70%;
  min-height: 100%;
}

.goals-section__routine-record {
  position: absolute;
  bottom: 0;
  left: 50%;
  display: block;
  width: 55%;
  height: auto;
  transform: translateX(-50%);
}

.goals-section__visual--earn {
  display: flex;
  align-items: center;
  justify-content: center;
}

.goals-section__earn-cards {
  display: block;
  width: 65%;
  height: auto;
}

.goals-section__retain-corner {
  display: flex;
  flex: 1;
  flex-direction: row;
  gap: 20px;
  align-items: flex-end;
  justify-content: flex-end;
}

.goals-section__retain-arrow,
.goals-section__retain-max {
  display: block;
  flex: none;
}

.goals-section__retain-max {
  width: 80px;
  height: 76px;
  object-fit: contain;
}

.goals-section__retain-sms {
  position: relative;
}

.goals-section__sms {
  width: 260px;
}

.goals-section__visual--realtime {
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.goals-section__traffic {
  display: block;
  max-width: 100%;
  height: auto;
}
</style>
