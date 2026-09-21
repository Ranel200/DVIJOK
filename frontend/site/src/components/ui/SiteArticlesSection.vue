<template>
  <section class="articles-section">
    <div class="articles-section__headings">
      <SiteSectionHeadings eyebrow="Популярное" title="Статьи" />
    </div>

    <div class="articles-section__list">
      <div
        class="articles-section__viewport"
        :style="articlesHeight != null ? { '--articles-height': `${articlesHeight}px` } : undefined"
      >
        <div
          ref="trackRef"
          class="articles-section__track"
          :style="{ '--article-index': articleIndex }"
        >
          <div v-for="article in articles" :key="article.id" class="articles-section__slide">
            <article class="articles-section__card">
              <div class="articles-section__photo">
                <img :src="article.photo" :alt="article.title" />
              </div>

              <h3 class="articles-section__title">{{ article.title }}</h3>
              <p class="articles-section__desc">{{ article.description }}</p>

              <SiteTextLink :to="{ name: 'blog-article', params: { id: String(article.id) } }">
                Читать всю статью
              </SiteTextLink>
            </article>
          </div>
        </div>
      </div>

      <div class="articles-section__nav">
        <button
          type="button"
          class="articles-section__nav-btn"
          aria-label="Предыдущая статья"
          @click="prevArticle"
        >
          <ArrowIcon color="#2E68FF" direction="left" />
        </button>
        <button
          type="button"
          class="articles-section__nav-btn"
          aria-label="Следующая статья"
          @click="nextArticle"
        >
          <ArrowIcon color="#2E68FF" direction="right" />
        </button>
      </div>
    </div>

    <div class="articles-section__cta">
      <SiteBtn :width="330" :to="{ name: 'blog' }">Посмотреть все статьи</SiteBtn>
    </div>
  </section>
</template>

<script setup>
import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import ArrowIcon from '@/components/ui/ArrowIcon.vue'
import SiteBtn from '@/components/ui/SiteBtn.vue'
import SiteSectionHeadings from '@/components/ui/SiteSectionHeadings.vue'
import SiteTextLink from '@/components/ui/SiteTextLink.vue'

const props = defineProps({
  articles: {
    type: Array,
    default: () => []
  }
})

const articleIndex = ref(0)
const trackRef = ref(null)
const articlesHeight = ref(null)
let resizeRaf = 0

async function syncHeight() {
  await nextTick()
  const track = trackRef.value
  if (!track) {
    articlesHeight.value = null
    return
  }

  const cards = [...track.querySelectorAll('.articles-section__card')]
  if (!cards.length) return

  const prev = articlesHeight.value
  articlesHeight.value = null
  await nextTick()

  let max = 0
  cards.forEach(card => {
    max = Math.max(max, card.getBoundingClientRect().height)
  })

  articlesHeight.value = Math.ceil(max) || prev
}

function scheduleHeightSync() {
  if (resizeRaf) return
  resizeRaf = requestAnimationFrame(() => {
    resizeRaf = 0
    syncHeight()
  })
}

function bindImageLoads() {
  const track = trackRef.value
  if (!track) return
  track.querySelectorAll('img').forEach(img => {
    if (!img.complete) {
      img.addEventListener('load', syncHeight, { once: true })
    }
  })
}

function prevArticle() {
  const total = props.articles.length
  if (!total) return
  articleIndex.value = (articleIndex.value - 1 + total) % total
}

function nextArticle() {
  const total = props.articles.length
  if (!total) return
  articleIndex.value = (articleIndex.value + 1) % total
}

onMounted(() => {
  window.addEventListener('resize', scheduleHeightSync)
})

onUnmounted(() => {
  window.removeEventListener('resize', scheduleHeightSync)
  if (resizeRaf) {
    cancelAnimationFrame(resizeRaf)
    resizeRaf = 0
  }
})

watch(
  () => props.articles,
  async () => {
    articleIndex.value = 0
    await syncHeight()
    bindImageLoads()
  }
)
</script>

<style scoped>
.articles-section {
  position: relative;
  z-index: 1;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 50px;
  padding: 40px 80px;
  background: var(--dvijok-white);
}

.articles-section__list {
  display: flex;
  flex-direction: column;
}

.articles-section__track {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 50px;
}

.articles-section__slide {
  display: flex;
  min-width: 0;
  height: var(--articles-height, auto);
}

.articles-section__nav {
  display: none;
}

.articles-section__card {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  height: 100%;
  padding: 19px;
  border: 1px solid #7a82a0;
}

.articles-section__card > :last-child {
  margin-top: auto;
}

.articles-section__photo {
  width: 100%;
  aspect-ratio: 16 / 9;
  overflow: hidden;
  line-height: 0;
}

.articles-section__photo img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.articles-section__title {
  margin: 0;
  font-family: Inter, sans-serif;
  font-weight: 600;
  font-size: 24px;
  line-height: 29px;
  text-transform: uppercase;
  color: #000;
}

.articles-section__desc {
  margin: 0;
  font-family: Inter, sans-serif;
  font-weight: 400;
  font-size: 18px;
  line-height: 22px;
  color: #000;
}

.articles-section__cta {
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 1023px) {
  .articles-section {
    gap: 50px;
    padding: 40px 0;
  }

  .articles-section__headings,
  .articles-section__cta {
    padding: 0 20px;
  }

  .articles-section__cta :deep(.site-btn) {
    width: 100% !important;
    flex: none;
  }

  .articles-section__list {
    gap: 10px;
  }

  .articles-section__viewport {
    overflow: hidden;
    width: 100%;
    height: var(--articles-height, auto);
  }

  .articles-section__track {
    display: flex;
    align-items: stretch;
    gap: 0;
    height: 100%;
    transition: transform 0.35s cubic-bezier(0.22, 1, 0.36, 1);
    transform: translateX(calc(-100% * var(--article-index, 0)));
  }

  .articles-section__slide {
    box-sizing: border-box;
    display: flex;
    flex: 0 0 100%;
    width: 100%;
    height: 100%;
    padding: 0 20px;
  }

  .articles-section__card {
    width: 100%;
    height: 100%;
  }

  .articles-section__nav {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
  }

  .articles-section__nav-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    margin: 0;
    padding: 8px;
    border: none;
    background: transparent;
    cursor: pointer;
  }

  @media (prefers-reduced-motion: reduce) {
    .articles-section__track {
      transition: none;
    }
  }
}
</style>
