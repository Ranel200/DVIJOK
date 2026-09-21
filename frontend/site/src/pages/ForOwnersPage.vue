<template>
  <q-page class="for-owners">
    <img
      class="for-owners__device"
      src="/site/icons/for-clients/mobile.webp"
      alt="DVIJOK на смартфоне"
      width="600"
      height="900"
    />

    <section class="for-owners__hero">
      <div class="for-owners__intro">
        <div class="for-owners__eyebrow">
          <span class="for-owners__eyebrow-dot" aria-hidden="true" />
          <span class="for-owners__eyebrow-text">Для автовладельцев • бесплатно</span>
        </div>

        <div class="for-owners__divider" aria-hidden="true" />

        <div class="for-owners__intro-main">
          <div class="for-owners__intro-copy">
            <div class="for-owners__intro-texts">
              <h1 class="for-owners__title">
                Вся ваша история
                <br />
                автомобиля
                <br />
                <span class="for-owners__title-accent">в одном месте</span>
              </h1>
              <p class="for-owners__lead">
                Цифровая сервисная книжка, онлайн-запись в автосервис и история каждого ремонта.
                Бесплатно для автовладельцев.
              </p>
            </div>

            <div class="for-owners__actions">
              <SiteBtn variant="primary" stretch type="button">Начать бесплатно</SiteBtn>
              <SiteBtn variant="outline" stretch type="button">Найти автосервис</SiteBtn>
            </div>
          </div>
        </div>
      </div>

      <div class="for-owners__cards">
        <article v-for="card in heroCards" :key="card.title" class="for-owners__card">
          <h2 class="for-owners__card-title">{{ card.title }}</h2>
          <p class="for-owners__card-desc">{{ card.description }}</p>
        </article>
      </div>
    </section>

    <section class="for-owners__advantages">
      <SiteSectionHeadings eyebrow="Внутри ДВИЖКА" title="Работа личного кабинета" />

      <div class="for-owners__advantages-media">
        <div class="for-owners__advantages-video">
          <video
            class="for-owners__advantages-video-el"
            controls
            playsinline
            preload="metadata"
            src="https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4"
          >
            Ваш браузер не поддерживает воспроизведение видео.
          </video>
        </div>
        <p class="for-owners__advantages-caption">
          На видео представлен процесс работы в клиентском сервисе «ДВИЖОК»
        </p>
      </div>
    </section>

    <ForOwnersGoalsSection />

    <SiteSupportSection
      :items="supportItems"
      client-label="Дмитрий У."
      :client-message="supportSmsClient"
      :agent-message="supportSmsAgent"
    />

    <SiteArticlesSection :articles="popularArticles" />

    <SiteFaqSection variant="light" :items="faqItems" />
  </q-page>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { blogApi, faqApi } from '@/api/index.js'
import ForOwnersGoalsSection from '@/components/for-owners/ForOwnersGoalsSection.vue'
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
    faqApi.list({ limit: 4, audience: 'owners' })
  ])
  popularArticles.value = articles
  faqItems.value = faqs
})

const heroCards = [
  {
    title: 'История вашего авто',
    description:
      'Все работы и обслуживание в одном месте. Больше не нужно искать чеки и вспоминать даты'
  },
  {
    title: 'Удобная онлайн-запись',
    description: 'Выберите удобное время и запишитесь в автосервис за пару кликов'
  },
  {
    title: 'Важные оповещения',
    description: 'Запустите бота ДВИЖОК и получайте уведомления о записи, ТО и обслуживании'
  }
]

const supportItems = [
  {
    title: 'Круглосуточная техподдержка',
    description:
      'Что-то заглохло? Не проблема. Наша поддержка всегда на связи и поможет быстро разобраться с любым вопросом. Подскажем, настроим, объясним и поможем вернуть ДВИЖОК в рабочий режим.'
  },
  {
    title: 'Есть идеи, как прокачать ДВИЖОК?',
    description:
      'Поделитесь своими предложениями по улучшению сервиса.\nПринимаем любые идеи, которые помогут сделать ДВИЖОК ещё мощнее.'
  }
]

const supportSmsClient =
  '\n\nЗдравствуйте! Купил автомобиль с рук.\nМожно узнать, что с ним делали раньше?'

const supportSmsAgent =
  '\n\nЗдравствуйте, Дмитрий! Если обслуживание\nпроходило через ДВИЖОК — вся история\nавтомобиля уже сохранена в личном кабинете'
</script>

<style scoped>
.for-owners {
  position: relative;
  box-sizing: border-box;
  padding: 0;
}

.for-owners__device {
  position: absolute;
  top: 80px;
  left: 10%;
  z-index: 0;
  width: min(40vw, 360px);
  height: auto;
  pointer-events: none;
  animation: for-owners-device-in 1.45s cubic-bezier(0.33, 0.9, 0.4, 1) both;
}

@keyframes for-owners-device-in {
  0% {
    opacity: 0;
    transform: translateY(70vh);
  }

  58% {
    opacity: 1;
    transform: translateY(-14px);
  }

  78% {
    transform: translateY(-5px);
  }

  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes for-owners-device-in-mobile {
  0% {
    opacity: 0;
    transform: translate(-50%, 70vh);
  }

  58% {
    opacity: 1;
    transform: translate(-50%, -14px);
  }

  78% {
    transform: translate(-50%, -5px);
  }

  100% {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}

@media (prefers-reduced-motion: reduce) {
  .for-owners__device {
    animation: none;
  }
}

.for-owners__hero {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  gap: 150px;
  padding: 20px 80px 60px;
}

.for-owners__intro {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.for-owners__eyebrow {
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 10px;
  width: fit-content;
  padding: 8px 12px;
  border: 1px solid #2e68ff;
}

.for-owners__eyebrow-dot {
  flex: none;
  width: 17px;
  height: 17px;
  border-radius: 50%;
  background: var(--dvijok-blue-bright);
}

.for-owners__eyebrow-text {
  font-weight: 400;
  font-size: 16px;
  line-height: 19px;
  color: var(--dvijok-blue-bright);
}

.for-owners__divider {
  width: 100%;
  height: 3px;
  background: var(--dvijok-blue-bright);
}

.for-owners__intro-main {
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
}

.for-owners__intro-copy {
  display: flex;
  flex-direction: column;
  gap: 80px;
  width: 50%;
}

.for-owners__intro-texts {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.for-owners__title {
  margin: 0;
  font-family: var(--dvijok-font-display);
  font-weight: 400;
  font-size: 32px;
  line-height: 46px;
  text-transform: uppercase;
  color: #000;
}

.for-owners__title-accent {
  color: var(--dvijok-blue-bright);
}

.for-owners__lead {
  margin: 0;
  font-weight: 500;
  font-size: 20px;
  line-height: 24px;
  color: #000;
}

.for-owners__actions {
  display: flex;
  flex-direction: row;
  gap: 30px;
}

.for-owners__cards {
  display: flex;
  flex-direction: row;
  gap: 15px;
  align-items: stretch;
}

.for-owners__card {
  box-sizing: border-box;
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 20px;
  padding: 13px 18px;
  border: 2px solid var(--dvijok-blue-bright);
  background: var(--dvijok-white);
}

.for-owners__card-title {
  margin: 0;
  font-weight: 600;
  font-size: 24px;
  line-height: 29px;
  white-space: pre-line;
  color: #000;
}

.for-owners__card-desc {
  margin: 0;
  font-weight: 400;
  font-size: 18px;
  line-height: 22px;
  color: #000;
}

.for-owners__advantages {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 50px;
  padding: 60px 80px;
  background: var(--dvijok-white);
  box-shadow: 0 0 40px 80px var(--dvijok-white);
}

.for-owners__advantages-media {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 0 60px;
}

.for-owners__advantages-video {
  width: 100%;
  aspect-ratio: 16 / 9;
  overflow: hidden;
  background: #000;
}

.for-owners__advantages-video-el {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.for-owners__advantages-caption {
  margin: 0;
  font-weight: 400;
  font-size: 16px;
  line-height: 19px;
  text-align: left;
  color: var(--dvijok-text-secondary);
}

@media (max-width: 1023px) {
  .for-owners__device {
    top: 100px;
    left: 50%;
    width: 55%;
    animation-name: for-owners-device-in-mobile;
  }

  @media (prefers-reduced-motion: reduce) {
    .for-owners__device {
      transform: translateX(-50%);
    }
  }

  .for-owners__hero {
    gap: 50px;
    padding: 30px 20px 60px;
  }

  .for-owners__intro-main {
    padding-top: calc(55vw * 900 / 600);
  }

  .for-owners__intro-copy {
    width: 100%;
  }

  .for-owners__title {
    font-size: 24px;
    line-height: 35px;
  }

  .for-owners__actions {
    flex-direction: column;
    gap: 15px;
  }

  .for-owners__actions :deep(.site-btn--stretch) {
    flex: none;
    width: 100%;
  }

  .for-owners__cards {
    flex-direction: column;
  }

  .for-owners__card {
    flex: none;
    width: 100%;
  }

  .for-owners__advantages {
    display: none;
  }
}
</style>
