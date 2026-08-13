<template>
  <AdminHeader :action="action" @action-click="onAction">
    <template #action-icon>
      <PrinterIcon />
    </template>
  </AdminHeader>
  <div class="qr">
    <div class="qr__card">
      <div class="qr__code" v-html="referral?.qr_svg"></div>
      <div class="qr__info">
        <img
          src="/admin/icons/qr/logo-client.png"
          alt="Логотип клиентского сервиса"
          class="qr__logo"
        />
        <div class="qr__text">
          <h2 class="qr__title">Добро пожаловать в клиентский сервис!</h2>
          <p class="qr__subtitle">
            Войдите, чтобы управлять своими заказами<br />
            и отслеживать состояние автомобиля
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import AdminHeader from '@/components/layout/AdminHeader.vue'
import PrinterIcon from '@/components/ui/PrinterIcon.vue'
import { referralsApi } from '@/api/index.js'

const action = { label: 'Напечатать QR-код' }
const referral = ref(null)

function withBrandColor(svg) {
  return svg?.replace('fill="#000000"', 'fill="#051b54"')
}

function onAction() {
  const svg = referral.value?.qr_svg
  if (!svg) return

  const printWindow = window.open('', '_blank')
  if (!printWindow) return
  printWindow.opener = null

  printWindow.document.open()
  printWindow.document.write(`<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8" />
    <title>QR-код автосервиса</title>
    <style>
      body { margin: 0; min-height: 100vh; display: grid; place-items: center; }
      svg { width: 120mm; height: 120mm; }
      @page { margin: 15mm; }
    </style>
  </head>
  <body>${svg}</body>
</html>`)
  printWindow.document.close()
  printWindow.focus()
  printWindow.print()
  printWindow.close()
}

onMounted(async () => {
  const result = await referralsApi.getOrCreate()
  referral.value = { ...result, qr_svg: withBrandColor(result.qr_svg) }
})
</script>

<style scoped lang="scss">
.qr {
  padding: 0 20px 20px;
}

.qr__card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 50px;
  padding: 100px 80px;
  background-color: var(--dvijok-white);
  border-radius: 15px;
}

.qr__code {
  width: 415px;
  height: 415px;
  flex: 0 0 415px;
}

.qr__code :deep(svg) {
  display: block;
  width: 100%;
  height: 100%;
}

.qr__info {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 50px;
  justify-content: center;
  min-width: 0;
}

.qr__logo {
  display: block;
  max-width: 100%;
  height: auto;
}

.qr__text {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.qr__title {
  margin: 0;
  font-weight: 600;
  font-size: 24px;
  line-height: 29px;
  color: var(--dvijok-bg-dark);
}

.qr__subtitle {
  margin: 0;
  font-weight: 400;
  font-size: 20px;
  line-height: 24px;
  color: var(--dvijok-text-secondary);
}
</style>
