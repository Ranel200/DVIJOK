<template>
  <q-page class="home-page">
    <img
      class="home-page__device"
      src="/site/icons/phone-laptop.webp"
      alt="DVIJOK на телефоне и ноутбуке"
      width="1200"
      height="900"
    />

    <section class="home-page__hero">
      <h1 class="home-page__title">Автосервисы и автовладельцы в одной системе</h1>

      <div class="home-page__audiences">
        <div v-for="audience in audiences" :key="audience.id" class="home-page__audience">
          <div class="home-page__audience-body">
            <h2 class="home-page__audience-title">{{ audience.heading }}</h2>

            <div class="home-page__audience-content">
              <p class="home-page__audience-lead">{{ audience.lead }}</p>

              <ul class="home-page__features">
                <li
                  v-for="feature in audience.features"
                  :key="feature.title"
                  class="home-page__feature"
                >
                  <img
                    class="home-page__feature-icon"
                    :src="feature.icon"
                    alt=""
                    width="50"
                    height="50"
                  />
                  <div class="home-page__feature-texts">
                    <p class="home-page__feature-title">{{ feature.title }}</p>
                    <p class="home-page__feature-subtitle">{{ feature.subtitle }}</p>
                  </div>
                </li>
              </ul>
            </div>
          </div>

          <router-link class="home-page__cta" :to="audience.to">
            {{ audience.cta }}
          </router-link>
        </div>
      </div>
    </section>

    <section class="home-page__advantages">
      <div class="home-page__advantages-intro">
        <div class="home-page__advantages-headings">
          <p class="home-page__advantages-eyebrow">Наши преимущества</p>
          <h2 class="home-page__advantages-title">ERP-система «ДВИЖОК»</h2>
        </div>
        <p class="home-page__advantages-lead">
          Целостный программный комплекс, который объединяет ключевые бизнес-процессы компании в
          единую информационную среду
        </p>
      </div>

      <div class="home-page__advantages-grid">
        <div
          v-for="card in advantageCards"
          :key="card.title"
          class="home-page__advantage-card"
          :class="[
            `home-page__advantage-card--${card.variant}`,
            `home-page__advantage-card--span-${card.span}`
          ]"
        >
          <img class="home-page__advantage-logo" :src="card.logo" alt="" />
          <h3 class="home-page__advantage-title">{{ card.title }}</h3>
          <p class="home-page__advantage-desc">{{ card.description }}</p>
        </div>
      </div>
    </section>
  </q-page>
</template>

<script setup>
const ICONS = {
  today: '/site/icons/today.svg',
  car: '/site/icons/car.svg',
  bookmark: '/site/icons/bookmark.svg',
  notifications: '/site/icons/notifications.svg'
}

const advantageCards = [
  {
    variant: 'dark',
    span: 3,
    logo: '/site/icons/chain.png',
    title: 'ДВИЖОК объединяет',
    description:
      'Автосервис и автовладелец в одной системе — запись, обслуживание и история автомобиля всегда под рукой'
  },
  {
    variant: 'light',
    span: 3,
    logo: '/site/icons/books.png',
    title: 'История автомобиля не теряется',
    description:
      'Смена автосервиса — не проблема. Вся история хранится в ДВИЖОК и принадлежит владельцу автомобиля, а не сервису.'
  },
  {
    variant: 'light',
    span: 2,
    logo: '/site/icons/record.png',
    title: 'Онлайн-запись',
    description: 'Онлайн-запись для клиентов и удобное управление расписанием для автосервиса'
  },
  {
    variant: 'light',
    span: 2,
    logo: '/site/icons/notification.png',
    title: 'Автоматические\nуведомления',
    description: 'Напоминания о записи, статусе ремонта и готовности автомобиля через MAX-бот'
  },
  {
    variant: 'light',
    span: 2,
    logo: '/site/icons/analytic.png',
    title: 'Аналитика для бизнеса',
    description:
      'Контролируйте выручку, загрузку сервиса, количество записей и рост клиентской базы в удобном дашборде'
  }
]

const audiences = [
  {
    id: 'owners',
    heading: 'Для автовладельцев',
    lead: 'Все данные о вашем автомобиле\nвсегда под рукой',
    cta: 'Я — автовладелец',
    to: { name: 'for-owners' },
    features: [
      {
        icon: ICONS.today,
        title: 'Запись в автосервис',
        subtitle: 'Онлайн-запись за 1 минуту'
      },
      {
        icon: ICONS.car,
        title: 'Мои автомобили',
        subtitle: 'Вся информация\nо вашем авто'
      },
      {
        icon: ICONS.bookmark,
        title: 'История и сервисная\nкнижка',
        subtitle: 'История ремонта\nи плановое ТО'
      },
      {
        icon: ICONS.notifications,
        title: 'Уведомления',
        subtitle: 'Напомнить о ТО и статусе\nвашего ремонта'
      }
    ]
  },
  {
    id: 'services',
    heading: 'Для автосервисов',
    lead: 'Полный контроль над работой\nавтосервиса в одном кабинете',
    cta: 'Я — владелец автосервиса',
    to: { name: 'for-services' },
    features: [
      {
        icon: ICONS.today,
        title: 'Запись в автосервис',
        subtitle: 'Управляйте онлайн-записью и\nзагруженностью сервиса'
      },
      {
        icon: ICONS.car,
        title: 'CRM',
        subtitle: 'Все клиенты, автомобили и записи\nв одном месте'
      },
      {
        icon: ICONS.bookmark,
        title: 'Задачник',
        subtitle: 'Ставьте задачи сотрудникам\nи контролируйте их выполнение'
      },
      {
        icon: ICONS.notifications,
        title: 'Уведомления',
        subtitle: 'Автоматически информируйте клиентов о записи,\nремонте и ТО'
      }
    ]
  }
]
</script>

<style scoped>
.home-page {
  position: relative;
  box-sizing: border-box;
  padding: 0;
  background: var(--dvijok-bg-light);
}

.home-page__device {
  position: absolute;
  top: 270px;
  left: 50%;
  z-index: 0;
  width: 60vw;
  height: auto;
  pointer-events: none;
  transform: translateX(-50%);
}

.home-page__hero {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 30px;
  padding: 20px 40px;
}

.home-page__title {
  margin: 0;
  font-family: var(--dvijok-font-display);
  font-weight: 400;
  font-size: 48px;
  line-height: 70px;
  text-transform: uppercase;
  color: var(--dvijok-text-heading);
}

.home-page__audiences {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  gap: 30px;
}

.home-page__audience {
  display: flex;
  flex-direction: column;
  gap: 70px;
}

.home-page__audience-body {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.home-page__audience-title {
  margin: 0;
  font-family: var(--dvijok-font-display);
  font-weight: 400;
  font-size: 24px;
  line-height: 35px;
  text-transform: uppercase;
  color: var(--dvijok-blue-bright);
}

.home-page__audience-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.home-page__audience-lead {
  margin: 0;
  font-weight: 400;
  font-size: 18px;
  line-height: 22px;
  white-space: pre-line;
  color: var(--dvijok-text-primary);
}

.home-page__features {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.home-page__feature {
  display: flex;
  flex-direction: row;
  gap: 20px;
  align-items: flex-start;
}

.home-page__feature-icon {
  flex: 0 0 50px;
  width: 50px;
  height: 50px;
  object-fit: contain;
}

.home-page__feature-texts {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.home-page__feature-title {
  margin: 0;
  font-weight: 500;
  font-size: 16px;
  line-height: 19px;
  white-space: pre-line;
  color: var(--dvijok-text-primary);
}

.home-page__feature-subtitle {
  margin: 0;
  font-weight: 400;
  font-size: 14px;
  line-height: 17px;
  white-space: pre-line;
  color: var(--dvijok-text-secondary);
}

.home-page__cta {
  box-sizing: border-box;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  max-width: 350px;
  padding: 15px;
  border: none;
  background: var(--dvijok-blue-bright);
  font-weight: 600;
  font-size: 14px;
  line-height: 17px;
  text-align: center;
  text-decoration: none;
  color: var(--dvijok-white);
}

.home-page__advantages {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 50px;
  padding: 120px 80px 80px;
}

.home-page__advantages-intro {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  text-align: center;
}

.home-page__advantages-headings {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.home-page__advantages-eyebrow {
  margin: 0;
  font-weight: 500;
  font-size: 20px;
  line-height: 24px;
  text-transform: uppercase;
  color: var(--dvijok-blue-bright);
}

.home-page__advantages-title {
  margin: 0;
  font-family: var(--dvijok-font-display);
  font-weight: 400;
  font-size: 32px;
  line-height: 46px;
  text-transform: uppercase;
  color: var(--dvijok-text-heading);
}

.home-page__advantages-lead {
  margin: 0;
  font-weight: 400;
  font-size: 16px;
  line-height: 19px;
  color: var(--dvijok-text-secondary);
}

.home-page__advantages-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 20px;
}

.home-page__advantage-card {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.home-page__advantage-card--span-3 {
  grid-column: span 3;
}

.home-page__advantage-card--span-2 {
  grid-column: span 2;
}

.home-page__advantage-card--dark {
  padding: 20px;
  background: var(--dvijok-navy);
  color: var(--dvijok-white);
}

.home-page__advantage-card--light {
  padding: 19px;
  border: 1px solid var(--dvijok-text-secondary);
  background: transparent;
  color: var(--dvijok-text-primary);
}

.home-page__advantage-logo {
  display: block;
  flex: none;
  align-self: flex-start;
  width: auto;
  height: auto;
}

.home-page__advantage-title {
  margin: 0;
  font-weight: 600;
  font-size: 24px;
  line-height: 29px;
  white-space: pre-line;
  color: inherit;
}

.home-page__advantage-desc {
  margin: 0;
  font-weight: 400;
  font-size: 18px;
  line-height: 22px;
  color: inherit;
}
</style>
