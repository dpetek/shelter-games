<template>
  <div>
    <md-list>
      <md-list-item v-for="game in games" :key="game.id">
        <router-link :to="{name: 'wits_game', params: { id: game.id }}" >{{game.name}}
        </router-link>
        <hr/>
      </md-list-item>
    </md-list>
  <form v-on:submit.prevent="createGame">
    <div class="input-group mb-3">
        <md-field>
          <md-input v-model="newName" placeholder = "Game name" name = "newName"></md-input>
        </md-field>
        <div class="input-group-append">
          <button class="btn btn-outline-secondary" type="submit">Create Game</button>
        </div>
    </div>
  </form>
</div>
</template>

<script>
import { mapGetters } from "vuex";
import store from "@/store";

export default {
  name: "wits-index",

  data() {
    return {
      error: ''
    }
  },

  beforeRouteEnter(to, from, next) {
    Promise.all([
      store.dispatch("aFetchGames")
    ]).then(() => {
      next();
    });
  },

  methods: {
    createGame() {
      this.error = "";
      this.$store.dispatch("aCreateGame", this.newName);
      this.newName = "";
    }
  },
  
  computed: {
    ...mapGetters(["games"])
  }

};
</script>
