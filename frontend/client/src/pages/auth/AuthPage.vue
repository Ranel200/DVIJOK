<template>
  <q-page class="auth-page">
    <h1 class="auth-page__title">{{ title }}</h1>

    <q-btn flat color="primary" :label="toggleLabel" :to="{ name: toggleRoute }" />
  </q-page>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const isLogin = computed(() => route.name === 'login')
const title = computed(() => route.meta.title || (isLogin.value ? 'Вход' : 'Регистрация'))
const toggleLabel = computed(() => (isLogin.value ? 'Регистрация' : 'Вход'))
const toggleRoute = computed(() => (isLogin.value ? 'register' : 'login'))
</script>

<style scoped></style>
