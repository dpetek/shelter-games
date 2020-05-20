import Vue from "vue";
import axios from "axios";
import VueAxios from "vue-axios";
import { API_URL } from "@/common/config";

const ApiService = {
  init() {
    Vue.use(VueAxios, axios);
    Vue.axios.defaults.baseURL = API_URL;
  },

  query(resource, params) {
    return Vue.axios.get(resource, params).catch(error => {
      throw new Error(`ApiService Query Error: ${error}`);
    });
  },

  get(resource) {
    return Vue.axios.get(`${resource}`).catch(error => {
      throw new Error(`ApiService Get Error: ${error}`);
    });
  },

  getById(resource, id = "") {
     return Vue.axios.get(`${resource}/${id}`).catch(error => {
      throw new Error(`ApiService Get Error: ${error}`);
    }); 
  },

  post(resource, params) {
    return Vue.axios.post(`${resource}`, params);
  },

  update(resource, id, params) {
    return Vue.axios.put(`${resource}/${id}`, params);
  },

  put(resource, params) {
    return Vue.axios.put(`${resource}`, params);
  },

  delete(resource) {
    return Vue.axios.delete(resource).catch(error => {
      throw new Error(`ApiService Delete Error ${error}`);
    });
  }
};

export default ApiService;

export const AuthService = {
  currentUser() {
      return ApiService.get("/api/current_user");
  },
  login(name) {
      return ApiService.post("/api/login", {"username": name});
  },
  logout() {
      return ApiService.post("/api/logout");
  }
};

export const WitsService = {
  list() {
    return ApiService.get("/api/wits/games");
  },

  create(name) {
    return ApiService.post("/api/wits/create", {"name": name});
  },

  get(id) {
    return ApiService.getById("/api/wits/game", id);
  },

  getBoardAnswers(board_id) {
    return ApiService.get("/api/wits/game/board/" + board_id + "/answers");
  },

  addAnswer(board_id, answer) {
    return ApiService.post("/api/wits/game/board/" + board_id + "/answer", {"answer": answer});
  },
  getGamePlayers(game_id) {
    return ApiService.get("/api/wits/game/" + game_id + "/players");
  },
  addQuestion(payload) {
    return ApiService.post("/api/wits/add_question", payload)
  },
  advanceBoard(board_id, from_phase, answer) {
    return ApiService.post("/api/wits/game/board/" + board_id + "/advance",
        {"from_phase": from_phase, "answer_value": answer});
  },
  placeBet(answer_id, payload) {
    return ApiService.post("/api/wits/game/answer/" + answer_id + "/bet", payload);
  }
};
