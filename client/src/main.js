import App from './App.vue'
import Vue from 'vue'
import router from "./router";
import store from "./store";
import ApiService from "./common/api.service";

import VueMaterial from 'vue-material'
import 'vue-material/dist/vue-material.min.css'
import 'vue-material/dist/theme/default.css'

Vue.use(VueMaterial)

Vue.config.productionTip = false;

ApiService.init();

router.beforeEach((to, from, next) =>
  Promise.all([store.dispatch("aFetchCurrentUser")]).then(next)
);

new Vue({
  store,
  router,
  render: h => h(App),
}).$mount('#app')
