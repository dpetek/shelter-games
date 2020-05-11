import Vue from "vue";
import Router from "vue-router";

Vue.use(Router);

export default new Router({
  routes: [
    {
      name: "Home",
      path: "/",
      component: () => import("@/views/Home"),
    },
    {
      name: "login",
      path: "/login",
      component: () => import("@/views/Login")
    },
    {
      name: "wits",
      path: "/wits/:slug",
      component: () => import("@/views/Wits"),
      props: true
    },
    {
      name: "codenames",
      path: "/codenames/:slug",
      props: true,
      component: () => import("@/views/Codenames")
    }
  ]
});
