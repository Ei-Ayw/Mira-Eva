<template>
  <div class="document-upload-page">
    <div class="page-header">
      <h1>文档上传与学习包</h1>
      <p>上传PDF、Word、Markdown等文档，自动解析为学习材料</p>
    </div>

    <!-- 文档上传区域 -->
    <div class="upload-section">
      <h2>上传文档</h2>
      <div class="upload-area" @drop="handleDrop" @dragover.prevent @dragenter.prevent>
        <div v-if="!uploading" class="upload-content">
          <a-upload
            :file-list="fileList"
            :before-upload="beforeUpload"
            :custom-request="customUpload"
            :multiple="true"
            :show-upload-list="false"
            accept=".pdf,.docx,.doc,.md,.markdown,.txt"
          >
            <div class="upload-trigger">
              <a-icon type="inbox" class="upload-icon" />
              <p>点击或拖拽文件到此区域上传</p>
              <p class="upload-hint">支持 PDF、Word、Markdown、TXT 格式</p>
            </div>
          </a-upload>
        </div>
        <div v-else class="uploading-content">
          <a-spin size="large" />
          <p>正在处理文档...</p>
        </div>
      </div>
    </div>

    <!-- 文档列表 -->
    <div class="documents-section">
      <h2>我的文档</h2>
      <div class="documents-header">
        <a-input-search
          v-model:value="searchQuery"
          placeholder="搜索文档..."
          style="width: 300px"
          @search="searchDocuments"
        />
        <a-button type="primary" @click="refreshDocuments">
          <a-icon type="reload" />
          刷新
        </a-button>
      </div>

      <a-table
        :columns="documentColumns"
        :data-source="documents"
        :loading="loading"
        :pagination="{ pageSize: 10 }"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">
              {{ getStatusText(record.status) }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'file_type'">
            <a-tag>{{ record.file_type_display }}</a-tag>
          </template>
          <template v-else-if="column.key === 'actions'">
            <a-space>
              <a-button size="small" @click="viewDocument(record)">
                查看
              </a-button>
              <a-button 
                size="small" 
                type="primary" 
                @click="reprocessDocument(record)"
                :disabled="record.status === 'processing'"
              >
                重新处理
              </a-button>
              <a-button 
                size="small" 
                type="danger" 
                @click="deleteDocument(record)"
              >
                删除
              </a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </div>

    <!-- 学习包管理 -->
    <div class="packages-section">
      <h2>学习包管理</h2>
      <div class="packages-header">
        <a-button type="primary" @click="showCreatePackage">
          <a-icon type="plus" />
          创建学习包
        </a-button>
      </div>

      <a-table
        :columns="packageColumns"
        :data-source="learningPackages"
        :loading="packagesLoading"
        :pagination="{ pageSize: 5 }"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'package_type'">
            <a-tag>{{ record.package_type_display }}</a-tag>
          </template>
          <template v-else-if="column.key === 'actions'">
            <a-space>
              <a-button size="small" @click="viewPackage(record)">
                查看
              </a-button>
              <a-button size="small" @click="editPackage(record)">
                编辑
              </a-button>
              <a-button size="small" type="danger" @click="deletePackage(record)">
                删除
              </a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </div>

    <!-- 创建学习包弹窗 -->
    <a-modal
      v-model:open="createPackageVisible"
      title="创建学习包"
      @ok="createPackage"
      @cancel="createPackageVisible = false"
    >
      <a-form :model="packageForm" layout="vertical">
        <a-form-item label="包名称" required>
          <a-input v-model:value="packageForm.name" placeholder="输入学习包名称" />
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea v-model:value="packageForm.description" placeholder="输入学习包描述" />
        </a-form-item>
        <a-form-item label="包类型" required>
          <a-select v-model:value="packageForm.package_type" placeholder="选择包类型">
            <a-select-option value="conversation">对话示例</a-select-option>
            <a-select-option value="knowledge">知识库</a-select-option>
            <a-select-option value="training">训练材料</a-select-option>
            <a-select-option value="reference">参考资料</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="选择文档">
          <a-select
            v-model:value="packageForm.document_ids"
            mode="multiple"
            placeholder="选择要包含的文档"
            style="width: 100%"
          >
            <a-select-option 
              v-for="doc in availableDocuments" 
              :key="doc.id" 
              :value="doc.id"
            >
              {{ doc.title }}
            </a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 文档详情弹窗 -->
    <a-modal
      v-model:open="documentDetailVisible"
      title="文档详情"
      width="800px"
      @cancel="documentDetailVisible = false"
    >
      <div v-if="selectedDocument">
        <a-descriptions title="基本信息" bordered>
          <a-descriptions-item label="标题">{{ selectedDocument.title }}</a-descriptions-item>
          <a-descriptions-item label="类型">{{ selectedDocument.file_type_display }}</a-descriptions-item>
          <a-descriptions-item label="大小">{{ selectedDocument.file_size_mb }} MB</a-descriptions-item>
          <a-descriptions-item label="状态">
            <a-tag :color="getStatusColor(selectedDocument.status)">
              {{ getStatusText(selectedDocument.status) }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="上传时间">{{ selectedDocument.created_at }}</a-descriptions-item>
          <a-descriptions-item label="处理时间" v-if="selectedDocument.processed_at">
            {{ selectedDocument.processed_at }}
          </a-descriptions-item>
        </a-descriptions>

        <div class="document-content" v-if="selectedDocument.extracted_text">
          <h3>提取的文本</h3>
          <a-textarea
            :value="selectedDocument.extracted_text"
            :rows="10"
            readonly
          />
        </div>

        <div class="document-chunks" v-if="selectedDocument.chunks && selectedDocument.chunks.length">
          <h3>文档分块 ({{ selectedDocument.chunks.length }})</h3>
          <a-collapse>
            <a-collapse-panel
              v-for="chunk in selectedDocument.chunks"
              :key="chunk.id"
              :header="`${chunk.chunk_type_display} - ${chunk.content.substring(0, 50)}...`"
            >
              <div class="chunk-content">
                <a-tag>{{ chunk.chunk_type_display }}</a-tag>
                <p>{{ chunk.content }}</p>
                <small>长度: {{ chunk.content.length }} 字符</small>
              </div>
            </a-collapse-panel>
          </a-collapse>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { useAuth } from '@/composables/useAuth'

const { getAuthHeaders } = useAuth()

// 响应式数据
const uploading = ref(false)
const loading = ref(false)
const packagesLoading = ref(false)
const fileList = ref([])
const documents = ref([])
const learningPackages = ref([])
const availableDocuments = ref([])
const searchQuery = ref('')
const createPackageVisible = ref(false)
const documentDetailVisible = ref(false)
const selectedDocument = ref(null)

// 表单数据
const packageForm = reactive({
  name: '',
  description: '',
  package_type: '',
  document_ids: []
})

// 表格列定义
const documentColumns = [
  {
    title: '标题',
    dataIndex: 'title',
    key: 'title',
    width: 200,
  },
  {
    title: '类型',
    dataIndex: 'file_type',
    key: 'file_type',
    width: 100,
  },
  {
    title: '大小',
    dataIndex: 'file_size_mb',
    key: 'file_size_mb',
    width: 100,
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 100,
  },
  {
    title: '上传时间',
    dataIndex: 'created_at',
    key: 'created_at',
    width: 150,
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
  },
]

const packageColumns = [
  {
    title: '名称',
    dataIndex: 'name',
    key: 'name',
  },
  {
    title: '类型',
    dataIndex: 'package_type',
    key: 'package_type',
    width: 120,
  },
  {
    title: '文档数',
    dataIndex: 'document_count',
    key: 'document_count',
    width: 100,
  },
  {
    title: '分块数',
    dataIndex: 'total_chunks',
    key: 'total_chunks',
    width: 100,
  },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    key: 'created_at',
    width: 150,
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
  },
]

// 生命周期
onMounted(() => {
  loadDocuments()
  loadLearningPackages()
  loadAvailableDocuments()
})

// 方法
const beforeUpload = (file) => {
  const allowedMimeTypes = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/msword',
    'text/markdown',
    'text/plain'
  ]

  const allowedExts = ['pdf', 'docx', 'doc', 'md', 'markdown', 'txt']
  const fileExt = (file.name?.split('.')?.pop() || '').toLowerCase()
  const isValidType = allowedMimeTypes.includes(file.type) || allowedExts.includes(fileExt)

  if (!isValidType) {
    message.error('不支持的文件类型！')
    return false // 阻止非法文件
  }

  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    message.error('文件大小不能超过 10MB！')
    return false
  }

  return true // 通过校验，允许开始上传，从而触发 customRequest
}

const customUpload = async ({ file, onSuccess, onError }) => {
  try {
    uploading.value = true
    
    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', file.name)
    
    const response = await fetch('/api/documents/', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: formData
    })
    
    if (!response.ok) {
      throw new Error('上传失败')
    }
    
    const result = await response.json()
    
    if (result.success) {
      message.success('文档上传成功！')
      onSuccess(result)
      loadDocuments() // 刷新文档列表
    } else {
      throw new Error(result.error || '上传失败')
    }
  } catch (error) {
    message.error(`上传失败: ${error.message}`)
    onError(error)
  } finally {
    uploading.value = false
  }
}

const handleDrop = (e) => {
  e.preventDefault()
  const files = Array.from(e.dataTransfer.files)
  
  if (files.length > 0) {
    const file = files[0]
    customUpload({
      file,
      onSuccess: () => {},
      onError: () => {}
    })
  }
}

const loadDocuments = async () => {
  try {
    loading.value = true
    const response = await fetch('/api/documents/', {
      headers: getAuthHeaders()
    })
    
    if (response.ok) {
      const result = await response.json()
      documents.value = result.results || result
    }
  } catch (error) {
    message.error('加载文档失败')
  } finally {
    loading.value = false
  }
}

const loadLearningPackages = async () => {
  try {
    packagesLoading.value = true
    const response = await fetch('/api/packages/', {
      headers: getAuthHeaders()
    })
    
    if (response.ok) {
      const result = await response.json()
      learningPackages.value = result.results || result
    }
  } catch (error) {
    message.error('加载学习包失败')
  } finally {
    packagesLoading.value = false
  }
}

const loadAvailableDocuments = async () => {
  try {
    const response = await fetch('/api/documents/', {
      headers: getAuthHeaders()
    })
    
    if (response.ok) {
      const result = await response.json()
      availableDocuments.value = (result.results || result).filter(doc => doc.status === 'completed')
    }
  } catch (error) {
    console.error('加载可用文档失败:', error)
  }
}

const searchDocuments = () => {
  // 实现搜索逻辑
  console.log('搜索:', searchQuery.value)
}

const refreshDocuments = () => {
  loadDocuments()
  loadLearningPackages()
}

const viewDocument = (document) => {
  selectedDocument.value = document
  documentDetailVisible.value = true
}

const reprocessDocument = async (document) => {
  try {
    const response = await fetch(`/api/documents/${document.id}/reprocess/`, {
      method: 'POST',
      headers: getAuthHeaders()
    })
    
    if (response.ok) {
      message.success('文档重新处理成功！')
      loadDocuments()
    } else {
      throw new Error('重新处理失败')
    }
  } catch (error) {
    message.error(`重新处理失败: ${error.message}`)
  }
}

const deleteDocument = (document) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除文档 "${document.title}" 吗？`,
    onOk: async () => {
      try {
        const response = await fetch(`/api/documents/${document.id}/`, {
          method: 'DELETE',
          headers: getAuthHeaders()
        })
        
        if (response.ok) {
          message.success('文档删除成功！')
          loadDocuments()
        } else {
          throw new Error('删除失败')
        }
      } catch (error) {
        message.error(`删除失败: ${error.message}`)
      }
    }
  })
}

const showCreatePackage = () => {
  packageForm.name = ''
  packageForm.description = ''
  packageForm.package_type = ''
  packageForm.document_ids = []
  createPackageVisible.value = true
}

const createPackage = async () => {
  try {
    if (!packageForm.name || !packageForm.package_type) {
      message.error('请填写必填字段')
      return
    }
    
    const response = await fetch('/api/packages/', {
      method: 'POST',
      headers: getAuthHeaders('application/json'),
      body: JSON.stringify(packageForm)
    })
    
    if (response.ok) {
      const result = await response.json()
      if (result.success) {
        message.success('学习包创建成功！')
        createPackageVisible.value = false
        loadLearningPackages()
      } else {
        throw new Error(result.error || '创建失败')
      }
    } else {
      throw new Error('创建失败')
    }
  } catch (error) {
    message.error(`创建失败: ${error.message}`)
  }
}

const viewPackage = (pkg) => {
  // 实现查看学习包逻辑
  console.log('查看学习包:', pkg)
}

const editPackage = (pkg) => {
  // 实现编辑学习包逻辑
  console.log('编辑学习包:', pkg)
}

const deletePackage = (pkg) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除学习包 "${pkg.name}" 吗？`,
    onOk: async () => {
      try {
                  const response = await fetch(`/api/packages/${pkg.id}/`, {
          method: 'DELETE',
          headers: getAuthHeaders()
        })
        
        if (response.ok) {
          message.success('学习包删除成功！')
          loadLearningPackages()
        } else {
          throw new Error('删除失败')
        }
      } catch (error) {
        message.error(`删除失败: ${error.message}`)
      }
    }
  })
}

const getStatusColor = (status) => {
  const colors = {
    'uploading': 'blue',
    'processing': 'orange',
    'completed': 'green',
    'failed': 'red'
  }
  return colors[status] || 'default'
}

const getStatusText = (status) => {
  const texts = {
    'uploading': '上传中',
    'processing': '处理中',
    'completed': '已完成',
    'failed': '失败'
  }
  return texts[status] || status
}
</script>

<style scoped>
.document-upload-page {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 32px;
}

.page-header h1 {
  font-size: 28px;
  margin-bottom: 8px;
  color: #000000;
}

.page-header p {
  font-size: 16px;
  color: #8E8E93;
}

.upload-section,
.documents-section,
.packages-section {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.upload-section h2,
.documents-section h2,
.packages-section h2 {
  font-size: 20px;
  margin-bottom: 16px;
  color: #000000;
}

.upload-area {
  border: 2px dashed #D9D9D9;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  transition: border-color 0.3s;
}

.upload-area:hover {
  border-color: #007AFF;
}

.upload-trigger {
  cursor: pointer;
}

.upload-icon {
  font-size: 48px;
  color: #8E8E93;
  margin-bottom: 16px;
}

.upload-hint {
  color: #8E8E93;
  font-size: 14px;
  margin-top: 8px;
}

.uploading-content {
  text-align: center;
}

.documents-header,
.packages-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.document-content,
.document-chunks {
  margin-top: 24px;
}

.document-content h3,
.document-chunks h3 {
  font-size: 16px;
  margin-bottom: 12px;
  color: #000000;
}

.chunk-content {
  padding: 12px;
  background: #F5F5F5;
  border-radius: 6px;
  margin-bottom: 8px;
}

.chunk-content p {
  margin: 8px 0;
  line-height: 1.6;
}

.chunk-content small {
  color: #8E8E93;
}

@media (max-width: 768px) {
  .document-upload-page {
    padding: 16px;
  }
  
  .upload-area {
    padding: 24px;
  }
  
  .documents-header,
  .packages-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
}
</style>
