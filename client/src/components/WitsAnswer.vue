<template>
  <span @click="showBetting" v-click-outside="hideBetting">
    <md-card class="answer-media-item md-elevation-4" v-bind:style="{color: bgColor}">
      <md-card-header>
        <md-card-header-text>
          <div v-if="isSystemAnswer">
            <div class="md-title">SMALLER</div>
            <div class="md-subheading">than the smallest guess</div>
          </div>
          <div v-else-if="answer.answer" class="md-title">Answer: {{answer.answer}}
            <span v-if="answer.won"><md-icon class="md-size fa fa-check-circle md-answer-won"></md-icon></span>
          </div>
          <div v-else class="md-title">?</div>
          <div v-if="answer.user" class="md-subhead">{{answer.user.name}}</div>
        </md-card-header-text>

        <md-card-media>
          <img src="static/thumb/anonymous.png" alt="People">
        </md-card-media>
      </md-card-header>

      <md-card-content>
        <!--
        <div v-if="board.phase == 2 && bettingDialogActive">
          <form myclass="md-layout" v-on:submit.prevent="placeBet(answer.id, betAmount[answer.id])">
            <md-field v-bind:class="['place-bet-field', {'md-invalid': !!betError}]">
              <md-input class="md-primary" v-on:click.stop v-model="betAmount[answer.id]" placeholder="How much?" type="number"></md-input>
              <span class="md-helper-text">Current bet: {{betAmount[answer.id]}}</span>
              <span class="md-error">{{betError}}</span>
            </md-field>
          </form>
        </div>
        -->

        <div v-if="board.phase == 2 && bettingDialogActive">

          <div class="md-layout md-gutter md-alignment-top-center">
            <div class="md-layout-item md-size-35">
              <md-button v-on:click.stop="decBet()"><md-icon class="fa fa-minus"></md-icon></md-button>
            </div>

            <div class="md-layout-item md-size-30">
              <span v-if="placingBet">
                <md-progress-spinner class="md-accent" :md-diameter="20" md-mode="indeterminate"></md-progress-spinner></span>
              <span v-else class="md-display-1">{{myBetAmount}}</span>
            </div>

            <div class="md-layout-item md-size-35">
              <md-button v-on:click.stop="incBet()"><md-icon class="fa fa-plus"></md-icon></md-button>
            </div>
          </div>

          <md-button class="bet-button md-raised md-accent" v-on:click.stop="placeBet">Bet</md-button>
          <span v-if="betError" class="md-error">{{betError}}</span>
        </div>

        <div v-if="board.phase>=2 && !bettingDialogActive">
          <md-badge  v-for="bet in answer.bets" :key="bet.id"  :md-content="bet.amount">
              <md-avatar class="md-avatar-icon">
                <img src="static/thumb/anonymous.png">
            </md-avatar>
          </md-badge>
        </div>
      </md-card-content>

      <md-card-actions v-if="board.phase==2" md-alignment="right">
        <span class="md-caption">Payout {{answer.odds}}:1 | </span>
        <span class="md-caption">Click card to place your bet. </span>
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
  width: 280px;
  min-height: 260px;
  margin: 5px 5px 10px 5px;
  background-color: #fff !important;
  border: 2px solid #26c6da;
  border-radius: 25px;
  color: black !important;
  display: inline-block
}
.answer-media-item .md-card-content{
  height: 120px;
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
.md-answer-won {
  color: green !important;
}
.place-bet-button {
  font-size: 20px;
}
.md-error {
  color: red !important;
}
</style>

<script>
import ClickOutside from 'vue-click-outside';

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
    incBet() {
      this.myBetAmount ++;
    },
    decBet() {
      if (this.myBetAmount > 0) {
        this.myBetAmount --;
      }
    },
    showBetting() {
      this.bettingDialogActive = true;
      this.bgColor = '#bbb';
    },
    hideBetting() {
      this.bettingDialogActive = false;
      this.bgColor = '#eee';
    }
  },
  directives: {
    ClickOutside
  }
};

</script>
