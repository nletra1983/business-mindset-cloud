(function () {
  const thread = document.getElementById("demo-thread");
  const form = document.getElementById("demo-form");
  const input = document.getElementById("demo-input");
  const waitEl = document.getElementById("demo-wait");
  const gateEl = document.getElementById("demo-gate");
  const payGateEl = document.getElementById("demo-pay-gate");
  const errEl = document.getElementById("demo-error");
  const startNews = document.getElementById("demo-start-news");
  const clearBtn = document.getElementById("demo-clear");
  const captchaBox = document.getElementById("captcha-box");
  const emailForm = document.getElementById("email-gate-form");
  const emailInput = document.getElementById("email-input");
  const emailResume = document.getElementById("email-resume");
  const paywallCopy = document.getElementById("paywall-copy");
  const paywallForm = document.getElementById("paywall-form");
  const payAmount = document.getElementById("pay-amount");
  const payConfirm = document.getElementById("paywall-confirm");

  let started = false;
  let emailMode = false;
  let captchaWidgetId = null;
  let lastToken = "";
  let guestStep = 0;
  let emailStep = 0;

  function track(name, params) {
    try {
      if (window.GBI_METRIKA && window.GBI_METRIKA.track) {
        window.GBI_METRIKA.track(name, params);
      }
    } catch (_e) {}
  }

  document.querySelectorAll('a.cta[href="#demo"]').forEach(function (el) {
    el.addEventListener("click", function () {
      track("cta_hero");
    });
  });

  function showError(msg) {
    errEl.textContent = msg || "";
    errEl.classList.toggle("hidden", !msg);
  }

  function setWaiting(on) {
    waitEl.classList.toggle("hidden", !on);
    form.querySelectorAll("button").forEach((b) => {
      b.disabled = on;
    });
  }

  function addBubble(role, text) {
    const div = document.createElement("div");
    div.className = "bubble " + (role === "human" ? "human" : "agent");
    div.textContent = text;
    thread.appendChild(div);
    thread.scrollTop = thread.scrollHeight;
  }

  function clearUi() {
    thread.innerHTML = "";
    gateEl.classList.add("hidden");
    payGateEl.classList.add("hidden");
    showError("");
    input.value = "";
    started = false;
    emailMode = false;
    lastToken = "";
    guestStep = 0;
    emailStep = 0;
  }

  function showMessages(list) {
    thread.innerHTML = "";
    (list || []).forEach(function (m) {
      addBubble(m.role === "human" ? "human" : "agent", m.text || "");
    });
  }

  async function openPaywall() {
    payGateEl.classList.remove("hidden");
    payConfirm.classList.add("hidden");
    track("paywall_shown");
    try {
      const res = await fetch("/web/v1/paywall", { credentials: "same-origin" });
      const data = await res.json();
      if (paywallCopy) paywallCopy.textContent = data.copy || "";
      if (payAmount && data.default_amount != null) {
        payAmount.value = String(data.default_amount);
      }
    } catch (_e) {
      if (paywallCopy) {
        paywallCopy.textContent =
          "Хочешь качать своё предпринимательское мышление регулярно и на результат? Внеси небольшую оплату, чтоб мы смогли продолжить предлагать тебе лучшие ответы.";
      }
    }
  }

  function readCaptchaToken() {
    if (lastToken) return lastToken;
    const hidden = captchaBox.querySelector('input[name="smart-token"]');
    return hidden ? hidden.value : "";
  }

  function mountCaptcha() {
    const key = window.SMARTCAPTCHA_CLIENT_KEY || "";
    if (!key || typeof window.smartCaptcha === "undefined") {
      captchaBox.innerHTML =
        '<p class="muted">Капча подключится, когда задан SMARTCAPTCHA_CLIENT_KEY.</p>';
      return;
    }
    captchaBox.innerHTML = "";
    captchaWidgetId = window.smartCaptcha.render(captchaBox, {
      sitekey: key,
      callback: function (token) {
        lastToken = token || "";
      },
    });
  }

  async function api(path, body) {
    const res = await fetch(path, {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body || {}),
    });
    const data = await res.json().catch(function () {
      return { message: "Ответ сервера не разобран" };
    });
    return { status: res.status, data: data };
  }

  startNews.addEventListener("click", async function () {
    showError("");
    setWaiting(true);
    try {
      const { status, data } = await api("/web/v1/guest/window/start", {
        use_news: true,
      });
      if (status >= 400) {
        showError(data.message || "Не удалось начать");
        return;
      }
      clearUi();
      started = true;
      if (data.topic) {
        addBubble("agent", "Факт для разбора:\n" + data.topic);
      }
      if (data.agent_reply) addBubble("agent", data.agent_reply);
    } catch (e) {
      showError("Сеть недоступна. Попробуйте ещё раз.");
    } finally {
      setWaiting(false);
    }
  });

  form.addEventListener("submit", async function (ev) {
    ev.preventDefault();
    showError("");
    const text = (input.value || "").trim();
    if (!text) {
      showError("Напишите факт или ответ.");
      return;
    }
    setWaiting(true);
    try {
      if (emailMode) {
        addBubble("human", text);
        input.value = "";
        const { status, data } = await api("/web/v1/gate/message", { text: text });
        if (status >= 400) {
          showError(data.message || "Ошибка шага");
          if (data.payment_gate) openPaywall();
          return;
        }
        if (data.agent_reply) addBubble("agent", data.agent_reply);
        emailStep = data.email_steps_done || emailStep + 1;
        if (emailStep === 1) track("step_4");
        if (emailStep === 2) track("step_5");
        if (emailStep === 3) track("step_6");
        if (data.payment_gate) openPaywall();
        return;
      }
      if (!started) {
        const { status, data } = await api("/web/v1/guest/window/start", {
          fact: text,
          use_news: false,
        });
        if (status >= 400) {
          showError(data.message || "Не удалось начать");
          return;
        }
        started = true;
        addBubble("human", text);
        if (data.agent_reply) addBubble("agent", data.agent_reply);
        input.value = "";
        return;
      }
      const token = readCaptchaToken();
      addBubble("human", text);
      input.value = "";
      const { status, data } = await api("/web/v1/guest/window/message", {
        text: text,
        captcha_token: token,
      });
      if (status >= 400) {
        showError(data.message || "Ошибка шага");
        if (data.gate_required) {
          gateEl.classList.remove("hidden");
          track("gate_shown");
        }
        return;
      }
      if (data.agent_reply) addBubble("agent", data.agent_reply);
      guestStep = data.step_count || guestStep + 1;
      if (guestStep === 1) track("step_1");
      if (guestStep === 2) track("step_2");
      if (guestStep === 3) track("step_3");
      if (data.gate_required) {
        gateEl.classList.remove("hidden");
        track("gate_shown");
      }
      lastToken = "";
      if (captchaWidgetId != null && window.smartCaptcha) {
        try {
          window.smartCaptcha.reset(captchaWidgetId);
        } catch (_e) {}
      }
    } catch (e) {
      showError("Сеть недоступна. Попробуйте ещё раз.");
    } finally {
      setWaiting(false);
    }
  });

  async function sendEmail(path) {
    showError("");
    const email = (emailInput.value || "").trim();
    if (!email) {
      showError("Укажите email.");
      return;
    }
    setWaiting(true);
    try {
      const { status, data } = await api(path, { email: email });
      if (status >= 400) {
        showError(data.message || "Не удалось продолжить");
        return;
      }
      emailMode = true;
      gateEl.classList.add("hidden");
      if (path.indexOf("resume") >= 0) track("day2_return");
      else track("email_submitted");
      if (data.messages) showMessages(data.messages);
      else if (data.agent_reply) addBubble("agent", data.agent_reply);
      if (data.payment_gate) openPaywall();
    } catch (e) {
      showError("Сеть недоступна. Попробуйте ещё раз.");
    } finally {
      setWaiting(false);
    }
  }

  if (emailForm) {
    emailForm.addEventListener("submit", function (ev) {
      ev.preventDefault();
      sendEmail("/web/v1/gate/email");
    });
  }
  if (emailResume) {
    emailResume.addEventListener("click", function () {
      sendEmail("/web/v1/gate/resume");
    });
  }
  if (paywallForm) {
    paywallForm.addEventListener("submit", async function (ev) {
      ev.preventDefault();
      showError("");
      setWaiting(true);
      try {
        const { status, data } = await api("/web/v1/paywall/click", {
          amount: payAmount ? payAmount.value : 100,
        });
        if (status >= 400) {
          showError(data.message || "Сумма не принята");
          return;
        }
        track("pay_click", { amount: data.amount });
        payConfirm.textContent = data.confirmation || "";
        payConfirm.classList.remove("hidden");
      } catch (e) {
        showError("Сеть недоступна. Попробуйте ещё раз.");
      } finally {
        setWaiting(false);
      }
    });
  }

  clearBtn.addEventListener("click", async function () {
    setWaiting(true);
    try {
      await api("/web/v1/guest/window/clear", {});
    } catch (_e) {}
    clearUi();
    setWaiting(false);
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mountCaptcha);
  } else {
    mountCaptcha();
  }
})();
