<template>
  <section class="page-section">
    <div class="page-heading">
      <div><p class="eyebrow">OVERVIEW</p><h1>工作台</h1></div>
    </div>
    <div class="dashboard-grid">
      <router-link class="dashboard-card" to="/catalog">
        <span>01</span><h2>产品管理</h2><p>维护分类、产品资料、上下架和产品图片。</p>
      </router-link>
      <router-link class="dashboard-card" to="/content">
        <span>02</span><h2>网站内容</h2><p>维护首页、品牌、联系信息、政策页面和轮播图。</p>
      </router-link>
    </div>
    <div class="notice-card">
      <strong>上线前提醒</strong>
      <p>请核验公司主体、备案号、联系方式、政策正文及产品功效表述。系统不会自动采用旧站中混入的婵泉信息。</p>
    </div>
  </section>
</template>
