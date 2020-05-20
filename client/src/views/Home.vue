<template>
  <div>
    <GameCard name="Wits & Wagers"
              type="wits"
              thumbnail="/static/thumb/ww.jpg"
              description=""></GameCard>
    <GameCard name="Codenames"
              type="codenames"
              notFinished=true
              thumbnail="/static/thumb/cn.jpg"
              description=""></GameCard>
  </div>
</template>

<script>
import GameCard from "@/components/GameCard";

export default {
  name: "home",
  components: {
    GameCard
  },
}
</script>
