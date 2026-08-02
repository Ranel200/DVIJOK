<template>
  <BookingFlow
    v-if="bookingService"
    :service-id="bookingService.id"
    :service-name="bookingService.name"
    @close="bookingService = null"
    @complete="onBookingComplete"
    @go-to-car="onGoToCar"
  />

  <div v-else class="book-panel">
    <AppBlock title="Найдите автосервис">
      <BaseInput
        v-model="query"
        class="book-panel__search"
        placeholder="Введите название или услугу"
        block
        :input-attrs="{ 'aria-label': 'Поиск автосервиса' }"
      >
        <template #prepend>
          <img
            class="book-panel__search-icon"
            src="/client/icons/record/search.svg"
            alt=""
            width="13"
            height="13"
          />
        </template>
      </BaseInput>
    </AppBlock>

    <section class="book-panel__section" aria-labelledby="book-yours-title">
      <h2 id="book-yours-title" class="book-panel__section-title">Ваши автосервисы</h2>
      <div class="book-panel__list">
        <ServiceCard
          v-for="item in yourServices"
          :key="item.id"
          :name="item.name"
          :address="item.address"
          :hours="item.hours"
          :description="item.description"
          :rating="item.rating"
          :reviews="item.reviews"
          :last-visit="item.lastVisit"
          @book="startBooking(item)"
        />
      </div>
    </section>

    <section class="book-panel__section" aria-labelledby="book-all-title">
      <div class="book-panel__section-head">
        <h2 id="book-all-title" class="book-panel__section-title">Все сервисы</h2>
        <span class="book-panel__city">{{ city }}</span>
      </div>
      <div class="book-panel__list">
        <ServiceCard
          v-for="item in allServices"
          :key="item.id"
          :name="item.name"
          :address="item.address"
          :hours="item.hours"
          :description="item.description"
          :rating="item.rating"
          :reviews="item.reviews"
          @book="startBooking(item)"
        />
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { servicesApi } from '@/api/index.js'
import AppBlock from '@/components/ui/AppBlock.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BookingFlow from '@/components/home/BookingFlow.vue'
import ServiceCard from '@/components/home/ServiceCard.vue'

const emit = defineEmits(['go-to-car'])

const query = ref('')
const city = ref('г. Казань')
const yourServices = ref([])
const allServices = ref([])
const bookingService = ref(null)

let loadSeq = 0
let searchTimer = null

async function loadServices() {
  const seq = ++loadSeq
  const data = await servicesApi.list({ query: query.value })
  if (seq !== loadSeq) return
  city.value = data.city
  yourServices.value = data.yours
  allServices.value = data.all
}

function startBooking(item) {
  bookingService.value = item
}

function onBookingComplete() {
  bookingService.value = null
}

function onGoToCar() {
  bookingService.value = null
  emit('go-to-car')
}

watch(query, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    loadServices()
  }, 250)
})

onMounted(() => {
  loadServices()
})
</script>

<style scoped lang="scss">
.book-panel {
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 25px 15px;
}

.book-panel__search {
  :deep(.q-field__prepend) {
    padding-right: 10px;
  }
}

.book-panel__search-icon {
  display: block;
}

.book-panel__section {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.book-panel__section-head {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.book-panel__section-title {
  margin: 0;
  font-weight: 600;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-text-secondary);
  text-transform: uppercase;
}

.book-panel__city {
  flex-shrink: 0;
  font-weight: 400;
  font-size: 13px;
  line-height: 16px;
  color: var(--dvijok-text-secondary);
}

.book-panel__list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
</style>
