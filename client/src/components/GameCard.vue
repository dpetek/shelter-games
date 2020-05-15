<template>
<md-card class="game-card">
  <md-card-media-cover md-solid>
    <md-card-media md-ratio="16:9">
      <img :src="thubmnail" :alt="name">
    </md-card-media>

    <md-card-area>
      <md-card-header>
        <span class="md-title">{{name}}</span>
        <span class="md-subhead">{{description}}</span>
      </md-card-header>

      <md-card-actions>
        <md-button>Join</md-button>
        <md-button>Create</md-button>
      </md-card-actions>
    </md-card-area>
  </md-card-media-cover>
</md-card>
</template>

<style>
.game-card {
  width: 300px;
  margin: 25px;
  display: inline-block;
}

</style>

<script>

export default {
  name: "GameCard",
  props: {
    name: { type: String, required: true },
    thumbnail: { type: String, required: true },
    description: { type: String, required: false}
  },
  data() {
    return {
      cardState: 0
    }
  }
}
</script>
