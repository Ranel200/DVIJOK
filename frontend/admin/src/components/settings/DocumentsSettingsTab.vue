<template>
  <div class="documents">
    <article v-for="doc in PLATFORM_DOCUMENTS" :key="doc.id" class="doc-card">
      <span class="doc-card__icon" :style="{ backgroundColor: doc.iconColor }" aria-hidden="true" />
      <div class="doc-card__body">
        <h2 class="doc-card__title">{{ doc.title }}</h2>
        <span v-if="acceptedLabel(doc.id)" class="doc-card__pill">
          Документ принят {{ acceptedLabel(doc.id) }}
        </span>
        <BaseButton text :icon-spacing="10" @click="openDocument(doc.href)">
          {{ doc.actionLabel }}
          <template #append>
            <ArrowIcon direction="right" :size="16" />
          </template>
        </BaseButton>
      </div>
    </article>

    <div class="documents__operator">
      <div class="documents__komit-wrap">
        <img class="documents__komit" src="/admin/icons/logo-komit.png" alt="КОМИТ" />
      </div>
      <section class="documents__requisites" aria-labelledby="documents-requisites-title">
        <h2 class="documents__requisites-title" id="documents-requisites-title">
          Реквизиты оператора
        </h2>
        <p>Сокращенное наименование: {{ OPERATOR_REQUISITES.shortName }}</p>
        <p>ИНН: {{ OPERATOR_REQUISITES.inn }}</p>
        <p>
          Email:
          <a :href="OPERATOR_REQUISITES.emailHref">{{ OPERATOR_REQUISITES.email }}</a>
        </p>
        <p>
          Контакты:
          <a :href="OPERATOR_REQUISITES.phoneHref">{{ OPERATOR_REQUISITES.phone }}</a>
        </p>
      </section>
    </div>
  </div>
</template>

<script setup>
import ArrowIcon from '@/components/ui/ArrowIcon.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import { OPERATOR_REQUISITES, PLATFORM_DOCUMENTS } from '@/constants/platformDocuments.js'
import { formatRuDateNumeric } from '@/utils/formatDateRu.js'

const props = defineProps({
  acceptedAtById: {
    type: Object,
    default: () => ({})
  }
})

function acceptedLabel(docId) {
  return formatRuDateNumeric(props.acceptedAtById?.[docId])
}

function openDocument(href) {
  window.open(href, '_blank', 'noopener,noreferrer')
}
</script>

<style scoped lang="scss">
.documents {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 0 20px 20px;
  overflow-y: auto;
  scrollbar-width: none;

  &::-webkit-scrollbar {
    display: none;
  }
}

.doc-card {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  width: 100%;
  padding: 20px;
  border-radius: 15px;
  background: var(--dvijok-white);
}

.doc-card__icon {
  display: block;
  flex-shrink: 0;
  width: 54px;
  height: 66px;
  -webkit-mask: url('/admin/icons/settings/doc.svg') center / contain no-repeat;
  mask: url('/admin/icons/settings/doc.svg') center / contain no-repeat;
}

.doc-card__body {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 5px;
  min-width: 0;
}

.doc-card__title {
  margin: 0;
  color: var(--dvijok-bg-dark);
  font-size: 16px;
  font-weight: 600;
  line-height: 19px;
  text-transform: uppercase;
}

.doc-card__pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6px 10px;
  border-radius: 50px;
  background: var(--dvijok-success-bg);
  color: var(--dvijok-success);
  font-weight: 400;
  font-size: 10px;
  line-height: 12px;
  white-space: nowrap;
}

.documents__operator {
  display: flex;
  align-items: center;
  gap: 25px;
  width: fit-content;
  max-width: 100%;
  margin-top: auto;
  min-width: 0;
  flex-shrink: 0;
}

.documents__komit-wrap {
  flex-shrink: 0;
  width: 106px;
  height: 116px;
}

.documents__komit {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.documents__requisites {
  display: flex;
  flex-direction: column;
  gap: 0;
  min-width: 0;
  color: var(--dvijok-text-secondary);
  font-weight: 400;
  font-size: 14px;
  line-height: 17px;
}

.documents__requisites p {
  margin: 0;
}

.documents__requisites a {
  color: inherit;
  text-decoration: none;
}

.documents__requisites-title {
  margin: 0 0 14px;
  font-size: inherit;
  line-height: inherit;
  font-weight: 700;
  text-transform: uppercase;
  color: inherit;
}
</style>
