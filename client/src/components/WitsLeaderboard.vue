<template>
  <md-table>
    <md-table-toolbar>
      <h1 class="md-title">Leaderboard</h1>
    </md-table-toolbar>

    <md-table-row>
      <md-table-head></md-table-head>
      <md-table-head>Name</md-table-head>
      <md-table-head>Wins</md-table-head>
      <md-table-head>Coins</md-table-head>
    </md-table-row>

    <md-table-row v-for="player in players" :key="player.id">
      <md-table-cell>
        <md-avatar class="md-avatar-icon md-primary">
          <img :src="player.avatar">
      </md-avatar>
    </md-table-cell>
      <md-table-cell>{{player.name}}</md-table-cell>
      <md-table-cell>{{player.num_wins}}</md-table-cell>
      <md-table-cell>{{player.coins}}</md-table-cell>
    </md-table-row>
  </md-table>
</template>
<style>

</style>

<script>
export default {
  name: "WitsLeaderboard",
  props: {
    players: { type: Array, required: true }
  },
  data() {
    return {}
  },
  computed: {
  }
};

</script>
