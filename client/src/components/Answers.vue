<template>
  <div>
    <md-content v-for="answer in answers" :key="answer.id">{{answer.user.name}}</md-content>
  </div>
</template>

<style lang="scss" scoped>
  .md-content {
    width: 200px;
    height: 200px;
    display: inline-flex;
    justify-content: center;
    align-items: center;
  }
</style>

<script>
import { mapGetters } from "vuex";
import store from "@/store";

export default {
  name: "Answers",
  props: {
    boardId: { type: String, required: true }
  },
  beforeRouteEnter(to, from, next) {
    Promise.all([
      store.dispatch("aFetchAnswers")
    ]).then(() => {
      next();
    });
  },
  ...mapGetters(["board", "myAnswer", "answers"]) 
}
</script>
