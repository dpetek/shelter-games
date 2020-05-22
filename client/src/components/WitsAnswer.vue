<template>
  <span @click="showBetting" class="card-container-span"  v-click-outside="hideBetting">
    <md-card class="answer-media-item md-elevation-4" v-bind:class="[{'winning-answer': answer.won}]" md-with-hover>
      <md-card-header class="md-elevation-1">
        <md-card-header-text>
          <div v-if="isSystemAnswer">
            <div class="md-title">LOWER</div>
            <div class="md-subhead">Smaller than the smallest guess.</div>
          </div>
          <div v-else-if="answer.answer" class="md-title">{{answer.answer}} </div>
          <div v-else class="md-title">???</div>
          <div v-if="answer.player" class="md-subhead">{{answer.player.name}}</div>
        </md-card-header-text>

        <md-card-media>
          <img v-if="answer.player" :src="answer.player.avatar" alt="People">
          <md-icon v-else class="md-size-3x fa fa-reddit-alien"></md-icon>
        </md-card-media>
      </md-card-header>

      <md-card-content  flex>
        <div v-if="board.phase == 2 && bettingDialogActive" class="betting-controls">
          <div class="md-caption">Set the bet amount for this answer:</div>
          <div class="md-layout md-alignment-top-center">
            <div class="md-layout-item md-size-20 md-alignment-top-right">
              <md-button v-on:click.stop="decBet()" class="md-icon-button"><md-icon class="fa fa-minus"></md-icon></md-button>
            </div>

            <div class="md-layout-item md-size-15">
              <span v-if="placingBet">
                <md-progress-spinner class="md-accent" :md-diameter="20" md-mode="indeterminate"></md-progress-spinner></span>
                <md-field v-else class="md-field-betting">
                  <md-input v-model="myBetAmount" class="my-bet-amount"></md-input>
                </md-field>
            </div>

            <div class="md-layout-item md-size-20">
              <md-button v-on:click.stop="incBet()" class="md-icon-button"><md-icon class="fa fa-plus"></md-icon></md-button>
            </div>
          </div>

          <md-button class="bet-button md-raised md-accent" v-on:click.stop="placeBet">Save</md-button>
          <div v-if="betError" class="md-error">{{betError}}</div>
        </div>

        <div v-if="board.phase >= 2 && !bettingDialogActive" class="bets-container">
          <div class="md-caption">Click on the card to place or adjust your bet.<span v-if="answer.bets">Answer bets:</span></div>
          <md-badge  v-for="bet in answer.bets" :key="bet.id" v-bind:class="[{'md-primary': board.phase == 2 || answer.won}]" :md-content="getBetString(bet)">
              <md-avatar class="md-primary md-elevation-4">
                <img v-if="bet.player" :src="bet.player.avatar">
                <md-tooltip>{{bet.player.name}}</md-tooltip>
            </md-avatar>
          </md-badge>
        </div>
        <!--
        <div v-if="board.phase == 2 && !bettingDialogActive" class="md-subheding">Click card to place your bet. </div>
        -->
      </md-card-content>

      <md-card-actions  md-alignment="right">
        <span v-if="board.phase==2" class="md-subheading">Payout {{answer.odds}}:1</span>
        <span v-else-if="board.phase==3 && answer.won == 1" class="md-caption">
            Winner! Closest without going over. 
            <span v-if="answer.player"> +1 coin for {{answer.player.name}}</span></span>
          <span v-else-if="board.phase==3 && answer.won == 2" class="md-caption">
            Winner! Exact guess!
            <span v-if="answer.player"> +2 coins for {{answer.player.name}}</span></span>
        <!--<md-button v-if="!bettingDialogActive" @click="toggleBetting(answer.id)" class="place-bet-button">
          Place Bet
        </md-button>
        <md-button v-else @click="placeBet(answer.id, betAmount[answer.id])">
          Save Bet
        </md-button>-->
      </md-card-actions>
    </md-card>
  </span>
</template>

<style scoped>
.answer-media-item {
  width: 300px;
  background-color: #dedede !important;
  border: 2px solid #26c6da;
  border-radius: 25px;
  color: black !important;
  display: inline-block
}

.betting-controls {
  height: 50px;
}

.md-field-betting  {
  margin: 0px !important;
}
.md-field-betting .md-input{
  -webkit-text-fill-color:#121212 !important;
  color:#121212 !important;
}

.winning-answer {
  border: 8px solid #f57f17 !important;
}
.answer-media-item .md-card-header{
  height: 100px;
  border-radius: 20px;
}
.answer-media-item .md-card-content{
  height: 130px;
  padding-top: 5px;
}
.answer-media-item .md-card-actions {
  height: 60px;
  padding-right: 15px;
}
.answer-media-item * {
  color: black !important;
}

.answer-media-item  {
  color: black !important;
}
#answer-input::placeholder {
  color: black !important;
}
#answer-input {
  -webkit-text-fill-color:#121212 !important;
  color:#121212 !important;
}
.bet-button {
  width: 220px;
}
.bets-container {
  min-height: 80px;
}
.card-container-span {
  margin: 10px 10px 0px 0px;
}
.md-avatar-icon {
  border: 3px solid #f57f17;
}
.md-answer-won {
  color: green !important;
}
.place-bet-button {
  font-size: 20px;
}
.md-error {
  color: red !important;
}
.my-green-back {
  background-color: #255d00 !important;
}
.my-bet-amount {
  font-size: 30px !important;
}
</style>

<script>
import ClickOutside from 'vue-click-outside';
import { mapGetters } from "vuex";

export default {
  name: "WitsAnswer",
  props: {
    answer: { type: Object, required: true },
    board: {type: Object, required: true},
    betAmount: {type: Array, required: true}
  },
  data() {
    return  {
      betError: null,
      isSystemAnswer: this.answer.answer <= -1000000,
      myBetAmount: this.betAmount[this.answer.id],
      bettingDialogActive: false,
      bgColor: '#eee',
      placingBet: false
    }
  },
  methods: {
    placeBet() {
    this.placingBet = true;
    this.betError = null;
    this.$store
      .dispatch("aPlaceBet", {"answer_id": this.answer.id, "amount": this.myBetAmount})
      .then(() => {
        this.bettingDialogActive = false;
        this.bgColor = '#eee';
        this.placingBet = false;
      })
      .catch(( error ) => {
        this.betError = error.message;
        this.placingBet = false;
      });
    },
    getBetString(bet) {
      if (this.board.phase == 2) {
        return bet.amount;
      }
      if (this.board.phase == 3) {
        if (this.answer.won) {
          return "+" + (bet.amount * (this.answer.odds - 1));
        } else {
          return "-" + bet.amount;
        }
      }
      return "";
    },
    trimPlayerName(name) {
      if (name.length > 8) {
        return name.substr(0, 6) + "...";
      }
      return name;
    },
    incBet() {
      this.myBetAmount ++;
    },
    decBet() {
      if (this.myBetAmount > 0) {
        this.myBetAmount --;
      }
    },
    showBetting() {
      if (this.board.phase != 2) {
        return;
      }
      this.bettingDialogActive = true;
    },
    hideBetting() {
      if (this.board.phase != 2) {
        return;
      }
      this.bettingDialogActive = false;
    }
  },
  directives: {
    ClickOutside
  },
  computed: {
    ...mapGetters(["currentGamePlayer"]),
  }
};

</script>
