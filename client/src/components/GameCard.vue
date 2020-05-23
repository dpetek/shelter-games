<template>
<div class="game-card-container">
  <md-card v-if="cardState == 0" class="game-card">
    <md-card-media-cover md-solid>
      <md-card-media md-ratio="16:9">
        <img :src="thumbnail" :alt="name">
      </md-card-media>

      <md-card-area>
        <md-card-header>
          <span class="md-title">{{name}}</span>
          <span class="md-subhead">{{description}}</span>
        </md-card-header>

        <md-card-actions>
          <md-button @click="showJoin()">Join</md-button>
          <md-button @click="showCreate()">Create</md-button>
        </md-card-actions>
      </md-card-area>
    </md-card-media-cover>
  </md-card>

  <md-card v-if="cardState == 1" class="game-card game-card-join">
    <md-card-media-cover md-solid>
      <md-card-media md-ratio="16:9">
        <img :src="thumbnail" :alt="name">
      </md-card-media>
      <md-card-area>
        <md-card-header>
          <span class="md-title">{{name}}</span>
        </md-card-header>
        
        <md-card-content v-if="!notFinished">
          <form v-on:submit.prevent="joinGame()">
            <md-field v-bind:class="['game-input-field', {'md-invalid': !!joinError}]">
              <label>Game code</label>
              <md-input v-model="gameCode"></md-input>
              <span class="md-error">{{joinError}}</span>
            </md-field>
          </form>
        </md-card-content>
        <md-card-content v-else>
          Game is not available yet.
        </md-card-content>

        <md-card-actions v-if="!notFinished">
          <md-button @click="joinGame()">Join</md-button>
        </md-card-actions>

      </md-card-area>
    </md-card-media-cover>
  </md-card>

  <md-card v-if="cardState == 2" class="game-card game-card-create">
    <md-card-media-cover md-solid>
      <md-card-media md-ratio="16:9">
        <img :src="thumbnail" :alt="name">
      </md-card-media>
      <md-card-area>
        <md-card-header>
          <span class="md-title">{{name}}</span>
        </md-card-header>
        
        <md-card-content v-if="!notFinished">
          <form v-on:submit.prevent="createGame()">
            <md-field v-bind:class="['game-input-field', {'md-invalid': !!joinError}]">
              <label>Game Name</label>
              <md-input v-model="gameName"></md-input>
              <span class="md-error">{{createError}}</span>
            </md-field>
          </form>
        </md-card-content>
        <md-card-content v-else>
          Game is not available yet.
        </md-card-content>

        <md-card-actions v-if="!notFinished">
          <md-button @click="createGame()">Create</md-button>
        </md-card-actions>

      </md-card-area>
    </md-card-media-cover>
  </md-card>
</div>

</template>

<style>
.game-card-container {
  display: inline-block;
}
.game-card {
  width: 340px;
  margin: 25px;
  display: inline-block;
}
.game-input-field {
  border-bottom: 1px solid white;
}
.game-input-field label {
  color: white;
}

.game-card-join .md-card-content{
  padding-bottom: 0px;
}
.game-card-join .md-card-header{
  padding-bottom: 0px;
  padding-top: 0px;
}

.game-card-create .md-card-content{
  padding-bottom: 0px;
}
.game-card-create .md-card-header{
  padding-bottom: 0px;
  padding-top: 0px;
}

</style>

<script>
import ClickOutside from 'vue-click-outside';
import {
  WitsService
} from "@/common/api.service";

export default {
  name: "GameCard",
  props: {
    name: { type: String, required: true },
    thumbnail: { type: String, required: true },
    description: { type: String, required: false},
    resourceName: { type: String, required: true},
    routeName: { type: String, required: true},
    notFinished: { type: Boolean, required: false}
  },
  data() {
    return {
      cardState: 0,
      gameCode: null,
      joinError: null,
      gameName: null,
      createError: null
    }
  },
  methods: {
    showJoin() {
      this.cardState = 1;
    },
    showCreate() {
      console.log("Changing card state to 2");
      this.cardState = 2;
    },
    resetCardState() {
      this.cardState = 0;
    },
    joinGame() {
      this.joinError = null;
      var that = this;
      WitsService.get(this.gameCode).then(function(resp){
        if (resp.data.error) {
          that.joinError = resp.data.error;
          return;
        }
      });
      this.$router.push({name: "wits_game", params: {"id": this.gameCode}});
    },
    createGame() {
      this.createError = null;
      var that = this;
      WitsService.create(this.gameName).then(function(resp){
        if (resp.data.error) {
          that.createError = resp.data.error;
          return;
        }
        that.$router.push({name: "wits_game", params: {"id": resp.data.game.code}});
      });
    }
  },
  directives: {
    ClickOutside
  }
}
</script>
