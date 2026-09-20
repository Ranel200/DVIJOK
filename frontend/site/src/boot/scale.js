const DESIGN_WIDTH = 1440

function updateSiteScale() {
  const scale = Math.max(1, window.innerWidth / DESIGN_WIDTH)
  document.documentElement.style.setProperty('--site-scale', String(scale))
}

updateSiteScale()
window.addEventListener('resize', updateSiteScale)
