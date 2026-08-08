<template>
  <div class="details-step">
    <BookingStepHead :name="branchName" :address="branchAddress" @back="emit('back')" />

    <h2 class="booking-step-title">Детали записи</h2>

    <BookingDetailRow
      avatar
      :avatar-color="specialistAvatarColor"
      :title="specialistName"
      :subtitle="specialistRole"
      edit-label="Изменить специалиста"
      @edit="emit('edit', 'specialist')"
    />

    <BookingDetailRow
      icon="/client/icons/record/calendar.svg"
      :icon-width="23"
      :icon-height="25"
      :title="dateLabel"
      :subtitle="timeRange"
      edit-label="Изменить дату"
      @edit="emit('edit', 'datetime')"
    />

    <BookingDetailRow
      icon="/client/icons/record/doc.svg"
      :icon-width="21"
      :icon-height="25"
      :title="serviceLabel"
      :subtitle="timeRange"
      :price="servicePrice"
      edit-label="Изменить услугу"
      @edit="emit('edit', 'service')"
    />

    <h2 class="booking-step-title">Ваши данные</h2>

    <form class="details-step__form" @submit.prevent="onSubmit">
      <BaseField v-model="form.name" label="Фамилия Имя *" placeholder="Иванов Иван" block />
      <BaseField
        v-model="form.phone"
        label="Номер телефона *"
        placeholder="+7 999 999 99 99"
        mask="+7 ### ### ## ##"
        block
      />
      <BaseField v-model="form.brand" label="Марка автомобиля *" placeholder="Toyota" block />
      <BaseField v-model="form.model" label="Модель автомобиля *" placeholder="Camry" block />

      <PlateNumberField v-model="plate" v-model:type="plateType" />

      <div class="details-step__consents">
        <BaseCheckbox v-model="form.consentPersonal">
          Я даю согласие на
          <a
            class="details-step__link"
            href="/docs/consent-personal-data.html"
            target="_blank"
            rel="noopener noreferrer"
            @click.stop
            >обработку персональных данных</a
          >
        </BaseCheckbox>
        <BaseCheckbox v-model="form.consentTransfer">
          Я даю согласие на
          <a
            class="details-step__link"
            href="/docs/consent-transfer-autoservice.html"
            target="_blank"
            rel="noopener noreferrer"
            @click.stop
            >передачу моих данных выбранному автосервису</a
          >
        </BaseCheckbox>
      </div>

      <BaseButton color="green" size="sm" block type="submit">Записаться</BaseButton>
    </form>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseCheckbox from '@/components/ui/BaseCheckbox.vue'
import BaseField from '@/components/ui/BaseField.vue'
import BookingDetailRow from '@/components/booking/BookingDetailRow.vue'
import BookingStepHead from '@/components/booking/BookingStepHead.vue'
import PlateNumberField from '@/components/booking/PlateNumberField.vue'

defineProps({
  branchName: {
    type: String,
    default: ''
  },
  branchAddress: {
    type: String,
    default: ''
  },
  specialistName: {
    type: String,
    default: ''
  },
  specialistRole: {
    type: String,
    default: ''
  },
  specialistAvatarColor: {
    type: String,
    default: 'var(--dvijok-accent-coral)'
  },
  dateLabel: {
    type: String,
    default: ''
  },
  timeRange: {
    type: String,
    default: ''
  },
  serviceLabel: {
    type: String,
    default: ''
  },
  servicePrice: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['back', 'edit', 'submit'])

const form = reactive({
  name: '',
  phone: '',
  brand: '',
  model: '',
  consentPersonal: false,
  consentTransfer: false
})

const plate = ref('')
const plateType = ref('ru')

function onSubmit() {
  emit('submit', {
    ...form,
    plateType: plateType.value,
    plate: plate.value
  })
}
</script>

<style scoped lang="scss">
.details-step {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.details-step__form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.details-step__consents {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.details-step__link {
  color: var(--dvijok-bg-dark);
  text-decoration: underline;
}
</style>
