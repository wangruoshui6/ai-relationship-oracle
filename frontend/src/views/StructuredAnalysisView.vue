<template>
  <section class="workspace-card">
    <div class="hero-center">
      <div class="hero-badge">双人模式</div>
      <h2>结构化资料分析</h2>
      <p>先录入双方资料，再流式返回情感分析结果。</p>
    </div>

    <div class="compact-summary">
      <button class="summary-pill" type="button" @click="showEditor = !showEditor">
        <span>{{ summaryText }}</span>
        <span>{{ showEditor ? "收起" : "编辑" }}</span>
      </button>
    </div>

    <section v-if="showEditor" class="editor-card">
      <div class="editor-grid">
        <section class="editor-section">
          <h3>我的资料</h3>
          <div class="grid two">
            <label><span>性别</span><select v-model="form.user_profile.gender"><option value="male">男</option><option value="female">女</option><option value="other">其他</option><option value="unknown">未知</option></select></label>
            <label><span>历法</span><select v-model="form.user_profile.calendar_type"><option value="solar">公历</option><option value="lunar">农历</option></select></label>
            <label><span>出生日期</span><input v-model="form.user_profile.birth_date" type="date" /></label>
            <label><span>出生时间</span><input v-model="form.user_profile.birth_time" type="time" step="60" /></label>
            <label v-if="form.user_profile.calendar_type === 'lunar'"><span>是否闰月</span><select v-model="form.user_profile.is_leap_month"><option :value="false">否</option><option :value="true">是</option></select></label>
            <label><span>城市</span><input v-model="form.user_profile.birth_city" type="text" /></label>
            <label><span>国家</span><input v-model="form.user_profile.birth_country" type="text" /></label>
          </div>
        </section>

        <section class="editor-section">
          <h3>对方资料</h3>
          <div class="grid two">
            <label><span>昵称</span><input v-model="form.partner_profile.nickname" type="text" /></label>
            <label><span>关系</span><select v-model="form.partner_profile.relationship_type"><option value="unknown">未知</option><option value="ex">前任</option><option value="current">现任</option><option value="crush">暧昧对象</option><option value="spouse">配偶</option><option value="friend">朋友</option></select></label>
            <label><span>性别</span><select v-model="form.partner_profile.gender"><option value="female">女</option><option value="male">男</option><option value="other">其他</option><option value="unknown">未知</option></select></label>
            <label><span>历法</span><select v-model="form.partner_profile.calendar_type"><option value="solar">公历</option><option value="lunar">农历</option></select></label>
            <label><span>出生日期</span><input v-model="form.partner_profile.birth_date" type="date" /></label>
            <label><span>出生时间</span><input v-model="form.partner_profile.birth_time" type="time" step="60" /></label>
            <label v-if="form.partner_profile.calendar_type === 'lunar'"><span>是否闰月</span><select v-model="form.partner_profile.is_leap_month"><option :value="false">否</option><option :value="true">是</option></select></label>
            <label><span>城市</span><input v-model="form.partner_profile.birth_city" type="text" /></label>
            <label><span>国家</span><input v-model="form.partner_profile.birth_country" type="text" /></label>
          </div>
        </section>
      </div>
    </section>

    <div class="chat-workbench">
      <div class="chat-status">{{ streamStatus }}</div>

      <div class="conversation-panel">
        <article v-for="item in messages" :key="item.id" class="bubble" :class="item.role">
          <p class="bubble-role">{{ item.role === 'user' ? '你' : '系统' }}</p>
          <p class="bubble-content">{{ item.content }}</p>
        </article>
      </div>

      <form class="composer-card" @submit.prevent="submitStructured">
        <textarea v-model="form.question" rows="4" placeholder="请输入你想了解的情感问题"></textarea>
        <div class="composer-footer">
          <div class="mode-pills">
            <label><input v-model="methodMap.bazi" type="checkbox" /> 八字</label>
            <label><input v-model="methodMap.psychology" type="checkbox" /> 心理学</label>
            <label><input v-model="methodMap.tarot" type="checkbox" /> 塔罗</label>
          </div>
          <button class="send-circle" type="submit">发送</button>
        </div>
      </form>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from "vue";

import { streamStructuredConsultation } from "@/api/analysis";

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

const STORAGE_KEY = "structured-analysis-form";

function defaultForm() {
  return {
    user_profile: {
      gender: "male",
      calendar_type: "solar",
      birth_date: "2005-08-25",
      is_leap_month: false,
      birth_time: "10:20:00",
      birth_city: "Tangshan",
      birth_country: "China",
    },
    partner_profile: {
      nickname: "她",
      gender: "female",
      relationship_type: "unknown",
      calendar_type: "lunar",
      birth_date: "2007-01-27",
      is_leap_month: false,
      birth_time: "02:05:00",
      birth_city: "Shijiazhuang",
      birth_country: "China",
    },
    question: "我们现在分开了，还能复合吗？",
  };
}

const savedForm = localStorage.getItem(STORAGE_KEY);
const form = reactive(savedForm ? JSON.parse(savedForm) : defaultForm());
const showEditor = ref(false);
const methodMap = reactive({ bazi: true, psychology: true, tarot: false });
const streamStatus = ref("命盘初始化完成");
const messages = ref<ChatMessage[]>([]);

const summaryText = computed(() => {
  const userText = `${form.user_profile.gender === "male" ? "男" : "女"} ${form.user_profile.birth_date || "未填"}`;
  const partnerText = `${form.partner_profile.nickname || "对方"} ${form.partner_profile.calendar_type === "lunar" ? "农历" : "公历"} ${form.partner_profile.birth_date || "未填"}`;
  return `${userText} / ${partnerText}`;
});

async function submitStructured() {
  const question = form.question;
  messages.value.push({ id: crypto.randomUUID(), role: "user", content: question });
  const assistantMessage: ChatMessage = { id: crypto.randomUUID(), role: "assistant", content: "" };
  messages.value.push(assistantMessage);
  streamStatus.value = "正在整理双方资料并生成分析...";

  await streamStructuredConsultation(
    {
      user_profile: form.user_profile,
      partner_profile: form.partner_profile,
      question,
      analysis_methods: Object.entries(methodMap)
        .filter(([, enabled]) => enabled)
        .map(([key]) => key),
    },
    (event, data) => {
      if (event === "status") {
        streamStatus.value = data.message || data.stage || "处理中";
      } else if (event === "delta") {
        assistantMessage.content += data.content || "";
      } else if (event === "done") {
        streamStatus.value = "分析完成";
        if (!assistantMessage.content) {
          assistantMessage.content = data.answer || "本次暂无分析结果。";
        }
      }
    }
  );
}

watch(
  form,
  (value) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(value));
  },
  { deep: true }
);
</script>
