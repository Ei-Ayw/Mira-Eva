<template>
  <div id="app" class="mobile-app">
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
/* 移动端适配样式 */
.mobile-app {
  max-width: 100vw;
  min-height: 100vh;
  overflow-x: hidden;
}

/* 移动端触摸优化 */
* {
  -webkit-tap-highlight-color: transparent;
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  user-select: none;
}

/* 输入框允许选择 */
input, textarea {
  -webkit-user-select: text;
  user-select: text;
}

/* 防止页面缩放 */
html, body {
  touch-action: manipulation;
  -webkit-text-size-adjust: 100%;
}
</style>
