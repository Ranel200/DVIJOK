function detectBrowser(ua) {
  if (/Edg\//i.test(ua)) return 'Edge'
  if (/OPR\/|Opera/i.test(ua)) return 'Opera'
  if (/YaBrowser/i.test(ua)) return 'Яндекс'
  if (/Firefox\//i.test(ua)) return 'Firefox'
  if (/Chrome\//i.test(ua) && !/Chromium/i.test(ua)) return 'Chrome'
  if (/Safari\//i.test(ua) && !/Chrome/i.test(ua)) return 'Safari'
  return 'Браузер'
}

function detectDeviceType(ua) {
  if (/Mobi|Android.*Mobile|iPhone|iPod|webOS|BlackBerry|IEMobile|Opera Mini/i.test(ua)) {
    return 'phone'
  }
  if (/Macintosh|Mac OS X|iPad/i.test(ua)) return 'laptop'
  return 'pc'
}

function detectDeviceName(ua) {
  if (/iPhone/i.test(ua)) return 'iPhone'
  if (/iPad/i.test(ua)) return 'iPad'
  if (/Android/i.test(ua)) return 'Android'
  if (/Macintosh|Mac OS X/i.test(ua)) return 'Mac'
  if (/Windows NT/i.test(ua)) return 'Windows PC'
  if (/Linux/i.test(ua)) return 'Linux PC'
  return 'Устройство'
}

export function detectClientSession() {
  const ua = navigator.userAgent || ''
  return {
    current: true,
    type: detectDeviceType(ua),
    deviceName: detectDeviceName(ua),
    browser: detectBrowser(ua),
    lastActiveAt: new Date().toISOString()
  }
}
