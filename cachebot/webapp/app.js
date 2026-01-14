(() => {
  const tg = window.Telegram?.WebApp;
  const logEl = document.getElementById("log");
  const sellQuick = document.getElementById("sellQuick");
  const sellModal = document.getElementById("sellModal");
  const sellModalClose = document.getElementById("sellModalClose");
  const sellForm = document.getElementById("sellForm");
  const sellAmount = document.getElementById("sellAmount");
  const userBadge = document.getElementById("userBadge");
  const profileNameTop = document.getElementById("profileNameTop");
  const profileAvatar = document.getElementById("profileAvatar");
  const profileQuick = document.getElementById("profileQuick");
  const profileModal = document.getElementById("profileModal");
  const profileModalClose = document.getElementById("profileModalClose");
  const profileQuickName = document.getElementById("profileQuickName");
  const profileQuickUsername = document.getElementById("profileQuickUsername");
  const profileGo = document.getElementById("profileGo");
  const themeToggle = document.getElementById("themeToggle");
  const navButtons = document.querySelectorAll(".nav-btn");
  const views = document.querySelectorAll(".view");

  const profileName = document.getElementById("profileName");
  const profileUsername = document.getElementById("profileUsername");
  const profileRegistered = document.getElementById("profileRegistered");
  const profileRole = document.getElementById("profileRole");
  const profileMerchantSince = document.getElementById("profileMerchantSince");
  const profileBalance = document.getElementById("profileBalance");
  const dealsCount = document.getElementById("dealsCount");
  const dealsList = document.getElementById("dealsList");
  const dealModal = document.getElementById("dealModal");
  const dealModalTitle = document.getElementById("dealModalTitle");
  const dealModalBody = document.getElementById("dealModalBody");
  const dealModalActions = document.getElementById("dealModalActions");
  const dealModalClose = document.getElementById("dealModalClose");
  const p2pList = document.getElementById("p2pList");
  const p2pTradingBadge = document.getElementById("p2pTradingBadge");
  const p2pTradingToggle = document.getElementById("p2pTradingToggle");
  const p2pBuyBtn = document.getElementById("p2pBuyBtn");
  const p2pSellBtn = document.getElementById("p2pSellBtn");
  const p2pMyAdsBtn = document.getElementById("p2pMyAdsBtn");
  const p2pCreateBtn = document.getElementById("p2pCreateBtn");
  const p2pModal = document.getElementById("p2pModal");
  const p2pModalTitle = document.getElementById("p2pModalTitle");
  const p2pModalBody = document.getElementById("p2pModalBody");
  const p2pModalActions = document.getElementById("p2pModalActions");
  const p2pModalClose = document.getElementById("p2pModalClose");
  const p2pCreateModal = document.getElementById("p2pCreateModal");
  const p2pCreateClose = document.getElementById("p2pCreateClose");
  const p2pCreateForm = document.getElementById("p2pCreateForm");
  const p2pSide = document.getElementById("p2pSide");
  const p2pVolume = document.getElementById("p2pVolume");
  const p2pVolumeMax = document.getElementById("p2pVolumeMax");
  const p2pPrice = document.getElementById("p2pPrice");
  const p2pLimits = document.getElementById("p2pLimits");
  const p2pBanks = document.getElementById("p2pBanks");
  const p2pTerms = document.getElementById("p2pTerms");
  const p2pBalanceHint = document.getElementById("p2pBalanceHint");
  const disputesTab = document.getElementById("disputesTab");
  const disputesCount = document.getElementById("disputesCount");
  const disputesList = document.getElementById("disputesList");
  const adminTab = document.getElementById("adminTab");
  const adminRate = document.getElementById("adminRate");
  const adminFee = document.getElementById("adminFee");
  const adminWithdrawFee = document.getElementById("adminWithdrawFee");
  const adminSaveRates = document.getElementById("adminSaveRates");
  const adminModeratorUsername = document.getElementById("adminModeratorUsername");
  const adminAddModerator = document.getElementById("adminAddModerator");
  const adminModerators = document.getElementById("adminModerators");
  const adminMerchants = document.getElementById("adminMerchants");
  const reviewsOpen = document.getElementById("reviewsOpen");
  const reviewsModal = document.getElementById("reviewsModal");
  const reviewsClose = document.getElementById("reviewsClose");
  const reviewsList = document.getElementById("reviewsList");
  const reviewsSummary = document.getElementById("reviewsSummary");
  const reviewTabButtons = document.querySelectorAll(".tab-btn");

  const state = {
    user: null,
    initData: "",
    balance: null,
    p2pMode: "buy",
    p2pAds: [],
    myAds: [],
  };

  const log = (message, type = "info") => {
    if (!logEl) return;
    const line = document.createElement("div");
    line.className = `log-line ${type}`;
    line.textContent = message;
    logEl.prepend(line);
  };

  const applyTheme = (theme) => {
    document.documentElement.dataset.theme = theme;
    if (tg) {
      try {
        tg.setHeaderColor(theme === "dark" ? "#0e0f13" : "#f6f3ee");
        tg.setBackgroundColor(theme === "dark" ? "#0e0f13" : "#f6f3ee");
      } catch (err) {
        // Ignore if WebApp methods are unavailable.
      }
    }
  };

  const detectTheme = () => {
    if (tg?.colorScheme) return tg.colorScheme;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  };

  const setAuthState = (user) => {
    state.user = user;
    const display = user?.username
      ? `@${user.username}`
      : user?.first_name
        ? user.first_name
        : "Гость";
    userBadge.textContent = display;
    if (profileNameTop) profileNameTop.textContent = display;
    if (profileAvatar) profileAvatar.textContent = display.slice(0, 2).toUpperCase();
  };

  const formatAmount = (value, digits = 3) => {
    const num = Number(value);
    if (!Number.isFinite(num)) return "—";
    return num.toFixed(digits).replace(/\\.?0+$/, "");
  };

  const formatDate = (iso) => {
    if (!iso) return "—";
    const dt = new Date(iso);
    return dt.toLocaleString("ru-RU", { dateStyle: "short", timeStyle: "short" });
  };

  const statusLabel = (deal) => {
    if (deal.status === "open") return "Ожидаем Мерчанта";
    if (deal.status === "reserved") return "Ждем оплату";
    if (deal.status === "paid") {
      if (deal.qr_stage === "awaiting_buyer_ready") return "Ожидаем готовность";
      if (deal.qr_stage === "awaiting_seller_photo") return "Прикрепление QR";
      return "Отправка QR";
    }
    if (deal.status === "dispute") return "Открыт спор";
    if (deal.status === "completed") return "Завершена";
    if (deal.status === "canceled") return "Отменена";
    if (deal.status === "expired") return "Истекла";
    return "Статус";
  };

  const fetchMe = async () => {
    if (!state.initData) {
      log("initData не найден. Откройте WebApp из Telegram.", "error");
      return null;
    }
    try {
      const res = await fetch("/api/me", {
        method: "GET",
        headers: {
          "X-Telegram-Init-Data": state.initData,
        },
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `HTTP ${res.status}`);
      }
      const payload = await res.json();
      return payload.user || null;
    } catch (err) {
      log(`Ошибка авторизации: ${err.message}`, "error");
      return null;
    }
  };

  const fetchJson = async (path, options = {}) => {
    if (!state.initData) {
      log("initData не найден. Откройте WebApp из Telegram.", "error");
      return null;
    }
    try {
      const method = options.method || "GET";
      const res = await fetch(path, {
        method,
        headers: {
          "Content-Type": "application/json",
          "X-Telegram-Init-Data": state.initData,
        },
        body: options.body,
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `HTTP ${res.status}`);
      }
      return await res.json();
    } catch (err) {
      log(`Ошибка API ${path}: ${err.message}`, "error");
      return null;
    }
  };

  const loadProfile = async () => {
    const payload = await fetchJson("/api/profile");
    if (!payload?.ok) return;
    const { data } = payload;
    const profile = data?.profile;
    profileName.textContent = profile?.full_name || "Без имени";
    profileUsername.textContent = profile?.username ? `@${profile.username}` : "Без ника";
    profileRegistered.textContent = profile?.registered_at
      ? `Регистрация: ${formatDate(profile.registered_at)}`
      : "Регистрация: —";
    profileRole.textContent = data?.role === "buyer" ? "Мерчант" : "Продавец";
    profileMerchantSince.textContent = data?.merchant_since
      ? `Мерчант с: ${formatDate(data.merchant_since)}`
      : "Мерчант с: —";
  };

  const loadBalance = async () => {
    const payload = await fetchJson("/api/balance");
    if (!payload?.ok) return;
    state.balance = payload.balance;
    if (profileBalance) {
      profileBalance.textContent = `${formatAmount(payload.balance)} USDT`;
    }
  };

  const loadDeals = async () => {
    const payload = await fetchJson("/api/my-deals");
    if (!payload?.ok) return;
    const deals = payload.deals || [];
    dealsCount.textContent = `${deals.length}`;
    dealsList.innerHTML = "";
    if (!deals.length) {
      dealsList.innerHTML = "<div class=\"deal-empty\">Сделок пока нет.</div>";
      return;
    }
    deals.forEach((deal) => {
      const item = document.createElement("div");
      item.className = "deal-item";
      const counterparty = deal.counterparty?.full_name || deal.counterparty?.username || "—";
      item.innerHTML = `
        <div class="deal-header">
          <div class="deal-id">Сделка #${deal.public_id}</div>
          <div class="deal-status">${statusLabel(deal)}</div>
        </div>
        <div class="deal-row">Наличные: ₽${formatAmount(deal.cash_rub, 2)}</div>
        <div class="deal-row">USDT к оплате: ${formatAmount(deal.usdt_amount)} USDT</div>
        <div class="deal-row">Курс: 1 USDT = ${formatAmount(deal.rate, 2)} RUB</div>
        <div class="deal-row">Создано: ${formatDate(deal.created_at)}</div>
        <div class="deal-row">Контрагент: ${counterparty}</div>
      `;
      item.addEventListener("click", () => openDealModal(deal.id));
      dealsList.appendChild(item);
    });
  };

  const loadSummary = async () => {
    const payload = await fetchJson("/api/summary");
    if (!payload?.ok) return;
  };

  const renderP2PItem = (ad, type) => {
    const item = document.createElement("div");
    item.className = "deal-item";
    const owner = ad.owner?.full_name || ad.owner?.username || "—";
    const limit = `₽${formatAmount(ad.min_rub, 2)}-₽${formatAmount(ad.max_rub, 2)}`;
    const price = `₽${formatAmount(ad.price_rub, 2)}/USDT`;
    if (type === "public") {
      item.innerHTML = `
        <div class="deal-header">
          <div class="deal-id">${owner} | ${limit} | ${price}</div>
          <div class="deal-status">${ad.side === "sell" ? "Продажа" : "Покупка"}</div>
        </div>
        <div class="deal-row">Доступно: ${formatAmount(ad.remaining_usdt)} USDT</div>
        <div class="deal-row">Банки: ${(ad.banks || []).join(", ") || "—"}</div>
      `;
      item.addEventListener("click", () => openP2PAd(ad.id));
    } else {
      const status = ad.active ? "Активно" : "Не активно";
      item.innerHTML = `
        <div class="deal-header">
          <div class="deal-id">${ad.side === "sell" ? "Продажа" : "Покупка"} • ${price}</div>
          <div class="deal-status">${status}</div>
        </div>
        <div class="deal-row">Остаток: ${formatAmount(ad.remaining_usdt)} / ${formatAmount(ad.total_usdt)} USDT</div>
        <div class="deal-row">Лимиты: ${limit}</div>
      `;
      item.addEventListener("click", () => openMyAd(ad.id));
    }
    return item;
  };

  const loadP2PSummary = async () => {
    const payload = await fetchJson("/api/p2p/summary");
    if (!payload?.ok) return;
    p2pTradingBadge.textContent = `${payload.active}/${payload.total}`;
    p2pTradingToggle.textContent = payload.trading ? "Торги: включены" : "Торги: остановлены";
  };

  const loadPublicAds = async (side) => {
    const payload = await fetchJson(`/api/p2p/ads?side=${side}`);
    if (!payload?.ok) return;
    state.p2pMode = side === "sell" ? "buy" : "sell";
    state.p2pAds = payload.ads || [];
    p2pList.innerHTML = "";
    if (!state.p2pAds.length) {
      p2pList.innerHTML = "<div class=\"deal-empty\">Нет объявлений.</div>";
      return;
    }
    state.p2pAds.forEach((ad) => p2pList.appendChild(renderP2PItem(ad, "public")));
  };

  const loadMyAds = async () => {
    const payload = await fetchJson("/api/p2p/my-ads");
    if (!payload?.ok) return;
    state.myAds = payload.ads || [];
    p2pList.innerHTML = "";
    if (!state.myAds.length) {
      p2pList.innerHTML = "<div class=\"deal-empty\">Объявлений пока нет.</div>";
      return;
    }
    state.myAds.forEach((ad) => p2pList.appendChild(renderP2PItem(ad, "my")));
  };

  const openP2PAd = async (adId) => {
    const ad = state.p2pAds.find((item) => item.id === adId);
    if (!ad) return;
    p2pModalTitle.textContent = `Объявление #${ad.public_id}`;
    p2pModalBody.innerHTML = `
      <div class="deal-detail-row"><span>Сторона:</span>${ad.side === "sell" ? "Продажа" : "Покупка"}</div>
      <div class="deal-detail-row"><span>Цена:</span>₽${formatAmount(ad.price_rub, 2)}/USDT</div>
      <div class="deal-detail-row"><span>Объём:</span>${formatAmount(ad.remaining_usdt)} USDT</div>
      <div class="deal-detail-row"><span>Лимиты:</span>₽${formatAmount(ad.min_rub, 2)}-₽${formatAmount(ad.max_rub, 2)}</div>
      <div class="deal-detail-row"><span>Банки:</span>${(ad.banks || []).join(", ") || "—"}</div>
      <div class="deal-detail-row"><span>Условия:</span>${ad.terms || "—"}</div>
    `;
    p2pModalActions.innerHTML = "";
    const input = document.createElement("input");
    input.type = "number";
    input.placeholder = "Сумма в RUB";
    input.className = "p2p-offer-input";
    const btn = document.createElement("button");
    btn.className = "btn primary";
    btn.textContent = ad.side === "sell" ? "Купить" : "Продать";
    btn.addEventListener("click", async () => {
      const rub = Number(input.value);
      if (!rub || rub <= 0) {
        log("Введите сумму в RUB", "warn");
        return;
      }
      const offer = await fetchJson(`/api/p2p/ads/${ad.id}/offer`, {
        method: "POST",
        body: JSON.stringify({ rub_amount: rub }),
      });
      if (offer?.ok) {
        p2pModal.classList.remove("open");
        await loadDeals();
        await loadPublicAds(ad.side === "sell" ? "sell" : "buy");
        if (offer.pay_url && tg?.openLink) {
          tg.openLink(offer.pay_url);
        }
      }
    });
    p2pModalActions.appendChild(input);
    p2pModalActions.appendChild(btn);
    p2pModal.classList.add("open");
  };

  const openMyAd = async (adId) => {
    const ad = state.myAds.find((item) => item.id === adId);
    if (!ad) return;
    p2pModalTitle.textContent = `Объявление #${ad.public_id}`;
    p2pModalBody.innerHTML = `
      <div class="deal-detail-row"><span>Сторона:</span>${ad.side === "sell" ? "Продажа" : "Покупка"}</div>
      <div class="deal-detail-row"><span>Цена:</span>₽${formatAmount(ad.price_rub, 2)}/USDT</div>
      <div class="deal-detail-row"><span>Объём:</span>${formatAmount(ad.remaining_usdt)} / ${formatAmount(ad.total_usdt)} USDT</div>
      <div class="deal-detail-row"><span>Лимиты:</span>₽${formatAmount(ad.min_rub, 2)}-₽${formatAmount(ad.max_rub, 2)}</div>
      <div class="deal-detail-row"><span>Банки:</span>${(ad.banks || []).join(", ") || "—"}</div>
      <div class="deal-detail-row"><span>Условия:</span>${ad.terms || "—"}</div>
      <div class="p2p-edit-grid">
        <label>Цена (RUB)
          <input id="adEditPrice" type="number" step="0.01" value="${ad.price_rub}" />
        </label>
        <label>Объём (USDT)
          <input id="adEditVolume" type="number" step="0.001" value="${ad.total_usdt}" />
        </label>
        <label>Лимиты (RUB)
          <input id="adEditLimits" type="text" value="${ad.min_rub}-${ad.max_rub}" />
        </label>
        <label>Условия
          <textarea id="adEditTerms" rows="2">${ad.terms || ""}</textarea>
        </label>
      </div>
      <div class="p2p-edit-banks" id="adEditBanks"></div>
    `;
    p2pModalActions.innerHTML = "";
    const toggle = document.createElement("button");
    toggle.className = "btn primary";
    toggle.textContent = ad.active ? "Отключить" : "Опубликовать";
    toggle.addEventListener("click", async () => {
      const updated = await fetchJson(`/api/p2p/ads/${ad.id}/toggle`, {
        method: "POST",
        body: JSON.stringify({ active: !ad.active }),
      });
      if (updated?.ok) {
        p2pModal.classList.remove("open");
        await loadMyAds();
        await loadP2PSummary();
      }
    });
    const del = document.createElement("button");
    del.className = "btn";
    del.textContent = "Удалить";
    del.addEventListener("click", async () => {
      const ok = await fetchJson(`/api/p2p/ads/${ad.id}/delete`, { method: "POST", body: "{}" });
      if (ok?.ok) {
        p2pModal.classList.remove("open");
        await loadMyAds();
        await loadP2PSummary();
      }
    });
    const save = document.createElement("button");
    save.className = "btn";
    save.textContent = "Сохранить";
    save.addEventListener("click", async () => {
      const price = document.getElementById("adEditPrice").value;
      const volume = document.getElementById("adEditVolume").value;
      const limits = document.getElementById("adEditLimits").value;
      const [minStr, maxStr] = (limits || "").split("-");
      const min = Number(minStr);
      const max = Number(maxStr);
      if (!min || !max || min > max) {
        log("Лимиты должны быть в формате 1000-10000", "warn");
        return;
      }
      const banks = Array.from(
        document.querySelectorAll("#adEditBanks input:checked")
      ).map((el) => el.value);
      const terms = document.getElementById("adEditTerms").value;
      const updated = await fetchJson(`/api/p2p/ads/${ad.id}`, {
        method: "POST",
        body: JSON.stringify({
          price_rub: price,
          total_usdt: volume,
          min_rub: min,
          max_rub: max,
          banks,
          terms,
        }),
      });
      if (updated?.ok) {
        p2pModal.classList.remove("open");
        await loadMyAds();
        await loadP2PSummary();
      }
    });
    p2pModalActions.appendChild(toggle);
    p2pModalActions.appendChild(save);
    p2pModalActions.appendChild(del);
    p2pModal.classList.add("open");
    const banksContainer = document.getElementById("adEditBanks");
    banksContainer.innerHTML = "";
    (p2pBanks?.querySelectorAll("input") || []).forEach((bankInput) => {
      const label = document.createElement("label");
      label.className = "p2p-bank";
      const input = document.createElement("input");
      input.type = "checkbox";
      input.value = bankInput.value;
      if (ad.banks?.includes(bankInput.value)) {
        input.checked = true;
      }
      label.appendChild(input);
      label.appendChild(document.createTextNode(bankInput.parentElement.textContent.trim()));
      banksContainer.appendChild(label);
    });
  };

  const loadBanks = async () => {
    const payload = await fetchJson("/api/p2p/banks");
    if (!payload?.ok) return;
    p2pBanks.innerHTML = "";
    payload.banks.forEach((bank) => {
      const label = document.createElement("label");
      label.className = "p2p-bank";
      const input = document.createElement("input");
      input.type = "checkbox";
      input.value = bank.key;
      label.appendChild(input);
      label.appendChild(document.createTextNode(bank.label));
      p2pBanks.appendChild(label);
    });
  };

  const setView = (viewId) => {
    views.forEach((view) => {
      view.classList.toggle("active", view.id === `view-${viewId}`);
    });
    navButtons.forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.view === viewId);
    });
  };

  const loadDisputes = async () => {
    const summary = await fetchJson("/api/disputes/summary");
    if (!summary?.ok || !summary.can_access) {
      if (disputesTab) disputesTab.style.display = "none";
      return;
    }
    if (disputesTab) disputesTab.style.display = "inline-flex";
    disputesCount.textContent = `${summary.count || 0}`;
    const payload = await fetchJson("/api/disputes");
    if (!payload?.ok) return;
    const disputes = payload.disputes || [];
    disputesList.innerHTML = "";
    if (!disputes.length) {
      disputesList.innerHTML = "<div class=\"deal-empty\">Открытых споров нет.</div>";
      return;
    }
    disputes.forEach((item) => {
      const row = document.createElement("div");
      row.className = "deal-item";
      row.innerHTML = `
        <div class="deal-header">
          <div class="deal-id">Спор #${item.id.slice(0, 6)} • Сделка #${item.public_id}</div>
          <div class="deal-status">${item.assigned_to ? "В работе" : "Новый"}</div>
        </div>
        <div class="deal-row">Причина: ${item.reason || "—"}</div>
        <div class="deal-row">Открыт: ${formatDate(item.opened_at)}</div>
      `;
      row.addEventListener("click", () => openDispute(item.id));
      disputesList.appendChild(row);
    });
  };

  const loadAdmin = async () => {
    const summary = await fetchJson("/api/admin/summary");
    if (!summary?.ok || !summary.can_access) {
      if (adminTab) adminTab.style.display = "none";
      return;
    }
    if (adminTab) adminTab.style.display = "inline-flex";
    const settings = await fetchJson("/api/admin/settings");
    if (settings?.ok) {
      adminRate.value = settings.usd_rate;
      adminFee.value = settings.fee_percent;
      adminWithdrawFee.value = settings.withdraw_fee_percent;
    }
    const mods = await fetchJson("/api/admin/moderators");
    if (mods?.ok) {
      adminModerators.innerHTML = "";
      mods.moderators.forEach((mod) => {
        const row = document.createElement("div");
        row.className = "admin-item";
        const name = mod.profile?.full_name || mod.profile?.username || mod.user_id;
        row.innerHTML = `
          <span>${name}</span>
          <span>Решено: ${mod.resolved}</span>
        `;
        const btn = document.createElement("button");
        btn.className = "btn";
        btn.textContent = "Исключить";
        btn.addEventListener("click", async () => {
          await fetchJson(`/api/admin/moderators/${mod.user_id}`, { method: "DELETE" });
          await loadAdmin();
        });
        row.appendChild(btn);
        adminModerators.appendChild(row);
      });
    }
    const merchants = await fetchJson("/api/admin/merchants");
    if (merchants?.ok) {
      adminMerchants.innerHTML = "";
      merchants.merchants.forEach((merchant) => {
        const row = document.createElement("div");
        row.className = "admin-item";
        const name =
          merchant.profile?.full_name || merchant.profile?.username || merchant.user_id;
        const stats = merchant.stats || {};
        row.innerHTML = `
          <span>${name}</span>
          <span>${stats.completed || 0}/${stats.total || 0}</span>
        `;
        const btn = document.createElement("button");
        btn.className = "btn";
        btn.textContent = "Исключить";
        btn.addEventListener("click", async () => {
          await fetchJson(`/api/admin/merchants/${merchant.user_id}/revoke`, {
            method: "POST",
            body: "{}",
          });
          await loadAdmin();
        });
        row.appendChild(btn);
        adminMerchants.appendChild(row);
      });
    }
  };

  const openDispute = async (disputeId) => {
    const payload = await fetchJson(`/api/disputes/${disputeId}`);
    if (!payload?.ok) return;
    const dispute = payload.dispute;
    p2pModalTitle.textContent = `Спор по сделке #${dispute.deal.public_id}`;
    const seller = dispute.seller?.full_name || dispute.seller?.username || "—";
    const buyer = dispute.buyer?.full_name || dispute.buyer?.username || "—";
    p2pModalBody.innerHTML = `
      <div class="deal-detail-row"><span>Продавец:</span>${seller}</div>
      <div class="deal-detail-row"><span>Мерчант:</span>${buyer}</div>
      <div class="deal-detail-row"><span>Причина:</span>${dispute.reason}</div>
      <div class="deal-detail-row"><span>Комментарий:</span>${dispute.comment || "—"}</div>
      <div class="deal-detail-row"><span>Открыт:</span>${formatDate(dispute.opened_at)}</div>
      <div class="deal-detail-row"><span>Сумма:</span>${formatAmount(dispute.deal.usdt_amount)} USDT</div>
      <div class="deal-detail-row"><span>Доказательства:</span>${dispute.evidence.length}</div>
    `;
    if (dispute.evidence.length) {
      const evidenceList = document.createElement("div");
      evidenceList.className = "p2p-evidence";
      dispute.evidence.forEach((item, index) => {
        const link = document.createElement("a");
        link.href = item.url || "#";
        link.textContent = `${index + 1}. ${item.kind}`;
        link.target = "_blank";
        link.rel = "noopener";
        evidenceList.appendChild(link);
      });
      p2pModalBody.appendChild(evidenceList);
    }
    p2pModalActions.innerHTML = "";
    if (!dispute.assigned_to) {
      const take = document.createElement("button");
      take.className = "btn primary";
      take.textContent = "Взять в работу";
      take.addEventListener("click", async () => {
        const res = await fetchJson(`/api/disputes/${dispute.id}/assign`, { method: "POST", body: "{}" });
        if (res?.ok) {
          await loadDisputes();
          p2pModal.classList.remove("open");
        }
      });
      p2pModalActions.appendChild(take);
    }
    const sellerInput = document.createElement("input");
    sellerInput.className = "p2p-offer-input";
    sellerInput.placeholder = "USDT продавцу";
    const buyerInput = document.createElement("input");
    buyerInput.className = "p2p-offer-input";
    buyerInput.placeholder = "USDT мерчанту";
    const resolve = document.createElement("button");
    resolve.className = "btn";
    resolve.textContent = "Закрыть спор";
    resolve.addEventListener("click", async () => {
      const sellerAmount = Number(sellerInput.value || 0);
      const buyerAmount = Number(buyerInput.value || 0);
      const res = await fetchJson(`/api/disputes/${dispute.id}/resolve`, {
        method: "POST",
        body: JSON.stringify({ seller_amount: sellerAmount, buyer_amount: buyerAmount }),
      });
      if (res?.ok) {
        p2pModal.classList.remove("open");
        await loadDisputes();
      }
    });
    p2pModalActions.appendChild(sellerInput);
    p2pModalActions.appendChild(buyerInput);
    p2pModalActions.appendChild(resolve);
    p2pModal.classList.add("open");
  };

  const renderDealModal = (deal) => {
    dealModalTitle.textContent = `Сделка #${deal.public_id}`;
    const counterparty = deal.counterparty?.full_name || deal.counterparty?.username || "—";
    const roleLabel = deal.role === "seller" ? "Продавец" : "Покупатель";
    dealModalBody.innerHTML = `
      <div class="deal-detail-row"><span>Роль:</span>${roleLabel}</div>
      <div class="deal-detail-row"><span>Статус:</span>${statusLabel(deal)}</div>
      <div class="deal-detail-row"><span>Наличные:</span>₽${formatAmount(deal.cash_rub, 2)}</div>
      <div class="deal-detail-row"><span>USDT:</span>${formatAmount(deal.usdt_amount)} USDT</div>
      <div class="deal-detail-row"><span>Курс:</span>1 USDT = ${formatAmount(deal.rate, 2)} RUB</div>
      <div class="deal-detail-row"><span>Создано:</span>${formatDate(deal.created_at)}</div>
      <div class="deal-detail-row"><span>Банкомат:</span>${deal.atm_bank || "—"}</div>
      <div class="deal-detail-row"><span>Контрагент:</span>${counterparty}</div>
    `;
    dealModalActions.innerHTML = "";
    const actions = deal.actions || {};
    const addAction = (label, handler, primary = false) => {
      const btn = document.createElement("button");
      btn.className = `btn ${primary ? "primary" : ""}`;
      btn.textContent = label;
      btn.addEventListener("click", handler);
      dealModalActions.appendChild(btn);
    };
    if (actions.cancel) {
      addAction("Отменить сделку", () => dealAction("cancel", deal.id), false);
    }
    if (actions.seller_ready) {
      addAction("Готов отправить QR", () => dealAction("seller-ready", deal.id), true);
    }
    if (actions.buyer_ready) {
      addAction("Готов сканировать", () => dealAction("buyer-ready", deal.id), true);
    }
    if (actions.confirm_seller) {
      addAction("Получил нал", () => dealAction("confirm-seller", deal.id), true);
    }
    if (actions.confirm_buyer) {
      addAction("Успешно снял", () => dealAction("confirm-buyer", deal.id), true);
    }
    if (actions.open_dispute) {
      addAction("Открыть спор", () => dealAction("open-dispute", deal.id), false);
    }
  };

  const openDealModal = async (dealId) => {
    const payload = await fetchJson(`/api/deals/${dealId}`);
    if (!payload?.ok) return;
    renderDealModal(payload.deal);
    dealModal.classList.add("open");
  };

  const dealAction = async (action, dealId) => {
    const path = `/api/deals/${dealId}/${action}`;
    const payload = await fetchJson(path);
    if (!payload?.ok) return;
    renderDealModal(payload.deal);
    await loadDeals();
  };

  const initTelegram = async () => {
    if (tg) {
      tg.ready();
      tg.expand();
      state.initData = tg.initData || "";
      applyTheme(detectTheme());
    } else {
      applyTheme(detectTheme());
      log("WebApp API не найден. Проверьте запуск через Telegram.", "warn");
    }
    const user = await fetchMe();
    if (user) {
      setAuthState(user);
      log(`Готово. Пользователь: ${user.username || user.first_name || user.id}`);
      await loadSummary();
      await loadProfile();
      await loadBalance();
      await loadDeals();
      await loadP2PSummary();
      await loadPublicAds("sell");
      if (p2pBalanceHint && state.balance !== null) {
        p2pBalanceHint.textContent = `Баланс: ${formatAmount(state.balance)} USDT`;
      }
      await loadBanks();
      await loadDisputes();
      await loadAdmin();
    }
  };

  const renderReviews = (reviews, rating) => {
    reviewsList.innerHTML = "";
    const filtered = reviews.filter((item) => item.rating === rating);
    if (!filtered.length) {
      reviewsList.innerHTML = "<div class=\"deal-empty\">Пока нет отзывов.</div>";
      return;
    }
    filtered.forEach((item) => {
      const row = document.createElement("div");
      row.className = "deal-item";
      const author = item.author?.full_name || item.author?.username || "—";
      row.innerHTML = `
        <div class="deal-header">
          <div class="deal-id">${author}</div>
          <div class="deal-status">${item.rating > 0 ? "Плюс" : "Минус"}</div>
        </div>
        <div class="deal-row">${item.comment || "Без комментария"}</div>
        <div class="deal-row">Сделка: #${item.deal_id.slice(0, 6)}</div>
        <div class="deal-row">${formatDate(item.created_at)}</div>
      `;
      reviewsList.appendChild(row);
    });
  };

  const loadReviews = async () => {
    const payload = await fetchJson("/api/reviews");
    if (!payload?.ok) return null;
    reviewsSummary.textContent = `👍 ${payload.positive} • 👎 ${payload.negative}`;
    return payload.reviews || [];
  };

  themeToggle?.addEventListener("click", () => {
    const current = document.documentElement.dataset.theme || "light";
    applyTheme(current === "light" ? "dark" : "light");
  });

  navButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      setView(btn.dataset.view);
    });
  });

  dealModalClose?.addEventListener("click", () => {
    dealModal.classList.remove("open");
  });

  p2pModalClose?.addEventListener("click", () => {
    p2pModal.classList.remove("open");
  });

  p2pCreateClose?.addEventListener("click", () => {
    p2pCreateModal.classList.remove("open");
  });

  p2pCreateBtn?.addEventListener("click", () => {
    p2pCreateModal.classList.add("open");
  });

  p2pVolumeMax?.addEventListener("click", async () => {
    if (state.balance !== null) {
      p2pVolume.value = state.balance;
      return;
    }
    const balancePayload = await fetchJson("/api/balance");
    if (balancePayload?.ok) {
      p2pVolume.value = balancePayload.balance;
    }
  });

  p2pTradingToggle?.addEventListener("click", async () => {
    const payload = await fetchJson("/api/p2p/summary");
    if (!payload?.ok) return;
    const next = !payload.trading;
    const updated = await fetchJson("/api/p2p/trading", {
      method: "POST",
      body: JSON.stringify({ enabled: next }),
    });
    if (updated?.ok) {
      await loadP2PSummary();
    }
  });

  p2pBuyBtn?.addEventListener("click", () => {
    p2pBuyBtn.classList.add("primary");
    p2pSellBtn.classList.remove("primary");
    p2pMyAdsBtn.classList.remove("primary");
    loadPublicAds("sell");
  });

  p2pSellBtn?.addEventListener("click", () => {
    p2pSellBtn.classList.add("primary");
    p2pBuyBtn.classList.remove("primary");
    p2pMyAdsBtn.classList.remove("primary");
    loadPublicAds("buy");
  });

  p2pMyAdsBtn?.addEventListener("click", () => {
    p2pMyAdsBtn.classList.add("primary");
    p2pBuyBtn.classList.remove("primary");
    p2pSellBtn.classList.remove("primary");
    loadMyAds();
  });

  p2pCreateForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const [minStr, maxStr] = (p2pLimits.value || "").split("-");
    const min = Number(minStr);
    const max = Number(maxStr);
    if (!min || !max || min > max) {
      log("Лимиты должны быть в формате 1000-10000", "warn");
      return;
    }
    const banks = Array.from(p2pBanks.querySelectorAll("input:checked")).map((el) => el.value);
    const payload = await fetchJson("/api/p2p/ads", {
      method: "POST",
      body: JSON.stringify({
        side: p2pSide.value,
        total_usdt: p2pVolume.value,
        price_rub: p2pPrice.value,
        min_rub: min,
        max_rub: max,
        banks,
        terms: p2pTerms.value,
      }),
    });
    if (payload?.ok) {
      p2pCreateModal.classList.remove("open");
      p2pCreateForm.reset();
      await loadMyAds();
      await loadP2PSummary();
    }
  });

  adminSaveRates?.addEventListener("click", async () => {
    await fetchJson("/api/admin/settings", {
      method: "POST",
      body: JSON.stringify({
        usd_rate: adminRate.value,
        fee_percent: adminFee.value,
        withdraw_fee_percent: adminWithdrawFee.value,
      }),
    });
    await loadAdmin();
  });

  adminAddModerator?.addEventListener("click", async () => {
    const username = adminModeratorUsername.value.trim();
    if (!username) {
      log("Укажи username", "warn");
      return;
    }
    await fetchJson("/api/admin/moderators", {
      method: "POST",
      body: JSON.stringify({ username }),
    });
    adminModeratorUsername.value = "";
    await loadAdmin();
  });

  reviewsOpen?.addEventListener("click", async () => {
    const reviews = await loadReviews();
    if (!reviews) return;
    renderReviews(reviews, 1);
    reviewsModal.classList.add("open");
  });

  reviewsClose?.addEventListener("click", () => {
    reviewsModal.classList.remove("open");
  });

  reviewTabButtons.forEach((btn) => {
    btn.addEventListener("click", async () => {
      reviewTabButtons.forEach((item) => item.classList.remove("active"));
      btn.classList.add("active");
      const reviews = await loadReviews();
      if (!reviews) return;
      const rating = btn.dataset.tab === "positive" ? 1 : -1;
      renderReviews(reviews, rating);
    });
  });

  profileQuick?.addEventListener("click", () => {
    profileQuickName.textContent = userBadge.textContent || "—";
    profileQuickUsername.textContent = profileNameTop?.textContent || "—";
    profileModal.classList.add("open");
  });

  profileModalClose?.addEventListener("click", () => {
    profileModal.classList.remove("open");
  });

  profileGo?.addEventListener("click", () => {
    setView("profile");
    profileModal.classList.remove("open");
  });

  sellQuick?.addEventListener("click", () => {
    sellModal.classList.add("open");
  });

  sellModalClose?.addEventListener("click", () => {
    sellModal.classList.remove("open");
  });

  sellForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const amount = Number(sellAmount.value);
    if (!amount || amount <= 0) {
      log("Введите сумму в RUB", "warn");
      return;
    }
    const payload = await fetchJson("/api/deals", {
      method: "POST",
      body: JSON.stringify({ rub_amount: amount }),
    });
    if (payload?.ok) {
      sellModal.classList.remove("open");
      sellForm.reset();
      await loadDeals();
      setView("deals");
    }
  });

  initTelegram();
})();
