<template>
  <section class="owners-goals">
    <h2 class="owners-goals__title">Ваш автомобиль. Ваша история. Ваш ДВИЖОК</h2>

    <div class="owners-goals__grid">
      <article class="owners-goals__card">
        <div class="owners-goals__copy">
          <h3 class="owners-goals__card-title">Сопровождение{{ '\n' }}на всем пути бесплатно</h3>
          <p class="owners-goals__card-desc">
            От записи до завершения обслуживания, ДВИЖОК помогает быть в курсе каждого этапа
          </p>
        </div>

        <div class="owners-goals__escort-row">
          <img class="owners-goals__man" src="/site/icons/for-clients/man.png" alt="" />
          <div class="owners-goals__free-badge">
            <p class="owners-goals__free-text">0 ₽{{ '\n' }}Всегда{{ '\n' }}бесплатно</p>
          </div>
        </div>
      </article>

      <article class="owners-goals__card owners-goals__card--control">
        <div class="owners-goals__copy">
          <h3 class="owners-goals__card-title">
            Контроль обслуживания{{ '\n' }}автомобиля на весь срок{{ '\n' }}владения
          </h3>
          <p class="owners-goals__card-desc">
            Все ТО, ремонты и важные события автомобиля в одной истории
          </p>
        </div>

        <div class="owners-goals__control-visual">
          <div class="owners-goals__control-max-wrap">
            <img
              class="owners-goals__control-max"
              src="/site/icons/for-services/max+1.png"
              alt=""
              width="80"
              height="76"
            />
          </div>

          <div class="owners-goals__control-col">
            <div class="owners-goals__control-data-wrap">
              <img
                class="owners-goals__control-data"
                src="/site/icons/for-clients/data-and-service.png"
                alt=""
              />
            </div>
            <SmsBubble side="left" color="blue" class="owners-goals__sms">
              {{ controlSms }}
            </SmsBubble>
          </div>
        </div>
      </article>

      <article class="owners-goals__card">
        <div class="owners-goals__copy">
          <h3 class="owners-goals__card-title">Сервис в пару кликов</h3>
          <p class="owners-goals__card-desc">
            Больше не нужно искать номер — выберите дату и время онлайн
          </p>
        </div>

        <div class="owners-goals__clicks-visual">
          <img
            class="owners-goals__no-phone"
            src="/site/icons/for-clients/no-phone-docs.png"
            alt=""
          />
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import SmsBubble from '@/components/ui/SmsBubble.vue'

const controlSms =
  'Добрый день!\n\nНапоминание о записи\n22 августа в 14:00, диагностика.\nАдрес мастерской: ул. Пушкина, 26'
</script>

<style scoped>
.owners-goals {
  display: flex;
  flex-direction: column;
  gap: 50px;
  padding: 80px;
  background: var(--dvijok-white);
}

.owners-goals__title {
  margin: 0;
  font-family: var(--dvijok-font-display);
  font-weight: 400;
  font-size: 32px;
  line-height: 46px;
  text-align: center;
  text-transform: uppercase;
  color: #000;
}

.owners-goals__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  align-items: stretch;
}

.owners-goals__card {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 40px;
  min-width: 0;
  padding: 19px;
  overflow: hidden;
  border: 1px solid var(--dvijok-text-secondary);
  background: transparent;
}

.owners-goals__card--control {
  gap: 5px;
}

.owners-goals__copy {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.owners-goals__card-title {
  margin: 0;
  font-weight: 600;
  font-size: 24px;
  line-height: 29px;
  white-space: pre-line;
  color: #000;
}

.owners-goals__card-desc {
  margin: 0;
  font-weight: 400;
  font-size: 18px;
  line-height: 22px;
  color: #000;
}

.owners-goals__escort-row {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: flex-start;
  gap: 5px;
  padding: 0 10px 0 20px;
}

.owners-goals__man {
  display: block;
  flex: none;
  width: 50%;
  height: auto;
  object-fit: contain;
}

.owners-goals__free-badge {
  box-sizing: border-box;
  flex: none;
  padding: 9px;
  border: 1px solid #8d8d8d;
  border-radius: 8px;
  background: var(--dvijok-white);
  box-shadow: 4px 4px 4px 0 #00000040;
}

.owners-goals__free-text {
  margin: 0;
  font-family: Inter, sans-serif;
  font-weight: 600;
  font-size: 16px;
  line-height: 19px;
  white-space: pre-line;
  color: #2e68ff;
}

.owners-goals__control-visual {
  display: flex;
  flex: 1;
  flex-direction: row;
  gap: 5px;
  align-items: stretch;
  min-height: 360px;
  min-width: 0;
}

.owners-goals__control-max-wrap {
  display: flex;
  flex: none;
  align-items: center;
  justify-content: center;
  align-self: stretch;
  transform: translateY(20px);
}

.owners-goals__control-max {
  display: block;
  width: 80px;
  height: 76px;
  object-fit: contain;
}

.owners-goals__control-col {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 5px;
  align-items: center;
  min-width: 0;
  min-height: 0;
  height: 100%;
}

.owners-goals__control-data-wrap {
  display: flex;
  flex: 0 0 60%;
  align-items: center;
  justify-content: center;
  min-height: 0;
  overflow: hidden;
}

.owners-goals__control-data {
  display: block;
  width: auto;
  max-width: 100%;
  max-height: 100%;
  height: auto;
  object-fit: contain;
  object-position: center;
}

.owners-goals__sms {
  flex: none;
  width: 100%;
  max-width: 260px;
}

.owners-goals__clicks-visual {
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: center;
  min-height: 220px;
}

.owners-goals__no-phone {
  display: block;
  max-width: 80%;
  max-height: 220px;
  height: auto;
  object-fit: contain;
}

@media (max-width: 1023px) {
  .owners-goals {
    position: relative;
    z-index: 1;
    padding: 40px 20px;
    box-shadow: 0 0 40px 80px var(--dvijok-white);
  }

  .owners-goals__title {
    font-size: 20px;
    line-height: 29px;
  }

  .owners-goals__grid {
    grid-template-columns: 1fr;
  }

  .owners-goals__card,
  .owners-goals__card--control {
    gap: 20px;
  }

  .owners-goals__card-title {
    font-size: 20px;
    line-height: 24px;
  }

  .owners-goals__control-visual {
    min-height: 360px;
  }

  .owners-goals__control-data {
    max-width: 85%;
  }

  .owners-goals__sms {
    max-width: 100%;
  }

  .owners-goals__clicks-visual {
    min-height: 160px;
  }
}
</style>
