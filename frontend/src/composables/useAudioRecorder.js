import { ref } from 'vue'

export function useAudioRecorder() {
  const isRecording = ref(false)
  const recordingTime = ref(0)
  const mediaRecorder = ref(null)
  const audioChunks = ref([])
  const recordingInterval = ref(null)
  
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      
      mediaRecorder.value = new MediaRecorder(stream)
      audioChunks.value = []
      
      mediaRecorder.value.ondataavailable = (event) => {
        audioChunks.value.push(event.data)
      }
      
      mediaRecorder.value.onstop = () => {
        const audioBlob = new Blob(audioChunks.value, { type: 'audio/wav' })
        const audioUrl = URL.createObjectURL(audioBlob)
        
        // 这里可以处理录制的音频
        console.log('录音完成:', audioUrl)
        
        // 停止所有轨道
        stream.getTracks().forEach(track => track.stop())
      }
      
      mediaRecorder.value.start()
      isRecording.value = true
      recordingTime.value = 0
      
      // 开始计时
      recordingInterval.value = setInterval(() => {
        recordingTime.value++
      }, 1000)
      
    } catch (error) {
      console.error('启动录音失败:', error)
      alert('无法访问麦克风，请检查权限设置')
    }
  }
  
  const stopRecording = () => {
    if (mediaRecorder.value && isRecording.value) {
      mediaRecorder.value.stop()
      isRecording.value = false
      
      if (recordingInterval.value) {
        clearInterval(recordingInterval.value)
        recordingInterval.value = null
      }
      
      return recordingTime.value
    }
    return 0
  }
  
  const cancelRecording = () => {
    if (mediaRecorder.value && isRecording.value) {
      mediaRecorder.value.stop()
      isRecording.value = false
      
      if (recordingInterval.value) {
        clearInterval(recordingInterval.value)
        recordingInterval.value = null
      }
      
      recordingTime.value = 0
      audioChunks.value = []
    }
  }
  
  return {
    isRecording,
    recordingTime,
    startRecording,
    stopRecording,
    cancelRecording
  }
}
