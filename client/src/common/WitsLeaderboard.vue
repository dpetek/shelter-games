<template>
  <md-table md-card>

    <md-table-row v-for="player in players">
      <md-table-cell>{{player.user.name}}</md-table-cell>
      <md-table-cell>{{player.num_wins}}</md-table-cell>
      <md-table-cell>{{player.coins}}</md-table-cell>
    </md-table-row>

  </md-table>
</template>

<script>
export default {
  name: "WitsLeaderboard",
  props {
    players: { type: Array, required: true }
  },
  data() {
    return {}
  },
  computed: {
  }
};

</script>
