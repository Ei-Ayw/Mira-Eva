import { defineStore } from 'pinia'
import axios from 'axios'

export const useChatStore = defineStore('chat', {
  state: () => ({
    conversations: [],
    currentConversation: null,
    messages: [],
    isLoading: false,
    error: null
  }),

  actions: {
    async sendMessage(messageData) {
      try {
        this.isLoading = true
        const response = await axios.post('/api/chat/', messageData)
        
        if (response.data.success) {
          // 消息发送成功
          return response.data
        } else {
          throw new Error(response.data.error)
        }
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async getHistoryMessages(conversationId = null) {
      try {
        this.isLoading = true
        const url = conversationId 
          ? `/api/conversations/${conversationId}/`
          : '/api/conversations/'
        
        const response = await axios.get(url)
        
        if (response.data.success) {
          if (conversationId) {
            this.messages = response.data.messages
            this.currentConversation = response.data.conversation
          } else {
            this.conversations = response.data.conversations
          }
          return response.data
        } else {
          throw new Error(response.data.error)
        }
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async createConversation(conversationData) {
      try {
        this.isLoading = true
        const response = await axios.post('/api/conversations/create/', conversationData)
        
        if (response.data.success) {
          this.conversations.unshift(response.data.conversation)
          return response.data.conversation
        } else {
          throw new Error(response.data.error)
        }
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async deleteConversation(conversationId) {
      try {
        this.isLoading = true
        const response = await axios.delete(`/api/conversations/${conversationId}/delete/`)
        
        if (response.data.success) {
          this.conversations = this.conversations.filter(
            conv => conv.id !== conversationId
          )
          if (this.currentConversation?.id === conversationId) {
            this.currentConversation = null
            this.messages = []
          }
          return true
        } else {
          throw new Error(response.data.error)
        }
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.isLoading = false
      }
    },

    clearError() {
      this.error = null
    }
  }
})
