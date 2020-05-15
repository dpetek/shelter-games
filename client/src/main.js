import App from './App.vue'
import Vue from 'vue'
import router from "./router";
import store from "./store";
import ApiService from "./common/api.service";
import VueSocketIO from 'vue-socket.io'
import SocketIO from "socket.io-client"

import VueMaterial from 'vue-material'
import 'vue-material/dist/vue-material.min.css'
import 'vue-material/dist/theme/default.css'

Vue.use(VueMaterial)

Vue.config.productionTip = false;

ApiService.init();

router.beforeEach((to, from, next) =>
  Promise.all([store.dispatch("aFetchCurrentUser")]).then(next)
);

const options = {};
Vue.use(new VueSocketIO({
    debug: true,
    connection: SocketIO('ws://localhost:5000', options),
    vuex: {
      store,
      actionPrefix: "SOCKET_",
      mutationPrefix: "SOCKET_"
    }
  })
);

new Vue({
  store,
  router,
  render: h => h(App),
}).$mount('#app')
