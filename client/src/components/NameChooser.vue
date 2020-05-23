<template>
    <md-card>
      <md-card-header>
        <div class="md-title">Create profile for game "{{game.name}}"</div>
      </md-card-header>
      <md-card-content>

        <div>
          <form class="md-layout" v-on:submit.prevent="enterGame">
            <!--
            <div>
              <md-switch v-model="returning" class="md-primary">Returning into the game room? Check this if you already played in this game room and you want to resume your session.</md-switch>
            </div>
            -->
            <md-field>
              <md-input v-model="name" :placeholder="chooseNamePlaceholder()"></md-input>
            </md-field>
            <md-field>
              <md-input v-model="password" type="password" placeholder="Password (Optional)"></md-input>
            </md-field>
          </form>
          <div v-if="!returning" class="md-caption">Please don't use your real passwords.
            This is only used so you can return back into the game and nobody else steals your character.
          </div>
          <div v-if="enterError" class="md-error" style="color:red">{{enterError}}</div>
        </div>

        <div v-if="!returning">
        <div class="md-subheading choose-avatar">Choose your avatar:</div>
          <span v-for="n in 14" :key="n"
              @click="selectAvatar(n)" class="avatar-span">
            <md-avatar  class="md-large md-elevated-5"
              v-bind:class="[{'avatar-selected': selectedAvatar == n}]">
              <img :src="avatarPath(n)" alt="">
            </md-avatar>
          </span>
        </div>
      <div>

        <!-- <a href='https://dryicons.com/free-icons/animated-animals'> Icon by Dryicons </a>-->
      </div>
      </md-card-content>
      <md-card-actions>
        <md-button @click="enterGame" class="md-primary md-raised enter-game-button">Enter Game</md-button>
      </md-card-actions>
    </md-card>
</template>

<style scoped>

.avatar-span {
  margin: 5px;
}
.avatar-selected {
  border: 8px solid #7f0000;
}
.choose-avatar {
  margin-top: 20px;
}
.enter-game-button {
  width: 100vw;
}

</style>

<script>

export default {
  name: "NameChooser",
  props: {
    game: {type: Object, required: true}
  },
  data () {
    return {
      selectedAvatar: null,
      returning: false,
      enterError: null
    }
  },
  methods: {
    enterGame() {
      this.enterError = null;
      this.$store.dispatch("aEnterGame", {"id": this.game.code,
        "name": this.name, "password": this.password,
        "avatar": this.avatarPath(this.selectedAvatar),
        "returning": this.returning}).then(
          () => {
          }).catch((error) => {
            this.enterError = error.message;
          });


    },
    avatarPath(num) {
      if (num) {
        return 'static/avatars/a' + num + '.svg';
      }
      return null;
    },
    selectAvatar(num) {
      this.selectedAvatar = num;
    },
    chooseNamePlaceholder() {
      if (this.returning) {
        return "What was your name?";
      }
      return "Choose your name.";
    }
  },
};

</script>
