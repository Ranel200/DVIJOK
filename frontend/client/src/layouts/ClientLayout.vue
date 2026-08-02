<template>
  <q-layout view="lHh Lpr lFf" class="client-layout">
    <q-page-container class="client-layout__content">
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup></script>

<style scoped lang="scss">
.client-layout {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.client-layout__content {
  flex: 1;
  min-height: 0;
  overflow: auto;
}
</style>
