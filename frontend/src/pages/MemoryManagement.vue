<template>
  <div class="memory-management-page">
    <div class="page-header">
      <button class="back-btn" @click="goBack">
        <span class="back-icon">←</span>
      </button>
      <h1 class="page-title">记忆库管理</h1>
      <div class="header-actions">
        <a-button type="primary" @click="refreshMemories">
          <ReloadOutlined />
          刷新
        </a-button>
      </div>
    </div>

    <!-- 记忆统计 -->
    <div class="memory-stats">
      <a-row :gutter="16">
        <a-col :span="6">
          <a-card>
            <a-statistic title="总记忆数" :value="memoryStats.total_memories" />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card>
            <a-statistic title="个人信息" :value="memoryStats.type_counts.personal || 0" />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card>
            <a-statistic title="偏好设置" :value="memoryStats.type_counts.preference || 0" />
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card>
            <a-statistic title="人际关系" :value="memoryStats.type_counts.relationship || 0" />
          </a-card>
        </a-col>
      </a-row>
    </div>

    <!-- 搜索和筛选 -->
    <div class="memory-filters">
      <a-row :gutter="16" align="middle">
        <a-col :span="8">
          <a-input-search
            v-model:value="searchQuery"
            placeholder="搜索记忆..."
            @search="searchMemories"
            enter-button
          />
        </a-col>
        <a-col :span="6">
          <a-select
            v-model:value="selectedType"
            placeholder="选择记忆类型"
            style="width: 100%"
            @change="filterByType"
          >
            <a-select-option value="">全部类型</a-select-option>
            <a-select-option value="personal">个人信息</a-select-option>
            <a-select-option value="preference">偏好</a-select-option>
            <a-select-option value="relationship">人际关系</a-select-option>
            <a-select-option value="event">重要事件</a-select-option>
            <a-select-option value="emotion">情绪状态</a-select-option>
          </a-select>
        </a-col>
        <a-col :span="6">
          <a-select
            v-model:value="sortBy"
            placeholder="排序方式"
            style="width: 100%"
            @change="sortMemories"
          >
            <a-select-option value="importance">重要性</a-select-option>
            <a-select-option value="recent">最近访问</a-select-option>
            <a-select-option value="created">创建时间</a-select-option>
          </a-select>
        </a-col>
        <a-col :span="4">
          <a-button type="primary" @click="showAddMemory">
            <PlusOutlined />
            添加记忆
          </a-button>
        </a-col>
      </a-row>
    </div>

    <!-- 记忆列表 -->
    <div class="memory-list">
      <a-table
        :columns="memoryColumns"
        :data-source="filteredMemories"
        :loading="loading"
        :pagination="{ pageSize: 10, showSizeChanger: true }"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'memory_type'">
            <a-tag :color="getTypeColor(record.memory_type)">
              {{ getTypeText(record.memory_type) }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'importance_score'">
            <a-progress
              :percent="record.importance_score * 100"
              :show-info="false"
              size="small"
            />
            <span class="score-text">{{ (record.importance_score * 100).toFixed(0) }}%</span>
          </template>
          <template v-else-if="column.key === 'last_accessed'">
            {{ formatDate(record.last_accessed) }}
          </template>
          <template v-else-if="column.key === 'actions'">
            <a-space>
              <a-button size="small" @click="editMemory(record)">
                编辑
              </a-button>
              <a-button size="small" type="danger" @click="deleteMemory(record)">
                删除
              </a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </div>

    <!-- 添加/编辑记忆弹窗 -->
    <a-modal
      v-model:open="memoryModalVisible"
      :title="editingMemory ? '编辑记忆' : '添加记忆'"
      @ok="saveMemory"
      @cancel="cancelEdit"
    >
      <a-form :model="memoryForm" layout="vertical">
        <a-form-item label="记忆类型" required>
          <a-select v-model:value="memoryForm.memory_type" placeholder="选择记忆类型">
            <a-select-option value="personal">个人信息</a-select-option>
            <a-select-option value="preference">偏好</a-select-option>
            <a-select-option value="relationship">人际关系</a-select-option>
            <a-select-option value="event">重要事件</a-select-option>
            <a-select-option value="emotion">情绪状态</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="记忆键" required>
          <a-input v-model:value="memoryForm.key" placeholder="如：pet_name" />
        </a-form-item>
        <a-form-item label="记忆值" required>
          <a-textarea v-model:value="memoryForm.value" placeholder="如：小白" :rows="3" />
        </a-form-item>
        <a-form-item label="上下文">
          <a-textarea v-model:value="memoryForm.context" placeholder="相关上下文信息" :rows="2" />
        </a-form-item>
        <a-form-item label="重要性评分">
          <a-slider
            v-model:value="memoryForm.importance_score"
            :min="0"
            :max="1"
            :step="0.1"
            :marks="{ 0: '0', 0.5: '0.5', 1: '1' }"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, reactive } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { ReloadOutlined, PlusOutlined } from '@ant-design/icons-vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const { getAuthHeaders } = useAuth()
const router = useRouter()

// 响应式数据
const loading = ref(false)
const memories = ref([])
const memoryStats = ref({
  total_memories: 0,
  type_counts: {},
  recent_accessed: 0
})
const searchQuery = ref('')
const selectedType = ref('')
const sortBy = ref('importance')
const memoryModalVisible = ref(false)
const editingMemory = ref(null)

// 表单数据
const memoryForm = reactive({
  memory_type: '',
  key: '',
  value: '',
  context: '',
  importance_score: 0.5
})

// 表格列定义
const memoryColumns = [
  {
    title: '记忆键',
    dataIndex: 'key',
    key: 'key',
    width: 150,
  },
  {
    title: '记忆值',
    dataIndex: 'value',
    key: 'value',
    width: 200,
  },
  {
    title: '类型',
    dataIndex: 'memory_type',
    key: 'memory_type',
    width: 100,
  },
  {
    title: '重要性',
    dataIndex: 'importance_score',
    key: 'importance_score',
    width: 120,
  },
  {
    title: '最后访问',
    dataIndex: 'last_accessed',
    key: 'last_accessed',
    width: 150,
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
    width: 150,
  },
]

// 计算属性
const filteredMemories = computed(() => {
  let filtered = memories.value

  // 按类型筛选
  if (selectedType.value) {
    filtered = filtered.filter(memory => memory.memory_type === selectedType.value)
  }

  // 按搜索词筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(memory => 
      memory.key.toLowerCase().includes(query) ||
      memory.value.toLowerCase().includes(query) ||
      memory.context.toLowerCase().includes(query)
    )
  }

  // 排序
  if (sortBy.value === 'importance') {
    filtered.sort((a, b) => b.importance_score - a.importance_score)
  } else if (sortBy.value === 'recent') {
    filtered.sort((a, b) => new Date(b.last_accessed) - new Date(a.last_accessed))
  } else if (sortBy.value === 'created') {
    filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  }

  return filtered
})

// 生命周期
onMounted(() => {
  loadMemories()
  loadMemoryStats()
})

// 方法
const goBack = () => {
  router.back()
}

const loadMemories = async () => {
  try {
    loading.value = true
    const response = await fetch('/api/memories/', {
      headers: getAuthHeaders()
    })
    
    if (response.ok) {
      const result = await response.json()
      memories.value = result.results || result
    } else {
      throw new Error('加载记忆失败')
    }
  } catch (error) {
    message.error('加载记忆失败')
  } finally {
    loading.value = false
  }
}

const loadMemoryStats = async () => {
  try {
    const response = await fetch('/api/memories/stats/', {
      headers: getAuthHeaders()
    })
    
    if (response.ok) {
      const result = await response.json()
      memoryStats.value = result
    }
  } catch (error) {
    console.error('加载记忆统计失败:', error)
  }
}

const refreshMemories = () => {
  loadMemories()
  loadMemoryStats()
}

const searchMemories = () => {
  // 搜索逻辑在计算属性中处理
}

const filterByType = () => {
  // 筛选逻辑在计算属性中处理
}

const sortMemories = () => {
  // 排序逻辑在计算属性中处理
}

const showAddMemory = () => {
  editingMemory.value = null
  resetMemoryForm()
  memoryModalVisible.value = true
}

const editMemory = (memory) => {
  editingMemory.value = memory
  memoryForm.memory_type = memory.memory_type
  memoryForm.key = memory.key
  memoryForm.value = memory.value
  memoryForm.context = memory.context
  memoryForm.importance_score = memory.importance_score
  memoryModalVisible.value = true
}

const saveMemory = async () => {
  try {
    if (!memoryForm.memory_type || !memoryForm.key || !memoryForm.value) {
      message.error('请填写必填字段')
      return
    }

    const url = editingMemory.value 
      ? `/api/memories/${editingMemory.value.id}/`
      : '/api/memories/'
    
    const method = editingMemory.value ? 'PUT' : 'POST'
    
    const response = await fetch(url, {
      method,
      headers: getAuthHeaders('application/json'),
      body: JSON.stringify(memoryForm)
    })
    
    if (response.ok) {
      message.success(editingMemory.value ? '记忆更新成功！' : '记忆添加成功！')
      memoryModalVisible.value = false
      loadMemories()
      loadMemoryStats()
    } else {
      throw new Error('保存失败')
    }
  } catch (error) {
    message.error(`保存失败: ${error.message}`)
  }
}

const deleteMemory = (memory) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除记忆 "${memory.key}: ${memory.value}" 吗？`,
    onOk: async () => {
      try {
        const response = await fetch(`/api/memories/${memory.id}/`, {
          method: 'DELETE',
          headers: getAuthHeaders()
        })
        
        if (response.ok) {
          message.success('记忆删除成功！')
          loadMemories()
          loadMemoryStats()
        } else {
          throw new Error('删除失败')
        }
      } catch (error) {
        message.error(`删除失败: ${error.message}`)
      }
    }
  })
}

const cancelEdit = () => {
  memoryModalVisible.value = false
  resetMemoryForm()
}

const resetMemoryForm = () => {
  memoryForm.memory_type = ''
  memoryForm.key = ''
  memoryForm.value = ''
  memoryForm.context = ''
  memoryForm.importance_score = 0.5
}

const getTypeColor = (type) => {
  const colors = {
    'personal': 'blue',
    'preference': 'green',
    'relationship': 'orange',
    'event': 'purple',
    'emotion': 'red'
  }
  return colors[type] || 'default'
}

const getTypeText = (type) => {
  const texts = {
    'personal': '个人信息',
    'preference': '偏好',
    'relationship': '人际关系',
    'event': '重要事件',
    'emotion': '情绪状态'
  }
  return texts[type] || type
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.memory-management-page {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.back-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: background-color 0.3s;
}

.back-btn:hover {
  background-color: #f5f5f5;
}

.page-title {
  font-size: 24px;
  margin: 0;
  color: #000000;
}

.memory-stats {
  margin-bottom: 24px;
}

.memory-filters {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.memory-list {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.score-text {
  margin-left: 8px;
  font-size: 12px;
  color: #8E8E93;
}

@media (max-width: 768px) {
  .memory-management-page {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .memory-filters .ant-row {
    flex-direction: column;
    gap: 12px;
  }
}
</style>
