<template>
  <section class="minimal-chat-page">
    <div class="minimal-chat-header">
      <p class="minimal-chat-kicker">AI Relationship Oracle</p>
      <h1>AI 情感关系顾问</h1>
      <p class="minimal-chat-copy">输入你的问题，系统会调用真实后端咨询接口并返回分析结果。</p>
    </div>

    <div class="minimal-chat-status">{{ streamStatus }}</div>

    <div class="minimal-chat-messages">
      <article v-for="item in messages" :key="item.id" class="minimal-bubble" :class="item.role">
        <div class="minimal-bubble-role">{{ item.role === 'user' ? '你' : 'AI' }}</div>
        <div class="minimal-bubble-content">{{ item.content }}</div>
      </article>
    </div>

    <form class="minimal-chat-form" @submit.prevent="submitConsultation">
      <textarea
        v-model="message"
        :disabled="isSending"
        rows="5"
        placeholder="比如：我和 Sarah 分手三个月了，她最近点赞我朋友圈，我们还有机会吗？"
      ></textarea>

      <div class="minimal-chat-actions">
        <button class="ghost-btn" type="button" :disabled="isSending" @click="clearConversation">清空</button>
        <button class="primary-btn" type="submit" :disabled="isSending || !trimmedMessage">
          {{ isSending ? '分析中...' : '发送' }}
        </button>
      </div>
    </form>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";

import { streamConsultation } from "@/api/analysis";

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

const DEFAULT_MESSAGE = "我和 Sarah 分手三个月了，她最近点赞我朋友圈，我们还有机会吗？";

const message = ref(DEFAULT_MESSAGE);
const streamStatus = ref("准备就绪");
const isSending = ref(false);
const conversationId = ref<string | null>(null);
const partnerId = ref<string | null>(null);
const messages = ref<ChatMessage[]>([]);

const trimmedMessage = computed(() => message.value.trim());

function clearConversation() {
  messages.value = [];
  conversationId.value = null;
  partnerId.value = null;
  streamStatus.value = "准备就绪";
}

async function submitConsultation() {
  if (!trimmedMessage.value || isSending.value) {
    return;
  }

  const userMessage = trimmedMessage.value;
  const assistantMessage: ChatMessage = {
    id: crypto.randomUUID(),
    role: "assistant",
    content: "",
  };

  messages.value.push({
    id: crypto.randomUUID(),
    role: "user",
    content: userMessage,
  });
  messages.value.push(assistantMessage);

  isSending.value = true;
  streamStatus.value = "已发送，正在分析...";

  try {
    await streamConsultation(
      {
        conversation_id: conversationId.value,
        partner_id: partnerId.value,
        message: userMessage,
        analysis_methods: ["bazi", "psychology"],
      },
      (event, data) => {
        if (event === "status") {
          streamStatus.value = data.message || data.stage || "处理中";
          return;
        }

        if (event === "delta") {
          assistantMessage.content += data.content || "";
          return;
        }

        if (event === "done") {
          conversationId.value = data.conversation_id || conversationId.value;
          partnerId.value = data.partner_id || partnerId.value;
          streamStatus.value = "分析完成";
          if (!assistantMessage.content) {
            assistantMessage.content = data.answer || "本次暂无分析结果。";
          }
        }
      }
    );
  } catch (error) {
    assistantMessage.content = "当前无法连接后端咨询接口，请先确认后端服务已启动并且账号已登录。";
    streamStatus.value = "请求失败";
    console.error(error);
  } finally {
    isSending.value = false;
    message.value = "";
  }
}
</script>
