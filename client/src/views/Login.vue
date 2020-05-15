<template>
  <div>
    <form novalidate class="md-layout" v-on:submit.prevent="doLogin">
      <md-card class="md-layout-item md-size-50 md-small-size-100">
        <md-card-header>
        </md-card-header>

        <md-card-content>
          <div class="md-layout md-gutter">
            <div class="md-layout-item md-small-size-100">
              <md-field>
                <label for="first-name">Name</label>
                <md-input name="first-name" id="user-name" v-model="name" />
              </md-field>
            </div>

            <div class="md-layout-item md-small-size-100">
              <md-field>
                <label for="last-name">Password</label>
                <md-input name="password" id="password"  v-model="password"  />
              </md-field>
            </div>
          </div>
        </md-card-content>


        <md-card-actions>
          <md-button type="submit" class="md-primary">Create user</md-button>
        </md-card-actions>
      </md-card>

    </form>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
// import store from "@/store";

export default {
  name: "login",

  data () {
    return {
    }
  },
  methods: {
    doLogin() {
      this.$store.dispatch("aLogin", this.name, this.password);
    }
  },
  computed: {
    ...mapGetters(["games"])
  }

};

</script>
