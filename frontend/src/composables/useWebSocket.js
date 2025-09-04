import { ref, onUnmounted } from 'vue'

export function useWebSocket() {
  const ws = ref(null)
  const isConnected = ref(false)
  const messages = ref([])
  const typing = ref({ ai: false, user: false })
  const sessionId = ref(null)
  let isConnecting = false
  let heartbeatTimer = null
  let reconnectTimer = null
  let reconnectAttempts = 0
  const maxReconnectDelay = 30000 // 30s
  
  const connect = (sessionIdParam) => {
    if (!sessionIdParam) {
      console.error('缺少session_id参数')
      return
    }
    
    // 避免重复连接：若已连接相同会话，直接返回
    if (ws.value && (isConnected.value || isConnecting) && sessionId.value === sessionIdParam) {
      return
    }
    // 若切换会话，先断开旧连接
    if (ws.value && sessionId.value && sessionId.value !== sessionIdParam) {
      disconnect()
    }

    sessionId.value = sessionIdParam
    // 使用相对路径，让Vite代理处理WebSocket连接
    const wsUrl = `ws://localhost:3001/ws/chat/${sessionIdParam}/`
    
    try {
      isConnecting = true
      ws.value = new WebSocket(wsUrl)
      
      ws.value.onopen = () => {
        console.log('WebSocket连接已建立')
        isConnected.value = true
        isConnecting = false
        reconnectAttempts = 0
        // 启动心跳：每30秒发送一次ping
        clearInterval(heartbeatTimer)
        heartbeatTimer = setInterval(() => {
          if (ws.value && isConnected.value) {
            try {
              ws.value.send(JSON.stringify({ type: 'ping', ts: Date.now() }))
            } catch (e) {
              console.warn('心跳发送失败', e)
            }
          }
        }, 30000)
      }
      
      ws.value.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          console.log('收到WebSocket消息:', data)
          
          // 处理不同类型的消息
          if (data.type === 'chat_message') {
            messages.value.push(data.message)
          } else if (data.type === 'typing_status') {
            const who = data.sender || 'ai'
            typing.value[who] = !!data.is_typing
          } else if (data.type === 'pong') {
            // 心跳响应
            // console.debug('收到pong')
          } else if (data.type === 'typing_status') {
            // 处理打字状态
            console.log('用户打字状态:', data)
          } else if (data.type === 'read_receipt') {
            // 处理已读回执
            console.log('消息已读:', data)
          } else if (data.type === 'connection_established') {
            console.log('连接已建立:', data)
          } else if (data.type === 'error') {
            console.error('WebSocket错误:', data.message)
          }
        } catch (error) {
          console.error('解析WebSocket消息失败:', error)
        }
      }
      
      ws.value.onclose = () => {
        console.log('WebSocket连接已关闭')
        isConnected.value = false
        isConnecting = false
        clearInterval(heartbeatTimer)
        heartbeatTimer = null
        // 自动重连（指数退避）
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), maxReconnectDelay)
        reconnectAttempts += 1
        clearTimeout(reconnectTimer)
        reconnectTimer = setTimeout(() => {
          if (sessionId.value) {
            console.log(`尝试重连，延迟: ${delay}ms ...`)
            connect(sessionId.value)
          }
        }, delay)
      }
      
      ws.value.onerror = (error) => {
        console.error('WebSocket错误:', error)
        isConnected.value = false
      }
    } catch (error) {
      console.error('创建WebSocket连接失败:', error)
    }
  }
  
  const disconnect = () => {
    if (ws.value) {
      ws.value.close()
      ws.value = null
      isConnected.value = false
      sessionId.value = null
      isConnecting = false
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
  }
  
  const sendMessage = (messageData) => {
    if (ws.value && isConnected.value) {
      try {
        const message = {
          type: 'chat_message',
          ...messageData
        }
        ws.value.send(JSON.stringify(message))
        return true
      } catch (error) {
        console.error('发送WebSocket消息失败:', error)
        return false
      }
    }
    return false
  }
  
  const sendTypingStatus = (isTyping) => {
    if (ws.value && isConnected.value) {
      try {
        const message = {
          type: 'typing',
          is_typing: isTyping
        }
        ws.value.send(JSON.stringify(message))
        return true
      } catch (error) {
        console.error('发送打字状态失败:', error)
        return false
      }
    }
    return false
  }

  const sendActivity = () => {
    if (ws.value && isConnected.value) {
      try {
        ws.value.send(JSON.stringify({ type: 'activity', ts: Date.now() }))
      } catch (e) {}
    }
  }
  
  const sendReadReceipt = (messageId) => {
    if (ws.value && isConnected.value) {
      try {
        const message = {
          type: 'read_receipt',
          message_id: messageId
        }
        ws.value.send(JSON.stringify(message))
        return true
      } catch (error) {
        console.error('发送已读回执失败:', error)
        return false
      }
    }
    return false
  }
  
  onUnmounted(() => {
    disconnect()
  })
  
  return {
    connect,
    disconnect,
    sendMessage,
    sendTypingStatus,
    sendActivity,
    sendReadReceipt,
    isConnected,
    messages,
    typing,
    sessionId
  }
}
