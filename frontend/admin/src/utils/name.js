export function getInitials(fullName) {
  if (!fullName) return ''
  const parts = fullName.trim().split(/\s+/).filter(Boolean)
  if (parts.length === 0) return ''
  if (parts.length === 1) return parts[0].charAt(0).toUpperCase()
  return (parts[1].charAt(0) + parts[0].charAt(0)).toUpperCase()
}

export function getShortName(fullName) {
  if (!fullName) return ''
  const parts = fullName.trim().split(/\s+/).filter(Boolean)
  if (parts.length === 0) return ''
  if (parts.length === 1) return parts[0]
  return `${parts[1]} ${parts[0].charAt(0).toUpperCase()}.`
}
