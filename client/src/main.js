import ApiService from "./common/api.service";
import App from './App.vue'
import Vue from 'vue'
import router from "./router";
import store from "./store";
import vueNumeralFilterInstaller from 'vue-numeral-filter';

import VueMaterial from 'vue-material'
import 'vue-material/dist/vue-material.min.css'
import 'vue-material/dist/theme/default.css'

Vue.use(VueMaterial)

Vue.config.productionTip = false;

ApiService.init();

Vue.use(vueNumeralFilterInstaller, { locale: 'en-gb' });

new Vue({
  store,
  router,
  render: h => h(App),
}).$mount('#app')
