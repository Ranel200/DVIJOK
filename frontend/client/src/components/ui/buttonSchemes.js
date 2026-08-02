export const BUTTON_VARIANTS = ['solid', 'light', 'outlined', 'outlinedWhite', 'accent']

export const BUTTON_SCHEMES = {
  'solid-light-outlined': {
    default: 'solid',
    hover: 'light',
    active: 'outlined'
  },
  'outlined-solid-light': {
    default: 'outlined',
    hover: 'solid',
    active: 'light'
  },
  'outlinedWhite-solid-light': {
    default: 'outlinedWhite',
    hover: 'solid',
    active: 'light'
  },
  'outlinedWhite-solid-outlinedWhite': {
    default: 'outlinedWhite',
    hover: 'solid',
    active: 'outlinedWhite'
  },
  'solid-light-accent': { default: 'solid', hover: 'light', active: 'accent' },
  'accent-solid-light': { default: 'accent', hover: 'solid', active: 'light' },
  'light-solid-accent': { default: 'light', hover: 'solid', active: 'accent' },
  'solid-solid-light': { default: 'solid', hover: 'solid', active: 'light' },
  'light-light-solid': { default: 'light', hover: 'light', active: 'solid' }
}

export const DEFAULT_BUTTON_SCHEME = 'solid-light-outlined'
