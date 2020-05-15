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
  </div>
</template>

<script>

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
    }
  }
}

</script>
