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
          <md-button>Create</md-button>
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
        <md-card-content>
          <md-field class="game-input-field">
            <label>Game code</label>
            <md-input v-model="gameCode"></md-input>
          </md-field>
        </md-card-content>
        <md-card-actions>
          <md-button @click="joinGame()">Join</md-button>
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
  width: 300px;
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

</style>

<script>

export default {
  name: "GameCard",
  props: {
    name: { type: String, required: true },
    thumbnail: { type: String, required: true },
    description: { type: String, required: false},
    resourceName: { type: String, required: true},
    routeName: { type: String, required: true},
  },
  data() {
    return {
      cardState: 0,
      gameCode: null
    }
  },
  methods: {
    showJoin() {
      this.cardState = 1;
    },
    joinGame() {
      this.$router.push({name: "wits_game", params: {"id": this.gameCode}});
    }
  }
}
</script>
