export const REPAIR_STATUS_STEPS = [
  { id: 'booked' },
  { id: 'in_progress' },
  { id: 'approval' },
  { id: 'ready' }
]

const CURRENT_STEP = {
  booked: 0,
  in_progress: 1,
  awaits_approval: 2,
  needs_approval: 2,
  approved: 2,
  ready: 3
}

const ACTIVE_THROUGH = {
  booked: 1,
  in_progress: 2,
  awaits_approval: 2,
  needs_approval: 2,
  approved: 2,
  ready: 3
}

function stepState(index, status) {
  const current = CURRENT_STEP[status]
  const through = ACTIVE_THROUGH[status]
  if (current == null || through == null) return 'inactive'

  if (index > through) return 'inactive'
  if (status === 'ready' || index < current) return 'done'
  if (index === current) return status === 'approved' ? 'done' : 'current'
  return 'pending'
}

function stepContent(stepId, status, repair) {
  const current = CURRENT_STEP[status] ?? -1

  if (stepId === 'booked') {
    return {
      title: 'Записан',
      subtitle: repair.bookedAt || ''
    }
  }

  if (stepId === 'in_progress') {
    if (current < 1) {
      return { title: 'Ожидает начала работ', subtitle: '' }
    }
    return {
      title: 'В работе',
      subtitle: repair.master ? `Работает мастер ${repair.master}` : ''
    }
  }

  if (stepId === 'approval') {
    if (status === 'needs_approval') {
      return {
        title: '! Нуждается в согласовании',
        subtitle: 'Ожидает вашего ответа',
        action: 'Связаться с мастером'
      }
    }
    if (status === 'approved' || status === 'ready') {
      return {
        title: 'Согласовано',
        subtitle: status === 'approved' ? 'Близится к завершению' : ''
      }
    }
    return {
      title: 'Ожидает согласования',
      subtitle: 'Ожидает вашего ответа'
    }
  }

  if (stepId === 'ready') {
    if (status === 'ready') {
      return { title: 'Готово', subtitle: 'Услуга выполнена' }
    }
    return {
      title: 'Еще не готово',
      subtitle: 'Ожидайте выполнения услуги'
    }
  }

  return { title: '', subtitle: '' }
}

export function buildRepairStatuses(repair) {
  if (!repair?.status || CURRENT_STEP[repair.status] == null) return []

  return REPAIR_STATUS_STEPS.map((step, index) => {
    const state = stepState(index, repair.status)
    const content = stepContent(step.id, repair.status, repair)

    return {
      id: step.id,
      state,
      title: content.title,
      subtitle: content.subtitle,
      action: state === 'current' ? content.action : undefined
    }
  })
}
