import { ref, onUnmounted } from 'vue'

export function useWebSocket() {
  const ws = ref(null)
  const isConnected = ref(false)
  const messages = ref([])
  const sessionId = ref(null)
  
  const connect = (sessionIdParam) => {
    if (!sessionIdParam) {
      console.error('缺少session_id参数')
      return
    }
    
    sessionId.value = sessionIdParam
    const wsUrl = `ws://localhost:8000/ws/chat/${sessionIdParam}/`
    
    try {
      ws.value = new WebSocket(wsUrl)
      
      ws.value.onopen = () => {
        console.log('WebSocket连接已建立')
        isConnected.value = true
      }
      
      ws.value.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          console.log('收到WebSocket消息:', data)
          
          // 处理不同类型的消息
          if (data.type === 'chat_message') {
            messages.value.push(data.message)
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
    sendReadReceipt,
    isConnected,
    messages,
    sessionId
  }
}
