const form = document.getElementById("structured-form");
const payloadPreview = document.getElementById("payload-preview");
const responsePreview = document.getElementById("response-preview");
const previewButton = document.getElementById("preview-btn");
const copyButton = document.getElementById("copy-btn");
const clearResponseButton = document.getElementById("clear-response-btn");
const apiBaseInput = document.getElementById("api-base");
const apiTokenInput = document.getElementById("api-token");
const modeButtons = document.querySelectorAll(".mode-pill");
const existingPartnerBox = document.getElementById("existing-partner-box");

function toggleLeapField(radioName, className) {
  const selected = document.querySelector(`input[name="${radioName}"]:checked`);
  const target = document.querySelector(`.${className}`);
  if (!selected || !target) return;
  target.classList.toggle("hidden", selected.value !== "lunar");
}

function bindCalendarToggles() {
  ["user_calendar_type", "partner_calendar_type"].forEach((name) => {
    document.querySelectorAll(`input[name="${name}"]`).forEach((input) => {
      input.addEventListener("change", () => {
        toggleLeapField(name, name.startsWith("user") ? "user-leap" : "partner-leap");
        renderPayloadPreview();
      });
    });
  });
}

function currentMode() {
  const active = document.querySelector(".mode-pill.active");
  return active?.dataset.mode || "new";
}

function parseBoolean(value) {
  return value === "true";
}

function checkedValues(name) {
  return Array.from(document.querySelectorAll(`input[name="${name}"]:checked`)).map(
    (item) => item.value
  );
}

function buildPayload() {
  const formData = new FormData(form);
  const mode = currentMode();

  const payload = {
    user_profile: {
      gender: formData.get("user_gender") || null,
      calendar_type: formData.get("user_calendar_type") || "solar",
      birth_date: formData.get("user_birth_date") || null,
      is_leap_month: parseBoolean(formData.get("user_is_leap_month") || "false"),
      birth_time: formData.get("user_birth_time") || null,
      birth_city: formData.get("user_birth_city") || null,
      birth_country: formData.get("user_birth_country") || null,
    },
    partner_profile: {
      nickname: formData.get("partner_nickname") || "",
      gender: formData.get("partner_gender") || null,
      relationship_type: formData.get("partner_relationship_type") || "unknown",
      calendar_type: formData.get("partner_calendar_type") || "solar",
      birth_date: formData.get("partner_birth_date") || null,
      is_leap_month: parseBoolean(formData.get("partner_is_leap_month") || "false"),
      birth_time: formData.get("partner_birth_time") || null,
      birth_city: formData.get("partner_birth_city") || null,
      birth_country: formData.get("partner_birth_country") || null,
    },
    question: formData.get("question") || "",
    analysis_methods: checkedValues("analysis_methods"),
  };

  if (mode === "existing") {
    payload.partner_id = formData.get("existing_partner_id") || null;
  }

  return payload;
}

function renderPayloadPreview() {
  payloadPreview.textContent = JSON.stringify(buildPayload(), null, 2);
}

async function submitPayload(event) {
  event.preventDefault();
  const payload = buildPayload();
  const url = `${apiBaseInput.value.replace(/\/$/, "")}/structured-consultations`;
  const token = apiTokenInput.value.trim();

  responsePreview.textContent = "提交中...";

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    responsePreview.textContent = JSON.stringify(
      {
        http_status: response.status,
        body: data,
      },
      null,
      2
    );
  } catch (error) {
    responsePreview.textContent = JSON.stringify(
      {
        error: String(error),
      },
      null,
      2
    );
  }
}

modeButtons.forEach((button) => {
  button.addEventListener("click", () => {
    modeButtons.forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    existingPartnerBox.classList.toggle("hidden", button.dataset.mode !== "existing");
    renderPayloadPreview();
  });
});

Array.from(form.elements).forEach((element) => {
  element.addEventListener?.("input", renderPayloadPreview);
  element.addEventListener?.("change", renderPayloadPreview);
});

previewButton.addEventListener("click", renderPayloadPreview);
copyButton.addEventListener("click", async () => {
  await navigator.clipboard.writeText(payloadPreview.textContent || "");
  copyButton.textContent = "已复制";
  window.setTimeout(() => {
    copyButton.textContent = "复制 JSON";
  }, 1400);
});
clearResponseButton.addEventListener("click", () => {
  responsePreview.textContent = "点击“提交结构化分析”后显示返回结果";
});

form.addEventListener("submit", submitPayload);

bindCalendarToggles();
toggleLeapField("user_calendar_type", "user-leap");
toggleLeapField("partner_calendar_type", "partner-leap");
renderPayloadPreview();
