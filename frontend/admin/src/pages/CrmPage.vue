<template>
  <AdminHeader
    :tabs="tabs"
    v-model:active-tab="activeTab"
    :action="action"
    @action-click="onAction"
  >
    <template #title-trailing>
      <div class="crm-filter">
        <span class="crm-filter__text">Все заказы</span>
        <ArrowIcon direction="down" :size="14" class="crm-filter__arrow" />
      </div>

      <div class="crm-filter">
        <span class="crm-filter__text">В работе</span>
        <img src="/admin/icons/close-14.svg" alt="" class="crm-filter__icon" />
      </div>

      <label class="crm-filter crm-filter--search">
        <img src="/admin/icons/search.svg" alt="" class="crm-filter__icon" />
        <input v-model="search" type="text" class="crm-filter__input" placeholder="Поиск" />
      </label>
    </template>
  </AdminHeader>
  <div class="crm"></div>
</template>

<script setup>
import { ref } from 'vue'
import AdminHeader from '@/components/layout/AdminHeader.vue'
import ArrowIcon from '@/components/ui/ArrowIcon.vue'

const tabs = [
  { label: 'Канбан', value: 'kanban' },
  { label: 'Список', value: 'list' }
]
const activeTab = ref('kanban')

const action = { label: '+ Новый заказ' }

const search = ref('')

function onAction() {
  // TODO: открыть форму нового заказа
}
</script>

<style scoped lang="scss">
.crm-filter {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 11px 15px;
  width: 160px;
  box-sizing: border-box;
  border: 1px solid var(--dvijok-bg-dark);
  border-radius: 8px;
}

.crm-filter__text {
  color: var(--dvijok-bg-dark);
  font-size: 12px;
  line-height: 14px;
  font-weight: 400;
}

.crm-filter__arrow {
  color: var(--dvijok-bg-dark);
  flex-shrink: 0;
}

.crm-filter__icon {
  display: block;
  flex-shrink: 0;
}

.crm-filter--search {
  padding: 6px 10px;
  width: 220px;
}

.crm-filter__input {
  flex: 1;
  min-width: 0;
  border: none;
  outline: none;
  background: transparent;
  color: var(--dvijok-bg-dark);
  font-size: 12px;
  line-height: 15px;
  font-weight: 400;

  &::placeholder {
    color: var(--dvijok-bg-dark);
  }
}
</style>
