<template>
  <q-page class="car-form">
    <ClientHeader :title="pageTitle" />

    <div class="car-form__body">
      <h2 class="car-form__section-title">{{ sectionTitle }}</h2>

      <form class="car-form__form" @submit.prevent="onSubmit">
        <BaseField
          v-model="form.brand"
          label="Марка автомобиля"
          placeholder="Toyota"
          required
          block
        />
        <BaseField
          v-model="form.model"
          label="Модель автомобиля"
          placeholder="Camry"
          required
          block
        />

        <PlateNumberField v-model="form.plate" v-model:type="form.plateType" />

        <BaseField
          v-model="form.vin"
          label="VIN"
          placeholder="17 символов из ПТС"
          mask="NNNNNNNNNNNNNNNNN"
          required
          block
        />
        <BaseField v-model="form.year" label="Год выпуска" placeholder="2019" mask="####" block />
        <BaseField
          v-model="form.color"
          label="Актуальный цвет автомобиля"
          placeholder="Белый"
          block
        />
        <BaseField
          v-model="form.mileage"
          label="Пробег (в км)"
          placeholder="66000"
          type="number"
          block
        />

        <BaseButton color="green" size="sm" block type="submit" :loading="saving">
          {{ submitLabel }}
        </BaseButton>
      </form>
    </div>

    <HomeTabs :model-value="tab" @update:model-value="goToHomeTab" />

    <SuccessModal
      v-model="successOpen"
      :title="successTitle"
      :note="successNote"
      @continue="onSuccessContinue"
    />
  </q-page>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { carsApi } from '@/api/index.js'
import PlateNumberField from '@/components/booking/PlateNumberField.vue'
import HomeTabs from '@/components/home/HomeTabs.vue'
import ClientHeader from '@/components/layout/ClientHeader.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseField from '@/components/ui/BaseField.vue'
import SuccessModal from '@/components/ui/SuccessModal.vue'

const route = useRoute()
const router = useRouter()

const tab = 'car'
const saving = ref(false)
const successOpen = ref(false)
const savedCarLabel = ref('')

const isEdit = computed(() => Boolean(route.params.id))
const pageTitle = computed(() => (isEdit.value ? 'Изменить автомобиль' : 'Добавить автомобиль'))
const sectionTitle = computed(() => (isEdit.value ? 'Введите новые данные' : 'Введите данные'))
const submitLabel = computed(() => (isEdit.value ? 'Сохранить изменения' : 'Добавить автомобиль'))

const successTitle = computed(() => {
  const label = savedCarLabel.value || 'автомобиль'
  if (isEdit.value) {
    return `Данные автомобиля ${label} успешно обновлены!`
  }
  return `Автомобиль ${label} успешно добавлен!`
})

const successNote = computed(() =>
  isEdit.value
    ? 'Изменения добавлены в раздел “Моё авто”'
    : 'Автомобиль добавлен в раздел “Моё авто”'
)

const form = reactive({
  brand: '',
  model: '',
  plate: '',
  plateType: 'ru',
  vin: '',
  year: '',
  color: '',
  mileage: ''
})

function fillForm(car) {
  form.brand = car.brand || ''
  form.model = car.model || ''
  form.plate = car.plate || ''
  form.plateType = car.plateType || 'ru'
  form.vin = car.vin || ''
  form.year = car.year != null ? String(car.year) : ''
  form.color = car.color || ''
  form.mileage = car.mileage != null ? String(car.mileage) : ''
}

function carLabelFromForm() {
  return [form.brand.trim(), form.model.trim()].filter(Boolean).join(' ')
}

function goToHomeTab(name) {
  router.push({ name: 'home', query: { tab: name } })
}

async function loadCar() {
  if (!isEdit.value) return
  const car = await carsApi.get(route.params.id)
  if (!car) {
    router.replace({ name: 'home', query: { tab: 'car' } })
    return
  }
  fillForm(car)
}

async function onSubmit() {
  if (saving.value) return
  if (!form.brand.trim() || !form.model.trim() || !form.vin.trim() || !form.plate.trim()) return

  saving.value = true
  try {
    const payload = {
      brand: form.brand.trim(),
      model: form.model.trim(),
      plate: form.plate.trim(),
      plateType: form.plateType,
      vin: form.vin.trim(),
      year: form.year.trim(),
      color: form.color.trim(),
      mileage: form.mileage
    }

    if (isEdit.value) {
      await carsApi.update(route.params.id, payload)
    } else {
      await carsApi.create(payload)
    }

    savedCarLabel.value = carLabelFromForm()
    successOpen.value = true
  } finally {
    saving.value = false
  }
}

function onSuccessContinue() {
  successOpen.value = false
  router.push({ name: 'home', query: { tab: 'car' } })
}

onMounted(loadCar)
</script>

<style scoped lang="scss">
.car-form {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 100%;
  overflow: auto;
}

.car-form__body {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 25px 15px;
  overflow: auto;
}

.car-form__section-title {
  margin: 0;
  font-weight: 600;
  font-size: 14px;
  line-height: 17px;
  color: var(--dvijok-text-secondary);
  text-transform: uppercase;
}

.car-form__form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.car-form__form :deep(.base-field__label),
.car-form__form :deep(.plate-field__label),
.car-form__form :deep(.plate-field__caption) {
  font-weight: 400;
  font-size: 12px;
  line-height: 15px;
  color: var(--dvijok-bg-dark);
}

.car-form__form :deep(.base-field__required),
.car-form__form :deep(.plate-field__required) {
  color: var(--dvijok-danger);
}
</style>
