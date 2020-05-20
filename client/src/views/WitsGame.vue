<template>
  <div class="main-div">
    <div v-if="!isAuthenticated"> <NameChooser /> </div>
    <div v-else>
          <md-toolbar class="md-dense">
            <h3>Wits & Wagers: {{ game.name }} (Code: {{game.id}})</h3>
          </md-toolbar>

          <!-- STEPPER -->
          <md-steppers :md-active-step.sync="stepperActiveStep[board.phase]" class="md-stepper-wits-game" md-linear md-editable=false>
            <md-step id="phase-answer" md-label="Answer" md-editable=false :md-done.sync="board.phase>1" @click="advanceGame(1)"></md-step>
            <md-step id="phase-bet" md-label="Bet" md-editable=false :md-done.sync="board.phase>2" @click="advanceGame(2)"></md-step>
            <md-step id="phase-score" md-label="Score" md-editable=false  :md-done.sync="board.phase>3" @click="advanceGame(3)"></md-step>
          </md-steppers>
          <!-- /STEPPER -->

          <!-- QUESTION CARD -->
          <md-card class="md-card-green-background md-card-question md-elevation-6">
            <md-card-header>
              <md-card-header-text>
                <div class="md-title div-text-align-center">{{board.question.question}}</div>
                <div v-if="board.phase > 2" class="md-subheading div-text-align-center">Answer: {{board.question.answer}}</div>
                <div v-if="board.phase > 2 && board.question.notes" class="md-caption div-text-align-center">{{board.question.notes}}</div>
              </md-card-header-text>

              <md-card-media>
                <md-icon class="md-size-4x fa fa-question-circle"></md-icon>
              </md-card-media>
            </md-card-header>
          </md-card>
          <!-- /QUESTION CARD -->

          <!-- INPUT ANSWER -->
            <md-card v-if="myAnswer == undefined && board.phase == 1" class="md-card-question md-card-green-background">
              <md-card-content>
                <form v-if="board.phase == 1" v-on:submit.prevent="addAnswer(answer)">
                  <md-field v-bind:class="[{'md-invalid': !!answerError}]">
                    <md-input v-model="answer" placeholder="What's your answer?"></md-input>
                    <span class="md-error">{{answerError}}</span>
                  </md-field>
                </form>
              </md-card-content>
              <md-card-actions>
                <md-button @click="addAnswer(answer)">Submit</md-button>
              </md-card-actions>
            </md-card>
          <!-- /INPUT ANSWER -->
      
          <md-card class="md-card-question md-card-green-background" v-if="answers && answers.length>0">
            <md-subheader>Answers</md-subheader>
            <md-card-content>
              
              <div class="md-layout md-gutter">
                  <WitsAnswer v-for="answer in answers" :key="answer.id"
                    :answer="answer" :board="board" :betAmount="betAmount" />
              </div>

            </md-card-content>
          </md-card>
          <md-card class="md-card-question">
          <WitsLeaderboard :players="gamePlayers"></WitsLeaderboard>
        </md-card>
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
  .div-text-align-center{
    text-align: center;
  }
  .chip-user-bets {
    background-color: #b2dfdb;
    margin: 2px;
    color: black;
  }
  .md-card-question {
    margin: 10px 0px 0px 0px;
    color: #333;
  }
  .md-card-question .md-subheader {
    color: #333;
  }

  .md-card-green-background {
    background-color: #60ad5e;
    border-radius: 20px;
    border: 2px solid white;
    min-height:150px;
  }
  .md-card-green-background .md-title{
    color: white;
  }
  .md-card-green-background .md-subheading {
    color: white;
  }
</style>

<script>
import NameChooser from "@/components/NameChooser";
import WitsAnswer from "@/components/WitsAnswer";
import WitsLeaderboard from "@/components/WitsLeaderboard";
import store from "@/store";
import { mapGetters } from "vuex";

export default {

  data() {
    return {
      stepperActiveStep: {
        1: "phase-answer",
        2: "phase-bet",
        3: "phase-score",
      },
      boardAnswer: 0.0,
      answer: "",
      betError: null,
      answerError: null
    }
  },

  components: {
    NameChooser,
    WitsLeaderboard,
    WitsAnswer,
  },

  methods: {
    addAnswer(ans) {
      this.answerError = null;
      this.$store
        .dispatch("aAddAnswer", ans)
        .then(() => {
          this.answer = "";
        })
        .catch(( error ) => {
          console.log("Error: ", error.message);
          this.answerError = error.message;
        });
    },
    advanceGame(from_phase) {
      if (from_phase != this.board.phase) {
        return ;
      }
      this.$store.dispatch("aAdvanceGameBoard", this.boardAnswer);
      this.boardAnswer = 0.0;
      this.answer = "";
    },
    placeBet(answerId, amount) {
      this.betError = null;
      this.$store
        .dispatch("aPlaceBet", {"answer_id": answerId, "amount": amount})
        .then(() => {
          this.amount = 0;
        })
        .catch(( error ) => {
          this.betError = error.message;
        });
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
  computed: {
    ...mapGetters(["game","myAnswer", "board", "isAuthenticated", "answers", "gamePlayers", "currentUser"]),
    betAmount() {
      var that = this;
      var betAmounts = {};
      if (!that.answers) {
        return betAmounts;
      }
      that.answers.forEach(function(ans){
        betAmounts[ans.id] = 0;
        if ( ans.bets ) {
          ans.bets.forEach(function(bet) {
            if (bet.user.id == that.currentUser.id) {
              betAmounts[ans.id] = bet.amount;
            }
          });
        }
      });
      return betAmounts;
    }
  },
  directives: {
  },
};

</script>
