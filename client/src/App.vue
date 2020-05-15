<template>
  <div class="page-container">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <md-app md-waterfall md-mode="fixed-last">
      <md-app-toolbar class="md-large md-dense md-primary">
        <div class="md-toolbar-row">
          <div class="md-toolbar-section-start">
            <router-link to="/Home" class="md-title">Shelter Games</router-link>
          </div>

          <div class="md-toolbar-section-end">
            Playing as {{currentUser.name}}
          </div>
        </div>
      </md-app-toolbar>

      <md-app-content>
          <div class="md-layout md-gutter md-alignment-top-center">
            <div class="md-layout-item md-xlarge-size-60
              md-large-size-60 md-medium-size-80 md-small-size-100 md-xsmall-size-100  md-elevation-3"
            ><router-view></router-view></div>
          </div>
      </md-app-content>
    </md-app>
  </div>
</template>

<style lang="scss" scoped>
  @import "~vue-material/src/components/MdAnimation/variables";
  @import "~vue-material/src/theme/engine";

  .md-app-content {
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
    //console.log("Starting connection to WebSocket Server")
    //this.connection = new WebSocket('ws://127.0.0.1:5000')
    //
    //this.connection.onmessage = function(event) {
    //  console.log("Message received: ");
    //  console.log(event);
    //}
    //
    //this.connection.onopen = function(event) {
    //  console.log(event)
    //  console.log("Successfully connected to the echo websocket server...")
    //  this.connection.send('Hello');
    //}
    //
  },
  computed: {
    ...mapGetters(["currentUser"])
  },
  data: () => ({
    connection: null
  })
}
</script>

<style>
</style>
