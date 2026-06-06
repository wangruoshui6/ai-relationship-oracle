<template>
  <div class="auth-screen">
    <section class="auth-card">
      <p class="auth-eyebrow">AI Relationship Oracle</p>
      <h1>情感关系顾问</h1>
      <p class="auth-copy">
        登录后进入咨询工作台。你可以先直接提问，也可以先录入双方资料做更完整的八字与关系分析。
      </p>

      <form class="auth-form" @submit.prevent="handleLogin">
        <label>
          <span>邮箱</span>
          <input v-model="email" type="email" placeholder="demo@example.com" />
        </label>
        <label>
          <span>密码</span>
          <input v-model="password" type="password" placeholder="password123" />
        </label>
        <div class="auth-actions">
          <button class="ghost-btn" type="button" @click="handleRegister">先注册</button>
          <button class="primary-btn" type="submit">登录</button>
        </div>
      </form>

      <div class="auth-status">
        <strong>状态</strong>
        <p>{{ statusText }}</p>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";

import { login, register } from "@/api/auth";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();
const router = useRouter();

const email = ref("demo@example.com");
const password = ref("password123");
const statusText = ref("请输入邮箱和密码。");

async function handleRegister() {
  const response = await register(email.value, password.value);
  statusText.value = response.data?.message === "ok" ? "注册成功，请继续登录。" : JSON.stringify(response.data);
}

async function handleLogin() {
  const response = await login(email.value, password.value);
  const token = response.data?.data?.access_token || "";
  if (token) {
    authStore.setToken(token);
    statusText.value = "登录成功，正在进入咨询工作台...";
    await router.push({ name: "workspace" });
  }
}
</script>
