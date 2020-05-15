import Vue from "vue";
import Vuex from "vuex";
import {
  AuthService,
  WitsService
} from "@/common/api.service";

Vue.use(Vuex);

export default new Vuex.Store({
    state: {
        games: [],
        game: {},
        board: {},
        answers: [],
        isAuthenticated: false,
        currentUser: {},
        myAnswer: null,
        gamePlayers: []
    },
    getters: {
        games (state) {
            return state.games;
        },
        game (state) {
            return state.game;
        },
        board (state) {
            return state.board;
        },
        answers(state) {
            return state.answers;
        },
        isAuthenticated(state) {
            return state.isAuthenticated;
        },
        currentUser(state) {
            return state.currentUser;
        },
        myAnswer(state) {
            return state.myAnswer;
        },
        gamePlayers(state) {
            console.log("Returning game players: " + state.gamePlayers);
            return state.gamePlayers;
        }
    },
    mutations: {
        mSetGames(state, games) {
            state.games = games;
        },
        mSetGame(state, game) {
            state.game = game;
        },
        mSetBoard(state, board) {
            state.board = board;
        },
        mSetAnswers(state, answers) {
            state.answers = answers;
            state.myAnswer = null;
            state.answers.forEach(function(ans){
                if (ans.user.id == state.currentUser.id) {
                    state.myAnswer = ans;
                }
            });
        },

        mSetCurrentUser(state, user) {
            if (user && user.id) {
                state.isAuthenticated = true;
                state.currentUser = user;
            } else {
                state.isAuthenticated = false;
            }
        },
        mSetGamePlayers(state, players) {
            console.log("Storing game players: " + players);
            state.gamePlayers = players;
        }
    },
    actions: {
        async aFetchCurrentUser(context) {
            const { data } = await AuthService.currentUser();
            context.commit("mSetCurrentUser", data.user);
        },
        async aLogin(context, name) {
            const { data } = await AuthService.login(name);
            context.commit("mSetCurrentUser", data.user);
        },
        async aFetchGames(context) {
            const { data } = await WitsService.list();
            context.commit("mSetGames", data.games)
        },
        async aCreateGame(context, name) {
            const { data } = await WitsService.create(name);
            var all_games = context.state.games
            all_games.push(data.game)
            context.commit("mSetGames", all_games);
        },
        async aFetchGame(context, id) {
            const { data } = await WitsService.get(id);
            context.commit("mSetGame", data.game);
            context.commit("mSetBoard", data.board);
            const result  = await WitsService.getBoardAnswers(data.board.id);
            context.commit("mSetAnswers", result.data.answers);

            const pl = await WitsService.getGamePlayers(id);
            context.commit("mSetGamePlayers", pl.data.players);
        },
        async aAddAnswer(context, answer) {
            await WitsService.addAnswer(context.state.board.id, answer);
            context.dispatch("aFetchAnswers");
        },
        async aFetchAnswers(context) {
            const { data } = await WitsService.getBoardAnswers(context.state.board.id);
            context.commit("mSetAnswers", data.answers);
        },
        async aAdvanceGameBoard(context, answer = 0.0) {
            await WitsService.advanceBoard(context.state.board.id, context.state.board.phase, answer);
            context.dispatch("aFetchGame", context.state.game.id);
        },
        async aAddQuestion(context, payload) {
            await WitsService.addQuestion(payload);
        },
        async aPlaceBet(context, payload) {
            await WitsService.placeBet(payload["answer_id"], payload);
            context.dispatch("aFetchGame", context.state.game.id);
        },
        async aFetchPlayers(context, game_id) {
            const { data } = await WitsService.getGamePlayers(game_id);
            context.commit("mSetGamePlayers", data.players);
        }
    },
});
