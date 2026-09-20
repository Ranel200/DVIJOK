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
      <div class="for-services__advantages-headings">
        <p class="for-services__advantages-eyebrow">Внутри ДВИЖКА</p>
        <h2 class="for-services__advantages-title">Работа системы</h2>
      </div>

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

    <section class="for-services__section for-services__section--plain">
      <div class="for-services__advantages-headings">
        <p class="for-services__advantages-eyebrow">Поддержка</p>
        <h2 class="for-services__advantages-title">Наша команда всегда поможет</h2>
      </div>

      <div class="for-services__support-row">
        <div class="for-services__support-info">
          <div v-for="item in supportItems" :key="item.title" class="for-services__support-item">
            <h3 class="for-services__support-item-title">{{ item.title }}</h3>
            <p class="for-services__support-item-desc">{{ item.description }}</p>
          </div>

          <SiteTextLink>Написать техподдержке</SiteTextLink>
        </div>

        <div class="for-services__support-chat">
          <SmsBubble
            side="right"
            color="blue"
            class="for-services__support-sms for-services__support-sms--right"
          >
            <strong>Сервис «Папин гараж»</strong>{{ supportSmsClient }}
          </SmsBubble>
          <SmsBubble
            side="left"
            color="gray"
            class="for-services__support-sms for-services__support-sms--left"
          >
            <strong>Специалист поддержки Алексей К.</strong>{{ supportSmsAgent }}
          </SmsBubble>
        </div>
      </div>
    </section>

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

    <section class="for-services__section for-services__section--mid">
      <div class="for-services__advantages-headings">
        <p class="for-services__advantages-eyebrow">Популярное</p>
        <h2 class="for-services__advantages-title">Статьи</h2>
      </div>

      <div class="for-services__articles-grid">
        <article
          v-for="article in popularArticles"
          :key="article.id"
          class="for-services__article-card"
        >
          <div class="for-services__article-photo">
            <img :src="article.photo" :alt="article.title" />
          </div>

          <h3 class="for-services__article-title">{{ article.title }}</h3>
          <p class="for-services__article-desc">{{ article.description }}</p>

          <SiteTextLink :to="{ name: 'blog-article', params: { id: String(article.id) } }">
            Читать всю статью
          </SiteTextLink>
        </article>
      </div>

      <div class="for-services__articles-cta">
        <SiteBtn :width="330" :to="{ name: 'blog' }">Посмотреть все статьи</SiteBtn>
      </div>
    </section>

    <ForServicesFaqSection :items="faqItems" />
  </q-page>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { blogApi, faqApi } from '@/api/index.js'
import ForServicesFaqSection from '@/components/for-services/ForServicesFaqSection.vue'
import ForServicesGoalsSection from '@/components/for-services/ForServicesGoalsSection.vue'
import ForServicesGrowthSection from '@/components/for-services/ForServicesGrowthSection.vue'
import SiteBtn from '@/components/ui/SiteBtn.vue'
import SiteTextLink from '@/components/ui/SiteTextLink.vue'
import SmsBubble from '@/components/ui/SmsBubble.vue'

const popularArticles = ref([])
const faqItems = ref([])

onMounted(async () => {
  const [articles, faqs] = await Promise.all([
    blogApi.list({ limit: 3 }),
    faqApi.list({ limit: 4 })
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
  padding: 8px 12px;
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

.for-services__advantages-headings {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.for-services__advantages-eyebrow {
  margin: 0;
  font-weight: 500;
  font-size: 20px;
  line-height: 24px;
  text-transform: uppercase;
  color: var(--dvijok-blue-bright);
}

.for-services__advantages-title {
  margin: 0;
  font-family: var(--dvijok-font-display);
  font-weight: 400;
  font-size: 32px;
  line-height: 48px;
  text-transform: uppercase;
  color: #000;
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

.for-services__section--plain {
  display: flex;
  flex-direction: column;
  gap: 50px;
  padding: 80px;
  background: var(--dvijok-white);
}

.for-services__support-row {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: stretch;
}

.for-services__support-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 33%;
}

.for-services__support-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.for-services__support-item-title {
  margin: 0;
  font-family: Inter, sans-serif;
  font-weight: 600;
  font-size: 24px;
  line-height: 29px;
  color: #000;
}

.for-services__support-item-desc {
  margin: 0;
  font-family: Inter, sans-serif;
  font-weight: 400;
  font-size: 16px;
  line-height: 19px;
  color: #7a82a0;
}

.for-services__support-chat {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 40px;
  width: 50%;
}

.for-services__support-sms {
  width: 60%;
}

.for-services__support-sms :deep(strong) {
  font-weight: 700;
}

.for-services__support-sms--right {
  align-self: flex-end;
}

.for-services__support-sms--left {
  align-self: flex-start;
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

.for-services__section--mid {
  display: flex;
  flex-direction: column;
  gap: 50px;
  padding: 40px 80px;
  background: var(--dvijok-white);
}

.for-services__articles-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 50px;
}

.for-services__article-card {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 19px;
  border: 1px solid #7a82a0;
}

.for-services__article-photo {
  width: 100%;
  aspect-ratio: 16 / 9;
  overflow: hidden;
  line-height: 0;
}

.for-services__article-photo img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.for-services__article-title {
  margin: 0;
  font-family: Inter, sans-serif;
  font-weight: 600;
  font-size: 24px;
  line-height: 29px;
  text-transform: uppercase;
  color: #000;
}

.for-services__article-desc {
  margin: 0;
  font-family: Inter, sans-serif;
  font-weight: 400;
  font-size: 18px;
  line-height: 22px;
  color: #000;
}

.for-services__articles-cta {
  display: flex;
  justify-content: flex-end;
}
</style>
