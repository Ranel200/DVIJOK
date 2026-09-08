<template>
  <footer class="site-footer" aria-label="Подвал сайта">
    <div class="site-footer__main">
      <img class="site-footer__logo" src="/site/icons/logo.png" alt="DVIJOK" />

      <p class="site-footer__lead">
        Единая платформа для автосервисов <br class="site-footer__lead-br" />и автовладельцев.
      </p>

      <div class="site-footer__columns">
        <div
          v-for="column in footerColumns"
          :key="column.id"
          class="site-footer__column"
          :class="`site-footer__column--${column.id}`"
        >
          <h2 class="site-footer__title">{{ column.title }}</h2>

          <ul class="site-footer__list">
            <li v-for="link in column.links" :key="link.label">
              <router-link v-if="link.to" :to="link.to" class="site-footer__link">
                <template v-if="link.lines">
                  <template v-for="(line, index) in link.lines" :key="line">
                    <br v-if="index > 0" />{{ line }}
                  </template>
                </template>
                <template v-else>{{ link.label }}</template>
              </router-link>

              <a
                v-else-if="link.href"
                :href="link.href"
                class="site-footer__link"
                target="_blank"
                rel="noopener noreferrer"
              >
                <template v-if="link.lines">
                  <template v-for="(line, index) in link.lines" :key="line">
                    <br v-if="index > 0" />{{ line }}
                  </template>
                </template>
                <template v-else>{{ link.label }}</template>
              </a>

              <span v-else class="site-footer__link">
                <template v-if="link.lines">
                  <template v-for="(line, index) in link.lines" :key="line">
                    <br v-if="index > 0" />{{ line }}
                  </template>
                </template>
                <template v-else>{{ link.label }}</template>
              </span>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <div class="site-footer__legal">
      <p class="site-footer__company">
        <span class="site-footer__company-name">ООО «КОМИТ»</span><br />
        <span class="site-footer__inn">ИНН:1686059159</span>
      </p>

      <p class="site-footer__copy">© 2026 ДВИЖОК. Все права защищены.</p>
    </div>
  </footer>
</template>

<script setup>
import { footerColumns } from '@/constants/navigation.js'
</script>

<style scoped>
.site-footer {
  box-sizing: border-box;
  display: grid;
  grid-template-columns: minmax(0, 400px) auto;
  justify-content: space-between;
  column-gap: 80px;
  row-gap: 30px;
  padding: 40px;
  background: var(--dvijok-navy);
}

.site-footer__main {
  display: contents;
}

.site-footer__logo {
  display: block;
  grid-column: 1;
  grid-row: 1;
  width: 100%;
  height: auto;
}

.site-footer__lead {
  grid-column: 1;
  grid-row: 2;
  margin: 0;
  font-weight: 500;
  font-size: 20px;
  line-height: 24px;
  color: var(--dvijok-white);
}

.site-footer__lead-br {
  display: none;
}

.site-footer__columns {
  display: flex;
  flex-direction: row;
  grid-column: 2;
  grid-row: 1 / span 4;
  align-self: start;
  gap: 30px;
}

.site-footer__column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.site-footer__title {
  margin: 0;
  font-weight: 600;
  font-size: 20px;
  line-height: 24px;
  color: var(--dvijok-text-secondary);
  text-transform: uppercase;
}

.site-footer__list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.site-footer__link {
  font-weight: 400;
  font-size: 16px;
  line-height: 19px;
  color: var(--dvijok-white);
  text-decoration: none;
}

.site-footer__legal {
  display: contents;
}

.site-footer__company {
  grid-column: 1;
  grid-row: 3;
  margin: 0;
  font-weight: 600;
  font-size: 16px;
  line-height: 19px;
  color: var(--dvijok-text-secondary);
}

.site-footer__inn {
  font-weight: 400;
}

.site-footer__copy {
  grid-column: 1;
  grid-row: 4;
  margin: 0;
  font-weight: 400;
  font-size: 16px;
  line-height: 19px;
  color: var(--dvijok-text-secondary);
}

@media (max-width: 1023px) {
  .site-footer {
    display: flex;
    flex-direction: column;
    gap: 50px;
  }

  .site-footer__main {
    display: flex;
    flex-direction: column;
    gap: 30px;
  }

  .site-footer__logo {
    width: 100%;
  }

  .site-footer__lead {
    font-size: 16px;
    line-height: 19px;
  }

  .site-footer__lead-br {
    display: inline;
  }

  .site-footer__columns {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-column: auto;
    grid-row: auto;
    gap: 30px;
  }

  .site-footer__column--product {
    grid-area: 1 / 1;
  }

  .site-footer__column--resources {
    grid-area: 1 / 2;
  }

  .site-footer__column--documents {
    grid-area: 2 / 1;
  }

  .site-footer__column--company {
    grid-area: 2 / 2;
  }

  .site-footer__legal {
    display: flex;
    flex-direction: column;
  }

  .site-footer__company {
    grid-column: auto;
    grid-row: auto;
    font-weight: 400;
  }

  .site-footer__company-name {
    font-weight: 600;
  }

  .site-footer__copy {
    grid-column: auto;
    grid-row: auto;
    margin-top: 19px;
  }
}
</style>
