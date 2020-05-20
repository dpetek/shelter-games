<template>
  <div class="page-container">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <md-app md-waterfall md-mode="fixed-last">
      <md-app-toolbar class="md-large md-dense">
        <div class="md-toolbar-row">
          <div class="md-toolbar-section-start">
            <router-link :to="{name: 'Home'}" class="md-display-1">Shelter Games</router-link>
          </div>

          <div v-if="!!currentUser" class="md-toolbar-section-end">
            Playing as {{currentUser.name}} | 
            <md-button class="md-dense" @click="logout()">Change</md-button>
          </div>
        </div>
      </md-app-toolbar>

      <md-app-content>
          <div class="md-layout md-gutter md-alignment-top-center">
            <div class="md-layout-item md-xlarge-size-80
              md-large-size-80 md-medium-size-90 md-small-size-100 md-xsmall-size-100  md-elevation-3 main-layout-item"
            ><router-view></router-view></div>
          </div>
      </md-app-content>
    </md-app>

  </div>
</template>

<style lang="scss">
  @import "~vue-material/src/components/MdAnimation/variables";
  @import "~vue-material/src/theme/engine";
  @import "~vue-material/src/theme/engine"; // Import the theme engine

  @include md-register-theme("default", (
    theme: dark
  ));
  @import "~vue-material/src/theme/all"; // Apply the theme

  .md-app-content {
    min-height: 100vh;
  }
  .main-layout-item {
    min-height: 100vh;
  }
</style>

<script>
import { mapGetters } from "vuex";

export default {
  name: 'App',
  components: {
  },
  created: function() {
  },
  computed: {
    ...mapGetters(["currentUser"])
  },
  methods: {
    logout() {
      this.$store.dispatch("aLogout");
    }
  },
  data: () => ({
    connection: null
  })
}
</script>

<style>
</style>
