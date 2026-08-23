<template>
  <section class="page-section">
    <div class="page-heading">
      <div><p class="eyebrow">OVERVIEW</p><h1>工作台</h1></div>
    </div>
    <div class="dashboard-grid">
      <router-link class="dashboard-card" to="/products">
        <span>01</span><h2>产品管理</h2><p>维护产品资料、上下架和产品图片。</p>
      </router-link>
      <router-link class="dashboard-card" to="/carousel">
        <span>02</span><h2>首页轮播</h2><p>维护电脑端与手机端轮播图片、链接和排序。</p>
      </router-link>
      <router-link class="dashboard-card" to="/company">
        <span>03</span><h2>公司信息</h2><p>维护公司主体、联系方式、二维码和备案信息。</p>
      </router-link>
    </div>
    <div class="notice-card">
      <strong>上线前提醒</strong>
      <p>请核验公司主体、备案号、联系方式及产品功效表述。产品分类和固定页面由开发人员维护。</p>
    </div>
  </section>
</template>
