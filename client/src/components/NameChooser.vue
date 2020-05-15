<template>
  <div>
    <form class="md-layout" v-on:submit.prevent="doLogin">
        <md-field>
          <md-input v-model="name" placeholder="Choose your name"></md-input>
        </md-field>
        <md-card-actions>
          <md-button type="submit" class="md-primary">Select</md-button>
        </md-card-actions>

    </form>
  </div>
</template>

<script>

export default {
  name: "NameChooser",
  data () {
    return {
    }
  },
  methods: {
    doLogin() {
      this.$store.dispatch("aLogin", this.name);
    }
  },
};

</script>
