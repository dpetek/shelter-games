<template>
  <div class="main-div">
    <div v-if="currentGamePlayer == undefined"> <NameChooser :game="game" /> </div>
    <div v-else>
            <md-toolbar md-elevation="4">
              <div class="md-toolbar-row">
                <h3 class="md-title" style="flex: 1">Wits & Wagers: {{game.name}}</h3>
                <h3 class="md-subheading" style="flex: 1">Code: {{game.id}}</h3>
                <md-button v-if="!gameAdvancing" class="md-fab md-raised md-primary" @click="advanceGame(board.phase)">
                  <md-icon v-if="board.phase != 3" class="fa fa-play"></md-icon>
                  <md-icon v-else class="fa fa-forward"></md-icon>
                </md-button>
                <span v-else>
                  <md-progress-spinner class="md-accent" :md-diameter="20" md-mode="indeterminate"></md-progress-spinner>
                </span>               
              </div>
            </md-toolbar>

          <!-- QUESTION CARD -->
          <md-card class="md-card-white-background md-card-question md-elevation-6">
            <md-card-header>
              <md-card-header-text>
                <div v-if="board.phase <= 2" class="md-title div-text-align-center">{{board.question.question}}</div>
                <div v-if="board.phase > 2" class="md-title div-text-align-center">{{board.question.answer}}</div>
                <div v-if="board.phase > 2 && board.question.notes" class="md-caption div-text-align-center">
                  {{board.question.notes}}</div>
                <div v-if="board.phase > 2" class="md-caption div-text-align-center">Question: {{board.question.question}}</div>
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
                <form v-if="board.phase == 1 && !answerSubmitting" v-on:submit.prevent="addAnswer(answer)">
                  <md-field v-bind:class="[{'md-invalid': !!answerError}]">
                    <md-input v-model="answer" placeholder="What's your answer?"></md-input>
                    <span class="md-error">{{answerError}}</span>
                  </md-field>
                </form>
                <span v-else-if="board.phase == 1 && answerSubmitting">
                <md-progress-spinner class="md-accent" :md-diameter="20" md-mode="indeterminate"></md-progress-spinner></span>
              </md-card-content>
              <md-card-actions>
                <md-button @click="addAnswer(answer)">Submit</md-button>
              </md-card-actions>
            </md-card>
          <!-- /INPUT ANSWER -->
      
          <md-card class="md-card-question md-card-green-background" v-if="answers && answers.length>0">
            <md-card-header>
              <div class="md-title">Answers</div>
              <div v-if="board.phase == 2" class="md-subhead">Click to bet on answers.</div>
              <div v-else-if="board.phase == 3" class="md-subhead">Check your winnings/losses.</div>
            </md-card-header>
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
  .md-card-question .md-title {
    color: #121212 !important;
  }
  .md-card-question .md-subhead {
    color: #232323 !important;
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

  .md-card-white-background {
    background-color: #eceff1;
    border-radius: 20px;
    border: 2px solid black;
    min-height:150px;
  }
  .md-card-white-background .md-title{
    color: #000000;
  }
  .md-card-white-background .md-subheading {
    color: #000000;
  }
  .md-card-white-background .md-caption {
    color: #343434;
  }
  .md-card-white-background .md-card-media .md-icon {
    color: #000000 !important;
  }

  .md-toolbar {
    border-radius: 10px;
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
      answerError: null,
      answerSubmitting: false,
      gameAdvancing: false
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
      this.answerSubmitting = true;
      this.$store
        .dispatch("aAddAnswer", ans)
        .then(() => {
          this.answer = "";
          this.answerSubmitting = false;
        })
        .catch(( error ) => {
          console.log("Error: ", error.message);
          this.answerError = error.message;
          this.answer = "";
          this.answerSubmitting = false;
        });
    },
    advanceGame(from_phase) {
      if (from_phase != this.board.phase) {
        return ;
      }
      this.gameAdvancing = true;
      this.$store.dispatch("aAdvanceGameBoard", this.boardAnswer).then(() =>{
        this.gameAdvancing = false;
      }).catch(() => {
          this.gameAdvancing = false;
      });
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
      store.dispatch("aFetchCurrentGamePlayer", to.params.id),
      store.dispatch("aFetchGame",  to.params.id)
    ]).then(() => {
      next();
    });
  },
  computed: {
    ...mapGetters(["game","myAnswer", "board", "isAuthenticated", "answers", "gamePlayers", "currentGamePlayer"]),
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
            if (bet.player.id == that.currentGamePlayer.id) {
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
