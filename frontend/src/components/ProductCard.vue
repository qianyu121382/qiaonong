<script setup>
defineProps({ product: { type: Object, required: true } })
</script>

<template>
  <router-link class="product-card" :to="`/product/${product.slug}`">
    <div class="product-image">
      <img v-if="product.cover" :src="product.cover" :alt="product.name" loading="lazy" />
      <span v-else>QIAONONG</span>
      <img v-if="product.hover_image" class="hover-image" :src="product.hover_image" :alt="`${product.name} 展示图`" loading="lazy" />
    </div>
    <div class="product-meta"><small>{{ product.tag || product.category?.name }}</small><h3>{{ product.name }}</h3><p>{{ product.summary }}</p></div>
  </router-link>
</template>
