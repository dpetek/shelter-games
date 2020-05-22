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
      name: "wits_index",
      path: "/wits",
      component: () => import("@/views/Wits"),
      props: true
    },
    {
      name: "wits_game",
      path: "/wits/game/:id",
      component: () => import("@/views/WitsGame"),
      props: true
    },
    {
        name: "question_editor",
        path: "/wits/question_editor",
        component: () => import("@/views/WitsAddQuestion"),
        props: true
    },
    {
        name: "question_editor_add",
        path: "/wits/question_editor/edit/:id",
        component: () => import("@/views/WitsAddQuestion"),
        props: true
    },
    {
      name: "codenames_index",
      path: "/codenames",
      props: true,
      component: () => import("@/views/Codenames")
    },
    {
      name: "codenames_game",
      path: "/codenames/:id",
      props: true,
      component: () => import("@/views/CodenamesGame")
    }
  ]
});
