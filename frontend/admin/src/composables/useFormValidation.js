import { computed, inject, onScopeDispose, provide, reactive } from 'vue'

export const FORM_VALIDATION_KEY = Symbol('formValidation')

export function isBlank(value) {
  return !String(value ?? '').trim()
}

export function requiredText(message) {
  return value => (isBlank(value) ? message : '')
}

export function requiredPhone(message) {
  return value => (String(value ?? '').replace(/\D/g, '').length === 11 ? '' : message)
}

export function getFieldError(value, options = {}) {
  if (options.readonly || options.disable) return ''
  if (options.required && isBlank(value)) {
    return options.requiredMessage || 'Заполните поле'
  }
  if (typeof options.validate === 'function') {
    const result = options.validate(value)
    if (typeof result === 'string' && result) return result
    if (result === false) return options.requiredMessage || 'Заполните поле'
  }
  return ''
}

export function createFormValidation() {
  const fields = new Map()
  const errors = reactive({})
  let seq = 0

  function register(getError) {
    const id = ++seq
    fields.set(id, getError)
    onScopeDispose(() => {
      fields.delete(id)
      delete errors[id]
    })
    return computed(() => errors[id] || '')
  }

  function validate() {
    for (const key of Object.keys(errors)) delete errors[key]
    let valid = true
    for (const [id, getError] of fields) {
      const message = getError()
      if (message) {
        errors[id] = message
        valid = false
      }
    }
    return valid
  }

  function reset() {
    for (const key of Object.keys(errors)) delete errors[key]
  }

  const api = { register, validate, reset }
  provide(FORM_VALIDATION_KEY, api)
  return api
}

export function useFormField(getError) {
  const form = inject(FORM_VALIDATION_KEY, null)
  if (!form) return computed(() => '')
  return form.register(getError)
}

export function useFieldError(props) {
  const formError = useFormField(() => getFieldError(props.modelValue, props))
  const errorMessage = computed(() => props.errorMessage || formError.value)
  const error = computed(() => Boolean(props.error) || Boolean(errorMessage.value))
  return { error, errorMessage }
}
