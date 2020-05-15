<template>
  <div class="main-div">
    <div v-if="!isAuthenticated"> <NameChooser /> </div>
    <div v-else>
          <md-toolbar class="md-dense">
            <h3>Wits & Wagers: {{ game.name }}</h3>
          </md-toolbar>

          <!-- STEPPER -->
          <md-steppers :md-active-step.sync="stepperActiveStep[board.phase]" class="md-stepper-wits-game" md-linear md-editable=false>
            <md-step id="phase-answer" md-label="Answer" :md-done.sync="board.phase>1" @click="advanceGame(1)"></md-step>
            <md-step id="phase-bet" md-label="Bet" :md-done.sync="board.phase>2" @click="advanceGame(2)"></md-step>
            <md-step id="phase-score" md-label="Score"  :md-done.sync="board.phase>3" @click="advanceGame(3)"></md-step>
          </md-steppers>
          <!-- /STEPPER -->

          <!-- QUESTION CARD -->
          <md-card class="md-card-question md-card-green-background">
            <md-subheader>Question</md-subheader>
            <md-card-content>
              <h2 v-if="board.phase <= 2">{{board.question.question}}</h2>
              <h2 v-else>Answer is: {{board.question.answer}}</h2>
            </md-card-content>
          </md-card>
          <!-- /QUESTION CARD -->

          <!-- INPUT ANSWER -->
          <div v-if="!myAnswer" class="user-input-container">
            <md-card class="md-card-answer">
              <md-card-content>
                <form v-if="board.phase == 1"  myclass="md-layout" v-on:submit.prevent="addAnswer">
                  <md-field>
                    <md-input v-model="answer" placeholder="What's your answer?"></md-input>
                  </md-field>
                  <md-button type="submit" class="md-primary">Submit</md-button>
                </form>
              </md-card-content>
            </md-card>
          </div>
          <!-- /INPUT ANSWER -->
      
        <md-card class="md-card-question" v-if="answers && answers.length>0">
          <md-subheader>Answers</md-subheader>
          <span v-for="answer in answers" :key="answer.id" @click="toggleBetting(answer.id)">
            <md-card v-if="board.phase != 2 || activeForBetting != answer.id"
              v-bind:class="['md-card-answer', {'md-correct-answer': answer.won == 1}]"
              :md-with-hover="board.phase == 2">

              <md-card-header>
                <md-card-header-text>
                  <div class="md-title">{{answer.user.name}}</div>
                </md-card-header-text>
              </md-card-header>

              <md-card-content>
                <h3 v-if="board.phase >= 2"> {{answer.answer}}</h3>
                  <div v-if="board.phase >= 2">
                    <md-chip class="md-primary md-chip-bet-player" v-for="bet in answer.bets" :key="bet.id">
                      <md-badge :md-content="bet.amount">{{ bet.user.name }}</md-badge>
                    </md-chip>
                  </div>
              </md-card-content>
            </md-card>
            <md-card v-else v-bind:class="['md-card-answer', {'md-accent': answer.won == 1}]"
              @click="toggleBetting(answer.id)" md-with-hover>
              <md-card-header @click="hideBetting(answer.id)">
                <md-card-header-text>
                  <div class="md-title">{{answer.user.name}} ({{answer.answer}})</div>
                </md-card-header-text>
              </md-card-header>
              <md-card-content>
                <p v-if="betError">{{betError}}</p>
                <form myclass="md-layout" v-on:submit.prevent="placeBet(answer.id, bet_amount)">
                  <md-field>
                    <md-input v-model="bet_amount" type = "number" placeholder="Amount..."></md-input>
                  </md-field>
                  <md-button type="submit" class="md-primary">Save</md-button>
                </form>
              </md-card-content>
            </md-card>
          </span>
        </md-card>
        <WitsLeaderboard :players="gamePlayers"></WitsLeaderboard>
  </div>
  </div> <!-- main-div -->
</template>

<style lang="scss" scoped>
  .md-layout-item {
    height: 40px;

    &:after {
      width: 100%;
      height: 100%;
      display: block;
      background: md-get-palette-color(green, 200);
      content: " ";
    }
  }
  .md-card-answer {
    width: 280px;
    min-height: 80px;
    margin: 4px;
    display: inline-block;
    vertical-align: top;
  }
  .md-card-question {
    margin: 10px 0px 0px 0px;
  }
  .md-card-green-background {
    background-color: #e0f2f1
  }

  .md-correct-answer {
    background-color: #a5d6a7
  }
</style>

<script>
import NameChooser from "@/components/NameChooser";
import WitsLeaderboard from "@/components/WitsLeaderboard";
import store from "@/store";
import { mapGetters } from "vuex";

export default {

  data() {
    return {
      activeForBetting: null,
      stepperActiveStep: {
        1: "phase-answer",
        2: "phase-bet",
        3: "phase-score",
      },
      boardAnswer: 0.0,
      answer: "",
      betError: null
    }
  },

  components: {
    NameChooser,
    WitsLeaderboard
  },

  methods: {
    addAnswer() {
      this.$store.dispatch("aAddAnswer", this.answer);
    },
    advanceGame(from_phase) {
      if (from_phase != this.board.phase) {
        return ;
      }
      this.$store.dispatch("aAdvanceGameBoard", this.boardAnswer);
      this.boardAnswer = 0.0;
      this.answer = "";
      this.activeForBetting = null;
    },
    placeBet(answerId, amount) {
      try {
      this.$store.dispatch("aPlaceBet", {"answer_id": answerId, "amount": amount});
      this.pingBoardUpdate();
      } catch (error) {
        this.betError = error;
        return;
      }
      this.activeForBetting = null;
      this.amount = 0;
    },
    toggleBetting(id) {
      if (this.activeForBetting == id) {
        return;
      } else {
        this.activeForBetting = id;
      }
    },
    hideBetting(id) {
      if (this.activeForBetting == id) {
        this.activeForBetting = null;
      }
    },
    pingBoardUpdate() {
      this.$socket.send({"answers": true})
    }
  },

  beforeRouteEnter(to, from, next) {
    Promise.all([
      store.dispatch("aFetchGame",  to.params.id)
    ]).then(() => {
      next();
    });
  },
  watch: {
  },

  computed: {
    ...mapGetters(["game", "board", "isAuthenticated", "myAnswer", "answers", "gamePlayers"])
  },
  directives: {
  },
};

</script>
