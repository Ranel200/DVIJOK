<template>
  <div class="car-panel">
    <div ref="carouselRef" class="car-panel__carousel" @scroll="onCarouselScroll">
      <AppBlock
        v-for="car in cars"
        :key="car.id"
        variant="dark"
        class="car-panel__slide car-panel__car"
      >
        <span class="car-panel__car-bg" aria-hidden="true">
          <span class="car-panel__car-glass" />
          <img src="/client/icons/my-car/car.svg" alt="" />
        </span>

        <div class="car-panel__car-body">
          <div class="car-panel__car-head">
            <span class="car-panel__car-label">Автомобиль</span>
            <button
              type="button"
              class="car-panel__edit"
              aria-label="Редактировать автомобиль"
              @click="onEdit(car)"
            >
              <img src="/client/icons/my-car/edit.svg" alt="" width="20" height="20" />
            </button>
          </div>

          <div class="car-panel__car-main">
            <span class="car-panel__car-brand">{{ car.brand }}</span>
            <span class="car-panel__car-meta">{{ car.year }} · {{ car.color }}</span>
          </div>

          <div class="car-panel__plate">{{ car.plate }}</div>

          <div class="car-panel__vin">
            <span class="car-panel__vin-label">VIN</span>
            <span class="car-panel__vin-value">{{ car.vin }}</span>
          </div>

          <div
            v-if="cars.length > 1"
            class="car-panel__dots"
            role="tablist"
            aria-label="Автомобили"
          >
            <button
              v-for="(_, index) in cars.length"
              :key="index"
              type="button"
              class="car-panel__dot"
              :class="{ 'car-panel__dot--active': activeCarIndex === index }"
              :aria-label="`Автомобиль ${index + 1}`"
              :aria-selected="activeCarIndex === index"
              @click="scrollToSlide(index)"
            />
          </div>
        </div>
      </AppBlock>

      <AppBlock variant="dark" class="car-panel__slide car-panel__add">
        <span class="car-panel__add-icon" aria-hidden="true">
          <img src="/client/icons/my-car/car.svg" alt="" width="342" height="113" />
        </span>
        <BaseButton color="blue2" size="sm" @click="onAddCar"> + Добавить автомобиль </BaseButton>
      </AppBlock>
    </div>

    <template v-if="activeCar">
      <AppBlock v-if="activeCar.nextAppointment" variant="dark">
        <div class="car-panel__appointment">
          <h2 class="car-panel__appointment-title">Ваша ближайшая запись</h2>
          <div class="car-panel__glass car-panel__appointment-card">
            <div class="car-panel__appointment-head">
              <span class="car-panel__appointment-service">
                Сервис: “{{ activeCar.nextAppointment.serviceName }}”
              </span>
              <span class="car-panel__appointment-datetime">
                {{ activeCar.nextAppointment.datetime }}
              </span>
            </div>
            <p class="car-panel__appointment-line">
              Услуга: {{ activeCar.nextAppointment.service }}
            </p>
            <p class="car-panel__appointment-line">
              Мастер: {{ activeCar.nextAppointment.master }}
            </p>
            <p class="car-panel__appointment-line">Авто: {{ activeCar.nextAppointment.car }}</p>
          </div>
        </div>
      </AppBlock>

      <AppBlock
        title="Получайте уведомления в чат боте"
        subtitle="Напоминания о ТО, замене масла, статус ремонта и другое"
      >
        <div class="car-panel__bots">
          <a
            v-for="bot in bots"
            :key="bot.id"
            class="car-panel__bot"
            :href="bot.href"
            target="_blank"
            rel="noopener noreferrer"
          >
            <img class="car-panel__bot-logo" :src="bot.icon" alt="" />
            <span class="car-panel__bot-label">{{ bot.label }}</span>
          </a>
        </div>
      </AppBlock>

      <AppBlock variant="dark">
        <div class="car-panel__data">
          <h2 class="car-panel__data-title">Данные и обслуживание</h2>
          <ul class="car-panel__data-list">
            <li
              v-for="item in activeCar.maintenance"
              :key="item.label"
              class="car-panel__glass car-panel__data-item"
            >
              <span class="car-panel__data-label">{{ item.label }}</span>
              <span class="car-panel__data-value">{{ item.value }}</span>
            </li>
          </ul>
        </div>
      </AppBlock>

      <AppBlock v-if="activeCar.repair" title="Статус ремонта" :subtitle="repairSubtitle">
        <div class="car-panel__status" role="list">
          <div
            v-for="(status, index) in activeCar.repair.statuses"
            :key="status.id"
            class="car-panel__status-row"
            role="listitem"
          >
            <div class="car-panel__status-rail">
              <StatusRadio :color="statusRadioColor(status)" :filled="status.state === 'done'" />
              <span
                v-if="index < activeCar.repair.statuses.length - 1"
                class="car-panel__status-line"
              />
            </div>

            <div class="car-panel__status-body">
              <span class="car-panel__status-title" :style="{ color: statusTitleColor(status) }">
                {{ status.title }}
              </span>
              <span class="car-panel__status-subtitle">{{ status.subtitle }}</span>
              <button
                v-if="status.state === 'current' && status.action"
                type="button"
                class="car-panel__status-action"
                @click="onStatusAction(status)"
              >
                {{ status.action }}
              </button>
            </div>
          </div>
        </div>
      </AppBlock>
    </template>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { carsApi } from '@/api/index.js'
import AppBlock from '@/components/ui/AppBlock.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import StatusRadio from '@/components/ui/StatusRadio.vue'

const INACTIVE_COLOR = '#7A82A0'

const cars = ref([])
const bots = ref([])
const activeSlide = ref(0)
const carouselRef = ref(null)

let removeSwipeGuards = null

const activeCarIndex = computed(() => {
  if (!cars.value.length) return 0
  return Math.min(activeSlide.value, cars.value.length - 1)
})

const activeCar = computed(() => {
  if (!cars.value.length) return null
  return cars.value[activeCarIndex.value] || null
})

const repairSubtitle = computed(() => {
  const car = activeCar.value
  if (!car?.repair) return ''
  return `Заказ-наряд №${car.repair.orderNumber} · ${car.repair.carLabel}`
})

function statusRadioColor(status) {
  if (status.state === 'inactive') return INACTIVE_COLOR
  return status.color
}

function statusTitleColor(status) {
  if (status.state === 'inactive') return INACTIVE_COLOR
  return status.color
}

function stopPageSwipe(event) {
  event.stopPropagation()
}

function bindSwipeGuards(el) {
  const opts = { capture: true, passive: true }
  el.addEventListener('touchstart', stopPageSwipe, opts)
  el.addEventListener('touchmove', stopPageSwipe, opts)
  el.addEventListener('touchend', stopPageSwipe, opts)
  el.addEventListener('pointerdown', stopPageSwipe, opts)
  return () => {
    el.removeEventListener('touchstart', stopPageSwipe, opts)
    el.removeEventListener('touchmove', stopPageSwipe, opts)
    el.removeEventListener('touchend', stopPageSwipe, opts)
    el.removeEventListener('pointerdown', stopPageSwipe, opts)
  }
}

function getCarouselGap(el) {
  const styles = getComputedStyle(el)
  return parseFloat(styles.columnGap || styles.gap) || 0
}

function onCarouselScroll() {
  const el = carouselRef.value
  if (!el) return
  const slide = el.querySelector('.car-panel__slide')
  if (!slide) return
  const slideWidth = slide.offsetWidth + getCarouselGap(el)
  const index = Math.round(el.scrollLeft / slideWidth)
  const maxIndex = cars.value.length
  activeSlide.value = Math.max(0, Math.min(index, maxIndex))
}

function scrollToSlide(index) {
  const el = carouselRef.value
  if (!el) return
  const slide = el.querySelector('.car-panel__slide')
  if (!slide) return
  el.scrollTo({
    left: index * (slide.offsetWidth + getCarouselGap(el)),
    behavior: 'smooth'
  })
  activeSlide.value = index
}

function onEdit() {}

function onAddCar() {}

function onStatusAction() {}

onMounted(async () => {
  const data = await carsApi.list()
  cars.value = data.cars || []
  bots.value = data.bots || []
  activeSlide.value = 0
  await nextTick()
  if (carouselRef.value) {
    carouselRef.value.scrollLeft = 0
    removeSwipeGuards = bindSwipeGuards(carouselRef.value)
  }
})

onBeforeUnmount(() => {
  removeSwipeGuards?.()
})
</script>

<style scoped lang="scss">
.car-panel {
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 25px 15px;
}

.car-panel__carousel {
  display: flex;
  flex-direction: row;
  gap: 20px;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  touch-action: pan-x;
  scrollbar-width: none;
  -ms-overflow-style: none;

  &::-webkit-scrollbar {
    display: none;
  }
}

.car-panel__slide {
  position: relative;
  flex: 0 0 100%;
  width: 100%;
  min-width: 100%;
  scroll-snap-align: start;
  box-sizing: border-box;
  overflow: hidden;
}

.car-panel__carousel .car-panel__car {
  padding: 15px 30px;
  gap: 0;
}

.car-panel__car-bg {
  position: absolute;
  right: 0;
  bottom: 25px;
  z-index: 0;
  width: 230px;
  height: auto;
  aspect-ratio: 342 / 113;
  pointer-events: none;
  transform: translate(20%, 0);
}

.car-panel__car-bg img,
.car-panel__add-icon img {
  position: relative;
  z-index: 1;
  display: block;
  width: 100%;
  height: auto;
}

.car-panel__car-glass {
  position: absolute;
  inset: 0;
  z-index: 0;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.14);
  -webkit-mask: url('/client/icons/my-car/car-mask.svg') center / contain no-repeat;
  mask: url('/client/icons/my-car/car-mask.svg') center / contain no-repeat;
}

.car-panel__car-body {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.car-panel__car-head {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.car-panel__car-label {
  font-weight: 400;
  font-size: 13px;
  line-height: 16px;
  color: var(--dvijok-tab-inactive);
  text-transform: uppercase;
}

.car-panel__edit {
  display: inline-flex;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
  line-height: 0;
}

.car-panel__car-main {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.car-panel__car-brand {
  font-weight: 600;
  font-size: 20px;
  line-height: 30px;
  color: var(--dvijok-white);
  text-transform: uppercase;
}

.car-panel__car-meta {
  font-weight: 600;
  font-size: 13px;
  line-height: 16px;
  color: var(--dvijok-white);
}

.car-panel__plate {
  align-self: flex-start;
  padding: 6px 10px;
  border-radius: 6px;
  background: var(--dvijok-white);
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-text-primary);
}

.car-panel__vin {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.car-panel__vin-label {
  font-weight: 400;
  font-size: 13px;
  line-height: 16px;
  color: var(--dvijok-tab-inactive);
}

.car-panel__vin-value {
  font-weight: 600;
  font-size: 13px;
  line-height: 16px;
  color: var(--dvijok-white);
}

.car-panel__dots {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  gap: 4px;
  padding-top: 10px;
}

.car-panel__dot {
  width: 8px;
  height: 8px;
  padding: 0;
  border: 1px solid var(--dvijok-tab-inactive);
  border-radius: 50%;
  background: transparent;
  cursor: pointer;
}

.car-panel__dot--active {
  border-color: var(--dvijok-white);
  background: var(--dvijok-white);
}

.car-panel__carousel .car-panel__add {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

.car-panel__add-icon {
  position: relative;
  display: block;
  width: 342px;
  height: 113px;
  max-width: 100%;
  flex-shrink: 0;
}

.car-panel__appointment {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.car-panel__appointment-title {
  margin: 0;
  font-weight: 700;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-white);
}

.car-panel__glass {
  position: relative;
  isolation: isolate;
  padding: 8px 10px;
  overflow: hidden;
  border-radius: 5px;
  box-sizing: border-box;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.14);

  &::before {
    content: '';
    position: absolute;
    inset: 0;
    z-index: 1;
    border-radius: inherit;
    padding: 1px;
    background: linear-gradient(
      135deg,
      rgba(255, 255, 255, 0.5) 0%,
      rgba(255, 255, 255, 0) 22%,
      rgba(255, 255, 255, 0) 78%,
      rgba(255, 255, 255, 0.4) 100%
    );
    -webkit-mask:
      linear-gradient(#fff 0 0) content-box,
      linear-gradient(#fff 0 0);
    mask:
      linear-gradient(#fff 0 0) content-box,
      linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    pointer-events: none;
  }

  > * {
    position: relative;
    z-index: 2;
  }
}

.car-panel__appointment-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
  border: none;
}

.car-panel__appointment-head {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.car-panel__appointment-service {
  font-weight: 700;
  font-size: 13px;
  line-height: 16px;
  color: var(--dvijok-white);
}

.car-panel__appointment-datetime {
  flex-shrink: 0;
  font-weight: 600;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-white);
}

.car-panel__appointment-line {
  margin: 0;
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-white);
}

.car-panel__bots {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}

.car-panel__bot {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  text-decoration: none;
  color: inherit;
}

.car-panel__bot-logo {
  display: block;
  width: 40px;
  height: 40px;
  object-fit: contain;
}

.car-panel__bot-label {
  font-weight: 400;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-blue-primary);
  text-decoration: underline;
  text-align: center;
}

.car-panel__data {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.car-panel__data-title {
  margin: 0;
  font-weight: 700;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-white);
}

.car-panel__data-list {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.car-panel__data-item {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.car-panel__data-label {
  font-weight: 400;
  font-size: 13px;
  line-height: 16px;
  color: var(--dvijok-white);
}

.car-panel__data-value {
  font-weight: 600;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-white);
  text-align: right;
}

.car-panel__status {
  display: flex;
  flex-direction: column;
}

.car-panel__status-row {
  display: grid;
  grid-template-columns: 27px 1fr;
  column-gap: 20px;
}

.car-panel__status-rail {
  display: flex;
  flex-direction: column;
  align-items: center;
  grid-row: 1 / -1;
}

.car-panel__status-line {
  flex: 1 0 auto;
  width: 1px;
  min-height: 12px;
  margin: 1px 0;
  background: var(--dvijok-tab-inactive);
}

.car-panel__status-body {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 2px;
  min-height: 27px;
  padding-bottom: 16px;
  min-width: 0;
}

.car-panel__status-row:last-child .car-panel__status-body {
  padding-bottom: 0;
}

.car-panel__status-title {
  font-weight: 700;
  font-size: 14px;
  line-height: 17px;
}

.car-panel__status-subtitle {
  font-weight: 400;
  font-size: 11px;
  line-height: 13px;
  color: var(--dvijok-text-secondary);
}

.car-panel__status-action {
  align-self: flex-start;
  margin-top: 2px;
  padding: 0;
  border: none;
  background: transparent;
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-blue-primary);
  text-decoration: underline;
  cursor: pointer;

  &:hover {
    text-decoration: none;
  }
}
</style>
