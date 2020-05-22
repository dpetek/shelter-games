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
        currentUser: null,
        currentGamePlayer: null,
        gamePlayers: [],
        myAnswer: null,
        questions: []
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
        gamePlayers(state) {
            return state.gamePlayers;
        },
        myAnswer(state) {
            return state.myAnswer;
        },
        currentGamePlayer(state) {
            return state.currentGamePlayer;
        },
        questions(state) {
            console.log("Returning from getter: " + state.questions);
            return state.questions;
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
            state.myAnswer = null;
            state.answers = answers;
            state.answers.forEach(function(ans){
            if (!ans.player || !state.currentGamePlayer) {
                return;
            }
            if (ans.player.id == state.currentGamePlayer.id) {
                state.myAnswer = ans;
            }});
        },

        mSetCurrentUser(state, user) {
            if (user && user.id) {
                state.isAuthenticated = true;
                state.currentUser = user;
            } else {
                state.isAuthenticated = false;
            }
        },
        mSetCurrentGamePlayer(state, player) {
            state.currentGamePlayer = player;
        },
        mSetGamePlayers(state, players) {
            state.gamePlayers = players;
        },
        mSetQuestions(state, questions) {
            console.log("Setting state question to: ", questions);
            state.questions = questions;
        },
        SOCKET_CONNECT(state) {
            state.isConnected = true;
        },
        SOCKET_DISCONNECT(state) {
            state.isConnected = false;
        }
    },
    actions: {
        async aFetchCurrentUser(context) {
            const { data } = await AuthService.currentUser();
            if (data.error) {
                context.commit("mSetCurrentUser", null);
            }else {
                context.commit("mSetCurrentUser", data.user);
            }
        },
        async aLogin(context, name) {
            const { data } = await AuthService.login(name);
            if (data.error) throw new Error(data.error);

            context.commit("mSetCurrentUser", data.user);
        },
        async aLogout(context) {
            const { data } = await AuthService.logout();
            if (data.error) throw new Error(data.error);

            context.commit("mSetCurrentUser", null);
        },
        async aFetchCurrentGamePlayer(context, id) {
            const { data } = await WitsService.getCurrentGamePlayer(id);
            if (data.error) {
                context.commit("mSetCurrentGamePlayer", null);
            }else {
                context.commit("mSetCurrentGamePlayer", data.player);
            }
        },
        async aEnterGame(context, payload) {
            const { data } = await WitsService.enter(payload["id"], payload);
            if (data.error) throw new Error(data.error);
            context.commit("mSetCurrentGamePlayer", data.player)
        },
        async aFetchGames(context) {
            const { data } = await WitsService.list();
            if (data.error) throw new Error(data.error);
            
            context.commit("mSetGames", data.games)
        },
        async aCreateGame(context, name) {
            const { data } = await WitsService.create(name);
            if (data.error) throw new Error(data.error);

            var all_games = context.state.games
            all_games.push(data.game)
            context.commit("mSetGames", all_games);
        },
        async aFetchGame(context, id) {
            const { data } = await WitsService.get(id);
            if (data.error) {
                throw new Error(data.error);
            }
            context.commit("mSetGame", data.game);
            context.commit("mSetBoard", data.board);
            const result  = await WitsService.getBoardAnswers(data.board.id);
            if (data.error) {
                throw new Error(data.error);
            }
            context.commit("mSetAnswers", result.data.answers);

            const pl = await WitsService.getGamePlayers(id);
            if (data.error) {
                throw new Error(data.error);
            }
            context.commit("mSetGamePlayers", pl.data.players);
        },
        async aAddAnswer(context, answer) {
            const { data } = await WitsService.addAnswer(context.state.board.id, answer);
            if (data.error) throw new Error(data.error);
            context.dispatch("aFetchAnswers");
        },
        async aFetchAnswers(context) {
            const { data } = await WitsService.getBoardAnswers(context.state.board.id);
            if (data.error) {
                throw new Error(data.error);
            }
            context.commit("mSetAnswers", data.answers);
        },
        async aAdvanceGameBoard(context, answer = 0.0) {
            const { data } = await WitsService.advanceBoard(context.state.board.id, context.state.board.phase, answer);
            if (data.error) throw new Error(data.error);

            context.dispatch("aFetchGame", context.state.game.id);
        },
        async aAddQuestion(context, payload) {
            const { data } = await WitsService.addQuestion(payload);
            if (data.error) throw new Error(data.error);
        },
        async aGetQuestions(context) {
            const { data } = await WitsService.getQuestions();
            if (data.error) throw new Error(data.error);
            console.log("Data received: ", data);
            context.commit("mSetQuestions", data.questions);
        },
        async aPlaceBet(context, payload) {
            const { data } = await WitsService.placeBet(payload["answer_id"], payload);
            if (data.error) {
                throw new Error(data.error);
            }
            context.dispatch("aFetchGame", context.state.game.id);
        },
        async aFetchPlayers(context, game_id) {
            const { data } = await WitsService.getGamePlayers(game_id);
            if (data.error) {
                throw new Error(data.error);
            }
            context.commit("mSetGamePlayers", data.players);
        },
        SOCKET_wits(context, message) {
            console.log("Received socket message: ", message);
            if (message.update) {
                message.update.forEach(function(update_str){
                    switch (update_str) {
                        case "answers":
                            context.dispatch("aFetchAnswers");
                            break;
                        case "leaderboard":
                            context.dispatch("aFetchPlayers", context.state.game.id);
                            break;
                        case "game":
                            context.dispatch("aFetchGame", context.state.game.id);
                            break;
                        default:
                            break;
                    }
                });
            }
        }
    },
});
