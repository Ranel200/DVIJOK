<template>
  <q-page class="for-services">
    <img
      class="for-services__device"
      src="/site/icons/laptop.webp"
      alt="DVIJOK на ноутбуке"
      width="1200"
      height="900"
    />

    <section class="for-services__hero">
      <div class="for-services__intro">
        <div class="for-services__eyebrow">
          <span class="for-services__eyebrow-dot" aria-hidden="true" />
          <span class="for-services__eyebrow-text">Для автосервисов</span>
        </div>

        <div class="for-services__divider" aria-hidden="true" />

        <div class="for-services__intro-main">
          <div class="for-services__intro-copy">
            <div class="for-services__intro-texts">
              <h1 class="for-services__title">
                Управляйте
                <br />
                автосервисами
                <br />
                <span class="for-services__title-accent">в одной системе</span>
              </h1>
              <p class="for-services__lead">
                CRM, расписание сотрудников, аналитика
                <br />
                и постановка задач. Всё что нужно для роста —
                <br />
                без лишних инструментов
              </p>
            </div>

            <div class="for-services__actions">
              <SiteBtn variant="primary" stretch type="button">Попробовать ДВИЖОК</SiteBtn>
              <SiteBtn variant="outline" stretch type="button">Смотреть тарифы</SiteBtn>
            </div>
          </div>
        </div>
      </div>

      <div class="for-services__cards">
        <article v-for="card in heroCards" :key="card.title" class="for-services__card">
          <h2 class="for-services__card-title">{{ card.title }}</h2>
          <p class="for-services__card-desc">{{ card.description }}</p>
        </article>
      </div>
    </section>

    <section class="for-services__advantages">
      <SiteSectionHeadings eyebrow="Внутри ДВИЖКА" title="Работа системы" />

      <div class="for-services__advantages-media">
        <div class="for-services__advantages-video">
          <video
            class="for-services__advantages-video-el"
            controls
            playsinline
            preload="metadata"
            src="https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4"
          >
            Ваш браузер не поддерживает воспроизведение видео.
          </video>
        </div>
        <p class="for-services__advantages-caption">
          На видео представлен процесс работы в ERP-системе «ДВИЖОК»
        </p>
      </div>
    </section>

    <ForServicesGoalsSection />

    <SiteSupportSection
      :items="supportItems"
      client-label="Сервис «Папин гараж»"
      :client-message="supportSmsClient"
      :agent-message="supportSmsAgent"
    />

    <section class="for-services__section for-services__section--navy-row">
      <div class="for-services__income-copy">
        <h2 class="for-services__income-title">Увеличьте доход уже сейчас</h2>
        <p class="for-services__income-lead">
          CRM, онлайн-запись, аналитика и уведомления.<br />
          Всё что нужно для роста — без лишних инструментов.
        </p>
        <SiteBtn :width="350" type="button">Попробовать 7 дней бесплатно</SiteBtn>
      </div>

      <div class="for-services__income-visual">
        <img
          class="for-services__income-graph"
          src="/site/icons/graph.png"
          alt="Рост дохода с ДВИЖОК"
          height="300"
        />
      </div>
    </section>

    <ForServicesGrowthSection />

    <SiteArticlesSection :articles="popularArticles" />

    <SiteFaqSection :items="faqItems" />
  </q-page>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { blogApi, faqApi } from '@/api/index.js'
import ForServicesGoalsSection from '@/components/for-services/ForServicesGoalsSection.vue'
import ForServicesGrowthSection from '@/components/for-services/ForServicesGrowthSection.vue'
import SiteArticlesSection from '@/components/ui/SiteArticlesSection.vue'
import SiteBtn from '@/components/ui/SiteBtn.vue'
import SiteFaqSection from '@/components/ui/SiteFaqSection.vue'
import SiteSectionHeadings from '@/components/ui/SiteSectionHeadings.vue'
import SiteSupportSection from '@/components/ui/SiteSupportSection.vue'

const popularArticles = ref([])
const faqItems = ref([])

onMounted(async () => {
  const [articles, faqs] = await Promise.all([
    blogApi.list({ limit: 3 }),
    faqApi.list({ limit: 4, audience: 'services' })
  ])
  popularArticles.value = articles
  faqItems.value = faqs
})

const heroCards = [
  {
    title: 'Возвращайте клиентов\nза 0 ₽',
    description: 'Автоматически напоминайте о ТО и приглашайте клиентов снова в автосервис'
  },
  {
    title: 'Грамотно распределяйте\nвремя сотрудников',
    description: 'Управляйте расписанием и равномерно распределяйте загрузку мастеров'
  },
  {
    title: 'Не теряйте клиентов!',
    description: 'Записывайте клиентов в автосервис онлайн в любое время, даже когда сервис закрыт'
  }
]

const supportItems = [
  {
    title: 'Личный механик по внедрению',
    description:
      'Подскажет, как настроить систему под ваш автосервис, обучит сотрудников и поможет быстро перейти на новый формат работы.'
  },
  {
    title: 'Круглосуточная техподдержка',
    description:
      'Что-то заглохло? Не проблема. Наша поддержка всегда на связи и поможет быстро разобраться с любым вопросом. Подскажем, настроим, объясним и поможем вернуть ДВИЖОК в рабочий режим.'
  }
]

const supportSmsClient = '\n\nЗдравствуйте! Хотим добавить кнопку\n«Записаться онлайн» на карты.'

const supportSmsAgent =
  '\n\nЗдравствуйте! Конечно! Поможем настроить\nонлайн-запись и подключить её к карточке\nавтосервиса.'
</script>

<style scoped>
.for-services {
  position: relative;
  box-sizing: border-box;
  padding: 0;
}

.for-services__device {
  position: absolute;
  top: 50px;
  left: 0;
  z-index: 0;
  width: min(60vw, 864px);
  height: auto;
  pointer-events: none;
  animation: for-services-device-in 1.1s cubic-bezier(0.22, 1, 0.36, 1) both;
}

@keyframes for-services-device-in {
  from {
    opacity: 0;
    transform: translateX(-55vw);
  }

  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@media (prefers-reduced-motion: reduce) {
  .for-services__device {
    animation: none;
  }
}

.for-services__hero {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  gap: 150px;
  padding: 20px 80px 60px;
}

.for-services__intro {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.for-services__eyebrow {
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 10px;
  width: fit-content;
  padding: 8px 12px;
  border: 1px solid #2e68ff;
}

.for-services__eyebrow-dot {
  flex: none;
  width: 17px;
  height: 17px;
  border-radius: 50%;
  background: var(--dvijok-blue-bright);
}

.for-services__eyebrow-text {
  font-weight: 400;
  font-size: 16px;
  line-height: 19px;
  color: var(--dvijok-blue-bright);
}

.for-services__divider {
  width: 100%;
  height: 3px;
  background: var(--dvijok-blue-bright);
}

.for-services__intro-main {
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
}

.for-services__intro-copy {
  display: flex;
  flex-direction: column;
  gap: 80px;
  width: 50%;
}

.for-services__intro-texts {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.for-services__title {
  margin: 0;
  font-family: var(--dvijok-font-display);
  font-weight: 400;
  font-size: 32px;
  line-height: 46px;
  text-transform: uppercase;
  color: #000;
}

.for-services__title-accent {
  color: var(--dvijok-blue-bright);
}

.for-services__lead {
  margin: 0;
  font-weight: 500;
  font-size: 20px;
  line-height: 24px;
  color: #000;
}

.for-services__actions {
  display: flex;
  flex-direction: row;
  gap: 30px;
}

.for-services__cards {
  display: flex;
  flex-direction: row;
  gap: 15px;
  align-items: stretch;
}

.for-services__card {
  box-sizing: border-box;
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 20px;
  padding: 13px 18px;
  border: 2px solid var(--dvijok-blue-bright);
  background: var(--dvijok-white);
}

.for-services__card-title {
  margin: 0;
  font-weight: 600;
  font-size: 24px;
  line-height: 29px;
  white-space: pre-line;
  color: #000;
}

.for-services__card-desc {
  margin: 0;
  font-weight: 400;
  font-size: 18px;
  line-height: 22px;
  color: #000;
}

.for-services__advantages {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 50px;
  padding: 60px 80px;
  background: var(--dvijok-white);
  box-shadow: 0 0 40px 80px var(--dvijok-white);
}

.for-services__advantages-media {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 0 60px;
}

.for-services__advantages-video {
  width: 100%;
  aspect-ratio: 16 / 9;
  overflow: hidden;
  background: #000;
}

.for-services__advantages-video-el {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.for-services__advantages-caption {
  margin: 0;
  font-weight: 400;
  font-size: 16px;
  line-height: 19px;
  text-align: left;
  color: var(--dvijok-text-secondary);
}

.for-services__section {
  position: relative;
  z-index: 1;
  box-sizing: border-box;
}

.for-services__section--navy-row {
  display: flex;
  flex-direction: row;
  gap: 100px;
  align-items: center;
  padding: 80px 70px;
  background: var(--dvijok-navy);
}

.for-services__income-copy {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 50px;
  min-width: 0;
}

.for-services__income-title {
  margin: 0;
  font-family: var(--dvijok-font-display);
  font-weight: 400;
  font-size: 32px;
  line-height: 46px;
  text-transform: uppercase;
  color: var(--dvijok-white);
}

.for-services__income-lead {
  margin: 0;
  font-family: Inter, sans-serif;
  font-weight: 500;
  font-size: 20px;
  line-height: 100%;
  color: var(--dvijok-white);
}

.for-services__income-visual {
  flex: none;
}

.for-services__income-graph {
  display: block;
  height: 300px;
  width: auto;
}

@media (max-width: 1023px) {
  .for-services__device {
    top: 100px;
    left: 5%;
    width: 90%;
  }

  .for-services__hero {
    gap: 50px;
    padding: 30px 20px 60px;
  }

  .for-services__intro-main {
    padding-top: calc(90vw * 900 / 1200);
  }

  .for-services__intro-copy {
    width: 100%;
  }

  .for-services__title {
    font-size: 24px;
    line-height: 35px;
  }

  .for-services__actions {
    flex-direction: column;
    gap: 15px;
  }

  .for-services__actions :deep(.site-btn--stretch) {
    flex: none;
    width: 100%;
  }

  .for-services__cards {
    flex-direction: column;
  }

  .for-services__card {
    flex: none;
    width: 100%;
  }

  .for-services__advantages {
    display: none;
  }

  .for-services__section--navy-row {
    flex-direction: column;
    gap: 30px;
    padding: 40px 20px;
  }

  .for-services__income-visual {
    order: -1;
    width: 90%;
  }

  .for-services__income-graph {
    width: 100%;
    height: auto;
  }

  .for-services__income-copy {
    width: 100%;
  }

  .for-services__income-copy :deep(.site-btn) {
    width: 100% !important;
    flex: none;
  }
}
</style>
