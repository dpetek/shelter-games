<template>
  <div>
    <md-table md-card>
      <md-table-head>Name</md-table-head>
      <md-table-head>Wins</md-table-head>
      <md-table-head>Coins</md-table-head>

      <md-table-row v-for="player in players" :key="player.id">
        <md-table-cell>{{player.user.name}}</md-table-cell>
        <md-table-cell>{{player.num_wins}}</md-table-cell>
        <md-table-cell>{{player.coins}}</md-table-cell>
      </md-table-row>

    </md-table>
  </div>
</template>

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
