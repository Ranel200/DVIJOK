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
        <div v-if="referral?.url" class="qr__link-row">
          <button
            type="button"
            class="qr__link"
            title="Скопировать ссылку"
            @click="copyReferralUrl"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path
                d="M10.6 13.4a1 1 0 0 1 0-1.4l3.4-3.4a3 3 0 1 1 4.2 4.2l-2.4 2.4a3 3 0 0 1-4.2 0 1 1 0 0 1 1.4-1.4 1 1 0 0 0 1.4 0l2.4-2.4a1 1 0 0 0-1.4-1.4L12 13.4a1 1 0 0 1-1.4 0Zm2.8-2.8a1 1 0 0 1 0 1.4L10 15.4a3 3 0 1 1-4.2-4.2l2.4-2.4a3 3 0 0 1 4.2 0 1 1 0 0 1-1.4 1.4 1 1 0 0 0-1.4 0l-2.4 2.4A1 1 0 0 0 8.6 14l3.4-3.4a1 1 0 0 1 1.4 0Z"
              />
            </svg>
            <span>{{ referral.url }}</span>
          </button>
          <span class="qr__link-label">Ссылка на регистрацию</span>
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

async function copyReferralUrl() {
  const url = referral.value?.url
  if (!url) return

  try {
    await navigator.clipboard.writeText(url)
  } catch {
    const textarea = document.createElement('textarea')
    textarea.value = url
    textarea.style.position = 'fixed'
    textarea.style.opacity = '0'
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    textarea.remove()
  }
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

.qr__link-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 30px;
}

.qr__link {
  display: inline-flex;
  align-items: center;
  gap: 16px;
  flex: 1;
  min-width: 0;
  margin: 0;
  padding: 0;
  overflow: hidden;
  border: none;
  background: none;
  cursor: pointer;
  font-family: inherit;
  text-align: left;
  color: var(--dvijok-link);
  font-size: 18px;
  line-height: 22px;
}

.qr__link svg {
  width: 36px;
  height: 36px;
  flex: 0 0 36px;
  fill: currentColor;
}

.qr__link span {
  min-width: 0;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  text-decoration: underline;
}

.qr__link-label {
  flex: 0 0 auto;
  color: var(--dvijok-text-secondary);
  font-size: 16px;
  line-height: 20px;
}
</style>
