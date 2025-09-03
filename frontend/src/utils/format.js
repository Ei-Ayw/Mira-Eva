import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'

// 设置中文语言
dayjs.locale('zh-cn')

/**
 * 格式化时间
 * @param {Date|string} time - 时间对象或时间字符串
 * @returns {string} 格式化后的时间字符串
 */
export function formatTime(time) {
  if (!time) return ''
  
  const now = dayjs()
  const target = dayjs(time)
  
  // 如果是今天
  if (target.isSame(now, 'day')) {
    return target.format('HH:mm')
  }
  
  // 如果是昨天
  if (target.isSame(now.subtract(1, 'day'), 'day')) {
    return `昨天 ${target.format('HH:mm')}`
  }
  
  // 如果是本周
  if (target.isSame(now, 'week')) {
    return target.format('ddd HH:mm')
  }
  
  // 其他情况显示完整日期
  return target.format('MM-DD HH:mm')
}

/**
 * 格式化时长
 * @param {number} seconds - 秒数
 * @returns {string} 格式化后的时长字符串
 */
export function formatDuration(seconds) {
  if (!seconds || seconds < 0) return '0:00'
  
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

/**
 * 格式化文件大小
 * @param {number} bytes - 字节数
 * @returns {string} 格式化后的文件大小字符串
 */
export function formatFileSize(bytes) {
  if (!bytes || bytes < 0) return '0 B'
  
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let size = bytes
  let unitIndex = 0
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  
  return `${size.toFixed(1)} ${units[unitIndex]}`
}

/**
 * 格式化数字
 * @param {number} num - 数字
 * @returns {string} 格式化后的数字字符串
 */
export function formatNumber(num) {
  if (!num && num !== 0) return '0'
  
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  
  return num.toString()
}

/**
 * 获取相对时间
 * @param {Date|string} time - 时间对象或时间字符串
 * @returns {string} 相对时间字符串
 */
export function getRelativeTime(time) {
  if (!time) return ''
  
  const now = dayjs()
  const target = dayjs(time)
  const diff = now.diff(target, 'second')
  
  if (diff < 60) {
    return '刚刚'
  } else if (diff < 3600) {
    return `${Math.floor(diff / 60)}分钟前`
  } else if (diff < 86400) {
    return `${Math.floor(diff / 3600)}小时前`
  } else if (diff < 2592000) {
    return `${Math.floor(diff / 86400)}天前`
  } else {
    return target.format('YYYY-MM-DD')
  }
}
