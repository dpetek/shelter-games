<template>
  <div class="md-toolbar-row">
    <div class="md-menu-item">
      <router-link :to="{name: 'wits_index'}" class="nav-link">Wits</router-link>
    </div>
    <div class="md-menu-item">
      <router-link :to="{name: 'codenames_index'}" class="nav-link">Codenames </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: "SGHeader"
};
</script>
