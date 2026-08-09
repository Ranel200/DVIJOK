// Configuration for your app
// https://v2.quasar.dev/quasar-cli-vite/quasar-config-file

import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from '#q-app'

const clientDir = path.dirname(fileURLToPath(import.meta.url))
const landingDocsDir = path.resolve(clientDir, '../landing/docs')

const CONTENT_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.ico': 'image/x-icon'
}

function serveLandingDocs() {
  return {
    name: 'serve-landing-docs',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        if (!req.url?.startsWith('/docs/')) return next()

        const relative = decodeURIComponent(req.url.slice('/docs/'.length).split('?')[0])
        if (!relative || relative.includes('..') || path.isAbsolute(relative)) return next()

        const filePath = path.resolve(landingDocsDir, relative)
        const relativeToDocs = path.relative(landingDocsDir, filePath)
        if (!relativeToDocs || relativeToDocs.startsWith('..') || path.isAbsolute(relativeToDocs)) {
          return next()
        }
        if (!fs.existsSync(filePath) || !fs.statSync(filePath).isFile()) return next()

        res.setHeader(
          'Content-Type',
          CONTENT_TYPES[path.extname(filePath)] || 'application/octet-stream'
        )
        fs.createReadStream(filePath).pipe(res)
      })
    }
  }
}

export default defineConfig((/* ctx */) => {
  return {
    // app boot file (/src/boot)
    // https://v2.quasar.dev/quasar-cli-vite/boot-files
    boot: ['fonts', 'auth'],

    // https://v2.quasar.dev/quasar-cli-vite/quasar-config-file#css
    css: ['app.scss'],

    // https://github.com/quasarframework/quasar/tree/dev/extras
    extras: ['material-icons'],

    // https://v2.quasar.dev/quasar-cli-vite/quasar-config-file#build
    build: {
      // available values: 'hash', 'history'
      vueRouterMode: 'history',
      publicPath: '/client/',
      extendViteConf(viteConf) {
        viteConf.plugins = [...(viteConf.plugins || []), serveLandingDocs()]
      },
      env: {
        clientPrefix: 'VITE_'
      }
    },

    // https://v2.quasar.dev/quasar-cli-vite/quasar-config-file#devserver
    devServer: {
      port: 9001,
      open: true // opens browser window automatically
    },

    // https://v2.quasar.dev/quasar-cli-vite/quasar-config-file#framework
    framework: {
      config: {},

      // Quasar plugins
      plugins: []
    },

    // https://v2.quasar.dev/options/animations
    animations: []
  }
})
