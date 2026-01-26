(() => {
  window.addEventListener("error", (event) => {
    try {
      fetch("/api/debug/initdata", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tag: "js-error",
          message: event.message,
          source: event.filename,
          line: event.lineno,
          col: event.colno,
          stack: event?.error?.stack || null,
        }),
      });
    } catch {
      // ignore
    }
  });
  window.addEventListener("unhandledrejection", (event) => {
    try {
      fetch("/api/debug/initdata", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tag: "js-rejection",
          reason: String(event.reason || ""),
        }),
      });
    } catch {
      // ignore
    }
  });
  let tg = window.Telegram?.WebApp || null;
  const logEl = document.getElementById("log");
  const successAnim = document.getElementById("successAnim");
  const centerNotice = document.getElementById("centerNotice");
  const sellQuick = document.getElementById("sellQuick");
  const pinOverlay = document.getElementById("pinOverlay");
  const pinTitle = document.getElementById("pinTitle");
  const pinDots = document.getElementById("pinDots");
  const pinHint = document.getElementById("pinHint");
  const pinKeypad = document.getElementById("pinKeypad");
  const pinActions = document.getElementById("pinActions");
  const pinBiometric = document.getElementById("pinBiometric");
  const pinSkipBiometric = document.getElementById("pinSkipBiometric");
  const pinBackBtn = document.getElementById("pinBackBtn");
  const sellModal = document.getElementById("sellModal");
  const sellModalClose = document.getElementById("sellModalClose");
  const sellForm = document.getElementById("sellForm");
  const sellAmount = document.getElementById("sellAmount");
  const topupOpen = document.getElementById("topupOpen");
  const topupModal = document.getElementById("topupModal");
  const topupClose = document.getElementById("topupClose");
  const topupForm = document.getElementById("topupForm");
  const topupAmount = document.getElementById("topupAmount");
  const balanceHistoryOpen = document.getElementById("balanceHistoryOpen");
  const balanceHistoryModal = document.getElementById("balanceHistoryModal");
  const balanceHistoryClose = document.getElementById("balanceHistoryClose");
  const balanceHistoryList = document.getElementById("balanceHistoryList");
  const withdrawModal = document.getElementById("withdrawModal");
  const withdrawClose = document.getElementById("withdrawClose");
  const withdrawForm = document.getElementById("withdrawForm");
  const withdrawAmount = document.getElementById("withdrawAmount");
  const userBadge = document.getElementById("userBadge");
  const profileNameTop = document.getElementById("profileNameTop");
  const initDebug = document.getElementById("initDebug");
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
  const confirmCompleteModal = document.getElementById("confirmCompleteModal");
  const confirmCompleteClose = document.getElementById("confirmCompleteClose");
  const confirmCompleteCancel = document.getElementById("confirmCompleteCancel");
  const confirmCompleteSubmit = document.getElementById("confirmCompleteSubmit");
  const confirmCompleteText = document.getElementById("confirmCompleteText");
  const chatModal = document.getElementById("chatModal");
  const chatModalTitle = document.getElementById("chatModalTitle");
  const chatModalClose = document.getElementById("chatModalClose");
  const chatList = document.getElementById("chatList");
  const chatForm = document.getElementById("chatForm");
  const chatInput = document.getElementById("chatInput");
  const chatFile = document.getElementById("chatFile");
  const chatFileHint = document.getElementById("chatFileHint");
  const imageModal = document.getElementById("imageModal");
  const imageModalImg = document.getElementById("imageModalImg");
  const imageModalClose = document.getElementById("imageModalClose");
  const videoModal = document.getElementById("videoModal");
  const videoModalPlayer = document.getElementById("videoModalPlayer");
  const videoModalClose = document.getElementById("videoModalClose");
  const commentModal = document.getElementById("commentModal");
  const commentModalClose = document.getElementById("commentModalClose");
  const commentModalText = document.getElementById("commentModalText");
  const disputeResolveModal = document.getElementById("disputeResolveModal");
  const disputeResolveClose = document.getElementById("disputeResolveClose");
  const disputeResolveCancel = document.getElementById("disputeResolveCancel");
  const disputeResolveConfirm = document.getElementById("disputeResolveConfirm");
  const disputeResolveInfo = document.getElementById("disputeResolveInfo");
  const buyerProofModal = document.getElementById("buyerProofModal");
  const buyerProofClose = document.getElementById("buyerProofClose");
  const buyerProofPick = document.getElementById("buyerProofPick");
  const buyerProofSend = document.getElementById("buyerProofSend");
  const buyerProofPreview = document.getElementById("buyerProofPreview");
  const buyerProofImg = document.getElementById("buyerProofImg");
  const buyerProofTitle = document.getElementById("buyerProofTitle");
  const buyerProofActions = document.getElementById("buyerProofActions");
  const disputeOpenModal = document.getElementById("disputeOpenModal");
  const disputeOpenClose = document.getElementById("disputeOpenClose");
  const disputeVideoPick = document.getElementById("disputeVideoPick");
  const disputeOpenSend = document.getElementById("disputeOpenSend");
  const disputeVideoName = document.getElementById("disputeVideoName");
  const disputeComment = document.getElementById("disputeComment");
  const disputeReason = document.getElementById("disputeReason");
  const disputeReasonCustomField = document.getElementById("disputeReasonCustomField");
  const disputeReasonCustom = document.getElementById("disputeReasonCustom");
  const disputeEvidenceModal = document.getElementById("disputeEvidenceModal");
  const disputeEvidenceClose = document.getElementById("disputeEvidenceClose");
  const disputeEvidencePick = document.getElementById("disputeEvidencePick");
  const disputeEvidenceSend = document.getElementById("disputeEvidenceSend");
  const disputeEvidenceName = document.getElementById("disputeEvidenceName");
  const disputeEvidenceComment = document.getElementById("disputeEvidenceComment");
  const quickDealsBtn = document.getElementById("quickDealsBtn");
  const quickDealsBadge = document.getElementById("quickDealsBadge");
  const quickDealsCount = document.getElementById("quickDealsCount");
  const quickDealsPanel = document.getElementById("quickDealsPanel");
  const quickDealsList = document.getElementById("quickDealsList");
  const systemNotice = document.getElementById("systemNotice");
  const systemNoticeTitle = document.getElementById("systemNoticeTitle");
  const systemNoticeList = document.getElementById("systemNoticeList");
  const systemNoticeActions = document.getElementById("systemNoticeActions");
  const systemNoticeRate = document.getElementById("systemNoticeRate");
  const systemNoticeSkip = document.getElementById("systemNoticeSkip");
  const systemNoticeRateForm = document.getElementById("systemNoticeRateForm");
  const systemNoticeLike = document.getElementById("systemNoticeLike");
  const systemNoticeDislike = document.getElementById("systemNoticeDislike");
  const systemNoticeComment = document.getElementById("systemNoticeComment");
  const systemNoticeSubmit = document.getElementById("systemNoticeSubmit");
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
    lastInitError: "",
    bootstrapRetry: null,
    balance: null,
    balanceReserved: 0,
    p2pMode: "buy",
    p2pAds: [],
    myAds: [],
    reviews: [],
    reviewsPage: 0,
    reviewsRating: "all",
    unreadDeals: new Set(),
    chatLastRead: {},
    chatUnreadCounts: {},
    chatLastSeenAt: {},
    chatInitDone: false,
    pendingRead: {},
    systemNotifications: [],
    dealStatusMap: {},
    lastQuickBadgeCount: 0,
    activeChatDealId: null,
    activeDealId: null,
    activeDealSnapshot: null,
    buyerProofDraft: {},
    buyerProofSent: {},
    buyerProofDealId: null,
    disputeOpenDealId: null,
    disputeOpenDraft: null,
    disputeEvidenceId: null,
    disputeEvidenceDraft: null,
    activeDisputeId: null,
    disputeSnapshot: null,
    disputeRefreshTimer: null,
    pendingResolve: null,
    completedNotified: {},
    disputeResolvedNotified: {},
    bootstrapDone: false,
    initRetryTimer: null,
    tgRetryTimer: null,
    systemNoticeShownOnce: false,
    systemNoticeTimer: null,
    systemNoticeActive: null,
    dealRefreshTimer: null,
    livePollTimer: null,
    livePollInFlight: false,
    reviewsTargetUserId: null,
    canManageDisputes: false,
  };

  const unreadStorageKey = "quickDealsUnread";
  const chatReadStorageKey = "dealChatLastRead";
  const chatUnreadStorageKey = "dealChatUnreadCounts";
  const chatSeenStorageKey = "dealChatLastSeenAt";
  const pendingReadStorageKey = "dealPendingRead";
  const systemNoticeStorageKey = "systemNotifications";
  const dealStatusStorageKey = "dealStatusMap";
  const buyerProofStorageKey = "buyerProofSent";
  const completedNoticeStorageKey = "dealCompletedNotified";
  const disputeResolvedStorageKey = "dealDisputeResolvedNotified";
  const themeStorageKey = "preferredTheme";
  const pinHashStorageKey = "appPinHash";
  const pinBioStorageKey = "appPinBio";
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
  const loadChatRead = () => {
    try {
      const raw = JSON.parse(window.localStorage.getItem(chatReadStorageKey) || "{}");
      return raw && typeof raw === "object" ? raw : {};
    } catch {
      return {};
    }
  };
  const persistChatRead = () => {
    try {
      window.localStorage.setItem(chatReadStorageKey, JSON.stringify(state.chatLastRead || {}));
    } catch {
      // ignore storage errors
    }
  };
  state.chatLastRead = loadChatRead();
  const loadChatUnreadCounts = () => {
    try {
      const raw = JSON.parse(window.localStorage.getItem(chatUnreadStorageKey) || "{}");
      return raw && typeof raw === "object" ? raw : {};
    } catch {
      return {};
    }
  };
  const persistChatUnreadCounts = () => {
    try {
      window.localStorage.setItem(
        chatUnreadStorageKey,
        JSON.stringify(state.chatUnreadCounts || {})
      );
    } catch {
      // ignore storage errors
    }
  };
  const loadChatSeen = () => {
    try {
      const raw = JSON.parse(window.localStorage.getItem(chatSeenStorageKey) || "{}");
      return raw && typeof raw === "object" ? raw : {};
    } catch {
      return {};
    }
  };
  const persistChatSeen = () => {
    try {
      window.localStorage.setItem(
        chatSeenStorageKey,
        JSON.stringify(state.chatLastSeenAt || {})
      );
    } catch {
      // ignore storage errors
    }
  };
  state.chatUnreadCounts = loadChatUnreadCounts();
  state.chatLastSeenAt = loadChatSeen();
  const loadPendingRead = () => {
    try {
      const raw = JSON.parse(window.localStorage.getItem(pendingReadStorageKey) || "{}");
      return raw && typeof raw === "object" ? raw : {};
    } catch {
      return {};
    }
  };
  const persistPendingRead = () => {
    try {
      window.localStorage.setItem(
        pendingReadStorageKey,
        JSON.stringify(state.pendingRead || {})
      );
    } catch {
      // ignore storage errors
    }
  };
  state.pendingRead = loadPendingRead();
  const loadSystemNotifications = () => {
    try {
      const raw = JSON.parse(window.localStorage.getItem(systemNoticeStorageKey) || "[]");
      if (!Array.isArray(raw)) return [];
      return raw
        .map((item) => {
          if (typeof item === "string") {
            return { key: item, message: item };
          }
          return item;
        })
        .filter(Boolean);
    } catch {
      return [];
    }
  };
  const persistSystemNotifications = () => {
    try {
      window.localStorage.setItem(
        systemNoticeStorageKey,
        JSON.stringify(state.systemNotifications || [])
      );
    } catch {
      // ignore storage errors
    }
  };
  const loadDealStatusMap = () => {
    try {
      const raw = JSON.parse(window.localStorage.getItem(dealStatusStorageKey) || "{}");
      return raw && typeof raw === "object" ? raw : {};
    } catch {
      return {};
    }
  };
  const persistDealStatusMap = () => {
    try {
      window.localStorage.setItem(
        dealStatusStorageKey,
        JSON.stringify(state.dealStatusMap || {})
      );
    } catch {
      // ignore storage errors
    }
  };
  const loadBuyerProofSent = () => {
    try {
      const raw = JSON.parse(window.localStorage.getItem(buyerProofStorageKey) || "{}");
      return raw && typeof raw === "object" ? raw : {};
    } catch {
      return {};
    }
  };
  const persistBuyerProofSent = () => {
    try {
      window.localStorage.setItem(
        buyerProofStorageKey,
        JSON.stringify(state.buyerProofSent || {})
      );
    } catch {
      // ignore storage errors
    }
  };
  state.systemNotifications = loadSystemNotifications();
  state.dealStatusMap = loadDealStatusMap();
  state.buyerProofSent = loadBuyerProofSent();
  let pendingReviewRating = null;
  const loadCompletedNotified = () => {
    try {
      const raw = JSON.parse(window.localStorage.getItem(completedNoticeStorageKey) || "{}");
      return raw && typeof raw === "object" ? raw : {};
    } catch {
      return {};
    }
  };
  const persistCompletedNotified = () => {
    try {
      window.localStorage.setItem(
        completedNoticeStorageKey,
        JSON.stringify(state.completedNotified || {})
      );
    } catch {
      // ignore storage errors
    }
  };
  state.completedNotified = loadCompletedNotified();

  const loadDisputeResolvedNotified = () => {
    try {
      return JSON.parse(window.localStorage.getItem(disputeResolvedStorageKey) || "{}");
    } catch {
      return {};
    }
  };

  const persistDisputeResolvedNotified = () => {
    try {
      window.localStorage.setItem(
        disputeResolvedStorageKey,
        JSON.stringify(state.disputeResolvedNotified || {})
      );
    } catch {
      // ignore storage errors
    }
  };

  state.disputeResolvedNotified = loadDisputeResolvedNotified();

  const clearSystemNoticeTimer = () => {
    if (state.systemNoticeTimer) {
      window.clearTimeout(state.systemNoticeTimer);
      state.systemNoticeTimer = null;
    }
  };

  const hideSystemNotice = () => {
    if (!systemNotice) return;
    systemNotice.classList.remove("show");
    clearSystemNoticeTimer();
  };

  const showSystemNotice = (item, { autoClose = true } = {}) => {
    if (!systemNotice || !systemNoticeList) return;
    state.systemNoticeActive = item;
    systemNoticeTitle.textContent = "Уведомление";
    systemNoticeList.innerHTML = "";
    const row = document.createElement("div");
    row.className = "system-notice-item";
    row.textContent = item?.message || "";
    systemNoticeList.appendChild(row);
    if (item?.type === "dispute_resolved") {
      systemNoticeActions?.classList.add("hidden");
      systemNoticeRateForm?.classList.remove("show");
    } else {
      systemNoticeActions?.classList.remove("hidden");
      systemNoticeRateForm?.classList.remove("show");
    }
    if (typeof pendingReviewRating !== "undefined") {
      pendingReviewRating = null;
    }
    systemNoticeLike?.classList.remove("active");
    systemNoticeDislike?.classList.remove("active");
    if (systemNoticeSubmit) systemNoticeSubmit.disabled = true;
    systemNotice.classList.add("show");
    clearSystemNoticeTimer();
    if (autoClose) {
      const timeoutMs = item?.type === "dispute_resolved" ? 3000 : 4000;
      state.systemNoticeTimer = window.setTimeout(() => {
        if (item?.key) {
          state.systemNotifications = (state.systemNotifications || []).filter(
            (entry) => entry.key !== item.key
          );
          persistSystemNotifications();
        }
        hideSystemNotice();
        renderSystemNotifications();
      }, timeoutMs);
    }
  };

  const openReviewForDeal = (deal) => {
    if (!deal?.id) return;
    const dealLabel = deal.public_id ? `#${deal.public_id}` : `#${deal.id}`;
    const item = {
      key: `manual-review-${deal.id}`,
      message: `Сделка ${dealLabel} завершена.`,
      type: "deal_completed",
      deal_id: deal.id,
      public_id: deal.public_id,
      counterparty_id: deal.counterparty?.user_id || null,
    };
    showSystemNotice(item, { autoClose: false });
    systemNoticeRateForm?.classList.add("show");
    if (systemNoticeSubmit) {
      systemNoticeSubmit.disabled = !pendingReviewRating;
    }
  };

  const renderSystemNotifications = () => {
    const items = state.systemNotifications || [];
    if (!items.length) {
      hideSystemNotice();
      return;
    }
    if (!state.systemNoticeShownOnce) {
      state.systemNoticeShownOnce = true;
      showSystemNotice(items[0], { autoClose: true });
    }
  };

  const pushSystemNotification = (entry) => {
    if (!entry?.message) return;
    const noticeKey = entry.key || `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    if ((state.systemNotifications || []).some((item) => item.key === noticeKey)) {
      return;
    }
    const payload = {
      ...entry,
      key: noticeKey,
      created_at: new Date().toISOString(),
    };
    const next = [...(state.systemNotifications || []), payload];
    state.systemNotifications = next.slice(-6);
    persistSystemNotifications();
    showSystemNotice(payload, { autoClose: true });
  };

  const clearDealAlerts = (dealId) => {
    if (!dealId) return;
    state.unreadDeals?.delete?.(dealId);
    if (state.pendingRead) {
      state.pendingRead[dealId] = true;
    }
    if (state.chatUnreadCounts) {
      state.chatUnreadCounts[dealId] = 0;
    }
    persistUnreadDeals();
    persistPendingRead();
    persistChatUnreadCounts();
  };

  renderSystemNotifications();

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

  const loadPinHash = () => {
    try {
      return window.localStorage.getItem(pinHashStorageKey) || "";
    } catch {
      return "";
    }
  };
  const savePinHash = (hash) => {
    try {
      window.localStorage.setItem(pinHashStorageKey, hash);
    } catch {
      // ignore
    }
  };
  const loadBioFlag = () => {
    try {
      return window.localStorage.getItem(pinBioStorageKey) === "1";
    } catch {
      return false;
    }
  };
  const saveBioFlag = (value) => {
    try {
      window.localStorage.setItem(pinBioStorageKey, value ? "1" : "0");
    } catch {
      // ignore
    }
  };

  const hashPin = async (pin) => {
    const enc = new TextEncoder().encode(pin);
    const buf = await crypto.subtle.digest("SHA-256", enc);
    return Array.from(new Uint8Array(buf))
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");
  };

  const renderPinDots = (len) => {
    if (!pinDots) return;
    pinDots.innerHTML = "";
    for (let i = 0; i < 4; i += 1) {
      const dot = document.createElement("span");
      dot.className = `pin-dot ${i < len ? "filled pop" : ""}`;
      pinDots.appendChild(dot);
    }
  };

  const showPinOverlay = () => {
    pinOverlay?.classList.add("show");
    document.body.classList.add("pin-lock");
    document.documentElement.style.backgroundColor = "#0b0714";
  };
  const hidePinOverlay = () => {
    pinOverlay?.classList.remove("show");
    document.body.classList.remove("pin-lock");
    document.documentElement.style.backgroundColor = "";
  };

  const initPinGate = () => {
    if (!pinOverlay || !pinKeypad || !pinTitle) return Promise.resolve(true);
    let mode = "unlock";
    let buffer = "";
    let firstPin = "";
    const savedHash = loadPinHash();
    let biometricEnabled = loadBioFlag();
    let autoBioTried = false;
    let biometricInFlight = false;
    let biometricResetTimer = null;
    let externalUnlockResolver = null;
    let allowPinDismiss = false;

    const setHint = (text = "") => {
      if (pinHint) pinHint.textContent = text;
    };

    const resetBuffer = () => {
      buffer = "";
      renderPinDots(0);
    };

    const triggerBiometric = (options = {}) => {
      const { enroll = false, unlockAfter = false } = options;
      const biometric = tg?.BiometricManager;
      if (!biometric || typeof biometric.authenticate !== "function") {
        setHint("Face ID недоступен");
        return;
      }
      if (biometricInFlight) {
        return;
      }
      biometricInFlight = true;
      if (biometricResetTimer) {
        window.clearTimeout(biometricResetTimer);
      }
      biometricResetTimer = window.setTimeout(() => {
        biometricInFlight = false;
        biometricResetTimer = null;
      }, 4000);
      const runAuth = () => {
        biometric.authenticate({ reason: "Вход в BC Cash" }, (result) => {
          biometricInFlight = false;
          if (biometricResetTimer) {
            window.clearTimeout(biometricResetTimer);
            biometricResetTimer = null;
          }
          if (result) {
            if (enroll) {
              saveBioFlag(true);
              biometricEnabled = true;
            }
            if (unlockAfter) {
              unlock();
            }
          } else {
            setHint("Face ID не сработал");
          }
        });
      };
      const runFlow = () => {
        if (!biometric.isAccessGranted) {
          biometric.requestAccess({ reason: "Вход в BC Cash" }, (granted) => {
            biometricInFlight = false;
            if (biometricResetTimer) {
              window.clearTimeout(biometricResetTimer);
              biometricResetTimer = null;
            }
            if (!granted) {
              setHint("Face ID не разрешен");
              return;
            }
            runAuth();
          });
          return;
        }
        runAuth();
      };
      if (!biometric.isInited && typeof biometric.init === "function") {
        let initDone = false;
        biometric.init(() => {
          initDone = true;
          runFlow();
        });
        window.setTimeout(() => {
          if (!initDone) runFlow();
        }, 300);
        return;
      }
      runFlow();
    };

    const setMode = (next) => {
      mode = next;
      resetBuffer();
      setHint("");
      if (mode === "setup1") pinTitle.textContent = "Придумайте PIN";
      if (mode === "setup2") pinTitle.textContent = "Повторите PIN";
      if (mode === "unlock") pinTitle.textContent = "Введите PIN";
      const biometricSupported = !!(tg?.BiometricManager && typeof tg.BiometricManager.authenticate === "function");
      const biometricAvailable = biometricEnabled || (tg?.BiometricManager && tg.BiometricManager.isAccessGranted);
      if (pinActions) {
        pinActions.classList.toggle("show", mode === "unlock" && biometricSupported);
      }
      if (pinBiometric) {
        pinBiometric.style.display = mode === "unlock" && biometricSupported ? "block" : "none";
      }
      if (pinSkipBiometric) {
        pinSkipBiometric.style.display = "none";
      }
      if (mode === "unlock" && biometricAvailable && !autoBioTried) {
        autoBioTried = true;
        setTimeout(() => {
          triggerBiometric({ unlockAfter: true });
        }, 400);
      }
    };

    const unlock = () => {
      hidePinOverlay();
      resolveGate();
      if (externalUnlockResolver) {
        externalUnlockResolver(true);
        externalUnlockResolver = null;
      }
    };

    let resolveGate = () => {};
    const gatePromise = new Promise((resolve) => {
      resolveGate = resolve;
    });

    if (!savedHash) {
      setMode("setup1");
      showPinOverlay();
    } else {
      setMode("unlock");
      showPinOverlay();
    }

    const requestPinUnlock = () => {
      if (!savedHash) {
        showNotice("PIN не настроен");
        return Promise.resolve(false);
      }
      return new Promise((resolve) => {
        externalUnlockResolver = resolve;
        allowPinDismiss = true;
        setMode("unlock");
        showPinOverlay();
        const biometricAvailable =
          biometricEnabled || (tg?.BiometricManager && tg.BiometricManager.isAccessGranted);
        if (biometricAvailable) {
          setTimeout(() => {
            triggerBiometric({ unlockAfter: true });
          }, 200);
        }
      });
    };

    window.requestPinUnlock = requestPinUnlock;

    if (pinBackBtn) {
      pinBackBtn.addEventListener("click", () => {
        if (!allowPinDismiss) return;
        hidePinOverlay();
        if (externalUnlockResolver) {
          externalUnlockResolver(false);
          externalUnlockResolver = null;
        }
        allowPinDismiss = false;
      });
    }

    const handleComplete = async () => {
      if (buffer.length < 4) return;
      const pin = buffer;
      if (mode === "setup1") {
        firstPin = pin;
        setMode("setup2");
        return;
      }
      if (mode === "setup2") {
        if (pin !== firstPin) {
          setHint("PIN не совпадает. Попробуйте снова.");
          setMode("setup1");
          return;
        }
        const pinHash = await hashPin(pin);
        savePinHash(pinHash);
        setMode("unlock");
        triggerBiometric({ enroll: true, unlockAfter: true });
        return;
      }
      if (mode === "unlock") {
        const pinHash = await hashPin(pin);
        if (pinHash !== savedHash) {
          setHint("Неверный PIN");
          resetBuffer();
          return;
        }
        unlock();
      }
    };

    pinKeypad.addEventListener("click", async (event) => {
      const btn = event.target.closest(".pin-key");
      if (!btn || mode === "biometric") return;
      const digit = btn.dataset.digit;
      const action = btn.dataset.action;
      if (action === "back") {
        buffer = buffer.slice(0, -1);
        renderPinDots(buffer.length);
        return;
      }
      if (action === "bio") {
        triggerBiometric({ enroll: true, unlockAfter: true });
        return;
      }
      if (!digit) return;
      if (buffer.length >= 4) return;
      buffer += digit;
      renderPinDots(buffer.length);
      if (buffer.length === 4) {
        await handleComplete();
      }
    });

    pinBiometric?.addEventListener("click", () => {
      triggerBiometric({ enroll: true, unlockAfter: true });
    });

    pinSkipBiometric?.addEventListener("click", () => {
      saveBioFlag(false);
      unlock();
    });

    return gatePromise;
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

  let bodyScrollY = 0;
  const updateModalLock = () => {
    const hasModal = Boolean(document.querySelector(".modal.open"));
    document.body.classList.toggle("modal-open", hasModal);
    if (hasModal) {
      bodyScrollY = window.scrollY || 0;
      document.body.style.position = "fixed";
      document.body.style.top = `-${bodyScrollY}px`;
      document.body.style.left = "0";
      document.body.style.right = "0";
      document.body.style.width = "100%";
    } else {
      document.body.style.position = "";
      document.body.style.top = "";
      document.body.style.left = "";
      document.body.style.right = "";
      document.body.style.width = "";
      window.scrollTo(0, bodyScrollY);
    }
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

  const persistTheme = (theme) => {
    try {
      window.localStorage.setItem(themeStorageKey, theme);
    } catch {
      // ignore storage errors
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
    try {
      const saved = window.localStorage.getItem(themeStorageKey);
      if (saved === "light" || saved === "dark") return saved;
    } catch {
      // ignore storage errors
    }
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
    updateInitDebug();
  };

  const updateInitDebug = () => {
    if (!initDebug) return;
    const hasTg = Boolean(tg);
    const hasInit = Boolean(state.initData);
    const hasUser = Boolean(state.user?.user_id || state.user?.id);
    const parts = [
      `TG:${hasTg ? "ok" : "нет"}`,
      `init:${hasInit ? "ok" : "нет"}`,
      `user:${hasUser ? "ok" : "нет"}`,
    ];
    if (state.lastInitError) {
      parts.push(`err:${state.lastInitError}`);
    }
    initDebug.textContent = parts.join(" ");
    initDebug.classList.toggle("show", !hasTg || !hasInit || !hasUser);
  };

  const formatAmount = (value, digits = 3) => {
    const num = Number(value);
    if (!Number.isFinite(num)) return "—";
    return num.toFixed(digits).replace(/\\.?0+$/, "");
  };

  const bankMeta = {
    ozon: { label: "Озон", icon: "/app/assets/bank-ozon.png" },
    ozonbank: { label: "Озон", icon: "/app/assets/bank-ozon.png" },
    sber: { label: "Сбер", icon: "/app/assets/bank-sber.png" },
    sberbank: { label: "Сбер", icon: "/app/assets/bank-sber.png" },
    sberbankonline: { label: "Сбер", icon: "/app/assets/bank-sber.png" },
    alfa: { label: "Альфа", icon: "/app/assets/bank-alfa.png" },
    alpha: { label: "Альфа", icon: "/app/assets/bank-alfa.png" },
    alfabank: { label: "Альфа", icon: "/app/assets/bank-alfa.png" },
    alfabankru: { label: "Альфа", icon: "/app/assets/bank-alfa.png" },
    alfabankrussia: { label: "Альфа", icon: "/app/assets/bank-alfa.png" },
    альфа: { label: "Альфа", icon: "/app/assets/bank-alfa.png" },
    сбер: { label: "Сбер", icon: "/app/assets/bank-sber.png" },
    озон: { label: "Озон", icon: "/app/assets/bank-ozon.png" },
  };

  const normalizeBankKey = (name) =>
    String(name || "")
      .trim()
      .toLowerCase()
      .replace(/[^a-zа-я0-9]+/gi, "");

  const getBankMeta = (name) => {
    const key = normalizeBankKey(name);
    return bankMeta[key] || null;
  };

  const bankLabel = (name) => {
    const meta = getBankMeta(name);
    return meta?.label || name || "—";
  };

  const bankIcon = (name) => {
    const meta = getBankMeta(name);
    return meta?.icon || "";
  };

  const formatDate = (iso) => {
    if (!iso) return "—";
    const dt = new Date(iso);
    return dt.toLocaleString("ru-RU", { dateStyle: "short", timeStyle: "short" });
  };

  const formatTime = (iso) => {
    if (!iso) return "—";
    const dt = new Date(iso);
    return dt.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" });
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
      if (deal.qr_stage === "ready") return "Выдача наличных";
      return "Отправка QR";
    }
    if (deal.status === "dispute") return "Открыт спор";
    if (deal.status === "completed") return "Завершена";
    if (deal.status === "canceled") return "Отменена";
    if (deal.status === "expired") return "Истекла";
    return "Статус";
  };

  const refreshInitData = () => {
    const urlParams = new URLSearchParams(window.location.search);
    const initFromUrl = urlParams.get("initData");
    const fresh = tg?.initData || initFromUrl || "";
    if (fresh) {
      state.initData = fresh;
      updateInitDebug();
      return true;
    }
    updateInitDebug();
    return Boolean(state.initData);
  };

  const fetchMe = async (retry = true) => {
    refreshInitData();
    if (!state.initData) {
      log("initData не найден. Откройте WebApp из Telegram.", "error");
      state.lastInitError = "no-init";
      updateInitDebug();
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
        if (retry && /initdata|invalid/i.test(text)) {
          state.initData = "";
          refreshInitData();
          return fetchMe(false);
        }
        state.lastInitError = text || `HTTP ${res.status}`;
        updateInitDebug();
        throw new Error(text || `HTTP ${res.status}`);
      }
      const payload = await res.json();
      state.lastInitError = "";
      updateInitDebug();
      return payload.user || null;
    } catch (err) {
      log(`Ошибка авторизации: ${err.message}`, "error");
      state.lastInitError = err.message || "fetch-me";
      updateInitDebug();
      return null;
    }
  };

  const fetchJson = async (path, options = {}, retry = true) => {
    refreshInitData();
    if (!state.initData) {
      log("initData не найден. Откройте WebApp из Telegram.", "error");
      state.lastInitError = "no-init";
      updateInitDebug();
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
        if (retry && /initdata|invalid/i.test(text)) {
          state.initData = "";
          refreshInitData();
          return fetchJson(path, options, false);
        }
        state.lastInitError = text || `HTTP ${res.status}`;
        updateInitDebug();
        throw new Error(text || `HTTP ${res.status}`);
      }
      state.lastInitError = "";
      updateInitDebug();
      return await res.json();
    } catch (err) {
      log(`Ошибка API ${path}: ${err.message}`, "error");
      state.lastInitError = err.message || "api";
      updateInitDebug();
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
      const reviewBadge =
        deal.status === "completed" && !deal.reviewed
          ? '<span class="deal-review-badge">Оставьте отзыв</span>'
          : "";
      item.innerHTML = `
        <div class="deal-header">
          <div class="deal-id">Сделка #${deal.public_id}</div>
          <div class="deal-status">${statusLabel(deal)}</div>
        </div>
        <div class="deal-row">${formatAmount(deal.cash_rub, 2)}₽-${formatAmount(
        deal.usdt_amount
      )} USDT | 1 USDT = ${formatAmount(deal.rate, 2)} RUB</div>
        <div class="deal-row deal-row-meta"><span>Дата: ${formatDate(
          deal.created_at
        )}</span>${reviewBadge}</div>
      `;
      item.addEventListener("click", () => openDealModal(deal.id));
      dealsList.appendChild(item);
    });
    if (dealsPagination) {
      const prevDisabled = safePage <= 0;
      const nextDisabled = safePage >= totalPages - 1;
      const showFirst = safePage >= totalPages - 1;
      const showLast = safePage < totalPages - 1;
      dealsPagination.innerHTML = `
        <button class="btn back-btn" ${prevDisabled ? "disabled" : ""} data-page="prev">Назад</button>
        <div class="page-info">Стр. ${safePage + 1} / ${totalPages}</div>
        ${showFirst ? `<button class="btn jump-btn" data-page="first">В начало</button>` : ""}
        ${showLast ? `<button class="btn jump-btn" data-page="last">В конец</button>` : ""}
        <button class="btn next-btn" ${nextDisabled ? "disabled" : ""} data-page="next">Вперёд</button>
      `;
      const prevBtn = dealsPagination.querySelector("[data-page=\"prev\"]");
      const nextBtn = dealsPagination.querySelector("[data-page=\"next\"]");
      const firstBtn = dealsPagination.querySelector("[data-page=\"first\"]");
      const lastBtn = dealsPagination.querySelector("[data-page=\"last\"]");
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
      firstBtn?.addEventListener("click", () => {
        if (state.dealsPage !== 0) {
          state.dealsPage = 0;
          renderDealsPage();
        }
      });
      lastBtn?.addEventListener("click", () => {
        if (state.dealsPage !== totalPages - 1) {
          state.dealsPage = totalPages - 1;
          renderDealsPage();
        }
      });
    }
  };

  const loadDeals = async () => {
    const payload = await fetchJson("/api/my-deals");
    if (!payload?.ok) return;
    const deals = payload.deals || [];
    const previousStatusMap = state.dealStatusMap || {};
    const nextStatusMap = {};
    deals.forEach((deal) => {
      nextStatusMap[deal.id] = deal.status;
      const prev = previousStatusMap[deal.id];
      const dealLabel = `#${deal.public_id || deal.id}`;
      const completedKey = `${deal.id}:completed`;
      if (deal.status === "completed" && !deal.reviewed && !state.completedNotified?.[completedKey]) {
        pushSystemNotification({
          key: completedKey,
          message: `Сделка ${dealLabel} завершена.`,
          type: "deal_completed",
          deal_id: deal.id,
          public_id: deal.public_id,
          counterparty_id: deal.counterparty?.user_id || null,
        });
        state.completedNotified[completedKey] = true;
      } else if ((prev && prev !== deal.status) || (!prev && deal.status === "completed")) {
        if (deal.status === "completed" && !deal.reviewed) {
          pushSystemNotification({
            key: completedKey,
            message: `Сделка ${dealLabel} завершена.`,
            type: "deal_completed",
            deal_id: deal.id,
            public_id: deal.public_id,
            counterparty_id: deal.counterparty?.user_id || null,
          });
          state.completedNotified[completedKey] = true;
        }
      }
      if (deal.dispute_resolution && !state.disputeResolvedNotified?.[`${deal.id}:dispute`]) {
        const sellerAmount = Number(deal.dispute_resolution.seller_amount || 0);
        const buyerAmount = Number(deal.dispute_resolution.buyer_amount || 0);
        const myAmount = deal.role === "seller" ? sellerAmount : buyerAmount;
        const counterpartyName =
          deal.counterparty?.display_name ||
          deal.counterparty?.full_name ||
          deal.counterparty?.username ||
          "другой стороны";
        const winnerIsSeller = sellerAmount >= buyerAmount;
        const winnerName = winnerIsSeller
          ? deal.role === "seller"
            ? "вас"
            : counterpartyName
          : deal.role === "buyer"
          ? "вас"
          : counterpartyName;
        const amountText = formatAmount(myAmount, 3);
        const message =
          myAmount > 0
            ? `Сделка ${dealLabel} была закрыта в вашу пользу.\nНа баланс было зачислено ${amountText} USDT.`
            : `Сделка ${dealLabel} была закрыта в пользу ${winnerName}.\nСредства отправлены ${winnerName}.`;
        pushSystemNotification({
          key: `${deal.id}:dispute`,
          message,
          type: "dispute_resolved",
          deal_id: deal.id,
          public_id: deal.public_id,
        });
        state.disputeResolvedNotified[`${deal.id}:dispute`] = true;
      }
      if (["completed", "canceled", "expired"].includes(deal.status)) {
        clearDealAlerts(deal.id);
      }
    });
    state.dealStatusMap = nextStatusMap;
    persistDealStatusMap();
    persistCompletedNotified();
    persistDisputeResolvedNotified();
    if (!state.chatInitDone) {
      deals.forEach((deal) => {
        if (!deal.chat_last_at) return;
        if (deal.chat_last_sender_id && isSelfSender(deal.chat_last_sender_id)) {
          state.chatLastSeenAt[deal.id] = deal.chat_last_at;
        }
      });
      state.chatInitDone = true;
      persistChatSeen();
    }
    dealsCount.textContent = `${deals.length}`;
    const desiredPage = state.dealsPage ?? 0;
    state.deals = deals;
    const totalPages = Math.max(1, Math.ceil(deals.length / 5));
    state.dealsPage = Math.max(0, Math.min(desiredPage, totalPages - 1));
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
    const isFinalStatus = (status) =>
      status === "completed" || status === "canceled" || status === "expired";
    const activeCount = deals.filter(
      (deal) => !["completed", "canceled", "expired"].includes(deal.status)
    ).length;
    const pendingSet = new Set();
    deals.forEach((deal) => {
      const isPending = deal.status === "pending" && deal.offer_initiator_id;
      if (isPending) {
        const wasRead = state.pendingRead?.[deal.id];
        if (!wasRead) {
          pendingSet.add(deal.id);
        }
      }
    });
    state.unreadDeals = pendingSet;
    persistUnreadDeals();
    const unreadDealIds = new Set(pendingSet);
    const chatUnreadCounts = state.chatUnreadCounts || {};
    const chatSeen = state.chatLastSeenAt || {};
    deals.forEach((deal) => {
      if (isFinalStatus(deal.status)) return;
      if (!deal.chat_last_at) return;
      if (deal.chat_last_sender_id && isSelfSender(deal.chat_last_sender_id)) return;
      const lastSeen = chatSeen[deal.id];
      if (!lastSeen) {
        chatSeen[deal.id] = deal.chat_last_at;
        chatUnreadCounts[deal.id] = (chatUnreadCounts[deal.id] || 0) + 1;
        return;
      }
      if (deal.chat_last_at !== lastSeen) {
        chatUnreadCounts[deal.id] = (chatUnreadCounts[deal.id] || 0) + 1;
        chatSeen[deal.id] = deal.chat_last_at;
        if (chatModal?.classList.contains("open") && state.activeChatDealId === deal.id) {
          try {
            tg?.HapticFeedback?.notificationOccurred("success");
          } catch {
            // ignore haptics errors
          }
        }
      }
    });
    state.chatUnreadCounts = chatUnreadCounts;
    state.chatLastSeenAt = chatSeen;
    persistChatUnreadCounts();
    persistChatSeen();
    deals.forEach((deal) => {
      if (isFinalStatus(deal.status)) return;
      if (isChatUnread(deal)) {
        unreadDealIds.add(deal.id);
      }
    });
    state.unreadDealIds = unreadDealIds;
    if (quickDealsCount) {
      quickDealsCount.textContent = activeCount > 9 ? "9+" : `${activeCount}`;
      quickDealsCount.classList.toggle("show", activeCount > 0);
    }
    if (quickDealsBadge) {
      const chatCount = Object.values(chatUnreadCounts).reduce((sum, value) => sum + (Number(value) || 0), 0);
      const count = chatCount + pendingSet.size;
      quickDealsBadge.textContent = count > 9 ? "9+" : `${count}`;
      quickDealsBadge.classList.toggle("show", count > 0);
      if (count > state.lastQuickBadgeCount) {
        try {
          tg?.HapticFeedback?.notificationOccurred("success");
        } catch {
          // ignore haptics errors
        }
      }
      state.lastQuickBadgeCount = count;
    }
  };

  const parseTime = (value) => {
    if (!value) return null;
    const ms = Date.parse(value);
    return Number.isNaN(ms) ? null : ms;
  };

  const isSelfSender = (senderId) => {
    if (state.userId === null || state.userId === undefined) return false;
    return Number(senderId) === Number(state.userId);
  };

  const isChatUnread = (deal) => {
    if (!deal?.chat_last_at) return false;
    if (deal.chat_last_sender_id && isSelfSender(deal.chat_last_sender_id)) {
      return false;
    }
    const unread = state.chatUnreadCounts?.[deal.id] || 0;
    return unread > 0;
  };

  const markChatRead = (dealId, isoValue) => {
    if (!dealId) return;
    const value = isoValue || new Date().toISOString();
    state.chatLastRead = state.chatLastRead || {};
    state.chatLastRead[dealId] = value;
    persistChatRead();
    state.chatLastSeenAt = state.chatLastSeenAt || {};
    state.chatLastSeenAt[dealId] = value;
    persistChatSeen();
    state.chatUnreadCounts = state.chatUnreadCounts || {};
    state.chatUnreadCounts[dealId] = 0;
    persistChatUnreadCounts();
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
    const unreadDealIds = state.unreadDealIds || new Set(state.unreadDeals);
    quickDealsList.innerHTML = "";
    if (!deals.length) {
      quickDealsList.innerHTML = '<div class="deal-empty">Активных сделок нет.</div>';
      return;
    }
    deals.forEach((deal) => {
      const row = document.createElement("div");
      row.className = "quick-deal-item";
      if (unreadDealIds.has(deal.id)) {
        row.classList.add("unread");
      }
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
        <div class="quick-deal-unread" aria-hidden="true"></div>
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
    const ownerId = ad.owner_id ?? ad.ownerId ?? ad.owner?.user_id;
    const isOwner = ownerId && state.userId && Number(ownerId) === Number(state.userId);
    if (type === "public") {
      item.innerHTML = `
        <div class="deal-header">
          <div class="deal-id">${sideLabel} • USDT - ${price}</div>
          <div class="deal-status">${sideLabel}</div>
        </div>
        <div class="deal-row">Объем: ${formatAmount(ad.remaining_usdt, 0)} USDT</div>
        <div class="deal-row deal-row-split">
          <span>Лимиты: ${limit}</span>
          ${isOwner ? '<span class="p2p-owner-badge">Это ваше объявление</span>' : ""}
        </div>
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
        state.reviewsTargetUserId = userId;
        const reviews = await loadReviews(userId);
        if (!reviews) return;
        renderReviews(reviews, "all");
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
    const ownerId = ad.owner_id ?? ad.ownerId ?? owner.user_id || "";
    const isOwner = ownerId && state.userId && Number(ownerId) === Number(state.userId);
    p2pModalTitle.textContent = `Объявление #${ad.public_id}`;
    p2pModalBody.innerHTML = `
      <div class="deal-detail-row">
        <span>Продавец:</span>
        <button class="link owner-link" data-owner="${ownerId}">${ownerName}</button>
      </div>
      <div class="deal-detail-row"><span>Цена:</span>1 USDT = ${formatAmount(ad.price_rub, 0)} RUB</div>
      <div class="deal-detail-row"><span>Доступный объем:</span>${formatAmount(ad.remaining_usdt, 0)} USDT</div>
      <div class="deal-detail-row"><span>Лимиты:</span>₽${formatAmount(ad.min_rub, 0)}-₽${formatAmount(ad.max_rub, 0)}</div>
      <div class="deal-detail-row"><span>Способ оплаты:</span>${(ad.banks || [])
        .map((bank) => bankLabel(bank))
        .join(", ") || "—"}</div>
      <div class="deal-detail-row"><span>Срок оплаты:</span>15 мин</div>
      <div class="deal-detail-row"><span>Условия сделки:</span>${ad.terms || "—"}</div>
    `;
    p2pModalActions.innerHTML = "";
    if (isOwner) {
      const editBtn = document.createElement("button");
      editBtn.className = "btn primary";
      editBtn.textContent = "Редактировать";
      editBtn.addEventListener("click", () => openMyAd(ad.id, ad));
      p2pModalActions.appendChild(editBtn);
      p2pModal.classList.add("open");
      return;
    }
    const input = document.createElement("input");
    input.type = "number";
    input.placeholder = "Сумма в RUB";
    input.className = "p2p-offer-input";
    const btn = document.createElement("button");
    btn.className = "btn primary";
    btn.textContent = ad.side === "sell" ? "Купить" : "Продать";
    let selectedBank = ad.banks?.length === 1 ? ad.banks[0] : "";
    const bankChoices = document.createElement("div");
    bankChoices.className = "p2p-bank-choices";
    if (ad.banks && ad.banks.length > 1) {
      ad.banks.forEach((bank) => {
        const bankBtn = document.createElement("button");
        bankBtn.type = "button";
        bankBtn.className = "btn pill p2p-bank-btn";
        bankBtn.dataset.bank = bank;
        const icon = bankIcon(bank);
        const label = bankLabel(bank);
        bankBtn.innerHTML = icon
          ? `<img class="p2p-bank-logo" src="${icon}" alt="" onerror="this.remove()" /><span>${label}</span>`
          : label;
        bankBtn.addEventListener("click", () => {
          selectedBank = bank;
          bankChoices.querySelectorAll(".p2p-bank-btn").forEach((el) => {
            el.classList.toggle("active", el.dataset.bank === bank);
          });
        });
        bankChoices.appendChild(bankBtn);
      });
    }
    btn.addEventListener("click", async () => {
      const rub = Number(input.value);
      if (!rub || rub <= 0) {
        log("Введите сумму в RUB", "warn");
        return;
      }
      p2pModalActions.innerHTML = "";
      if (ad.banks && ad.banks.length > 1) {
        const bankTitle = document.createElement("div");
        bankTitle.className = "deal-row";
        bankTitle.textContent = "Выберите банкомат для начала сделки";
        p2pModalActions.appendChild(bankTitle);
        p2pModalActions.appendChild(bankChoices);
      }
      const confirm = document.createElement("div");
      confirm.className = "deal-row";
      confirm.textContent = `Подтвердите сумму ₽${formatAmount(rub, 0)} для сделки.`;
      const confirmBtn = document.createElement("button");
      confirmBtn.className = "btn primary";
      confirmBtn.textContent = "Предложить сделку";
      if (ad.banks && ad.banks.length > 1 && !selectedBank) {
        confirmBtn.disabled = true;
      }
      const cancelBtn = document.createElement("button");
      cancelBtn.className = "btn";
      cancelBtn.textContent = "Отмена";
      cancelBtn.addEventListener("click", () => {
        p2pModalActions.innerHTML = "";
        p2pModalActions.appendChild(input);
        p2pModalActions.appendChild(btn);
      });
      if (ad.banks && ad.banks.length > 1) {
        bankChoices.addEventListener("click", () => {
          confirmBtn.disabled = !selectedBank;
        });
      }
      confirmBtn.addEventListener("click", async () => {
        if (ad.banks && ad.banks.length > 1 && !selectedBank) {
          showNotice("Выберите банкомат");
          return;
        }
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
            body: JSON.stringify({ rub_amount: rub, bank: selectedBank }),
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

  const openMyAd = async (adId, fallbackAd = null) => {
    const ad =
      state.myAds.find((item) => item.id === adId) ||
      fallbackAd ||
      state.p2pAds.find((item) => item.id === adId);
    if (!ad) return;
    p2pModalTitle.textContent = `Объявление #${ad.public_id}`;
    p2pModalBody.innerHTML = `
      <div class="deal-detail-row"><span>Сторона:</span>${ad.side === "sell" ? "Продажа" : "Покупка"}</div>
      <div class="deal-detail-row"><span>Цена:</span>₽${formatAmount(ad.price_rub, 2)}/USDT</div>
      <div class="deal-detail-row"><span>Объём:</span>${formatAmount(ad.remaining_usdt)} / ${formatAmount(ad.total_usdt)} USDT</div>
      <div class="deal-detail-row"><span>Лимиты:</span>₽${formatAmount(ad.min_rub, 2)}-₽${formatAmount(ad.max_rub, 2)}</div>
      <div class="deal-detail-row"><span>Банки:</span>${(ad.banks || [])
        .map((bank) => bankLabel(bank))
        .join(", ") || "—"}</div>
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
    const adEditTerms = document.getElementById("adEditTerms");
    const scrollEditTerms = () => {
      scrollFieldIntoCard(adEditTerms, 0.25);
    };
    adEditTerms?.addEventListener("focus", scrollEditTerms);
    adEditTerms?.addEventListener("click", scrollEditTerms);
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
      const text = document.createElement("span");
      text.className = "p2p-bank-label";
      text.textContent = bankLabel(bankInput.value);
      label.appendChild(input);
      label.appendChild(text);
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
      const text = document.createElement("span");
      text.className = "p2p-bank-label";
      text.textContent = bankLabel(bank.label || bank.key);
      label.appendChild(input);
      label.appendChild(text);
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
    state.canManageDisputes = !!summary.can_access;
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
          <div class="deal-status">${item.assigned_to ? "В&nbsp;работе" : "Новый"}</div>
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
    const canManage = !!dispute.can_manage;
    state.activeDisputeId = dispute.id;
    p2pModalTitle.textContent = `Спор по сделке #${dispute.deal.public_id}`;
    const seller =
      dispute.seller?.display_name || dispute.seller?.full_name || dispute.seller?.username || "—";
    const buyer =
      dispute.buyer?.display_name || dispute.buyer?.full_name || dispute.buyer?.username || "—";
    const sellerUsername = dispute.seller?.username ? `@${dispute.seller.username}` : "—";
    const buyerUsername = dispute.buyer?.username ? `@${dispute.buyer.username}` : "—";
    const openerName = dispute.opened_by_name || "—";
    const comments = [];
    if (dispute.comment) {
      comments.push({ author: openerName, text: dispute.comment });
    }
    (dispute.messages || []).forEach((msg) => {
      if (msg?.text) {
        comments.push({ author: msg.author_name || msg.author_id || "—", text: msg.text });
      }
    });
    const baseUsdtAmount = dispute.deal?.rate
      ? Number(dispute.deal.usd_amount || 0) / Number(dispute.deal.rate || 1)
      : Number(dispute.deal.usdt_amount || 0);
    p2pModalBody.innerHTML = `
      <div class="deal-detail-row"><span>Продавец:</span>
        <span class="dispute-party">
          <button class="link-btn" data-user="${dispute.seller?.user_id || ""}">${seller}</button>
          <button class="btn pill tg-profile-btn" data-username="${dispute.seller?.username || ""}">Профиль TG</button>
        </span>
      </div>
      <div class="deal-detail-row"><span>Мерчант:</span>
        <span class="dispute-party">
          <button class="link-btn" data-user="${dispute.buyer?.user_id || ""}">${buyer}</button>
          <button class="btn pill tg-profile-btn" data-username="${dispute.buyer?.username || ""}">Профиль TG</button>
        </span>
      </div>
      <div class="deal-detail-row"><span>Открыл:</span>${openerName}</div>
      <div class="deal-detail-row"><span>Причина:</span>${dispute.reason}</div>
      <div class="deal-detail-row"><span>Открыт:</span>${formatDate(dispute.opened_at)}</div>
      <div class="deal-detail-row"><span>Сумма:</span>${formatAmount(baseUsdtAmount, 3)} USDT${
        canManage && dispute.deal?.rate
          ? ` • 1 USDT = ${formatAmount(dispute.deal.rate, 2)} RUB`
          : ""
      }</div>
    `;
    if (dispute.evidence.length) {
      const evidenceList = document.createElement("div");
      evidenceList.className = "p2p-evidence";
      dispute.evidence.forEach((item, index) => {
        const btn = document.createElement("button");
        btn.className = "btn evidence-btn";
        const author = item.author_name || "—";
        const label = item.kind === "video" ? "Видео" : item.kind === "photo" ? "Фото" : "Файл";
        btn.textContent = `${label} от ${author}`;
        btn.addEventListener("click", () => {
          if (!item.url) return;
          if (item.kind === "video") {
            openVideoModal(item.url);
            return;
          }
          if (item.kind === "photo") {
            openImageModal(item.url, `${label} от ${author}`);
            return;
          }
          if (tg?.openLink) {
            tg.openLink(item.url);
          } else {
            window.open(item.url, "_blank", "noopener");
          }
        });
        evidenceList.appendChild(btn);
      });
      p2pModalBody.appendChild(evidenceList);
    }
    const commentRow = document.createElement("div");
    commentRow.className = "deal-detail-row comment-row";
    const commentLabel = document.createElement("span");
    commentLabel.textContent = "Комментарий:";
    const commentButtons = document.createElement("div");
    commentButtons.className = "comment-buttons";
    if (!comments.length) {
      const empty = document.createElement("div");
      empty.textContent = "—";
      commentButtons.appendChild(empty);
    } else {
      comments.slice(0, 2).forEach((item) => {
        const btn = document.createElement("button");
        btn.className = "btn pill";
        btn.textContent = item.author;
        btn.addEventListener("click", () => {
          openCommentModal(item.text);
        });
        commentButtons.appendChild(btn);
      });
    }
    commentRow.appendChild(commentLabel);
    commentRow.appendChild(commentButtons);
    p2pModalBody.appendChild(commentRow);
    p2pModalBody.querySelectorAll(".link-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const targetId = btn.getAttribute("data-user");
        if (!targetId) return;
        openUserProfile(targetId);
      });
    });
    p2pModalBody.querySelectorAll(".tg-profile-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const username = btn.getAttribute("data-username");
        if (!username) return;
        const handle = username.replace(/^@/, "");
        const url = `https://t.me/${handle}`;
        if (tg?.openTelegramLink) {
          tg.openTelegramLink(url);
        } else if (tg?.openLink) {
          tg.openLink(url);
        } else {
          window.open(url, "_blank", "noopener");
        }
      });
    });
    p2pModalActions.innerHTML = "";
    if (dispute.deal) {
      const chatBtn = document.createElement("button");
      chatBtn.className = "btn";
      chatBtn.textContent = "Чат сделки";
      chatBtn.addEventListener("click", () => openDealChat(dispute.deal));
      p2pModalActions.appendChild(chatBtn);
    }
    if (canManage && !dispute.assigned_to) {
      const take = document.createElement("button");
      take.className = "btn primary";
      take.textContent = "Взять в работу";
      take.addEventListener("click", async () => {
        const res = await fetchJson(`/api/disputes/${dispute.id}/assign`, { method: "POST", body: "{}" });
        if (res?.ok) {
          await loadDisputes();
          await openDispute(dispute.id);
        }
      });
      p2pModalActions.appendChild(take);
    }
    if (canManage && dispute.assigned_to) {
      const baseTotal = dispute.deal?.rate
        ? Number(dispute.deal.usd_amount || 0) / Number(dispute.deal.rate || 1)
        : Number(dispute.deal.usdt_amount || 0);
      const sellerRow = document.createElement("div");
      sellerRow.className = "dispute-resolve-row";
      const sellerInput = document.createElement("input");
      sellerInput.className = "p2p-offer-input";
      sellerInput.placeholder = "USDT продавцу";
      const sellerName = document.createElement("div");
      sellerName.className = "dispute-resolve-name";
      sellerName.textContent = seller || "Продавец";
      const sellerMax = document.createElement("button");
      sellerMax.className = "btn pill";
      sellerMax.textContent = "Макс";
      sellerMax.addEventListener("click", () => {
        const other = Number((buyerInput.value || "").replace(",", ".")) || 0;
        const value = Math.max(0, baseTotal - other);
        sellerInput.value = formatAmount(value, 3);
      });
      sellerRow.appendChild(sellerInput);
      sellerRow.appendChild(sellerMax);
      sellerRow.appendChild(sellerName);

      const buyerRow = document.createElement("div");
      buyerRow.className = "dispute-resolve-row";
      const buyerInput = document.createElement("input");
      buyerInput.className = "p2p-offer-input";
      buyerInput.placeholder = "USDT мерчанту";
      const buyerName = document.createElement("div");
      buyerName.className = "dispute-resolve-name";
      buyerName.textContent = buyer || "Мерчант";
      const buyerMax = document.createElement("button");
      buyerMax.className = "btn pill";
      buyerMax.textContent = "Макс";
      buyerMax.addEventListener("click", () => {
        const other = Number((sellerInput.value || "").replace(",", ".")) || 0;
        const value = Math.max(0, baseTotal - other);
        buyerInput.value = formatAmount(value, 3);
      });
      buyerRow.appendChild(buyerInput);
      buyerRow.appendChild(buyerMax);
      buyerRow.appendChild(buyerName);

      const resolve = document.createElement("button");
      resolve.className = "btn";
      resolve.textContent = "Закрыть спор";
      resolve.addEventListener("click", async () => {
        const sellerAmount = Number((sellerInput.value || "").replace(",", ".")) || 0;
        const buyerAmount = Number((buyerInput.value || "").replace(",", ".")) || 0;
        if (!disputeResolveModal || !disputeResolveInfo) return;
        const sellerName = seller || "Продавцу";
        const buyerName = buyer || "Мерчанту";
        disputeResolveInfo.innerHTML = `
          <div>Продавцу (${sellerName}): <strong>${formatAmount(sellerAmount, 3)} USDT</strong></div>
          <div>Мерчанту (${buyerName}): <strong>${formatAmount(buyerAmount, 3)} USDT</strong></div>
        `;
        disputeResolveModal.classList.add("open");
        state.pendingResolve = { id: dispute.id, sellerAmount, buyerAmount };
      });
      p2pModalActions.appendChild(sellerRow);
      p2pModalActions.appendChild(buyerRow);
      p2pModalActions.appendChild(resolve);
    }
    p2pModal.classList.add("open");
    const snapshot = JSON.stringify({
      evidence: dispute.evidence.length,
      messages: dispute.messages?.length || 0,
      assigned: dispute.assigned_to || null,
      reason: dispute.reason,
      comment: dispute.comment,
    });
    state.disputeSnapshot = snapshot;
    startDisputeAutoRefresh(dispute.id);
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
      <div class="deal-detail-row"><span>Банкомат:</span>${deal.atm_bank ? (() => {
        const label = bankLabel(deal.atm_bank);
        const icon = bankIcon(deal.atm_bank);
        return icon
          ? `<span class="bank-inline"><img class="bank-inline-logo" src="${icon}" alt="" onerror="this.remove()" /><span>${label}</span></span>`
          : label;
      })() : "—"}</div>
      <div class="deal-detail-row"><span>Контрагент:</span>
        <button class="link owner-link" data-owner="${deal.counterparty?.user_id || ""}">${counterparty}</button>
      </div>
    `;
    if (deal.status === "paid" && deal.qr_stage === "awaiting_seller_attach" && deal.role === "seller") {
      const alert = document.createElement("div");
      alert.className = "deal-alert";
      alert.textContent =
        "Как будете готовы отправить QR\nНажмите Готов отправить!";
      dealModalBody.appendChild(alert);
    }
    if (deal.status === "paid" && deal.qr_stage === "awaiting_seller_attach" && deal.role === "buyer") {
      const alert = document.createElement("div");
      alert.className = "deal-alert";
      alert.textContent = "Ожидаем пока продавец дойдет до банкомата.";
      dealModalBody.appendChild(alert);
    }
    if (deal.status === "paid" && deal.qr_stage === "awaiting_buyer_ready" && deal.role === "seller") {
      const alert = document.createElement("div");
      alert.className = "deal-alert";
      alert.textContent =
        "⚠️ Ожидайте готовность покупателя!\nКак покупатель будет готов вам придет уведомление.";
      dealModalBody.appendChild(alert);
    }
    if (deal.status === "paid" && deal.qr_stage === "awaiting_buyer_ready" && deal.role === "buyer") {
      const alert = document.createElement("div");
      alert.className = "deal-alert";
      alert.textContent = "⚠️ Продавец готов отправить QR.\nНажмите «Готов сканировать».";
      dealModalBody.appendChild(alert);
    }
    if (deal.status === "paid" && deal.qr_stage === "awaiting_seller_photo" && deal.role === "seller") {
      const alert = document.createElement("div");
      alert.className = "deal-alert";
      alert.textContent = "📎 Прикрепите QR по кнопке ниже.";
      dealModalBody.appendChild(alert);
    }
    if (deal.status === "paid" && deal.qr_stage === "ready" && deal.role === "seller") {
      const alert = document.createElement("div");
      alert.className = "deal-alert";
      alert.textContent = "✅ QR прикреплен и отправлен в чат.";
      dealModalBody.appendChild(alert);
    }
    const ownerLink = dealModalBody.querySelector(".owner-link");
    if (ownerLink && deal.counterparty?.user_id) {
      ownerLink.addEventListener("click", () => openUserProfile(deal.counterparty.user_id));
    }
    dealModalActions.innerHTML = "";
    const actions = deal.actions || {};
    const topRow = document.createElement("div");
    topRow.className = "modal-actions-row";
    const bottomRow = document.createElement("div");
    bottomRow.className = "modal-actions-row modal-actions-bottom";
    dealModalActions.appendChild(topRow);
    dealModalActions.appendChild(bottomRow);
    const addAction = (container, label, handler, primary = false, extraClass = "", options = {}) => {
      const btn = document.createElement("button");
      btn.className = `btn ${primary ? "primary" : ""} ${extraClass}`.trim();
      if (options.className) {
        btn.classList.add(options.className);
      }
      btn.textContent = label;
      btn.addEventListener("click", handler);
      if (options.badge) {
        const badge = document.createElement("span");
        badge.className = `btn-badge ${options.badgeClass || ""}`.trim();
        badge.textContent = options.badgeText || "";
        btn.classList.add("has-badge");
        btn.appendChild(badge);
      }
      container.appendChild(btn);
      return btn;
    };
    const isCompleted = deal.status === "completed";
    if (!isCompleted && actions.accept_offer) {
      addAction(topRow, "Принять", () => dealAction("accept", deal.id), true);
    }
    if (!isCompleted && actions.decline_offer) {
      addAction(topRow, "Отменить", () => dealAction("decline", deal.id), false, "status-bad");
    }
    if (!isCompleted && deal.status !== "dispute") {
      if (actions.seller_ready) {
        addAction(topRow, "Готов отправить", () => dealAction("seller-ready", deal.id), false, "status-ok");
      }
      if (actions.buyer_ready) {
        addAction(topRow, "Готов сканировать", () => dealAction("buyer-ready", deal.id), false, "status-ok");
      }
    }
    if (!isCompleted && actions.confirm_seller && deal.qr_stage === "ready") {
      addAction(topRow, "Получил нал", () => openConfirmComplete(deal), true);
    }
    if (
      !isCompleted &&
      deal.status === "paid" &&
      deal.role === "seller" &&
      ["awaiting_seller_photo", "ready"].includes(deal.qr_stage)
    ) {
      addAction(topRow, "Прикрепить QR", () => uploadQrForDeal(deal.id), true);
    }
    if (!isCompleted && actions.confirm_buyer && deal.qr_stage === "ready" && !deal.buyer_cash_confirmed) {
      addAction(topRow, "Успешно снял", () => openBuyerProofModal(deal.id), true);
    } else if (
      !isCompleted &&
      deal.role === "buyer" &&
      deal.buyer_cash_confirmed &&
      deal.status === "paid"
    ) {
      const doneBtn = addAction(topRow, "Снятие подтверждено", () => {}, false, "status-ok");
      doneBtn.disabled = true;
    }
    if (
      !isCompleted &&
      deal.buyer_id &&
      deal.seller_id &&
      ["reserved", "paid", "dispute"].includes(deal.status)
    ) {
      const hasUnread = isChatUnread(deal);
      addAction(topRow, "Открыть чат", () => openDealChat(deal), false, "", {
        badge: hasUnread,
        badgeClass: "dot",
        className: "deal-chat-btn",
      });
    }
    if (!isCompleted && deal.status === "dispute" && deal.dispute_id) {
      addAction(
        topRow,
        "Добавить доказательства",
        () => uploadDisputeEvidence(deal.dispute_id),
        true
      );
    }
    if (!isCompleted && deal.dispute_available_at && deal.status === "paid") {
      addAction(
        bottomRow,
        "⚠️ Открыть спор",
        () => {
          const availableAt = new Date(deal.dispute_available_at);
          const now = new Date();
          if (availableAt > now) {
            const diffMs = availableAt - now;
            const minutes = Math.ceil(diffMs / 60000);
            showNotice(`Открыть спор можно через ${minutes} мин`);
            return;
          }
          openDisputeModal(deal.id);
        },
        false,
        "status-bad"
      );
    }
    if (!isCompleted && actions.cancel) {
      addAction(
        bottomRow,
        "Отменить сделку",
        () => dealAction("cancel", deal.id),
        false,
        "status-bad"
      );
    }
    if (deal.status === "completed" && !deal.reviewed) {
      addAction(
        bottomRow,
        "Оценить сделку",
        () => openReviewForDeal(deal),
        true,
        "",
        { className: "review-btn" }
      );
    }
    if (isCompleted) {
      topRow.remove();
      if (!bottomRow.childElementCount) {
        bottomRow.remove();
      }
    }
    if (!bottomRow.childElementCount) {
      bottomRow.remove();
    }
  };

  const maybeRenderDealModal = (deal) => {
    if (!deal) return;
    let snapshot = "";
    try {
      const { chat_last_at, chat_last_sender_id, ...rest } = deal;
      snapshot = JSON.stringify(rest);
    } catch {
      snapshot = `${deal.id || ""}:${deal.status || ""}:${deal.qr_stage || ""}`;
    }
    if (state.activeDealSnapshot === snapshot) {
      return;
    }
    state.activeDealSnapshot = snapshot;
    renderDealModal(deal);
  };

  const uploadQrFromGallery = async (dealId) => {
    if (!state.initData) {
      showNotice("initData не найден. Откройте WebApp из Telegram.");
      return;
    }
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "image/*";
    input.style.position = "fixed";
    input.style.left = "-9999px";
    input.style.opacity = "0";
    document.body.appendChild(input);
    input.onchange = async () => {
      const file = input.files?.[0];
      input.remove();
      if (!file) return;
      const form = new FormData();
      form.append("file", file, file.name || "qr.png");
      showNotice("Загружаем QR...");
      try {
        const res = await fetch(`/api/deals/${dealId}/qr`, {
          method: "POST",
          headers: { "X-Telegram-Init-Data": state.initData },
          body: form,
        });
        if (!res.ok) {
          const text = await res.text();
          showNotice(text || "Не удалось отправить QR");
          return;
        }
        showNotice("QR отправлен");
        await loadChatMessages(dealId);
        const payload = await fetchJson(`/api/deals/${dealId}`);
        if (payload?.ok) {
          renderDealModal(payload.deal);
        }
      } catch (err) {
        showNotice(`Ошибка: ${err.message}`);
      }
    };
    input.click();
  };

  const uploadQrFromScan = async (dealId) => {
    if (!state.initData) {
      showNotice("initData не найден. Откройте WebApp из Telegram.");
      return;
    }
    if (!tg?.showScanQrPopup) {
      showNotice("Сканер QR недоступен");
      return;
    }
    const handleScan = async (data) => {
      try {
        const payload = await fetchJson(`/api/deals/${dealId}/qr-text`, {
          method: "POST",
          body: JSON.stringify({ text: data }),
        });
        if (!payload?.ok) {
          showNotice("Не удалось отправить QR");
          return;
        }
        showNotice("QR отправлен");
        await loadChatMessages(dealId);
        const dealPayload = await fetchJson(`/api/deals/${dealId}`);
        if (dealPayload?.ok) {
          renderDealModal(dealPayload.deal);
        }
      } catch {
        showNotice("Не удалось отправить QR");
      }
    };
    tg.showScanQrPopup({ text: "Наведите камеру на QR" }, (data) => {
      if (!data) return;
      tg.closeScanQrPopup?.();
      handleScan(data);
      return true;
    });
  };

  const resetBuyerProofModal = (dealId) => {
    if (!buyerProofModal) return;
    if (buyerProofTitle) {
      buyerProofTitle.textContent = "Прикрепите фото операции и нажмите отправить.";
    }
    if (buyerProofImg) buyerProofImg.removeAttribute("src");
    buyerProofPreview?.classList.remove("show");
    if (buyerProofSend) buyerProofSend.disabled = true;
    if (buyerProofPick) buyerProofPick.disabled = false;
    buyerProofActions?.classList.remove("is-hidden");
    const draft = state.buyerProofDraft?.[dealId];
    if (draft?.url && buyerProofImg && buyerProofPreview && buyerProofSend) {
      buyerProofImg.src = draft.url;
      buyerProofPreview.classList.add("show");
      buyerProofSend.disabled = false;
    }
    if (state.buyerProofSent?.[dealId]) {
      if (buyerProofTitle) buyerProofTitle.textContent = "Фото операции отправлено.";
      buyerProofActions?.classList.add("is-hidden");
      if (buyerProofSend) buyerProofSend.disabled = true;
      if (buyerProofPick) buyerProofPick.disabled = true;
    }
  };

  const openBuyerProofModal = (dealId) => {
    if (!buyerProofModal) return;
    state.buyerProofDealId = dealId;
    resetBuyerProofModal(dealId);
    buyerProofModal.classList.add("open");
  };

  const closeBuyerProofModal = () => {
    buyerProofModal?.classList.remove("open");
    state.buyerProofDealId = null;
  };

  const uploadBuyerProof = async (dealId) => {
    if (!state.initData) {
      showNotice("initData не найден. Откройте WebApp из Telegram.");
      return;
    }
    const draft = state.buyerProofDraft?.[dealId];
    if (!draft?.file) {
      showNotice("Выберите фото операции");
      return;
    }
    const form = new FormData();
    form.append("file", draft.file);
    try {
      const res = await fetch(`/api/deals/${dealId}/buyer-proof`, {
        method: "POST",
        headers: { "X-Telegram-Init-Data": state.initData },
        body: form,
      });
      if (!res.ok) {
        const text = await res.text();
        showNotice(text || "Не удалось отправить фото");
        return;
      }
      showNotice("Фото операции отправлено");
      state.buyerProofSent[dealId] = true;
      persistBuyerProofSent();
      state.buyerProofDraft[dealId] = null;
      resetBuyerProofModal(dealId);
      closeBuyerProofModal();
      const dealPayload = await fetchJson(`/api/deals/${dealId}`);
      if (dealPayload?.ok) {
        maybeRenderDealModal(dealPayload.deal);
      }
      await loadChatMessages(dealId);
    } catch (err) {
      showNotice(`Ошибка: ${err.message}`);
    }
  };

  const resetDisputeOpenModal = () => {
    if (disputeVideoName) {
      disputeVideoName.textContent = "Видео не выбрано.";
    }
    if (disputeReason) {
      disputeReason.value = "no_cash";
    }
    if (disputeReasonCustom) {
      disputeReasonCustom.value = "";
    }
    disputeReasonCustomField?.classList.add("is-hidden");
    if (disputeComment) {
      disputeComment.value = "";
    }
    if (disputeOpenSend) {
      disputeOpenSend.disabled = true;
    }
    state.disputeOpenDraft = null;
  };

  const openDisputeModal = (dealId) => {
    if (!disputeOpenModal) return;
    state.disputeOpenDealId = dealId;
    resetDisputeOpenModal();
    disputeOpenModal.classList.add("open");
  };

  const closeDisputeOpenModal = () => {
    disputeOpenModal?.classList.remove("open");
    state.disputeOpenDealId = null;
  };

  const submitOpenDispute = async (dealId) => {
    if (!state.initData) {
      showNotice("initData не найден. Откройте WebApp из Telegram.");
      return;
    }
    const draft = state.disputeOpenDraft;
    if (!draft?.file) {
      showNotice("Прикрепите видео с банкомата");
      return;
    }
    if (disputeVideoName) {
      disputeVideoName.textContent = "Загружается...";
    }
    const reasonKey = disputeReason?.value || "no_cash";
    const reasonText = (disputeReasonCustom?.value || "").trim();
    const comment = (disputeComment?.value || "").trim() || null;
    const payload = await fetchJson(`/api/deals/${dealId}/open-dispute`, {
      method: "POST",
      body: JSON.stringify({ comment, reason: reasonKey, reason_text: reasonText }),
    });
    if (!payload?.ok) {
      if (disputeVideoName) {
        disputeVideoName.textContent = "Ошибка загрузки.";
      }
      showNotice("Не удалось открыть спор");
      return;
    }
    let disputeId = payload.deal?.dispute_id || null;
    if (!disputeId) {
      const dealPayload = await fetchJson(`/api/deals/${dealId}`);
      disputeId = dealPayload?.deal?.dispute_id || null;
    }
    if (!disputeId) {
      showNotice("Спор открыт, но ID не найден");
      closeDisputeOpenModal();
      return;
    }
    const form = new FormData();
    form.append("file", draft.file);
    try {
      const res = await fetch(`/api/disputes/${disputeId}/evidence`, {
        method: "POST",
        headers: { "X-Telegram-Init-Data": state.initData },
        body: form,
      });
      if (!res.ok) {
        const text = await res.text();
        if (disputeVideoName) {
          disputeVideoName.textContent = "Ошибка загрузки.";
        }
        showNotice(text || "Не удалось отправить видео");
        return;
      }
      if (disputeVideoName) {
        disputeVideoName.textContent = "Загружено.";
      }
      showNotice("Спор открыт");
      closeDisputeOpenModal();
      const dealPayload = await fetchJson(`/api/deals/${dealId}`);
      if (dealPayload?.ok) {
        maybeRenderDealModal(dealPayload.deal);
      }
    } catch (err) {
      if (disputeVideoName) {
        disputeVideoName.textContent = "Ошибка загрузки.";
      }
      showNotice(`Ошибка: ${err.message}`);
    }
  };

  const uploadQrForDeal = async (dealId) => {
    if (!tg?.showPopup) {
      return uploadQrFromGallery(dealId);
    }
    tg.showPopup(
      {
        title: "QR код",
        message: "Выберите способ",
        buttons: [
          { id: "scan", type: "default", text: "Сканировать" },
          { id: "gallery", type: "default", text: "Из галереи" },
          { id: "cancel", type: "cancel", text: "Отмена" },
        ],
      },
      (buttonId) => {
        if (buttonId === "scan") {
          uploadQrFromScan(dealId);
        } else if (buttonId === "gallery") {
          uploadQrFromGallery(dealId);
        }
      }
    );
  };

  const uploadDisputeEvidence = async (disputeId) => {
    openDisputeEvidenceModal(disputeId);
  };

  const resetDisputeEvidenceModal = () => {
    if (disputeEvidenceName) {
      disputeEvidenceName.textContent = "Видео не выбрано.";
    }
    if (disputeEvidenceComment) {
      disputeEvidenceComment.value = "";
    }
    if (disputeEvidenceSend) {
      disputeEvidenceSend.disabled = true;
    }
    state.disputeEvidenceDraft = null;
  };

  const openDisputeEvidenceModal = (disputeId) => {
    if (!disputeEvidenceModal) return;
    state.disputeEvidenceId = disputeId;
    resetDisputeEvidenceModal();
    disputeEvidenceModal.classList.add("open");
  };

  const closeDisputeEvidenceModal = () => {
    disputeEvidenceModal?.classList.remove("open");
    state.disputeEvidenceId = null;
  };

  const submitDisputeEvidence = async (disputeId) => {
    if (!state.initData) {
      showNotice("initData не найден. Откройте WebApp из Telegram.");
      return;
    }
    const draft = state.disputeEvidenceDraft;
    if (!draft?.file) {
      showNotice("Прикрепите видео с Банка");
      return;
    }
    if (disputeEvidenceName) {
      disputeEvidenceName.textContent = "Загружается...";
    }
    const form = new FormData();
    form.append("file", draft.file);
    try {
      const res = await fetch(`/api/disputes/${disputeId}/evidence`, {
        method: "POST",
        headers: { "X-Telegram-Init-Data": state.initData },
        body: form,
      });
      if (!res.ok) {
        const text = await res.text();
        if (disputeEvidenceName) {
          disputeEvidenceName.textContent = "Ошибка загрузки.";
        }
        showNotice(text || "Не удалось отправить доказательство");
        return;
      }
      const note = (disputeEvidenceComment?.value || "").trim();
      if (note) {
        await fetchJson(`/api/disputes/${disputeId}/message`, {
          method: "POST",
          body: JSON.stringify({ text: note }),
        });
      }
      if (disputeEvidenceName) {
        disputeEvidenceName.textContent = "Загружено.";
      }
      showNotice("Доказательства отправлены");
      closeDisputeEvidenceModal();
      if (state.activeDisputeId === disputeId) {
        await openDispute(disputeId);
      }
    } catch (err) {
      if (disputeEvidenceName) {
        disputeEvidenceName.textContent = "Ошибка загрузки.";
      }
      showNotice(`Ошибка: ${err.message}`);
    }
  };

  const isChatAtBottom = () => {
    if (!chatList) return true;
    const threshold = 24;
    return chatList.scrollTop + chatList.clientHeight >= chatList.scrollHeight - threshold;
  };

  const renderChatMessages = (messages, options = {}) => {
    if (!chatList) return;
    const keepPosition = options.keepPosition;
    const wasAtBottom = keepPosition ? isChatAtBottom() : true;
    const prevScrollTop = chatList.scrollTop;
    const prevScrollHeight = chatList.scrollHeight;
    chatList.innerHTML = "";
    (messages || []).forEach((msg) => {
      const item = document.createElement("div");
      item.className = `chat-message ${isSelfSender(msg.sender_id) ? "self" : ""} ${
        msg.system ? "system" : ""
      }`.trim();
      if (msg.system) {
        const label = document.createElement("div");
        label.className = "chat-system-label chat-bc-label";
        label.textContent = "BC Cash";
        item.appendChild(label);
      } else if (msg.sender_label) {
        const label = document.createElement("div");
        label.className = "chat-system-label chat-mod-label";
        label.textContent = msg.sender_label;
        item.appendChild(label);
      }
      const fileName = (msg.file_name || "").toLowerCase();
      const isImage = /\.(png|jpe?g|gif|webp|bmp|svg)$/i.test(fileName);
      if (msg.file_url && !msg.system) {
        const label = document.createElement("div");
        label.className = "chat-file-label";
        label.textContent = isImage ? "📎 Фото" : "📎 Файл";
        item.appendChild(label);
      }
      if (msg.text) {
        const text = document.createElement("div");
        text.textContent = msg.text;
        item.appendChild(text);
      }
      if (msg.file_url) {
        if (isImage) {
          const img = document.createElement("img");
          img.src = msg.file_url;
          img.alt = msg.file_name || "Фото";
          img.className = "chat-image";
          img.addEventListener("click", () => openImageModal(msg.file_url, img.alt));
          item.appendChild(img);
        } else {
          const link = document.createElement("a");
          link.href = msg.file_url;
          link.target = "_blank";
          link.rel = "noopener";
          link.className = "chat-file";
          link.textContent = msg.file_name || "Файл";
          item.appendChild(link);
        }
      }
      const meta = document.createElement("div");
      meta.className = "chat-meta";
      meta.textContent = formatDate(msg.created_at);
      item.appendChild(meta);
      chatList.appendChild(item);
    });
    if (keepPosition && !wasAtBottom) {
      const nextScrollHeight = chatList.scrollHeight;
      chatList.scrollTop = prevScrollTop + (nextScrollHeight - prevScrollHeight);
    } else {
      chatList.scrollTop = chatList.scrollHeight;
    }
  };

  const loadChatMessages = async (dealId, options = {}) => {
    const payload = await fetchJson(`/api/deals/${dealId}/chat`);
    if (!payload?.ok) return;
    const messages = payload.messages || [];
    renderChatMessages(messages, { keepPosition: options.keepPosition !== false });
    return messages;
  };

  const openDealChat = async (deal) => {
    if (!chatModal) return;
    state.activeChatDealId = deal.id;
    if (chatModalTitle) {
      chatModalTitle.textContent = `Чат сделки #${deal.public_id}`;
    }
    const messages = await loadChatMessages(deal.id, { keepPosition: false });
    const lastMessage = Array.isArray(messages) && messages.length ? messages[messages.length - 1] : null;
    if (lastMessage?.created_at) {
      markChatRead(deal.id, lastMessage.created_at);
    } else if (deal.chat_last_at) {
      markChatRead(deal.id, deal.chat_last_at);
    } else {
      markChatRead(deal.id);
    }
    if (state.unreadDeals.has(deal.id)) {
      state.unreadDeals.delete(deal.id);
      persistUnreadDeals();
    }
    updateQuickDealsButton(state.deals || []);
    if (quickDealsPanel?.classList.contains("open")) {
      renderQuickDeals();
    }
    const chatBtn = dealModalActions?.querySelector(".deal-chat-btn");
    chatBtn?.classList.remove("has-badge");
    quickDealsBtn?.classList.add("dimmed");
    chatModal.classList.add("open");
  };

  const updateChatFileHint = () => {
    if (!chatFileHint) return;
    const file = chatFile?.files?.[0];
    if (file) {
      chatFileHint.textContent = `📎 ${file.name}`;
      chatFileHint.classList.add("show");
    } else {
      chatFileHint.textContent = "";
      chatFileHint.classList.remove("show");
    }
  };

  const openDealModal = async (dealId) => {
    const payload = await fetchJson(`/api/deals/${dealId}`);
    if (!payload?.ok) return;
    if (state.unreadDeals.has(dealId)) {
      state.unreadDeals.delete(dealId);
      persistUnreadDeals();
      updateQuickDealsButton(state.deals || []);
      if (quickDealsPanel?.classList.contains("open")) {
        renderQuickDeals();
      }
    }
    state.pendingRead = state.pendingRead || {};
    state.pendingRead[dealId] = true;
    persistPendingRead();
    state.activeDealSnapshot = null;
    maybeRenderDealModal(payload.deal);
    state.activeDealId = dealId;
    startDealAutoRefresh();
    dealModal.classList.add("open");
  };

  const dealAction = async (action, dealId) => {
    const path = `/api/deals/${dealId}/${action}`;
    const payload = await fetchJson(path, { method: "POST", body: "{}" });
    if (!payload?.ok) return;
    maybeRenderDealModal(payload.deal);
    await loadDeals();
  };

  const openConfirmComplete = (deal) => {
    if (!confirmCompleteModal || !confirmCompleteSubmit) {
      dealAction("confirm-seller", deal.id);
      return;
    }
    if (confirmCompleteText) {
      confirmCompleteText.textContent =
        "Вы уверены что хотите завершить сделку? деньги перейдут другой стороне.";
    }
    confirmCompleteModal.classList.add("open");
    const closeModal = () => {
      confirmCompleteModal.classList.remove("open");
    };
    const handleSubmit = async () => {
      confirmCompleteSubmit.disabled = true;
      try {
        const unlock =
          typeof window.requestPinUnlock === "function"
            ? await window.requestPinUnlock()
            : true;
        if (!unlock) {
          confirmCompleteSubmit.disabled = false;
          return;
        }
        await dealAction("confirm-seller", deal.id);
        closeModal();
      } finally {
        confirmCompleteSubmit.disabled = false;
      }
    };
    confirmCompleteSubmit.onclick = handleSubmit;
    confirmCompleteCancel && (confirmCompleteCancel.onclick = closeModal);
    confirmCompleteClose && (confirmCompleteClose.onclick = closeModal);
  };

  const stopDealAutoRefresh = () => {
    if (state.dealRefreshTimer) {
      window.clearInterval(state.dealRefreshTimer);
      state.dealRefreshTimer = null;
    }
  };

  const startDealAutoRefresh = () => {
    stopDealAutoRefresh();
    state.dealRefreshTimer = window.setInterval(async () => {
      if (!state.activeDealId || !dealModal?.classList.contains("open")) return;
    const payload = await fetchJson(`/api/deals/${state.activeDealId}`);
    if (!payload?.ok) return;
    maybeRenderDealModal(payload.deal);
    if (["completed", "canceled", "expired"].includes(payload.deal.status)) {
      stopDealAutoRefresh();
    }
    }, 2000);
  };

  const startLivePolling = () => {
    if (state.livePollTimer) return;
    state.livePollTimer = window.setInterval(async () => {
      if (state.livePollInFlight) return;
      state.livePollInFlight = true;
      try {
        await loadDeals();
        await loadBalance();
        if (state.activeDealId && dealModal?.classList.contains("open")) {
          const payload = await fetchJson(`/api/deals/${state.activeDealId}`);
          if (payload?.ok) {
            maybeRenderDealModal(payload.deal);
          }
        }
        if (state.activeChatDealId && chatModal?.classList.contains("open")) {
          await loadChatMessages(state.activeChatDealId);
        }
      } finally {
        state.livePollInFlight = false;
      }
    }, 500);
  };

  const parseInitDataUser = (initData) => {
    if (!initData) return null;
    try {
      const params = new URLSearchParams(initData);
      const rawUser = params.get("user");
      if (!rawUser) return null;
      return JSON.parse(rawUser);
    } catch {
      return null;
    }
  };

  const initTelegram = async () => {
    try {
      await fetch("/api/debug/initdata", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tag: "init-start" }),
      });
    } catch {
      // ignore debug
    }
    if (!tg && window.Telegram?.WebApp) {
      tg = window.Telegram.WebApp;
    }
    if (tg) {
      tg.ready();
      const platform = (tg.platform || "").toLowerCase();
      const isMobile =
        platform === "android" ||
        platform === "ios" ||
        /iphone|ipad|ipod|android/i.test(navigator.userAgent);
      if (isMobile) {
        tg.expand();
      }
      const urlParams = new URLSearchParams(window.location.search);
      const initFromUrl = urlParams.get("initData");
      state.initData = tg.initData || initFromUrl || "";
      refreshInitData();
      const theme = detectTheme();
      applyTheme(theme);
      updateThemeToggle(theme);
      updateInitDebug();
    } else {
      const theme = detectTheme();
      applyTheme(theme);
      updateThemeToggle(theme);
      log("WebApp API не найден. Проверьте запуск через Telegram.", "warn");
      updateInitDebug();
    }
    const unsafeUser = tg?.initDataUnsafe?.user;
    const parsedUser = !unsafeUser ? parseInitDataUser(state.initData) : null;
    const fallbackUser = unsafeUser || parsedUser;
    if (fallbackUser) {
      setAuthState(fallbackUser);
    }
    const bootstrapApp = async () => {
      if (state.bootstrapDone) return;
      if (!state.initData && !refreshInitData()) return;
      state.bootstrapDone = true;
      const user = await fetchMe();
      if (user) {
        setAuthState(user);
        log(
          `Готово. Пользователь: ${user.display_name || user.full_name || user.first_name || user.id}`
        );
      } else {
        state.bootstrapDone = false;
        if (!state.bootstrapRetry) {
          state.bootstrapRetry = window.setTimeout(() => {
            state.bootstrapRetry = null;
            bootstrapApp();
          }, 800);
        }
        return;
      }
      await loadSummary();
      await loadProfile();
      await loadBalance();
      await loadDeals();
      setView("profile");
      await loadP2PSummary();
      await loadPublicAds("sell");
      startLivePolling();
      if (p2pBalanceHint && state.balance !== null) {
        p2pBalanceHint.textContent = `Баланс: ${formatAmount(state.balance)} USDT`;
      }
      await loadBanks();
      await loadDisputes();
      await loadAdmin();
    };

    await bootstrapApp();
    try {
      await fetch("/api/debug/initdata", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tag: "init-after",
          has_init: Boolean(state.initData),
        }),
      });
    } catch {
      // ignore debug
    }
    if (!state.bootstrapDone && tg) {
      state.initRetryTimer = window.setInterval(async () => {
        if (state.bootstrapDone) {
          window.clearInterval(state.initRetryTimer);
          state.initRetryTimer = null;
          return;
        }
        const urlParams = new URLSearchParams(window.location.search);
        const initFromUrl = urlParams.get("initData");
        state.initData = tg.initData || initFromUrl || "";
        if (state.initData) {
          await bootstrapApp();
          if (state.bootstrapDone) {
            window.clearInterval(state.initRetryTimer);
            state.initRetryTimer = null;
          }
        }
      }, 500);
    }
    if (!state.initData) {
      showNotice("Нет initData. Откройте WebApp из Telegram.");
    }
    try {
      await fetch("/api/debug/initdata", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          init_data: state.initData || "",
          unsafe: tg?.initDataUnsafe || null,
        }),
      });
    } catch {
      // ignore debug errors
    }
    if (!tg && !state.tgRetryTimer) {
      state.tgRetryTimer = window.setInterval(() => {
        if (window.Telegram?.WebApp) {
          tg = window.Telegram.WebApp;
          window.clearInterval(state.tgRetryTimer);
          state.tgRetryTimer = null;
          initTelegram();
        }
      }, 500);
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
        ${item.comment ? `<div class="deal-row">${item.comment}</div>` : ""}
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

  const loadReviews = async (userId = null) => {
    const path = userId ? `/api/reviews?user_id=${userId}` : "/api/reviews";
    const payload = await fetchJson(path);
    if (!payload?.ok) return null;
    const positive = payload.positive ?? 0;
    const negative = payload.negative ?? 0;
    const total = positive + negative;
    const successPercent = total ? Math.round((positive / total) * 100) : 0;
    reviewsSummary.textContent = `Успешные сделки: ${successPercent}%`;
    return payload.reviews || [];
  };

  themeToggle?.addEventListener("click", () => {
    const current = document.documentElement.dataset.theme || "light";
    const next = current === "light" ? "dark" : "light";
    applyTheme(next);
    updateThemeToggle(next);
    persistTheme(next);
  });

  navButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      setView(btn.dataset.view);
    });
  });

  const setQuickDealsOpen = (open) => {
    if (!quickDealsPanel) return;
    quickDealsPanel.classList.toggle("open", open);
    quickDealsPanel.setAttribute("aria-hidden", open ? "false" : "true");
  };

  quickDealsBtn?.addEventListener("click", () => {
    const isOpen = quickDealsPanel?.classList.contains("open");
    if (isOpen) {
      setQuickDealsOpen(false);
      return;
    }
    renderQuickDeals();
    setQuickDealsOpen(true);
  });

  document.addEventListener("click", (event) => {
    if (!quickDealsPanel?.classList.contains("open")) return;
    const target = event.target;
    if (!target) return;
    if (quickDealsPanel.contains(target) || quickDealsBtn?.contains(target)) {
      return;
    }
    setQuickDealsOpen(false);
  });

  const removeSystemNotice = (key) => {
    state.systemNotifications = (state.systemNotifications || []).filter((item) => item.key !== key);
    persistSystemNotifications();
    state.systemNoticeActive = null;
    hideSystemNotice();
    renderSystemNotifications();
  };

  systemNoticeRate?.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
    clearSystemNoticeTimer();
    systemNoticeRateForm?.classList.add("show");
    if (systemNoticeSubmit) {
      systemNoticeSubmit.disabled = !pendingReviewRating;
    }
  });

  systemNoticeSkip?.addEventListener("click", () => {
    state.systemNoticeActive = null;
    if (typeof pendingReviewRating !== "undefined") {
      pendingReviewRating = null;
    }
    systemNoticeLike?.classList.remove("active");
    systemNoticeDislike?.classList.remove("active");
    if (systemNoticeComment) systemNoticeComment.value = "";
    systemNoticeRateForm?.classList.remove("show");
    hideSystemNotice();
  });

  const setReviewRating = (value) => {
    pendingReviewRating = value;
    systemNoticeLike?.classList.toggle("active", value === 1);
    systemNoticeDislike?.classList.toggle("active", value === -1);
    if (systemNoticeSubmit) {
      systemNoticeSubmit.disabled = !pendingReviewRating;
    }
  };

  systemNoticeLike?.addEventListener("click", () => setReviewRating(1));
  systemNoticeDislike?.addEventListener("click", () => setReviewRating(-1));

  systemNoticeSubmit?.addEventListener("click", async (event) => {
    event.preventDefault();
    event.stopPropagation();
    if (!systemNoticeSubmit) return;
    if (systemNoticeSubmit.disabled) {
      showNotice("Выберите оценку");
      return;
    }
    systemNoticeSubmit.disabled = true;
    systemNoticeSubmit.classList.add("loading");
    showNotice("Отправка…");
    const active = state.systemNoticeActive;
    if (!active?.deal_id || !pendingReviewRating) {
      showNotice("Выберите оценку");
      systemNoticeSubmit.disabled = false;
      systemNoticeSubmit.classList.remove("loading");
      return;
    }
    const comment = systemNoticeComment?.value || "";
    let payload = null;
    try {
      const res = await fetch("/api/reviews", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Telegram-Init-Data": state.initData,
        },
        body: JSON.stringify({
          deal_id: active.deal_id,
          rating: pendingReviewRating,
          comment,
        }),
      });
      if (!res.ok) {
        let text = await res.text();
        try {
          const data = JSON.parse(text);
          if (data && data.error) {
            text = data.error;
          }
        } catch {
          // ignore
        }
        showNotice(text || "Не удалось отправить отзыв");
        if (text && text.includes("Отзыв уже оставлен")) {
          removeSystemNotice(active.key);
          await loadDeals();
          return;
        }
        systemNoticeSubmit.disabled = false;
        systemNoticeSubmit.classList.remove("loading");
        return;
      }
      payload = await res.json();
    } catch (err) {
      showNotice(`Ошибка: ${err.message}`);
      systemNoticeSubmit.disabled = false;
      systemNoticeSubmit.classList.remove("loading");
      return;
    }
    pendingReviewRating = null;
    if (systemNoticeComment) systemNoticeComment.value = "";
    removeSystemNotice(active.key);
    await loadDeals();
  });

  const bindPressFeedback = () => {
    const pressClass = "is-pressed";
    const addPress = (btn) => {
      if (!btn || btn.classList.contains(pressClass)) return;
      btn.classList.add(pressClass);
      window.setTimeout(() => {
        btn.classList.remove(pressClass);
      }, 160);
    };
    const clearPress = (btn) => {
      btn?.classList?.remove?.(pressClass);
    };
    document.addEventListener(
      "touchstart",
      (event) => {
        const btn = event.target.closest(".back-btn");
        if (!btn) return;
        addPress(btn);
      },
      { passive: true }
    );
    document.addEventListener("touchend", (event) => {
      const btn = event.target.closest(".back-btn");
      if (!btn) return;
      clearPress(btn);
    });
    document.addEventListener("touchcancel", (event) => {
      const btn = event.target.closest(".back-btn");
      if (!btn) return;
      clearPress(btn);
    });
    document.addEventListener("mousedown", (event) => {
      const btn = event.target.closest(".back-btn");
      if (!btn) return;
      addPress(btn);
    });
    document.addEventListener("mouseup", (event) => {
      const btn = event.target.closest(".back-btn");
      if (!btn) return;
      clearPress(btn);
    });
    document.addEventListener("mouseleave", (event) => {
      const btn = event.target.closest(".back-btn");
      if (!btn) return;
      clearPress(btn);
    });
  };

  bindPressFeedback();

  dealModalClose?.addEventListener("click", () => {
    dealModal.classList.remove("open");
    state.activeDealId = null;
    stopDealAutoRefresh();
  });

  chatModalClose?.addEventListener("click", () => {
    chatModal?.classList.remove("open");
    quickDealsBtn?.classList.remove("dimmed");
  });

  p2pModalClose?.addEventListener("click", () => {
    p2pModal.classList.remove("open");
    stopDisputeAutoRefresh();
    state.activeDisputeId = null;
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

  chatForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const dealId = state.activeChatDealId;
    if (!dealId) return;
    const text = (chatInput?.value || "").trim();
    const file = chatFile?.files?.[0] || null;
    if (!text && !file) {
      showNotice("Введите сообщение или выберите файл");
      return;
    }
    if (!state.initData) {
      showNotice("initData не найден. Откройте WebApp из Telegram.");
      return;
    }
    try {
      let sentMessage = null;
      if (file) {
        const form = new FormData();
        form.append("file", file);
        if (text) {
          form.append("text", text);
        }
        const res = await fetch(`/api/deals/${dealId}/chat/file`, {
          method: "POST",
          headers: { "X-Telegram-Init-Data": state.initData },
          body: form,
        });
        if (!res.ok) {
          const errText = await res.text();
          showNotice(errText || "Не удалось отправить файл");
          return;
        }
        const payload = await res.json();
        sentMessage = payload?.message || null;
      } else {
        const payload = await fetchJson(`/api/deals/${dealId}/chat`, {
          method: "POST",
          body: JSON.stringify({ text }),
        });
        if (!payload?.ok) {
          return;
        }
        sentMessage = payload.message || null;
      }
      if (chatInput) chatInput.value = "";
      if (chatFile) chatFile.value = "";
      updateChatFileHint();
      await loadChatMessages(dealId);
      if (sentMessage?.created_at) {
        markChatRead(dealId, sentMessage.created_at);
      } else {
        markChatRead(dealId);
      }
      updateQuickDealsButton(state.deals || []);
      if (quickDealsPanel?.classList.contains("open")) {
        renderQuickDeals();
      }
    } catch (err) {
      showNotice(`Ошибка: ${err.message}`);
    }
  });

  const openImageModal = (src, alt = "Фото") => {
    if (!imageModal || !imageModalImg) return;
    imageModalImg.src = src;
    imageModalImg.alt = alt;
    imageModal.classList.add("open");
  };

  const openVideoModal = (src) => {
    if (!videoModal || !videoModalPlayer) return;
    videoModalPlayer.src = src;
    videoModalPlayer.currentTime = 0;
    videoModal.classList.add("open");
  };

  const openCommentModal = (text) => {
    if (!commentModal || !commentModalText) return;
    commentModalText.textContent = text;
    commentModal.classList.add("open");
  };

  imageModalClose?.addEventListener("click", () => {
    imageModal?.classList.remove("open");
  });

  videoModalClose?.addEventListener("click", () => {
    if (videoModalPlayer) {
      videoModalPlayer.pause?.();
      videoModalPlayer.removeAttribute("src");
      videoModalPlayer.load?.();
    }
    videoModal?.classList.remove("open");
  });

  commentModalClose?.addEventListener("click", () => {
    commentModal?.classList.remove("open");
  });

  const closeDisputeResolve = () => {
    disputeResolveModal?.classList.remove("open");
    state.pendingResolve = null;
  };

  disputeResolveClose?.addEventListener("click", closeDisputeResolve);
  disputeResolveCancel?.addEventListener("click", closeDisputeResolve);

  disputeResolveConfirm?.addEventListener("click", async () => {
    if (!state.pendingResolve) return;
    const { id, sellerAmount, buyerAmount } = state.pendingResolve;
    const res = await fetchJson(`/api/disputes/${id}/resolve`, {
      method: "POST",
      body: JSON.stringify({ seller_amount: sellerAmount, buyer_amount: buyerAmount }),
    });
    if (res?.ok) {
      closeDisputeResolve();
      p2pModal?.classList.remove("open");
      await loadDisputes();
    }
  });

  const stopDisputeAutoRefresh = () => {
    if (state.disputeRefreshTimer) {
      clearInterval(state.disputeRefreshTimer);
      state.disputeRefreshTimer = null;
    }
  };

  const startDisputeAutoRefresh = (disputeId) => {
    stopDisputeAutoRefresh();
    state.disputeRefreshTimer = setInterval(async () => {
      if (!p2pModal?.classList.contains("open")) return;
      if (state.activeDisputeId !== disputeId) return;
      const payload = await fetchJson(`/api/disputes/${disputeId}`);
      if (!payload?.ok) return;
      const dispute = payload.dispute;
      const snapshot = JSON.stringify({
        evidence: dispute.evidence.length,
        messages: dispute.messages?.length || 0,
        assigned: dispute.assigned_to || null,
        reason: dispute.reason,
        comment: dispute.comment,
      });
      if (snapshot !== state.disputeSnapshot) {
        state.disputeSnapshot = snapshot;
        await openDispute(disputeId);
      }
    }, 2500);
  };

  buyerProofClose?.addEventListener("click", () => {
    closeBuyerProofModal();
  });

  buyerProofPick?.addEventListener("click", () => {
    const dealId = state.buyerProofDealId;
    if (!dealId) return;
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "image/*";
    input.onchange = () => {
      const file = input.files?.[0];
      if (!file) return;
      const url = URL.createObjectURL(file);
      state.buyerProofDraft[dealId] = { file, url };
      if (buyerProofImg) buyerProofImg.src = url;
      buyerProofPreview?.classList.add("show");
      if (buyerProofSend) buyerProofSend.disabled = false;
    };
    input.click();
  });

  buyerProofSend?.addEventListener("click", () => {
    const dealId = state.buyerProofDealId;
    if (!dealId) return;
    uploadBuyerProof(dealId);
  });

  disputeOpenClose?.addEventListener("click", () => {
    closeDisputeOpenModal();
  });

  disputeReason?.addEventListener("change", () => {
    if (!disputeReasonCustomField) return;
    if (disputeReason?.value === "other") {
      disputeReasonCustomField.classList.remove("is-hidden");
    } else {
      disputeReasonCustomField.classList.add("is-hidden");
    }
  });

  disputeEvidenceClose?.addEventListener("click", () => {
    closeDisputeEvidenceModal();
  });

  disputeEvidencePick?.addEventListener("click", () => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "video/*";
    input.onchange = () => {
      const file = input.files?.[0];
      input.remove();
      if (!file) return;
      const name = (file.name || "").toLowerCase();
      const isVideo =
        (file.type && file.type.startsWith("video/")) ||
        name.endsWith(".mp4") ||
        name.endsWith(".mov") ||
        name.endsWith(".m4v") ||
        name.endsWith(".webm") ||
        name.endsWith(".avi") ||
        name.endsWith(".mkv") ||
        name.endsWith(".3gp");
      if (!isVideo) {
        showNotice("Нужен видеофайл");
        return;
      }
      state.disputeEvidenceDraft = { file, name: file.name || "Видео" };
      if (disputeEvidenceName) {
        disputeEvidenceName.textContent = `Выбрано: ${state.disputeEvidenceDraft.name}`;
      }
      if (disputeEvidenceSend) {
        disputeEvidenceSend.disabled = false;
      }
      showNotice("Видео выбрано");
    };
    input.style.display = "none";
    document.body.appendChild(input);
    input.click();
  });

  disputeEvidenceSend?.addEventListener("click", () => {
    const disputeId = state.disputeEvidenceId;
    if (!disputeId) return;
    submitDisputeEvidence(disputeId);
  });

  disputeVideoPick?.addEventListener("click", () => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "video/*";
    input.onchange = () => {
      const file = input.files?.[0];
      input.remove();
      if (!file) return;
      const name = (file.name || "").toLowerCase();
      const isVideo =
        (file.type && file.type.startsWith("video/")) ||
        name.endsWith(".mp4") ||
        name.endsWith(".mov") ||
        name.endsWith(".m4v") ||
        name.endsWith(".webm") ||
        name.endsWith(".avi") ||
        name.endsWith(".mkv") ||
        name.endsWith(".3gp");
      if (!isVideo) {
        showNotice("Нужен видеофайл");
        return;
      }
      state.disputeOpenDraft = { file, name: file.name || "Видео" };
      if (disputeVideoName) {
        disputeVideoName.textContent = `Выбрано: ${state.disputeOpenDraft.name}`;
      }
      if (disputeOpenSend) {
        disputeOpenSend.disabled = false;
      }
      showNotice("Видео выбрано");
    };
    input.style.display = "none";
    document.body.appendChild(input);
    input.click();
  });

  disputeOpenSend?.addEventListener("click", () => {
    const dealId = state.disputeOpenDealId;
    if (!dealId) return;
    submitOpenDispute(dealId);
  });

  chatFile?.addEventListener("change", updateChatFileHint);

  p2pVolumeMax?.addEventListener("click", async () => {
    if (state.balance !== null) {
      p2pVolume.value = formatAmount(state.balance, 3);
      updateP2PLimitsState();
      return;
    }
    const balancePayload = await fetchJson("/api/balance");
    if (balancePayload?.ok) {
      p2pVolume.value = formatAmount(balancePayload.balance, 3);
      updateP2PLimitsState();
    }
  });

  const scrollFieldIntoCard = (field, offsetRatio = 0.25) => {
    if (!field) return;
    const card = field.closest(".modal-card");
    if (!card) return;
    let offsetTop = 0;
    let node = field;
    while (node && node !== card) {
      offsetTop += node.offsetTop || 0;
      node = node.offsetParent;
    }
    const targetTop = offsetTop - card.clientHeight * offsetRatio;
    card.scrollTo({
      top: Math.max(0, targetTop),
      behavior: "smooth",
    });
  };

  const adjustP2PCreateCardForKeyboard = () => {
    const card = p2pCreateModal?.querySelector?.(".modal-card");
    if (!card) return;
    const vv = window.visualViewport;
    if (vv && vv.height) {
      card.style.maxHeight = `${Math.max(240, vv.height - 24)}px`;
    } else {
      card.style.maxHeight = "";
    }
  };

  const resetP2PCreateCardHeight = () => {
    const card = p2pCreateModal?.querySelector?.(".modal-card");
    if (!card) return;
    card.style.maxHeight = "";
  };

  const scrollP2PCreateToBottom = () => {
    const card = p2pCreateModal?.querySelector?.(".modal-card");
    if (!card) return;
    setTimeout(() => {
      adjustP2PCreateCardForKeyboard();
      card.scrollTo({ top: card.scrollHeight, behavior: "smooth" });
    }, 320);
  };

  const scrollP2PTermsIntoView = () => {
    if (!p2pTerms) return;
    setTimeout(() => {
      scrollFieldIntoCard(p2pTerms, 0.25);
    }, 320);
  };

  p2pTerms?.addEventListener("focus", scrollP2PCreateToBottom);
  p2pTerms?.addEventListener("click", scrollP2PCreateToBottom);

  p2pTerms?.addEventListener("blur", resetP2PCreateCardHeight);

  if (window.visualViewport) {
    window.visualViewport.addEventListener("resize", () => {
      if (!p2pCreateModal?.classList?.contains("open")) return;
      adjustP2PCreateCardForKeyboard();
      scrollP2PCreateToBottom();
    });
  }

  const computeMaxLimit = () => {
    const volume = Number(p2pVolume?.value);
    const price = Number(p2pPrice?.value);
    if (!Number.isFinite(volume) || volume <= 0 || !Number.isFinite(price) || price <= 0) {
      return null;
    }
    return volume * price;
  };

  const clampLimitsToMax = (maxLimit) => {
    if (!p2pLimits?.value) return;
    const [minStr, maxStr] = p2pLimits.value.split("-");
    if (!minStr || !maxStr) return;
    const min = Number(minStr);
    const max = Number(maxStr);
    if (!Number.isFinite(max)) return;
    const capped = Math.floor(maxLimit);
    if (max > capped) {
      const safeMax = Number.isFinite(min) && min > capped ? min : capped;
      p2pLimits.value = `${minStr}-${formatAmount(safeMax, 0)}`;
    }
  };

  const updateP2PLimitsState = () => {
    if (!p2pLimits) return;
    const maxLimit = computeMaxLimit();
    const enabled = maxLimit !== null;
    p2pLimits.disabled = !enabled;
    p2pLimits.placeholder = enabled ? "1000-10000" : "Введите объем и цену";
    if (enabled) {
      clampLimitsToMax(maxLimit);
    }
  };

  p2pVolume?.addEventListener("input", updateP2PLimitsState);
  p2pPrice?.addEventListener("input", updateP2PLimitsState);
  p2pLimits?.addEventListener("blur", () => {
    const maxLimit = computeMaxLimit();
    if (maxLimit !== null) clampLimitsToMax(maxLimit);
  });
  updateP2PLimitsState();

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
    let max = Number(maxStr);
    const maxLimit = computeMaxLimit();
    if (maxLimit !== null && Number.isFinite(max) && max > maxLimit) {
      const capped = Math.floor(maxLimit);
      max = Number.isFinite(min) && min > capped ? min : capped;
      p2pLimits.value = `${minStr}-${formatAmount(max, 0)}`;
    }
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
    state.reviewsTargetUserId = null;
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
      const reviews = await loadReviews(state.reviewsTargetUserId);
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

  document.addEventListener("focusin", (event) => {
    const el = event.target;
    if (!el) return;
    const tag = el.tagName;
    if (tag !== "INPUT" && tag !== "TEXTAREA" && tag !== "SELECT") return;
    const scrollP2PModal = () => {
      if (!p2pModal?.classList.contains("open")) return;
      if (!p2pModal.contains(el)) return;
      const modalCard = p2pModal.querySelector(".modal-card");
      if (modalCard) {
        modalCard.scrollTop = modalCard.scrollHeight;
      }
      p2pModalActions?.scrollIntoView({ block: "end", behavior: "smooth" });
    };
    window.setTimeout(() => {
      if (typeof el.scrollIntoView === "function") {
        el.scrollIntoView({ block: "center", behavior: "smooth" });
      }
      scrollP2PModal();
    }, 120);
    window.setTimeout(scrollP2PModal, 300);
    window.setTimeout(scrollP2PModal, 600);
  });

  if (window.visualViewport) {
    window.visualViewport.addEventListener("resize", () => {
      const el = document.activeElement;
      if (!el) return;
      if (!p2pModal?.classList.contains("open")) return;
      if (!p2pModal.contains(el)) return;
      const modalCard = p2pModal.querySelector(".modal-card");
      if (modalCard) {
        modalCard.scrollTop = modalCard.scrollHeight;
      }
      p2pModalActions?.scrollIntoView({ block: "end", behavior: "smooth" });
    });
  }

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

  balanceHistoryOpen?.addEventListener("click", async () => {
    if (!balanceHistoryModal || !balanceHistoryList) return;
    const payload = await fetchJson("/api/balance/history");
    if (!payload?.ok) return;
    const items = payload.items || [];
    balanceHistoryList.innerHTML = "";
    if (!items.length) {
      balanceHistoryList.innerHTML = "<div class=\"deal-empty\">Нет операций.</div>";
    } else {
      items.forEach((item) => {
        const amount = Number(item.amount || 0);
        const isPositive = amount > 0;
        const row = document.createElement("div");
        row.className = `balance-item ${isPositive ? "pos" : "neg"}`;
        let title = "Операция";
        if (item.kind === "topup") title = "Пополнение";
        if (item.kind === "withdraw") title = "Вывод";
        if (item.kind === "deal" || item.kind === "dispute") {
          const dealId = item.meta?.public_id ? `#${item.meta.public_id}` : "";
          title = isPositive ? `Получены средства по сделке ${dealId}` : `Списание по сделке ${dealId}`;
        }
        const date = item.created_at ? formatDate(item.created_at) : "";
        row.innerHTML = `
          <div class="balance-info">
            <div class="balance-title">${title}</div>
            <div class="balance-date">${date}</div>
          </div>
          <div class="balance-amount">${isPositive ? "+" : ""}${formatAmount(amount, 3)} USDT</div>
        `;
        balanceHistoryList.appendChild(row);
      });
    }
    balanceHistoryModal.classList.add("open");
  });

  balanceHistoryClose?.addEventListener("click", () => {
    balanceHistoryModal?.classList.remove("open");
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
  const startApp = async () => {
    await initTelegram();
  };

  initPinGate().then(() => {
    startApp();
  });
})();
