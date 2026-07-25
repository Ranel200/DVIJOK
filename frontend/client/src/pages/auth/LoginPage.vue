<template>
  <q-page class="login">
    <div class="login__card">
      <h1 class="login__title">Вход в кабинет</h1>
      <p class="login__subtitle">Введите данные вашего аккаунта</p>
    </div>
  </q-page>
</template>

<script setup></script>

<style scoped lang="scss">
.login {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: #d1daf3;
}

.login__card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
  max-width: 480px;
  padding: 48px;
  background-color: #fff;
  border-radius: 15px;
  text-align: center;
}

.login__title {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: #0f1f4a;
}

.login__subtitle {
  margin: 0;
  color: #7a82a0;
  font-size: 14px;
}
</style>
