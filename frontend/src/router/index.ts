import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";

import LoginView from "@/views/LoginView.vue";
import WorkspaceView from "@/views/WorkspaceView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "login", component: LoginView, meta: { public: true } },
    { path: "/workspace", name: "workspace", component: WorkspaceView },
    { path: "/structured-analysis", redirect: { name: "workspace" } },
    { path: "/quick-consult", redirect: { name: "workspace" } },
  ],
});

router.beforeEach((to) => {
  const authStore = useAuthStore();
  const isPublic = Boolean(to.meta.public);
  if (!isPublic && !authStore.token) {
    return { name: "login" };
  }
  if (to.name === "login" && authStore.token) {
    return { name: "workspace" };
  }
  return true;
});

export default router;
