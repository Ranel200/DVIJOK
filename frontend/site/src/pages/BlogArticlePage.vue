<template>
  <q-page v-if="article" class="blog-article-page">
    <div class="blog-article-page__top">
      <router-link class="blog-article-page__back" :to="{ name: 'blog' }">
        <ArrowIcon color="#2E68FF" direction="left" />
        Назад
      </router-link>

      <div class="blog-article-page__photo">
        <img :src="article.photo" :alt="article.title" />
      </div>

      <PageIntro :title="article.title" :lead="article.lead" />
    </div>

    <div class="blog-article-page__sections">
      <section
        v-for="(section, index) in article.sections"
        :key="`${article.id}-${index}`"
        class="blog-article-section"
      >
        <h2 v-if="section.title" class="blog-article-section__title">
          {{ section.title }}
        </h2>

        <div class="blog-article-section__body">
          <div v-if="section.photo?.side === 'left'" class="blog-article-section__photo">
            <img :src="section.photo.src" :alt="section.title || article.title" />
          </div>

          <p class="blog-article-section__text">{{ section.text }}</p>

          <div v-if="section.photo?.side === 'right'" class="blog-article-section__photo">
            <img :src="section.photo.src" :alt="section.title || article.title" />
          </div>
        </div>
      </section>
    </div>

    <router-link class="blog-article-page__back" :to="{ name: 'blog' }">
      <ArrowIcon color="#2E68FF" direction="left" />
      Вернуться к статьям
    </router-link>
  </q-page>

  <q-page v-else class="blog-article-page blog-article-page--empty">
    <router-link class="blog-article-page__back" :to="{ name: 'blog' }">
      <ArrowIcon color="#2E68FF" direction="left" />
      Назад
    </router-link>
    <p class="blog-article-page__missing">Статья не найдена</p>
  </q-page>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import ArrowIcon from '@/components/ui/ArrowIcon.vue'
import PageIntro from '@/components/ui/PageIntro.vue'
import { getBlogArticleById } from '@/constants/blog.js'

const route = useRoute()

const article = computed(() => getBlogArticleById(route.params.id))
</script>

<style scoped>
.blog-article-page {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 50px;
  padding: 30px 80px 50px;
}

.blog-article-page__top {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.blog-article-page__back {
  display: inline-flex;
  align-items: center;
  align-self: flex-start;
  gap: 10px;
  padding: 10px;
  font-weight: 600;
  font-size: 16px;
  line-height: 19px;
  color: #2e68ff;
  text-decoration: underline;
  cursor: pointer;
  transition: color 0.2s ease;
}

.blog-article-page__back:hover {
  color: #3061e2;
}

.blog-article-page__back:active {
  color: #1a4fd9;
}

.blog-article-page__photo {
  width: 100%;
  height: 440px;
  overflow: hidden;
  line-height: 0;
}

.blog-article-page__photo img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.blog-article-page__sections {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.blog-article-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.blog-article-section__title {
  margin: 0;
  font-weight: 600;
  font-size: 24px;
  line-height: 29px;
  text-transform: uppercase;
  color: #000;
}

.blog-article-section__body {
  display: flex;
  flex-direction: row;
  gap: 50px;
  align-items: flex-start;
}

.blog-article-section__photo {
  flex: 0 0 30%;
  width: 30%;
  overflow: hidden;
  line-height: 0;
}

.blog-article-section__photo img {
  display: block;
  width: 100%;
  height: auto;
}

.blog-article-section__text {
  flex: 1;
  min-width: 0;
  margin: 0;
  font-weight: 400;
  font-size: 18px;
  line-height: 22px;
  color: #000;
}

.blog-article-page__missing {
  margin: 0;
  font-weight: 500;
  font-size: 20px;
  line-height: 24px;
  color: #000;
}

@media (max-width: 1023px) {
  .blog-article-page {
    padding: 24px 40px 40px;
  }

  .blog-article-page__photo {
    height: 280px;
  }

  .blog-article-section__body {
    flex-direction: column;
    gap: 20px;
  }

  .blog-article-section__photo {
    flex-basis: auto;
    width: 100%;
  }
}
</style>
