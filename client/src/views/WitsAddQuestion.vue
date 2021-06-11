<template>
    <div>
      <form v-on:submit.prevent="addQuestion()">
        <md-field>
          <label>Question</label>
          <md-textarea v-model="question" md-autogrow></md-textarea>
        </md-field>

        <md-field>
          <label>Answer</label>
          <md-input v-model="answer" type="number" step="0.01" md-autogrow></md-input>
        </md-field>

        <md-field>
          <label>Notes</label>
          <md-textarea v-model="notes" md-autogrow></md-textarea>
        </md-field>

        <md-field>
          <label for="category">Category</label>
          <md-select v-model="category" name="category" id="category">
            <md-option value="general-knowledge">General Knowledge</md-option>
            <md-option value="sports">Sports</md-option>
            <md-option value="history">History</md-option>
            <md-option value="science">Science</md-option>
          </md-select>
        </md-field>

        <md-button type="submit" class="md-primary">Create Question</md-button>
      </form>
      <md-table>
        <md-table-toolbar>
          <h1 class="md-title">Questions</h1>
        </md-table-toolbar>

        <md-table-row>
          <md-table-head>Id</md-table-head>
          <md-table-head>Category</md-table-head>
          <md-table-head>Question</md-table-head>
          <md-table-head>Notes</md-table-head>
          <md-table-head>Answer</md-table-head>
          <md-table-head>Actions</md-table-head>
        </md-table-row>

        <md-table-row v-for="question in questions" :key="question.id">
          <md-table-cell>{{question.id}} </md-table-cell>
          <md-table-cell>{{question.category}} </md-table-cell>
          <md-table-cell>{{question.question}}</md-table-cell>
          <md-table-cell>{{question.notes}}</md-table-cell>
          <md-table-cell>{{question.answer}}</md-table-cell>
          <md-table-cell><md-button @click="deleteQuestion(question.id)">Delte</md-button>
        </md-table-row>
      </md-table>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import store from "@/store";

export default {
  name: "wits-question-editor",

  data() {
    return {
      question: null,
      answer: null,
      notes: null,
      category: null,
    }
  },
  methods: {
    addQuestion() {
      this.$store.dispatch("aAddQuestion", {"question": this.question,
        "answer": this.answer,
        "notes": this.notes, "category": this.category});
      this.question = null;
      this.answer = null;
      this.notes = null;
      this.category = null;
    },
    deleteQuestion(id) {
      this.$store.dispatch("aDeleteQuestion", id);
    }
  },
  beforeRouteEnter(to, from, next) {
    Promise.all([
      store.dispatch("aGetQuestions")
    ]).then(() => {
      next();
    });
  },
  computed: {
    ...mapGetters(["questions"]),
  }
}

</script>
