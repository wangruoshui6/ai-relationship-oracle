<template>
  <section class="workspace-page compact-workspace">
    <div class="workspace-header compact-header">
      <div>
        <p class="workspace-kicker">AI Relationship Oracle</p>
        <h1>AI 情感关系顾问</h1>
        <p class="workspace-copy">主页面只保留咨询区；八字资料通过按钮打开弹层编辑。</p>
      </div>
      <button class="ghost-btn" type="button" @click="logout">退出登录</button>
    </div>

    <section class="workspace-section compact-panel">
      <div class="selector-row">
        <div class="selector-wrap" ref="myMenuRef">
          <button class="selector-trigger" type="button" @click="toggleMyMenu">
            <strong>{{ myProfile.name || '未命名命主' }}</strong>
            <span>{{ myProfile.birth_date || '未填写日期' }} {{ myProfile.birth_time || '' }}</span>
            <span class="selector-arrow">⌄</span>
          </button>
          <div v-if="showMyMenu" class="selector-menu">
            <button class="selector-menu-item" type="button" @click="closeMenus">切换命主</button>
            <button class="selector-menu-item active" type="button" @click="openMyModalFromMenu">编辑命主</button>
            <button class="selector-menu-item" type="button" @click="openMyModalFromMenu">新建命主</button>
          </div>
        </div>

        <div class="selector-wrap" ref="partnerMenuRef">
          <button class="selector-trigger secondary" type="button" @click="togglePartnerMenu">
            <strong>{{ partnerSummary }}</strong>
            <span>{{ selectedPartnerId ? '当前分析对象' : '当前仅分析自己' }}</span>
            <span class="selector-arrow">⌄</span>
          </button>
          <div v-if="showPartnerMenu" class="selector-menu wide">
            <button class="selector-menu-item" type="button" @click="chooseSelfOnly">只分析自己</button>
            <button class="selector-menu-item" type="button" @click="openNewPartnerFromMenu">新增对象</button>
            <button v-for="item in partners" :key="item.id" class="selector-menu-item" :class="{ active: selectedPartnerId === item.id }" type="button" @click="openPartnerModalFromMenu(item.id)">
              {{ item.nickname }}
            </button>
          </div>
        </div>
      </div>

      <div class="checkbox-row compact-checkbox-row">
        <label class="check-pill"><input v-model="methodMap.bazi" type="checkbox" /> 八字</label>
        <label class="check-pill"><input v-model="methodMap.psychology" type="checkbox" /> 心理学</label>
        <label class="check-pill"><input v-model="methodMap.tarot" type="checkbox" /> 塔罗牌</label>
      </div>

      <div class="chat-messages compact-chat-messages">
        <article v-for="item in messages" :key="item.id" class="chat-bubble" :class="item.role">
          <div class="chat-role">{{ item.role === 'user' ? '你' : 'AI' }}</div>
          <div class="chat-content">{{ item.content }}</div>
        </article>
      </div>

      <form class="chat-form compact-chat-form" @submit.prevent="submitConsultation">
        <textarea v-model="question" :disabled="isSending" rows="5" placeholder="请输入你的问题"></textarea>
        <div class="chat-actions">
          <button class="ghost-btn" type="button" :disabled="isSending" @click="clearConversation">清空对话</button>
          <button class="primary-btn" type="submit" :disabled="isSending || !trimmedQuestion">{{ isSending ? '分析中...' : '发送' }}</button>
        </div>
      </form>
    </section>

    <div v-if="activeModal === 'my'" class="profile-modal-backdrop" @click.self="closeModal">
      <section class="profile-modal-card">
        <div class="profile-modal-head"><h2>编辑命主</h2><button class="modal-close-btn" type="button" @click="closeModal">×</button></div>
        <div class="modal-form-grid">
          <label><span>姓名：</span><input v-model="myProfile.name" type="text" placeholder="请输入命主姓名" /></label>
          <label><span>性别：</span><select v-model="myProfile.gender"><option value="male">男</option><option value="female">女</option><option value="other">其他</option><option value="unknown">未知</option></select></label>
          <label><span>出生时间历法：</span><select v-model="myProfile.calendar_type"><option value="solar">公历</option><option value="lunar">农历</option></select></label>
          <label><span>出生日期：</span><input v-model="myProfile.birth_date" type="date" /></label>
          <label><span>出生时间：</span><input v-model="myProfile.birth_time" type="time" step="60" /></label>
          <label><span>出生地点：</span><input v-model="myProfile.birth_city" type="text" /></label>
          <label><span>国家：</span><input v-model="myProfile.birth_country" type="text" /></label>
        </div>
        <div class="modal-actions"><button class="ghost-btn" type="button" @click="closeModal">取消</button><button class="primary-btn" type="button" :disabled="savingProfile" @click="saveMyProfile">{{ savingProfile ? '保存中...' : '保存' }}</button></div>
      </section>
    </div>

    <div v-if="activeModal === 'partner'" class="profile-modal-backdrop" @click.self="closeModal">
      <section class="profile-modal-card">
        <div class="profile-modal-head"><h2>{{ editingPartnerId ? '编辑对象' : '新增对象' }}</h2><button class="modal-close-btn" type="button" @click="closeModal">×</button></div>
        <div class="modal-form-grid">
          <label><span>姓名：</span><input v-model="partnerForm.nickname" type="text" /></label>
          <label><span>关系：</span><select v-model="partnerForm.relationship_type"><option value="unknown">未知</option><option value="ex">前任</option><option value="current">现任</option><option value="crush">暧昧对象</option><option value="spouse">配偶</option><option value="friend">朋友</option></select></label>
          <label><span>性别：</span><select v-model="partnerForm.gender"><option value="female">女</option><option value="male">男</option><option value="other">其他</option><option value="unknown">未知</option></select></label>
          <label><span>出生时间历法：</span><select v-model="partnerForm.calendar_type"><option value="solar">公历</option><option value="lunar">农历</option></select></label>
          <label><span>出生日期：</span><input v-model="partnerForm.birth_date" type="date" /></label>
          <label><span>出生时间：</span><input v-model="partnerForm.birth_time" type="time" step="60" /></label>
          <label><span>出生地点：</span><input v-model="partnerForm.birth_city" type="text" /></label>
          <label><span>国家：</span><input v-model="partnerForm.birth_country" type="text" /></label>
        </div>
        <div class="modal-actions between">
          <button v-if="editingPartnerId" class="ghost-btn danger" type="button" :disabled="deletingPartner" @click="removePartner(editingPartnerId)">{{ deletingPartner ? '删除中...' : '删除' }}</button>
          <div class="modal-actions-right"><button class="ghost-btn" type="button" @click="closeModal">取消</button><button class="primary-btn" type="button" :disabled="savingPartner || !partnerForm.nickname.trim()" @click="savePartner">{{ savingPartner ? '保存中...' : '保存' }}</button></div>
        </div>
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { streamConsultation } from '@/api/analysis';
import { createPartner, deletePartner, getPartner, listPartners, updatePartner } from '@/api/partners';
import { getMyProfile, upsertMyProfile } from '@/api/profiles';
import { useAuthStore } from '@/stores/auth';

type ChatMessage={id:string;role:'user'|'assistant';content:string};
type PartnerItem={id:string;nickname:string};
type ModalType='my'|'partner'|null;
const authStore=useAuthStore(); const router=useRouter(); const activeModal=ref<ModalType>(null); const showMyMenu=ref(false); const showPartnerMenu=ref(false); const myMenuRef=ref<HTMLElement|null>(null); const partnerMenuRef=ref<HTMLElement|null>(null);
const myProfile=reactive({name:'',gender:'male',calendar_type:'solar',birth_date:'',birth_time:'',birth_city:'',birth_country:'China',is_leap_month:false});
const partnerForm=reactive({nickname:'',gender:'female',relationship_type:'unknown',calendar_type:'solar',birth_date:'',birth_time:'',birth_city:'',birth_country:'China',is_leap_month:false});
const methodMap=reactive({bazi:true,psychology:true,tarot:false}); const partners=ref<PartnerItem[]>([]); const messages=ref<ChatMessage[]>([]);
const savingProfile=ref(false); const savingPartner=ref(false); const deletingPartner=ref(false); const isSending=ref(false); const streamStatus=ref('准备就绪');
const question=ref('我和 Sarah 分手三个月了，她最近点赞我朋友圈，我们还有机会吗？'); const conversationId=ref<string|null>(null); const selectedPartnerId=ref<string|null>(null); const editingPartnerId=ref<string|null>(null);
const trimmedQuestion=computed(()=>question.value.trim());
const myProfileSummary=computed(()=>`${myProfile.name||'未命名'} · ${myProfile.gender==='female'?'女':myProfile.gender==='male'?'男':'未知'} · ${myProfile.birth_date||'未填写'} ${myProfile.birth_time||''}`.trim());
const partnerSummary=computed(()=>!selectedPartnerId.value?'只分析自己':partners.value.find((i)=>i.id===selectedPartnerId.value)?.nickname||'当前对象');
const t=(v:any)=>v?String(v).slice(0,5):'';
function resetPartnerForm(){editingPartnerId.value=null;Object.assign(partnerForm,{nickname:'',gender:'female',relationship_type:'unknown',calendar_type:'solar',birth_date:'',birth_time:'',birth_city:'',birth_country:'China',is_leap_month:false});}
function closeMenus(){showMyMenu.value=false;showPartnerMenu.value=false;}
function toggleMyMenu(){showMyMenu.value=!showMyMenu.value;showPartnerMenu.value=false;}
function togglePartnerMenu(){showPartnerMenu.value=!showPartnerMenu.value;showMyMenu.value=false;}
function openMyModalFromMenu(){closeMenus();activeModal.value='my';}
function openNewPartnerFromMenu(){closeMenus();resetPartnerForm();activeModal.value='partner';}
async function openPartnerModalFromMenu(id:string){closeMenus();selectedPartnerId.value=id;editingPartnerId.value=id;const r=await getPartner(id);const d=r.data?.data;if(d){Object.assign(partnerForm,{nickname:d.nickname||'',gender:d.gender||'female',relationship_type:d.relationship_type||'unknown',calendar_type:d.calendar_type||'solar',birth_date:d.birth_date||'',birth_time:t(d.birth_time),birth_city:d.birth_city||'',birth_country:d.birth_country||'China',is_leap_month:Boolean(d.is_leap_month)});}activeModal.value='partner';}
function chooseSelfOnly(){selectedPartnerId.value=null;closeMenus();}
function handleOutsideClick(event:MouseEvent){const target=event.target as Node;if(myMenuRef.value&&!myMenuRef.value.contains(target))showMyMenu.value=false;if(partnerMenuRef.value&&!partnerMenuRef.value.contains(target))showPartnerMenu.value=false;}
function closeModal(){activeModal.value=null;}
async function loadMyProfile(){const r=await getMyProfile();const d=r.data?.data;if(!d)return;Object.assign(myProfile,{name:d.name||'',gender:d.gender||'male',calendar_type:d.calendar_type||'solar',birth_date:d.birth_date||'',birth_time:t(d.birth_time),birth_city:d.birth_city||'',birth_country:d.birth_country||'China',is_leap_month:Boolean(d.is_leap_month)});}
async function loadPartners(){const r=await listPartners();partners.value=r.data?.data||[];}
async function saveMyProfile(){savingProfile.value=true;try{await upsertMyProfile({...myProfile,birth_date:myProfile.birth_date||null,birth_time:myProfile.birth_time||null});streamStatus.value='命主资料已保存';closeModal();}finally{savingProfile.value=false;}}
async function savePartner(){if(!partnerForm.nickname.trim())return;savingPartner.value=true;const payload={...partnerForm,birth_date:partnerForm.birth_date||null,birth_time:partnerForm.birth_time||null};try{if(editingPartnerId.value){await updatePartner(editingPartnerId.value,payload);selectedPartnerId.value=editingPartnerId.value;streamStatus.value='对象资料已更新';}else{const r=await createPartner(payload);const id=r.data?.data?.id||null;if(id){selectedPartnerId.value=id;editingPartnerId.value=id;}streamStatus.value='对象资料已保存';}await loadPartners();closeModal();}finally{savingPartner.value=false;}}
async function removePartner(id:string){deletingPartner.value=true;try{await deletePartner(id);if(selectedPartnerId.value===id)selectedPartnerId.value=null;resetPartnerForm();await loadPartners();streamStatus.value='对象已删除';closeModal();}finally{deletingPartner.value=false;}}
function clearConversation(){messages.value=[];conversationId.value=null;streamStatus.value='准备就绪';}
async function submitConsultation(){if(!trimmedQuestion.value||isSending.value)return;const userMessage=trimmedQuestion.value;const assistant={id:crypto.randomUUID(),role:'assistant' as const,content:''};messages.value.push({id:crypto.randomUUID(),role:'user',content:userMessage});messages.value.push(assistant);isSending.value=true;streamStatus.value='已发送，正在分析...';try{await streamConsultation({conversation_id:conversationId.value,partner_id:selectedPartnerId.value,message:userMessage,analysis_methods:Object.entries(methodMap).filter(([,v])=>v).map(([k])=>k)},(event,data)=>{if(event==='status'){streamStatus.value=data.message||data.stage||'处理中';return;}if(event==='delta'){assistant.content+=data.content||'';return;}if(event==='done'){conversationId.value=data.conversation_id||conversationId.value;if(!selectedPartnerId.value&&data.partner_id){selectedPartnerId.value=data.partner_id;loadPartners();}streamStatus.value='分析完成';if(!assistant.content)assistant.content=data.answer||'本次暂无分析结果。';}});}catch(error){assistant.content='当前无法连接后端咨询接口，请确认后端服务已启动并且账号已登录。';streamStatus.value='请求失败';console.error(error);}finally{isSending.value=false;question.value='';}}
function logout(){authStore.clearToken();router.push({name:'login'});} onMounted(async()=>{document.addEventListener('click',handleOutsideClick);await Promise.all([loadMyProfile(),loadPartners()]);});
onBeforeUnmount(()=>{document.removeEventListener('click',handleOutsideClick);});
</script>
