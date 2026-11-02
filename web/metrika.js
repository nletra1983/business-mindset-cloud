(function (w) {
  var EVENT_NAMES = {
    cta_hero: "cta_hero",
    step_1: "step_1",
    step_2: "step_2",
    step_3: "step_3",
    gate_shown: "gate_shown",
    email_submitted: "email_submitted",
    step_4: "step_4",
    step_5: "step_5",
    step_6: "step_6",
    paywall_shown: "paywall_shown",
    pay_click: "pay_click",
    day2_return: "day2_return",
  };

  function counterId() {
    var raw = w.YANDEX_METRIKA_COUNTER_ID;
    if (raw == null || raw === "") return "";
    return String(raw).trim();
  }

  function reachGoal(name, params) {
    var id = counterId();
    if (!id) return false;
    try {
      if (typeof w.ym === "function") {
        if (params && Object.keys(params).length) {
          w.ym(Number(id) || id, "reachGoal", name, params);
        } else {
          w.ym(Number(id) || id, "reachGoal", name);
        }
        return true;
      }
    } catch (_e) {
      /* Metrika must never block the product */
    }
    return false;
  }

  w.GBI_METRIKA = {
    EVENT_NAMES: EVENT_NAMES,
    counterId: counterId,
    reachGoal: reachGoal,
    track: function (key, params) {
      var name = EVENT_NAMES[key] || key;
      return reachGoal(name, params);
    },
  };
})(window);
