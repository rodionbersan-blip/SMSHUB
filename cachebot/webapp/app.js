(() => {
  const tg = window.Telegram?.WebApp;
  const logEl = document.getElementById("log");
  const successAnim = document.getElementById("successAnim");
  const centerNotice = document.getElementById("centerNotice");
  const sellQuick = document.getElementById("sellQuick");
  const sellModal = document.getElementById("sellModal");
  const sellModalClose = document.getElementById("sellModalClose");
  const sellForm = document.getElementById("sellForm");
  const sellAmount = document.getElementById("sellAmount");
  const topupOpen = document.getElementById("topupOpen");
  const topupModal = document.getElementById("topupModal");
  const topupClose = document.getElementById("topupClose");
  const topupForm = document.getElementById("topupForm");
  const topupAmount = document.getElementById("topupAmount");
  const withdrawModal = document.getElementById("withdrawModal");
  const withdrawClose = document.getElementById("withdrawClose");
  const withdrawForm = document.getElementById("withdrawForm");
  const withdrawAmount = document.getElementById("withdrawAmount");
  const userBadge = document.getElementById("userBadge");
  const profileNameTop = document.getElementById("profileNameTop");
  const profileAvatar = document.getElementById("profileAvatar");
  const profileAvatarLarge = document.getElementById("profileAvatarLarge");
  const profileDisplayName = document.getElementById("profileDisplayName");
  const profileQuick = document.getElementById("profileQuick");
  const profileModal = document.getElementById("profileModal");
  const profileModalClose = document.getElementById("profileModalClose");
  const profileModalAvatar = document.getElementById("profileModalAvatar");
  const profileQuickName = document.getElementById("profileQuickName");
  const profileQuickUsername = document.getElementById("profileQuickUsername");
  const profileQuickBalance = document.getElementById("profileQuickBalance");
  const profileQuickReserved = document.getElementById("profileQuickReserved");
  const profileModalTopup = document.getElementById("profileModalTopup");
  const profileModalWithdraw = document.getElementById("profileModalWithdraw");
  const profileGo = document.getElementById("profileGo");
  const profileEditOpen = document.getElementById("profileEditOpen");
  const profileEditModal = document.getElementById("profileEditModal");
  const profileEditClose = document.getElementById("profileEditClose");
  const profileEditForm = document.getElementById("profileEditForm");
  const profileEditName = document.getElementById("profileEditName");
  const profileEditAvatar = document.getElementById("profileEditAvatar");
  const profileEditPreview = document.getElementById("profileEditPreview");
  const themeToggle = document.getElementById("themeToggle");
  const navButtons = document.querySelectorAll(".nav-btn");
  const views = document.querySelectorAll(".view");

  const profileName = document.getElementById("profileName");
  const profileUsername = document.getElementById("profileUsername");
  const profileRegistered = document.getElementById("profileRegistered");
  const profileRole = document.getElementById("profileRole");
  const profileRoleCard = document.getElementById("profileRoleCard");
  const profileMerchantSince = document.getElementById("profileMerchantSince");
  const profileBalance = document.getElementById("profileBalance");
  const profileBalanceReserved = document.getElementById("profileBalanceReserved");
  const profileWithdraw = document.getElementById("profileWithdraw");
  const profileDealsTotal = document.getElementById("profileDealsTotal");
  const profileDealsSuccess = document.getElementById("profileDealsSuccess");
  const profileReviewsCount = document.getElementById("profileReviewsCount");
  const dealsCount = document.getElementById("dealsCount");
  const dealsList = document.getElementById("dealsList");
  const dealsPagination = document.getElementById("dealsPagination");
  const dealModal = document.getElementById("dealModal");
  const dealModalTitle = document.getElementById("dealModalTitle");
  const dealModalBody = document.getElementById("dealModalBody");
  const dealModalActions = document.getElementById("dealModalActions");
  const dealModalClose = document.getElementById("dealModalClose");
  const quickDealsBtn = document.getElementById("quickDealsBtn");
  const quickDealsBadge = document.getElementById("quickDealsBadge");
  const quickDealsPanel = document.getElementById("quickDealsPanel");
  const quickDealsList = document.getElementById("quickDealsList");
  const quickDealsClose = document.getElementById("quickDealsClose");
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
  const userModal = document.getElementById("userModal");
  const userModalTitle = document.getElementById("userModalTitle");
  const userModalBody = document.getElementById("userModalBody");
  const userModalClose = document.getElementById("userModalClose");
  const userModalReviews = document.getElementById("userModalReviews");
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
  const systemPanel = document.getElementById("systemPanel");
  const reviewsOpen = document.getElementById("reviewsOpen");
  const reviewsModal = document.getElementById("reviewsModal");
  const reviewsClose = document.getElementById("reviewsClose");
  const reviewsList = document.getElementById("reviewsList");
  const reviewsSummary = document.getElementById("reviewsSummary");
  const reviewsPagination = document.getElementById("reviewsPagination");
  const reviewsTabs = document.querySelector(".reviews-tabs");
  const reviewTabButtons = document.querySelectorAll(".reviews-tabs .tab-btn");

  const state = {
    user: null,
    initData: "",
    balance: null,
    balanceReserved: 0,
    p2pMode: "buy",
    p2pAds: [],
    myAds: [],
    reviews: [],
    reviewsPage: 0,
    reviewsRating: "all",
    unreadDeals: new Set(),
  };

  const unreadStorageKey = "quickDealsUnread";
  const loadUnreadDeals = () => {
    try {
      const raw = JSON.parse(window.localStorage.getItem(unreadStorageKey) || "[]");
      return new Set(Array.isArray(raw) ? raw : []);
    } catch {
      return new Set();
    }
  };
  const persistUnreadDeals = () => {
    try {
      window.localStorage.setItem(unreadStorageKey, JSON.stringify([...state.unreadDeals]));
    } catch {
      // ignore storage errors
    }
  };
  state.unreadDeals = loadUnreadDeals();

  const log = (message, type = "info") => {
    if (!logEl) return;
    const line = document.createElement("div");
    line.className = `log-line ${type}`;
    line.textContent = message;
    logEl.prepend(line);
  };

  let successAnimInstance = null;
  let successAnimHideTimer = null;
  let noticeTimer = null;
  const showNotice = (message) => {
    if (!centerNotice) return;
    centerNotice.textContent = message;
    centerNotice.classList.add("show");
    if (noticeTimer) {
      window.clearTimeout(noticeTimer);
    }
    noticeTimer = window.setTimeout(() => {
      centerNotice.classList.remove("show");
    }, 2200);
  };
  const playSuccessAnimation = () => {
    if (!successAnim || !window.lottie) {
      return;
    }
    if (!successAnimInstance) {
      successAnimInstance = window.lottie.loadAnimation({
        container: successAnim,
        renderer: "svg",
        loop: false,
        autoplay: false,
        path: "/app/assets/withdraw-success.json",
      });
    }
    successAnim.classList.remove("fade-out");
    successAnim.classList.add("show", "blur");
    if (successAnimHideTimer) {
      window.clearTimeout(successAnimHideTimer);
      successAnimHideTimer = null;
    }
    const startSegment = () => {
      const totalSeconds = successAnimInstance.getDuration(false) || 0;
      const handleFail = () => {
        successAnim.classList.add("fade-out");
        successAnim.classList.remove("blur");
        window.setTimeout(() => {
          successAnim.classList.remove("show", "fade-out");
          successAnimInstance.stop();
        }, 350);
        successAnimInstance.removeEventListener("data_failed", handleFail);
      };
      successAnimInstance.removeEventListener("data_failed", handleFail);
      successAnimInstance.addEventListener("data_failed", handleFail);
      successAnimInstance.setSpeed(1);
      successAnimInstance.goToAndPlay(0, true);
      if (totalSeconds) {
        successAnimHideTimer = window.setTimeout(() => {
          successAnim.classList.add("fade-out");
          successAnim.classList.remove("blur");
          window.setTimeout(() => {
            successAnim.classList.remove("show", "fade-out");
            successAnimInstance.stop();
          }, 350);
        }, Math.ceil(totalSeconds * 1000) + 150);
      }
    };
    if (successAnimInstance.isLoaded) {
      startSegment();
    } else {
      successAnimInstance.addEventListener("DOMLoaded", startSegment, { once: true });
      successAnimHideTimer = window.setTimeout(() => {
        successAnim.classList.add("fade-out");
        successAnim.classList.remove("blur");
        window.setTimeout(() => {
          successAnim.classList.remove("show", "fade-out");
          successAnimInstance?.stop();
        }, 350);
      }, 2000);
    }
  };

  const updateModalLock = () => {
    document.body.classList.toggle("modal-open", Boolean(document.querySelector(".modal.open")));
  };

  const observeModals = () => {
    const observer = new MutationObserver(updateModalLock);
    document.querySelectorAll(".modal").forEach((modal) => {
      observer.observe(modal, { attributes: true, attributeFilter: ["class"] });
    });
    updateModalLock();
  };

  const openLink = (url) => {
    if (!url) return;
    if (tg?.openTelegramLink && url.includes("t.me/")) {
      tg.openTelegramLink(url);
      return;
    }
    if (tg?.openLink) {
      tg.openLink(url);
      return;
    }
    window.open(url, "_blank");
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

  const updateThemeToggle = (theme) => {
    if (!themeToggle) return;
    const label = themeToggle.querySelector(".theme-switch-label");
    const icon = themeToggle.querySelector(".theme-switch-icon");
    if (label) label.textContent = theme === "dark" ? "Ночь" : "День";
    if (icon) icon.textContent = theme === "dark" ? "🌙" : "☀️";
    themeToggle.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");
  };

  const detectTheme = () => {
    if (tg?.colorScheme) return tg.colorScheme;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  };

  const setAvatarNode = (node, display, avatarUrl) => {
    if (!node) return;
    if (avatarUrl) {
      node.style.backgroundImage = `url(${avatarUrl})`;
      node.textContent = "";
    } else {
      node.style.backgroundImage = "";
      node.textContent = display.slice(0, 2).toUpperCase();
    }
  };

  const setAuthState = (user) => {
    state.user = user;
    const display =
      user?.display_name ||
      user?.full_name ||
      user?.first_name ||
      (user?.username ? `@${user.username}` : "Гость");
    userBadge.textContent = display;
    if (profileNameTop) profileNameTop.textContent = display;
    setAvatarNode(profileAvatar, display, user?.avatar_url);
    setAvatarNode(profileAvatarLarge, display, user?.avatar_url);
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

  const formatReviewDate = (iso) => {
    if (!iso) return "—";
    const dt = new Date(iso);
    if (Number.isNaN(dt.getTime())) return "—";
    const datePart = new Intl.DateTimeFormat("ru-RU", {
      day: "numeric",
      month: "long",
      year: "numeric",
    }).format(dt).replace(" г.", "");
    const timePart = new Intl.DateTimeFormat("ru-RU", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    }).format(dt);
    return `${datePart} ${timePart}`;
  };

  const statusLabel = (deal) => {
    if (deal.status === "open") return "Ожидаем Мерчанта";
    if (deal.status === "pending") return "Ожидаем принятия";
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

  const applyProfileStats = (stats) => {
    if (profileDealsTotal) {
      profileDealsTotal.textContent = `Сделок: ${stats.total_deals ?? 0}`;
    }
    if (profileDealsSuccess) {
      profileDealsSuccess.textContent = `Успешные: ${stats.success_percent ?? 0}%`;
    }
    if (profileReviewsCount) {
      profileReviewsCount.textContent = `Отзывы: ${stats.reviews_count ?? 0}`;
    }
  };

  const loadProfile = async () => {
    const payload = await fetchJson("/api/profile");
    if (!payload?.ok) return;
    const { data } = payload;
    const profile = data?.profile;
    state.userId = profile?.user_id ?? null;
    const display = profile?.display_name || profile?.full_name || "Без имени";
    profileName.textContent = display;
    if (profileDisplayName) profileDisplayName.textContent = display;
    if (profileUsername) {
      const username = profile?.username?.trim();
      profileUsername.textContent = username ? `@${username}` : "";
      profileUsername.style.display = "none";
    }
    profileRegistered.textContent = profile?.registered_at
      ? `Регистрация: ${formatDate(profile.registered_at)}`
      : "Регистрация: —";
    const isMerchant = data?.role === "buyer";
    if (profileRoleCard) {
      profileRoleCard.style.display = isMerchant ? "" : "none";
    }
    if (profileRole) {
      profileRole.textContent = isMerchant ? "Мерчант" : "";
    }
    if (profileMerchantSince) {
      profileMerchantSince.textContent = isMerchant && data?.merchant_since
        ? `Мерчант с: ${formatDate(data.merchant_since)}`
        : "";
    }
    const stats = data?.stats || {};
    state.profileStats = {
      total_deals: stats.total_deals ?? 0,
      success_percent: stats.success_percent ?? 0,
      fail_percent: stats.fail_percent ?? 0,
      reviews_count: stats.reviews_count ?? 0,
    };
    applyProfileStats(state.profileStats);
    setAvatarNode(profileAvatar, display, profile?.avatar_url);
    setAvatarNode(profileAvatarLarge, display, profile?.avatar_url);
  };

  const loadBalance = async () => {
    const payload = await fetchJson("/api/balance");
    if (!payload?.ok) return;
    const available = Number(payload.balance ?? 0);
    const reserved = Number(payload.reserved ?? 0);
    state.balance = available;
    state.balanceReserved = reserved;
    if (profileBalance) {
      profileBalance.textContent = `${formatAmount(available, 2)} USDT`;
    }
    if (profileBalanceReserved) {
      profileBalanceReserved.textContent = `В резерве: ${formatAmount(reserved, 2)} USDT`;
    }
    if (profileQuickBalance) {
      profileQuickBalance.textContent = `${formatAmount(available, 2)} USDT`;
    }
    if (profileQuickReserved) {
      profileQuickReserved.textContent = `В резерве: ${formatAmount(reserved, 2)} USDT`;
    }
  };

  profileWithdraw?.addEventListener("click", () => {
    withdrawModal?.classList.add("open");
  });

  const renderDealsPage = () => {
    const deals = state.deals || [];
    const page = state.dealsPage || 0;
    const perPage = 5;
    const totalPages = Math.max(1, Math.ceil(deals.length / perPage));
    const safePage = Math.max(0, Math.min(page, totalPages - 1));
    state.dealsPage = safePage;
    const start = safePage * perPage;
    const chunk = deals.slice(start, start + perPage);
    dealsList.innerHTML = "";
    if (!deals.length) {
      dealsList.innerHTML = "<div class=\"deal-empty\">Сделок пока нет.</div>";
      if (dealsPagination) {
        dealsPagination.innerHTML = "";
      }
      return;
    }
    chunk.forEach((deal) => {
      const item = document.createElement("div");
      item.className = "deal-item";
      item.innerHTML = `
        <div class="deal-header">
          <div class="deal-id">Сделка #${deal.public_id}</div>
          <div class="deal-status">${statusLabel(deal)}</div>
        </div>
        <div class="deal-row">Сумма: ₽${formatAmount(deal.cash_rub, 2)} | ${formatAmount(
          deal.usdt_amount
        )} USDT</div>
        <div class="deal-row">Курс: 1 USDT = ${formatAmount(deal.rate, 2)} RUB</div>
        <div class="deal-row">Создано: ${formatDate(deal.created_at)}</div>
      `;
      item.addEventListener("click", () => openDealModal(deal.id));
      dealsList.appendChild(item);
    });
    if (dealsPagination) {
      const prevDisabled = safePage <= 0;
      const nextDisabled = safePage >= totalPages - 1;
      dealsPagination.innerHTML = `
        <button class="btn" ${prevDisabled ? "disabled" : ""} data-page="prev">Назад</button>
        <div class="page-info">Стр. ${safePage + 1} / ${totalPages}</div>
        <button class="btn" ${nextDisabled ? "disabled" : ""} data-page="next">Вперёд</button>
      `;
      const prevBtn = dealsPagination.querySelector("[data-page=\"prev\"]");
      const nextBtn = dealsPagination.querySelector("[data-page=\"next\"]");
      prevBtn?.addEventListener("click", () => {
        if (state.dealsPage > 0) {
          state.dealsPage -= 1;
          renderDealsPage();
        }
      });
      nextBtn?.addEventListener("click", () => {
        if (state.dealsPage < totalPages - 1) {
          state.dealsPage += 1;
          renderDealsPage();
        }
      });
    }
  };

  const loadDeals = async () => {
    const payload = await fetchJson("/api/my-deals");
    if (!payload?.ok) return;
    const deals = payload.deals || [];
    dealsCount.textContent = `${deals.length}`;
    state.deals = deals;
    state.dealsPage = 0;
    syncUnreadDeals(deals);
    updateQuickDealsButton(deals);
    const totalDeals = deals.length;
    const successDeals = deals.filter((deal) => deal.status === "completed").length;
    const failedDeals = deals.filter(
      (deal) => deal.status === "canceled" || deal.status === "expired"
    ).length;
    const successPercent = totalDeals ? Math.round((successDeals / totalDeals) * 100) : 0;
    const failPercent = totalDeals ? Math.round((failedDeals / totalDeals) * 100) : 0;
    const currentStats = state.profileStats || {
      total_deals: 0,
      success_percent: 0,
      fail_percent: 0,
      reviews_count: 0,
    };
    state.profileStats = {
      total_deals: totalDeals,
      success_percent: successPercent,
      fail_percent: failPercent,
      reviews_count: currentStats.reviews_count ?? 0,
    };
    applyProfileStats(state.profileStats);
    renderDealsPage();
  };

  const updateQuickDealsButton = (activeDeals) => {
    if (!quickDealsBtn) return;
    const deals = activeDeals || [];
    if (quickDealsBadge) {
      const count = state.unreadDeals.size;
      quickDealsBadge.textContent = count > 9 ? "9+" : `${count}`;
      quickDealsBadge.classList.toggle("show", count > 0);
    }
  };

  const syncUnreadDeals = (deals) => {
    if (!state.userId) return;
    const incomingPending = new Set();
    (deals || []).forEach((deal) => {
      const isPending = deal.status === "pending" && deal.offer_initiator_id;
      if (isPending) {
        incomingPending.add(deal.id);
        state.unreadDeals.add(deal.id);
      }
    });
    const nextUnread = new Set();
    state.unreadDeals.forEach((dealId) => {
      if (incomingPending.has(dealId)) {
        nextUnread.add(dealId);
      }
    });
    state.unreadDeals = nextUnread;
    persistUnreadDeals();
  };

  const renderQuickDeals = () => {
    if (!quickDealsList) return;
    const deals = (state.deals || []).filter(
      (deal) => !["completed", "canceled", "expired"].includes(deal.status)
    );
    quickDealsList.innerHTML = "";
    if (!deals.length) {
      quickDealsList.innerHTML = '<div class="deal-empty">Активных сделок нет.</div>';
      return;
    }
    deals.forEach((deal) => {
      const row = document.createElement("div");
      row.className = "quick-deal-item";
      const amountText = `₽${formatAmount(deal.cash_rub, 0)} · ${formatAmount(
        deal.usdt_amount,
        3
      )} USDT`;
      row.innerHTML = `
        <div class="quick-deal-info">
          <div class="quick-deal-id">Сделка #${deal.public_id}</div>
          <div class="quick-deal-meta">${amountText}</div>
        </div>
        <div class="quick-deal-status">${statusLabel(deal)}</div>
      `;
      row.addEventListener("click", () => {
        quickDealsPanel?.classList.remove("open");
        openDealModal(deal.id);
      });
      quickDealsList.appendChild(row);
    });
  };

  const loadSummary = async () => {
    const payload = await fetchJson("/api/summary");
    if (!payload?.ok) return;
  };

  const renderP2PItem = (ad, type) => {
    const item = document.createElement("div");
    item.className = "deal-item";
    const sideLabel = ad.side === "sell" ? "Продажа" : "Покупка";
    const limit = `₽${formatAmount(ad.min_rub, 0)}-₽${formatAmount(ad.max_rub, 0)}`;
    const price = `${formatAmount(ad.price_rub, 0)}р`;
    if (type === "public") {
      item.innerHTML = `
        <div class="deal-header">
          <div class="deal-id">${sideLabel} • USDT - ${price}</div>
          <div class="deal-status">${sideLabel}</div>
        </div>
        <div class="deal-row">Объем: ${formatAmount(ad.remaining_usdt, 0)} USDT</div>
        <div class="deal-row">Лимиты: ${limit}</div>
      `;
      item.addEventListener("click", () => openP2PAd(ad.id));
    } else {
      const status = ad.active ? "Активно" : "Не активно";
      const statusClass = ad.active ? "status-ok" : "status-bad";
      item.innerHTML = `
        <div class="deal-header">
          <div class="deal-id">${sideLabel} • USDT - ${price}</div>
          <div class="deal-status ${statusClass}">${status}</div>
        </div>
        <div class="deal-row">Объем: ${formatAmount(ad.remaining_usdt, 0)} / ${formatAmount(
        ad.total_usdt,
        0
      )} USDT</div>
        <div class="deal-row">Лимиты: ${limit}</div>
      `;
      item.addEventListener("click", () => openMyAd(ad.id));
    }
    return item;
  };

  const openUserProfile = async (userId) => {
    if (!userModal || !userModalBody) return;
    const payload = await fetchJson(`/api/users/${userId}`);
    if (!payload?.ok) return;
    const data = payload.data || {};
    const profile = data.profile || {};
    const stats = data.stats || {};
    const display = profile.display_name || "Без имени";
    const registered = profile.registered_at ? formatDate(profile.registered_at) : "—";
    userModalTitle.textContent = "Профиль";
    userModalBody.innerHTML = `
      <div class="profile-hero">
        <div class="profile-avatar-large" id="userModalAvatar">BC</div>
        <div>
          <div class="profile-value">${display}</div>
          <div class="profile-muted">Регистрация: ${registered}</div>
        </div>
      </div>
      <div class="profile-card">
        <div class="profile-title">Статистика</div>
        <div class="profile-value">Сделок: ${stats.total_deals ?? 0}</div>
        <div class="profile-muted">Успешные: ${stats.success_percent ?? 0}%</div>
        <div class="profile-muted">Отзывы: ${stats.reviews_count ?? 0}</div>
      </div>
    `;
    const avatarNode = userModalBody.querySelector("#userModalAvatar");
    setAvatarNode(avatarNode, display, profile.avatar_url);
    userModal.classList.add("open");
    if (userModalReviews) {
      userModalReviews.onclick = async () => {
        const reviewsPayload = await fetchJson(`/api/reviews?user_id=${userId}`);
        if (!reviewsPayload?.ok) return;
        renderReviews(reviewsPayload.reviews || [], "all");
        reviewsModal.classList.add("open");
        window.setTimeout(updateReviewsIndicator, 0);
      };
    }
  };

  const loadP2PSummary = async () => {
    const payload = await fetchJson("/api/p2p/summary");
    if (!payload?.ok) return;
    p2pTradingBadge.textContent = `${payload.active}/${payload.total}`;
    p2pTradingToggle.textContent = payload.trading ? "Торги: включены" : "Торги: остановлены";
    if (p2pMyAdsBtn) {
      p2pMyAdsBtn.textContent = "Объявления";
    }
    if (p2pTradingToggle) {
      p2pTradingToggle.classList.toggle("status-ok", payload.trading);
      p2pTradingToggle.classList.toggle("status-bad", !payload.trading);
    }
  };

  const loadPublicAds = async (side) => {
    const payload = await fetchJson(`/api/p2p/ads?side=${side}`);
    if (!payload?.ok) return;
    state.p2pMode = side === "sell" ? "buy" : "sell";
    state.p2pAds = payload.ads || [];
    p2pList.innerHTML = "";
    if (p2pCreateBtn) p2pCreateBtn.style.display = "none";
    if (p2pTradingToggle) p2pTradingToggle.style.display = "none";
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
    if (p2pCreateBtn) p2pCreateBtn.style.display = "";
    if (p2pTradingToggle) p2pTradingToggle.style.display = "";
    if (!state.myAds.length) {
      p2pList.innerHTML = "<div class=\"deal-empty\">Объявлений пока нет.</div>";
      return;
    }
    state.myAds.forEach((ad) => p2pList.appendChild(renderP2PItem(ad, "my")));
  };

  const openP2PAd = async (adId) => {
    const ad = state.p2pAds.find((item) => item.id === adId);
    if (!ad) return;
    const owner = ad.owner || {};
    const ownerName = owner.display_name || owner.full_name || "—";
    const ownerId = owner.user_id || "";
    p2pModalTitle.textContent = `Объявление #${ad.public_id}`;
    p2pModalBody.innerHTML = `
      <div class="deal-detail-row">
        <span>Продавец:</span>
        <button class="link owner-link" data-owner="${ownerId}">${ownerName}</button>
      </div>
      <div class="deal-detail-row"><span>Цена:</span>1 USDT = ${formatAmount(ad.price_rub, 0)} RUB</div>
      <div class="deal-detail-row"><span>Доступный объем:</span>${formatAmount(ad.remaining_usdt, 0)} USDT</div>
      <div class="deal-detail-row"><span>Лимиты:</span>₽${formatAmount(ad.min_rub, 0)}-₽${formatAmount(ad.max_rub, 0)}</div>
      <div class="deal-detail-row"><span>Способ оплаты:</span>${(ad.banks || []).join(", ") || "—"}</div>
      <div class="deal-detail-row"><span>Срок оплаты:</span>15 мин</div>
      <div class="deal-detail-row"><span>Условия сделки:</span>${ad.terms || "—"}</div>
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
      p2pModalActions.innerHTML = "";
      const confirm = document.createElement("div");
      confirm.className = "deal-row";
      confirm.textContent = `Подтвердите сумму ₽${formatAmount(rub, 0)} для сделки.`;
      const confirmBtn = document.createElement("button");
      confirmBtn.className = "btn primary";
      confirmBtn.textContent = "Предложить сделку";
      const cancelBtn = document.createElement("button");
      cancelBtn.className = "btn";
      cancelBtn.textContent = "Отмена";
      cancelBtn.addEventListener("click", () => {
        p2pModalActions.innerHTML = "";
        p2pModalActions.appendChild(input);
        p2pModalActions.appendChild(btn);
      });
      confirmBtn.addEventListener("click", async () => {
        if (!state.initData) {
          showNotice("initData не найден. Откройте WebApp из Telegram.");
          return;
        }
        try {
          const res = await fetch(`/api/p2p/ads/${ad.id}/offer`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-Telegram-Init-Data": state.initData,
            },
            body: JSON.stringify({ rub_amount: rub }),
          });
          if (!res.ok) {
            let message = "Не удалось создать сделку.";
            try {
              const text = await res.text();
              if (text) {
                message = text;
              }
            } catch {}
            showNotice(message);
            return;
          }
          const offer = await res.json();
          if (offer?.ok) {
            p2pModal.classList.remove("open");
            await loadDeals();
            await loadPublicAds(ad.side === "sell" ? "sell" : "buy");
            showNotice("Предложение отправлено");
          } else {
            showNotice("Не удалось создать сделку.");
          }
        } catch (err) {
          showNotice(`Ошибка: ${err.message}`);
        }
      });
      p2pModalActions.appendChild(confirm);
      p2pModalActions.appendChild(confirmBtn);
      p2pModalActions.appendChild(cancelBtn);
    });
    p2pModalActions.appendChild(input);
    p2pModalActions.appendChild(btn);
    p2pModal.classList.add("open");
    const ownerLink = p2pModalBody.querySelector(".owner-link");
    if (ownerLink && ownerId) {
      ownerLink.addEventListener("click", () => openUserProfile(ownerId));
    }
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
      if (systemPanel) systemPanel.style.display = "none";
      return;
    }
    if (adminTab) adminTab.style.display = "inline-flex";
    if (systemPanel) systemPanel.style.display = "block";
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
        const name =
          mod.profile?.display_name || mod.profile?.full_name || mod.profile?.username || mod.user_id;
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
          merchant.profile?.display_name ||
          merchant.profile?.full_name ||
          merchant.profile?.username ||
          merchant.user_id;
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
    const seller =
      dispute.seller?.display_name || dispute.seller?.full_name || dispute.seller?.username || "—";
    const buyer =
      dispute.buyer?.display_name || dispute.buyer?.full_name || dispute.buyer?.username || "—";
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
    const counterparty =
      deal.counterparty?.display_name ||
      deal.counterparty?.full_name ||
      deal.counterparty?.username ||
      "—";
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
    const addAction = (label, handler, primary = false, extraClass = "") => {
      const btn = document.createElement("button");
      btn.className = `btn ${primary ? "primary" : ""} ${extraClass}`.trim();
      btn.textContent = label;
      btn.addEventListener("click", handler);
      dealModalActions.appendChild(btn);
    };
    if (actions.cancel) {
      addAction("Отменить сделку", () => dealAction("cancel", deal.id), false, "status-bad");
    }
    if (actions.accept_offer) {
      addAction("Принять", () => dealAction("accept", deal.id), true);
    }
    if (actions.decline_offer) {
      addAction("Отменить", () => dealAction("decline", deal.id), false, "status-bad");
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
    const payload = await fetchJson(path, { method: "POST", body: "{}" });
    if (!payload?.ok) return;
    renderDealModal(payload.deal);
    await loadDeals();
  };

  const initTelegram = async () => {
    if (tg) {
      tg.ready();
      tg.expand();
      state.initData = tg.initData || "";
      const theme = detectTheme();
      applyTheme(theme);
      updateThemeToggle(theme);
    } else {
      const theme = detectTheme();
      applyTheme(theme);
      updateThemeToggle(theme);
      log("WebApp API не найден. Проверьте запуск через Telegram.", "warn");
    }
    const user = await fetchMe();
    if (user) {
      setAuthState(user);
      log(`Готово. Пользователь: ${user.display_name || user.full_name || user.first_name || user.id}`);
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

  const updateReviewsIndicator = () => {
    if (!reviewsTabs) return;
    const activeBtn = reviewsTabs.querySelector(".tab-btn.active");
    const indicator = reviewsTabs.querySelector(".tab-indicator");
    if (!activeBtn || !indicator) return;
    const containerRect = reviewsTabs.getBoundingClientRect();
    const buttonRect = activeBtn.getBoundingClientRect();
    const styles = window.getComputedStyle(reviewsTabs);
    const padLeft = parseFloat(styles.paddingLeft) || 0;
    const offset = buttonRect.left - containerRect.left - padLeft;
    indicator.style.width = `${buttonRect.width}px`;
    indicator.style.transform = `translateX(${offset}px)`;
  };

  const renderReviewsPage = () => {
    const reviews = state.reviews || [];
    const rating = state.reviewsRating || "all";
    const filtered =
      rating === "all" ? reviews : reviews.filter((item) => item.rating === rating);
    const perPage = 5;
    const totalPages = Math.max(1, Math.ceil(filtered.length / perPage));
    const safePage = Math.max(0, Math.min(state.reviewsPage || 0, totalPages - 1));
    state.reviewsPage = safePage;
    const start = safePage * perPage;
    const chunk = filtered.slice(start, start + perPage);
    reviewsList.innerHTML = "";
    if (!filtered.length) {
      reviewsList.innerHTML = "<div class=\"deal-empty\">Пока нет отзывов.</div>";
      if (reviewsPagination) {
        reviewsPagination.innerHTML = "";
      }
      return;
    }
    chunk.forEach((item) => {
      const row = document.createElement("div");
      row.className = "deal-item review-item";
      const author =
        item.author?.display_name || item.author?.full_name || item.author?.username || "—";
      const avatarUrl = item.author?.avatar_url || "";
      const initials = author.replace(/[^A-Za-zА-Яа-я0-9]/g, "").slice(0, 2).toUpperCase() || "BC";
      const statusLabel = item.rating > 0 ? "Положительный" : "Отрицательный";
      row.innerHTML = `
        <div class="review-header">
          <div class="review-avatar" ${avatarUrl ? `style="background-image:url('${avatarUrl}')"` : ""}>
            ${avatarUrl ? "" : initials}
          </div>
          <div class="review-meta">
            <div class="deal-id">${author}</div>
            <div class="deal-row">${formatReviewDate(item.created_at)}</div>
          </div>
          <div class="deal-status ${item.rating > 0 ? "positive" : "negative"}">${statusLabel}</div>
        </div>
        <div class="deal-row">${item.comment || "Без комментария"}</div>
      `;
      reviewsList.appendChild(row);
    });
    if (reviewsPagination) {
      const prevDisabled = safePage <= 0;
      const nextDisabled = safePage >= totalPages - 1;
      reviewsPagination.innerHTML = `
        <button class="btn" ${prevDisabled ? "disabled" : ""} data-page="prev">Назад</button>
        <div class="page-info">Стр. ${safePage + 1} / ${totalPages}</div>
        <button class="btn" ${nextDisabled ? "disabled" : ""} data-page="next">Вперёд</button>
      `;
      const prevBtn = reviewsPagination.querySelector("[data-page=\"prev\"]");
      const nextBtn = reviewsPagination.querySelector("[data-page=\"next\"]");
      prevBtn?.addEventListener("click", () => {
        if (state.reviewsPage > 0) {
          state.reviewsPage -= 1;
          renderReviewsPage();
        }
      });
      nextBtn?.addEventListener("click", () => {
        if (state.reviewsPage < totalPages - 1) {
          state.reviewsPage += 1;
          renderReviewsPage();
        }
      });
    }
    updateReviewsIndicator();
  };

  const renderReviews = (reviews, rating) => {
    state.reviews = reviews || [];
    state.reviewsRating = rating;
    state.reviewsPage = 0;
    renderReviewsPage();
  };

  const loadReviews = async () => {
    const payload = await fetchJson("/api/reviews");
    if (!payload?.ok) return null;
    const successPercent = state.profileStats?.success_percent ?? 0;
    reviewsSummary.textContent = `Успешные сделки: ${successPercent}%`;
    return payload.reviews || [];
  };

  themeToggle?.addEventListener("click", () => {
    const current = document.documentElement.dataset.theme || "light";
    const next = current === "light" ? "dark" : "light";
    applyTheme(next);
    updateThemeToggle(next);
  });

  navButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      setView(btn.dataset.view);
    });
  });

  quickDealsBtn?.addEventListener("click", () => {
    renderQuickDeals();
    quickDealsPanel?.classList.add("open");
    quickDealsPanel?.setAttribute("aria-hidden", "false");
  });

  quickDealsClose?.addEventListener("click", () => {
    quickDealsPanel?.classList.remove("open");
    quickDealsPanel?.setAttribute("aria-hidden", "true");
  });

  dealModalClose?.addEventListener("click", () => {
    dealModal.classList.remove("open");
  });

  p2pModalClose?.addEventListener("click", () => {
    p2pModal.classList.remove("open");
  });

  userModalClose?.addEventListener("click", () => {
    userModal?.classList.remove("open");
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
    renderReviews(reviews, "all");
    reviewsModal.classList.add("open");
    window.setTimeout(updateReviewsIndicator, 0);
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
      const rating =
        btn.dataset.tab === "positive" ? 1 : btn.dataset.tab === "negative" ? -1 : "all";
      renderReviews(reviews, rating);
      window.setTimeout(updateReviewsIndicator, 0);
    });
  });

  window.addEventListener("resize", () => {
    updateReviewsIndicator();
  });

  profileQuick?.addEventListener("click", () => {
    const display = userBadge.textContent || "—";
    profileQuickName.textContent = display;
    const quickRole = state.user?.role === "buyer" ? "Мерчант" : "";
    profileQuickUsername.textContent = quickRole;
    profileQuickUsername.style.display = quickRole ? "" : "none";
    setAvatarNode(profileModalAvatar, display, state.user?.avatar_url);
    if (profileQuickBalance) {
      const balance = state.balance ?? 0;
      profileQuickBalance.textContent = `${formatAmount(balance, 2)} USDT`;
    }
    if (profileQuickReserved) {
      const reserved = Number(state.balanceReserved ?? 0);
      profileQuickReserved.textContent = `В резерве: ${formatAmount(reserved, 2)} USDT`;
    }
    profileModal.classList.add("open");
  });

  profileModalClose?.addEventListener("click", () => {
    profileModal.classList.remove("open");
  });

  profileGo?.addEventListener("click", () => {
    setView("profile");
    profileModal.classList.remove("open");
  });

  profileModalTopup?.addEventListener("click", () => {
    profileModal.classList.remove("open");
    topupModal?.classList.add("open");
  });

  profileModalWithdraw?.addEventListener("click", () => {
    profileModal.classList.remove("open");
    withdrawModal?.classList.add("open");
  });

  profileEditOpen?.addEventListener("click", () => {
    const display = profileDisplayName?.textContent?.trim() || userBadge.textContent || "";
    if (profileEditName) profileEditName.value = display;
    if (profileEditPreview) {
      const avatarUrl = state.user?.avatar_url || "";
      if (avatarUrl) {
        profileEditPreview.style.backgroundImage = `url(${avatarUrl})`;
        profileEditPreview.textContent = "";
      } else {
        profileEditPreview.style.backgroundImage = "";
        profileEditPreview.textContent = display.slice(0, 2).toUpperCase();
      }
    }
    profileEditModal?.classList.add("open");
  });

  profileEditClose?.addEventListener("click", () => {
    profileEditModal?.classList.remove("open");
  });

  profileEditAvatar?.addEventListener("change", () => {
    const file = profileEditAvatar.files?.[0];
    if (!file || !profileEditPreview) return;
    const previewUrl = URL.createObjectURL(file);
    profileEditPreview.style.backgroundImage = `url(${previewUrl})`;
    profileEditPreview.textContent = "";
  });

  profileEditForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const displayName = profileEditName?.value.trim();
    if (!displayName) {
      log("Введите имя", "warn");
      return;
    }
    const payload = await fetchJson("/api/profile", {
      method: "POST",
      body: JSON.stringify({ display_name: displayName }),
    });
    if (!payload?.ok) return;
    const file = profileEditAvatar?.files?.[0];
    if (file) {
      const formData = new FormData();
      formData.append("avatar", file);
      try {
        const res = await fetch("/api/profile/avatar", {
          method: "POST",
          headers: { "X-Telegram-Init-Data": state.initData },
          body: formData,
        });
        if (!res.ok) {
          const text = await res.text();
          throw new Error(text || `HTTP ${res.status}`);
        }
      } catch (err) {
        log(`Ошибка API /api/profile/avatar: ${err.message}`, "error");
      }
    }
    profileEditModal?.classList.remove("open");
    const me = await fetchMe();
    if (me) setAuthState(me);
    await loadProfile();
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

  topupOpen?.addEventListener("click", () => {
    topupModal.classList.add("open");
  });

  topupClose?.addEventListener("click", () => {
    topupModal.classList.remove("open");
  });

  topupForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const amount = Number(topupAmount.value);
    if (!amount || amount <= 0) {
      log("Введите сумму в USDT", "warn");
      return;
    }
    const payload = await fetchJson("/api/balance/topup", {
      method: "POST",
      body: JSON.stringify({ amount }),
    });
    if (payload?.ok) {
      topupModal.classList.remove("open");
      topupForm.reset();
      openLink(payload.pay_url);
      log("Счёт создан. Если не открылось, используй кнопку в сообщении.", "info");
    }
  });

  withdrawClose?.addEventListener("click", () => {
    withdrawModal?.classList.remove("open");
  });

  withdrawForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const amount = Number(withdrawAmount?.value);
    if (!amount || amount <= 0) {
      showNotice("Вывод пока недоступен. Попробуйте немного позже.");
      log("Введите сумму в USDT", "warn");
      return;
    }
    if (!state.initData) {
      showNotice("Вывод пока недоступен. Попробуйте немного позже.");
      return;
    }
    const res = await fetch("/api/balance/withdraw", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Telegram-Init-Data": state.initData,
      },
      body: JSON.stringify({ amount }),
    });
    if (!res.ok) {
      const text = await res.text();
      if (text.includes("Недостаточно")) {
        showNotice("Вывод пока недоступен. Попробуйте немного позже.");
      } else {
        showNotice("Вывод пока недоступен. Попробуйте немного позже.");
      }
      log(`Ошибка API /api/balance/withdraw: ${text}`, "error");
      return;
    }
    const payload = await res.json();
    if (payload?.ok) {
      withdrawModal?.classList.remove("open");
      withdrawForm?.reset();
      await loadBalance();
      playSuccessAnimation();
      log("Вывод выполнен. Средства отправлены в Crypto Bot.", "info");
    }
  });

  observeModals();
  initTelegram();
})();
