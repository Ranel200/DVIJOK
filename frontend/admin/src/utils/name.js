function splitNameParts(fullName) {
  return String(fullName || '')
    .trim()
    .split(/\s+/)
    .filter(Boolean)
}

export function getInitials(fullName) {
  const parts = splitNameParts(fullName)
  if (parts.length === 0) return ''
  if (parts.length === 1) return parts[0].charAt(0).toUpperCase()
  return (parts[1].charAt(0) + parts[0].charAt(0)).toUpperCase()
}

export function getShortName(fullName) {
  const parts = splitNameParts(fullName)
  if (parts.length === 0) return ''
  if (parts.length === 1) return parts[0]
  return `${parts[1]} ${parts[0].charAt(0).toUpperCase()}.`
}

export function formatStaffName(fullName) {
  const parts = splitNameParts(fullName)
  if (parts.length === 0) return ''
  if (parts.length === 1) return parts[0]
  return `${parts[0]} ${parts[1]}`
}
