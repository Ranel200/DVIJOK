<template>
  <q-page class="dashboard">
    <h1 class="dashboard__title">Клиентский кабинет</h1>
    <p class="dashboard__lead">Здесь появится запись, история визитов и профиль.</p>
  </q-page>
</template>

<script setup></script>

<style scoped lang="scss">
.dashboard {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 48px 24px;
  text-align: center;
}

.dashboard__title {
  margin: 0;
  font-size: 32px;
  font-weight: 700;
}

.dashboard__lead {
  margin: 0;
  color: #7a82a0;
  font-size: 16px;
}
</style>
