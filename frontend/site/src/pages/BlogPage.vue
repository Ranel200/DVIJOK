<template>
  <q-page class="blog-page">
    <PageIntro title="Статьи" lead="Актуальный материал для автовладельцев и автосервисов" />

    <div v-if="loading" class="blog-page__loading" aria-busy="true" aria-live="polite">
      <q-spinner color="primary" size="40px" />
      <span>Загрузка статей…</span>
    </div>

    <template v-else>
      <div class="blog-page__feed">
        <template v-for="group in articleGroups" :key="group.key">
          <h2 class="blog-page__month">{{ group.label }}</h2>

          <article v-for="article in group.articles" :key="article.id" class="blog-article-card">
            <div class="blog-article-card__photo">
              <img :src="article.photo" :alt="article.title" />
            </div>

            <div class="blog-article-card__body">
              <div class="blog-article-card__texts">
                <h3 class="blog-article-card__title">{{ article.title }}</h3>
                <p class="blog-article-card__description">{{ article.description }}</p>
              </div>

              <router-link
                class="blog-article-card__read"
                :to="{ name: 'blog-article', params: { id: String(article.id) } }"
              >
                Читать всю статью
                <ArrowIcon direction="right" />
              </router-link>
            </div>
          </article>
        </template>
      </div>

      <nav class="blog-page__pagination" aria-label="Пагинация статей">
        <button
          type="button"
          class="blog-page__page-btn"
          :class="{ 'blog-page__page-btn--active': canGoPrev }"
          :disabled="!canGoPrev"
          @click="goToPrevPage"
        >
          <ArrowIcon :color="prevColor" direction="left" />
          Пред. стр.
        </button>

        <div class="blog-page__page-number" aria-current="page">{{ currentPage }}</div>

        <button
          type="button"
          class="blog-page__page-btn"
          :class="{ 'blog-page__page-btn--active': canGoNext }"
          :disabled="!canGoNext"
          @click="goToNextPage"
        >
          След. стр.
          <ArrowIcon :color="nextColor" direction="right" />
        </button>
      </nav>
    </template>
  </q-page>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { blogApi } from '@/api/index.js'
import ArrowIcon from '@/components/ui/ArrowIcon.vue'
import PageIntro from '@/components/ui/PageIntro.vue'
import { getBlogMonthKey, getBlogMonthLabel } from '@/constants/blog.js'

const ARTICLES_PER_PAGE = 4
const ACTIVE_COLOR = '#2E68FF'
const INACTIVE_COLOR = '#7A82A0'

const currentPage = ref(1)
const blogArticles = ref([])
const loading = ref(true)

onMounted(async () => {
  blogArticles.value = await blogApi.list()
  loading.value = false
})

const totalPages = computed(() =>
  Math.max(1, Math.ceil(blogArticles.value.length / ARTICLES_PER_PAGE))
)

const pageArticles = computed(() => {
  const start = (currentPage.value - 1) * ARTICLES_PER_PAGE
  return blogArticles.value.slice(start, start + ARTICLES_PER_PAGE)
})

const articleGroups = computed(() => {
  const groups = []

  for (const article of pageArticles.value) {
    const key = getBlogMonthKey(article.date)
    const lastGroup = groups[groups.length - 1]

    if (lastGroup?.key === key) {
      lastGroup.articles.push(article)
      continue
    }

    groups.push({
      key,
      label: getBlogMonthLabel(article.date),
      articles: [article]
    })
  }

  return groups
})

const canGoPrev = computed(() => currentPage.value > 1)
const canGoNext = computed(() => currentPage.value < totalPages.value)
const prevColor = computed(() => (canGoPrev.value ? ACTIVE_COLOR : INACTIVE_COLOR))
const nextColor = computed(() => (canGoNext.value ? ACTIVE_COLOR : INACTIVE_COLOR))

function goToPrevPage() {
  if (!canGoPrev.value) return
  currentPage.value -= 1
}

function goToNextPage() {
  if (!canGoNext.value) return
  currentPage.value += 1
}
</script>

<style scoped>
.blog-page {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 50px;
  padding: 30px 80px 50px;
}

.blog-page__loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  min-height: 240px;
  font-weight: 500;
  font-size: 16px;
  line-height: 19px;
  color: #7a82a0;
}

.blog-page__feed {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.blog-page__month {
  margin: 0;
  font-weight: 500;
  font-size: 20px;
  line-height: 24px;
  text-align: left;
  text-transform: uppercase;
  color: #7a82a0;
}

.blog-article-card {
  box-sizing: border-box;
  display: flex;
  flex-direction: row;
  gap: 30px;
  padding: 19px;
  border: 1px solid #7a82a0;
}

.blog-article-card__photo {
  flex: 0 0 40%;
  width: 40%;
  aspect-ratio: 4 / 3;
  overflow: hidden;
  line-height: 0;
}

.blog-article-card__photo img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.blog-article-card__body {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 30px;
  min-width: 0;
}

.blog-article-card__texts {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.blog-article-card__title {
  margin: 0;
  font-weight: 600;
  font-size: 24px;
  line-height: 29px;
  text-transform: uppercase;
  color: #000;
}

.blog-article-card__description {
  margin: 0;
  font-weight: 400;
  font-size: 18px;
  line-height: 22px;
  color: #000;
}

.blog-article-card__read {
  display: inline-flex;
  align-items: center;
  align-self: flex-end;
  gap: 10px;
  margin-top: auto;
  padding: 10px;
  font-weight: 600;
  font-size: 16px;
  line-height: 19px;
  color: #2e68ff;
  text-decoration: underline;
  cursor: pointer;
  transition: color 0.2s ease;
}

.blog-article-card__read:hover {
  color: #3061e2;
}

.blog-article-card__read:active {
  color: #1a4fd9;
}

.blog-page__pagination {
  display: flex;
  flex-direction: row;
  align-items: stretch;
  justify-content: center;
  gap: 40px;
  padding: 10px;
}

.blog-page__page-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 0;
  border: none;
  background: transparent;
  font-family: inherit;
  font-weight: 600;
  font-size: 16px;
  line-height: 19px;
  color: #7a82a0;
  text-decoration: underline;
  cursor: default;
}

.blog-page__page-btn--active {
  color: #2e68ff;
  cursor: pointer;
}

.blog-page__page-btn:disabled {
  cursor: default;
}

.blog-page__page-number {
  box-sizing: border-box;
  display: flex;
  align-items: center;
  height: auto;
  padding: 0 7px;
  border: 1px solid #2e68ff;
  font-weight: 400;
  font-size: 16px;
  line-height: 19px;
  color: #2e68ff;
}

@media (max-width: 1023px) {
  .blog-page {
    padding: 24px 40px 40px;
  }

  .blog-article-card {
    flex-direction: column;
  }

  .blog-article-card__photo {
    flex-basis: auto;
    width: 100%;
  }
}
</style>
