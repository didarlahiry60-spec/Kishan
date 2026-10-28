// Kishan (কৃষাণ) Full-Power AI Agro-Intelligence Application

// Base API endpoint URL detection (supports local, cloudflare, and GitHub Pages)
const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" || window.location.hostname.includes("trycloudflare");
const API_BASE = isLocal ? "" : "https://julian-awareness-cinema-quotes.trycloudflare.com";

let currentDistrict = "বগুড়া";
let currentCategory = "সব";
let currentSearch = "";
let selectedCrops = ["ধান", "আলু", "পেঁয়াজ"];
let deviceId = localStorage.getItem("kishan_device_id") || "farmer-" + Math.random().toString(36).substring(2, 9);
localStorage.setItem("kishan_device_id", deviceId);

const audioPlayer = document.getElementById("globalAudioPlayer");
let lastConsultantAudioUrl = null;
let lastScriptText = "";

// Bengali numeral conversion
function toBnNum(num) {
  const bnDigits = ['০', '১', '২', '৩', '৪', '৫', '৬', '৭', '৮', '৯'];
  return String(num).replace(/[0-9]/g, w => bnDigits[+w]);
}

// Bengali Speech Player
async function playBengaliSpeech(text, audioUrl = null) {
  if (audioUrl) {
    audioPlayer.src = audioUrl;
    try {
      await audioPlayer.play();
      return;
    } catch (e) {
      console.warn("Audio element play failed, falling back to Web Speech:", e);
    }
  }

  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'bn-BD';
    utterance.rate = 0.9;
    window.speechSynthesis.speak(utterance);
  }
}

// Speech-to-Text (STT) setup
let recognition = null;
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRec();
  recognition.lang = 'bn-BD';
  recognition.continuous = false;
  recognition.interimResults = false;
}

// Initial Load
document.addEventListener("DOMContentLoaded", () => {
  setupThemeToggle();
  setupTabs();
  setupFilters();
  setupDistrictSelector();
  setupProfileForm();
  setupAdminControls();
  setupConsultantAndDoctor();
  setupNegotiationCalc();
  setupTrendChart();

  // প্রাথমিক ডেটা লোড
  loadBazarData();
  loadWeatherData();
  loadProfileData();
  loadLiveCrawlerNews();
  loadStats();
});

// 0. Dark Mode Theme Setup
function setupThemeToggle() {
  const toggleBtn = document.getElementById("btnThemeToggle");
  const themeIcon = document.getElementById("themeIcon");
  const savedTheme = localStorage.getItem("kishan_theme") || (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');

  const applyTheme = (theme) => {
    if (theme === 'dark') {
      document.body.classList.add('dark-mode');
      if (themeIcon) themeIcon.innerText = '☀️';
      localStorage.setItem("kishan_theme", "dark");
    } else {
      document.body.classList.remove('dark-mode');
      if (themeIcon) themeIcon.innerText = '🌙';
      localStorage.setItem("kishan_theme", "light");
    }
    if (typeof renderTrendSvg === 'function') renderTrendSvg();
  };

  applyTheme(savedTheme);

  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      const isDark = document.body.classList.contains("dark-mode");
      applyTheme(isDark ? 'light' : 'dark');
    });
  }
}

// 1. Tab Navigation
function setupTabs() {
  const navItems = document.querySelectorAll(".bottom-nav .nav-item");
  const tabPanes = document.querySelectorAll(".tab-pane");

  navItems.forEach(item => {
    item.addEventListener("click", () => {
      navItems.forEach(n => n.classList.remove("active"));
      tabPanes.forEach(p => p.classList.remove("active"));

      item.classList.add("active");
      const targetId = item.getAttribute("data-tab");
      const targetPane = document.getElementById(targetId);
      if (targetPane) targetPane.classList.add("active");

      if (targetId === "tab-weather") loadWeatherData();
      else if (targetId === "tab-admin") loadStats();
      else if (targetId === "tab-bazar") renderTrendSvg();
    });
  });
}

// 2. District Selector
function setupDistrictSelector() {
  const districtSelect = document.getElementById("districtSelect");
  districtSelect.addEventListener("change", (e) => {
    currentDistrict = e.target.value;
    document.getElementById("profDistrict").value = currentDistrict;
    loadBazarData();
    loadWeatherData();
    renderTrendSvg();
  });
}

// 3. Live Crawler Ticker
async function loadLiveCrawlerNews() {
  try {
    const res = await fetch(API_BASE + "/api/v1/ai/live-crawler?limit=8");
    const data = await res.json();
    if (data.signals && data.signals.length > 0) {
      let idx = 0;
      const tickerEl = document.getElementById("crawlerTickerText");
      
      const updateTicker = () => {
        const item = data.signals[idx % data.signals.length];
        const trendSymbol = item.trend === "up" ? "▲" : (item.trend === "down" ? "▼" : "•");
        tickerEl.innerHTML = `<strong>[${item.source}]</strong> ${trendSymbol} ${item.title}`;
        idx++;
      };

      updateTicker();
      setInterval(updateTicker, 6000);
    }
  } catch (err) {
    console.log("Crawler ticker offline:", err);
  }
}

// 4. Interactive 7-Day Trend Chart (SVG)
function setupTrendChart() {
  const sel = document.getElementById("trendCropSelect");
  sel.addEventListener("change", () => renderTrendSvg());
  renderTrendSvg();
}

function renderTrendSvg() {
  const svg = document.getElementById("trendSvg");
  const crop = document.getElementById("trendCropSelect").value;
  
  // ডেমো হিস্টোরিক্যাল ৭ দিনের ট্রেন্ড পয়েন্টস
  let baseWholesale = 28;
  let baseRetail = 35;
  if (crop === "কাঁচা মরিচ") { baseWholesale = 120; baseRetail = 160; }
  else if (crop === "দেশি পেঁয়াজ") { baseWholesale = 78; baseRetail = 90; }
  else if (crop === "ব্রি ধান-২৮") { baseWholesale = 32; baseRetail = 38; }
  else if (crop === "টমেটো (পাকা)") { baseWholesale = 52; baseRetail = 68; }

  const days = ["৭ দিন আগে", "৬ দিন", "৫ দিন", "৪ দিন", "৩ দিন", "গতকাল", "আজ"];
  const wPoints = [baseWholesale - 3, baseWholesale - 2, baseWholesale - 1, baseWholesale + 1, baseWholesale, baseWholesale + 2, baseWholesale + 1];
  const rPoints = [baseRetail - 4, baseRetail - 2, baseRetail - 1, baseRetail + 2, baseRetail + 1, baseRetail + 3, baseRetail + 2];

  const minVal = Math.min(...wPoints) - 5;
  const maxVal = Math.max(...rPoints) + 5;
  const range = maxVal - minVal;

  const wCoords = wPoints.map((v, i) => {
    const x = 30 + i * 50;
    const y = 95 - ((v - minVal) / range) * 75;
    return `${x},${y}`;
  }).join(" ");

  const rCoords = rPoints.map((v, i) => {
    const x = 30 + i * 50;
    const y = 95 - ((v - minVal) / range) * 75;
    return `${x},${y}`;
  }).join(" ");

  const isDark = document.body.classList.contains("dark-mode");
  const gridStroke = isDark ? "#283229" : "#ebe5da";
  const axisStroke = isDark ? "#384539" : "#d8d1c4";
  const textFill = isDark ? "#a1ada0" : "#6f776a";

  svg.innerHTML = `
    <!-- Grid Lines -->
    <line x1="20" y1="20" x2="340" y2="20" stroke="${gridStroke}" stroke-dasharray="3,3" />
    <line x1="20" y1="55" x2="340" y2="55" stroke="${gridStroke}" stroke-dasharray="3,3" />
    <line x1="20" y1="95" x2="340" y2="95" stroke="${axisStroke}" />

    <!-- Retail Polyline (Warm Terracotta) -->
    <polyline fill="none" stroke="${isDark ? '#e06d5c' : '#b54f3d'}" stroke-width="2.5" points="${rCoords}" />
    <!-- Wholesale Polyline (Field Moss) -->
    <polyline fill="none" stroke="${isDark ? '#4e9e60' : '#2d5a37'}" stroke-width="2.5" points="${wCoords}" />

    <!-- Points and X Labels -->
    ${wPoints.map((v, i) => {
      const x = 30 + i * 50;
      const wy = 95 - ((v - minVal) / range) * 75;
      const ry = 95 - ((rPoints[i] - minVal) / range) * 75;
      const wColor = isDark ? '#4e9e60' : '#2d5a37';
      const rColor = isDark ? '#e06d5c' : '#b54f3d';
      return `
        <circle cx="${x}" cy="${wy}" r="3.5" fill="${wColor}" />
        <circle cx="${x}" cy="${ry}" r="3.5" fill="${rColor}" />
        <text x="${x}" y="112" font-size="9" text-anchor="middle" fill="${textFill}">${days[i]}</text>
      `;
    }).join("")}
  `;
}

// 5. AI Consultant & Voice Assistant Setup
function setupConsultantAndDoctor() {
  const inputEl = document.getElementById("consultantInput");
  const micBtn = document.getElementById("btnMicInput");
  const micIcon = document.getElementById("micIcon");

  // Mic Speech-to-Text
  if (recognition) {
    recognition.onstart = () => {
      micBtn.classList.add("recording");
      micIcon.innerText = "🔴";
    };
    recognition.onend = () => {
      micBtn.classList.remove("recording");
      micIcon.innerText = "🎙️";
    };
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      inputEl.value = transcript;
      askConsultant(transcript);
    };
    recognition.onerror = () => {
      micBtn.classList.remove("recording");
      micIcon.innerText = "🎙️";
    };

    micBtn.addEventListener("click", () => {
      try {
        recognition.start();
      } catch (e) {
        recognition.stop();
      }
    });
  } else {
    micBtn.addEventListener("click", () => {
      alert("আপনার ব্রাউজারে ভয়েস রিকগনিশন সক্রিয় নেই। অনুগ্রহ করে প্রশ্নটি টাইপ করুন।");
    });
  }

  // Quick chips
  document.querySelectorAll(".quick-q-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      const q = chip.getAttribute("data-q");
      inputEl.value = q;
      askConsultant(q);
    });
  });

  // Ask button
  document.getElementById("btnAskConsultant").addEventListener("click", () => {
    const q = inputEl.value.trim();
    if (q) askConsultant(q);
  });

  // Re-listen answer voice
  document.getElementById("btnListenAnswerVoice").addEventListener("click", () => {
    const text = document.getElementById("consultantAnswerText").innerText;
    playBengaliSpeech(text, lastConsultantAudioUrl);
  });

  // Crop Doctor
  document.getElementById("btnDiagnose").addEventListener("click", runCropDiagnosis);
}

async function askConsultant(query) {
  const card = document.getElementById("consultantResponseCard");
  const ansEl = document.getElementById("consultantAnswerText");
  const actionsBox = document.getElementById("consultantActionsBox");
  const actionsList = document.getElementById("consultantActionsList");
  const cautionBox = document.getElementById("consultantCautionBox");

  card.style.display = "block";
  ansEl.innerText = "এআই কৃষি কর্মকর্তা আপনার প্রশ্ন বিশ্লেষণ করছেন...";
  actionsBox.style.display = "none";
  cautionBox.innerText = "";

  try {
    const res = await fetch(API_BASE + "/api/v1/ai/consultant", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query_text: query,
        district: currentDistrict,
        crops: selectedCrops.join(",")
      })
    });
    const data = await res.json();
    ansEl.innerText = data.answer_bn;
    lastConsultantAudioUrl = data.audio_url;

    if (data.recommended_actions && data.recommended_actions.length > 0) {
      actionsList.innerHTML = "";
      data.recommended_actions.forEach(act => {
        const li = document.createElement("li");
        li.innerText = act;
        actionsList.appendChild(li);
      });
      actionsBox.style.display = "block";
    }

    if (data.caution_note) {
      cautionBox.innerText = `⚠️ সতর্কতা: ${data.caution_note}`;
    }

    // স্বয়ংক্রিয়ভাবে ভয়েস পড়ে শোনানো
    const voiceMsg = data.short_voice_summary || data.answer_bn;
    playBengaliSpeech(voiceMsg, data.audio_url);

  } catch (e) {
    ansEl.innerText = "পরামর্শ আনতে সমস্যা হয়েছে। ইন্টারনেট সংযোগ পরীক্ষা করুন।";
  }
}

// Crop Doctor Diagnose
async function runCropDiagnosis() {
  const crop = document.getElementById("docCropSelect").value;
  const symptom = document.getElementById("docSymptomInput").value.trim() || "পাতায় দাগ ও পচন";
  const resultCard = document.getElementById("diagnosisResultCard");

  resultCard.style.display = "block";
  document.getElementById("diagDiseaseName").innerText = "রোগ শনাক্তকরণ চলছে...";

  try {
    const res = await fetch(API_BASE + "/api/v1/ai/crop-doctor", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ crop: crop, symptom_description: symptom })
    });
    const data = await res.json();

    document.getElementById("diagDiseaseName").innerText = data.disease_name;
    document.getElementById("diagPathogen").innerText = `রোগ সৃষ্টিকারী উপাদান: ${data.pathogen}`;
    document.getElementById("diagSymptoms").innerText = data.symptoms;
    document.getElementById("diagChemical").innerText = data.prescription.chemical;
    document.getElementById("diagOrganic").innerText = data.prescription.organic;

    const sev = document.getElementById("diagSeverity");
    sev.innerText = data.severity === "severe" ? "🚨 তীব্র ক্ষতিকর রোগ" : (data.severity === "high" ? "⚠️ উচ্চ ঝুঁকিপূর্ণ" : "🟡 মাঝারি ঝুঁকি");
    sev.style.background = data.severity === "severe" ? "#ffebee" : "#fff8e1";
    sev.style.color = data.severity === "severe" ? "#c62828" : "#f57f17";

    // ভয়েসে রোগ ও সমাধান পড়ে শোনানো
    const speech = `${data.crop} ফসলে ${data.disease_name} শনাক্ত হয়েছে। ${data.prescription.chemical}`;
    playBengaliSpeech(speech);

  } catch (e) {
    document.getElementById("diagDiseaseName").innerText = "শনাক্তকরণে ত্রুটি হয়েছে।";
  }
}

// 6. Negotiation & Profit Calculator Setup
function setupNegotiationCalc() {
  document.getElementById("btnCalculateDeal").addEventListener("click", async () => {
    const crop = document.getElementById("calcCrop").value;
    const qty = parseFloat(document.getElementById("calcQty").value) || 50;
    const cost = parseFloat(document.getElementById("calcCost").value) || 750;
    const transport = parseFloat(document.getElementById("calcTransport").value) || 50;
    const wholesaleKg = parseFloat(document.getElementById("calcMarketPerKg").value) || 28;
    const aratdarOffer = parseFloat(document.getElementById("calcAratdarOffer").value) || 950;

    const payload = {
      crop_name: crop,
      quantity_mon: qty,
      production_cost_per_mon: cost,
      transport_cost_per_mon: transport,
      market_wholesale_per_kg: wholesaleKg,
      aratdar_offered_per_mon: aratdarOffer
    };

    try {
      const res = await fetch(API_BASE + "/api/v1/ai/negotiation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      document.getElementById("calcResultBox").style.display = "block";
      document.getElementById("resCostPerMon").innerText = `${toBnNum(data.break_even_per_mon)} ৳`;
      document.getElementById("resFairMon").innerText = `${toBnNum(data.fair_market_per_mon)} ৳`;
      document.getElementById("resNetProfit").innerText = `${toBnNum(data.fair_net_profit)} ৳ (${toBnNum(data.profit_margin_pct)}%)`;
      
      const evalEl = document.getElementById("resEvaluation");
      evalEl.innerText = data.aratdar_evaluation;

      lastScriptText = data.negotiation_script_bn;
      document.getElementById("resScript").innerText = data.negotiation_script_bn;

    } catch (e) {
      alert("হিসাব করতে সমস্যা হয়েছে।");
    }
  });

  document.getElementById("btnSpeakScript").addEventListener("click", () => {
    if (lastScriptText) playBengaliSpeech(lastScriptText);
  });
}

// 7. Filters & Bazar Loading
function setupFilters() {
  const chips = document.querySelectorAll("#categoryChips .chip");
  chips.forEach(chip => {
    chip.addEventListener("click", () => {
      chips.forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      currentCategory = chip.getAttribute("data-cat");
      loadBazarData();
    });
  });

  const searchInput = document.getElementById("searchInput");
  let debounceTimer;
  searchInput.addEventListener("input", (e) => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      currentSearch = e.target.value.trim();
      loadBazarData();
    }, 300);
  });

  document.getElementById("btnVoiceSummary").addEventListener("click", async () => {
    const summaryText = document.getElementById("marketSummaryText").innerText;
    const bargainText = document.getElementById("bargainTipText").innerText;
    const fullText = `আজকের বাজার বিশ্লেষণ। ${summaryText} দর কষাকষির পরামর্শ: ${bargainText}`;
    
    try {
      const res = await fetch(API_BASE + "/api/v1/voice/speak", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text_bn: fullText })
      });
      const data = await res.json();
      playBengaliSpeech(fullText, data.audio_url);
    } catch (e) {
      playBengaliSpeech(fullText);
    }
  });

  document.getElementById("btnListenAdvisory").addEventListener("click", async () => {
    const cropsParam = encodeURIComponent(selectedCrops.join(","));
    try {
      const res = await fetch(`${API_BASE}/api/v1/voice/advisory-audio?district=${encodeURIComponent(currentDistrict)}&crops=${cropsParam}`);
      const data = await res.json();
      playBengaliSpeech(data.speech_text, data.audio_url);
    } catch (e) {
      const headline = document.getElementById("advisoryHeadline").innerText;
      playBengaliSpeech(headline);
    }
  });
}

async function loadBazarData() {
  const container = document.getElementById("commodityContainer");
  container.innerHTML = `<div class="loading-spinner">বাজারদর লোড হচ্ছে...</div>`;

  const cacheKey = `kishan_cached_bazar_${currentDistrict}_${currentCategory}_${currentSearch}`;
  const summaryKey = `kishan_cached_summary_${currentDistrict}`;

  fetch(`${API_BASE}/api/v1/bazar/summary?district=${encodeURIComponent(currentDistrict)}`)
    .then(r => r.json())
    .then(summary => {
      localStorage.setItem(summaryKey, JSON.stringify(summary));
      if (summary.ai_summary) {
        document.getElementById("marketSummaryText").innerText = summary.ai_summary;
      }
      if (summary.bargaining_tip) {
        document.getElementById("bargainTipText").innerText = summary.bargaining_tip;
      }
    })
    .catch(() => {
      const cachedSum = localStorage.getItem(summaryKey);
      if (cachedSum) {
        try {
          const summary = JSON.parse(cachedSum);
          if (summary.ai_summary) document.getElementById("marketSummaryText").innerText = summary.ai_summary;
          if (summary.bargaining_tip) document.getElementById("bargainTipText").innerText = summary.bargaining_tip;
        } catch (e) {}
      }
    });

  let url = `${API_BASE}/api/v1/bazar/daily?district=${encodeURIComponent(currentDistrict)}`;
  if (currentCategory && currentCategory !== "সব") url += `&category=${encodeURIComponent(currentCategory)}`;
  if (currentSearch) url += `&search=${encodeURIComponent(currentSearch)}`;

  try {
    const res = await fetch(url);
    const items = await res.json();

    if (!items || items.length === 0) {
      container.innerHTML = `<div class="loading-spinner">কোনো পণ্য পাওয়া যায়নি।</div>`;
      return;
    }

    localStorage.setItem(cacheKey, JSON.stringify(items));
    container.innerHTML = "";
    items.forEach(item => {
      const card = createCommodityCard(item);
      container.appendChild(card);
    });
  } catch (err) {
    const cached = localStorage.getItem(cacheKey);
    if (cached) {
      try {
        const items = JSON.parse(cached);
        container.innerHTML = `<div class="offline-banner"><span>📴</span> অফলাইন মোড: ইন্টারনেটের অভাবে পূর্বে সংরক্ষিত বাজারদর দেখানো হচ্ছে</div>`;
        items.forEach(item => {
          const card = createCommodityCard(item);
          container.appendChild(card);
        });
        return;
      } catch (e) {}
    }
    container.innerHTML = `<div class="loading-spinner" style="color:#d32f2f;">বাজারদর লোড করতে সমস্যা হয়েছে। অনুগ্রহ করে ইন্টারনেট সংযোগ পরীক্ষা করুন।</div>`;
  }
}

function createCommodityCard(item) {
  const card = document.createElement("div");
  card.className = "commodity-card";

  let trendClass = "stable";
  let trendLabel = "অপরিবর্তিত";
  if (item.price_trend === "up") {
    trendClass = "up";
    trendLabel = `▲ +${toBnNum(item.price_change_pct)}% বৃদ্ধি`;
  } else if (item.price_trend === "down") {
    trendClass = "down";
    trendLabel = `▼ ${toBnNum(item.price_change_pct)}% হ্রাস`;
  }

  card.innerHTML = `
    <div class="item-left">
      <button class="item-speaker-btn" title="পড়ে শুনুন" data-id="${item.id}" data-name="${item.name_bn}" data-w="${item.wholesale_avg}" data-r="${item.retail_avg}" data-unit="${item.unit}">
        🔊
      </button>
      <div class="item-details">
        <h4>${item.name_bn}</h4>
        <span class="item-market">${item.market_name || item.district}</span>
      </div>
    </div>
    <div class="item-prices">
      <div class="price-row">
        <span class="price-type">পাইকারি:</span>
        <span class="price-val wholesale">৳${toBnNum(item.wholesale_min)}-${toBnNum(item.wholesale_max)}</span>
      </div>
      <div class="price-row">
        <span class="price-type">খুচরা:</span>
        <span class="price-val retail">৳${toBnNum(item.retail_avg)}/${item.unit}</span>
      </div>
      <span class="trend-badge ${trendClass}">${trendLabel}</span>
    </div>
  `;

  const speakerBtn = card.querySelector(".item-speaker-btn");
  speakerBtn.addEventListener("click", async (e) => {
    e.stopPropagation();
    const id = speakerBtn.getAttribute("data-id");
    try {
      const resp = await fetch(`${API_BASE}/api/v1/voice/commodity-audio/${id}`);
      const data = await resp.json();
      playBengaliSpeech(data.speech_text, data.audio_url);
    } catch (err) {
      const text = `${currentDistrict} বাজারে ${item.name_bn} পাইকারি প্রতি ${item.unit} ${item.wholesale_avg} টাকা, খুচরা ${item.retail_avg} টাকা।`;
      playBengaliSpeech(text);
    }
  });

  return card;
}

// 8. Weather & AI Agro-Advisory
async function loadWeatherData() {
  document.getElementById("weatherDistrict").innerText = currentDistrict;
  
  fetch(`${API_BASE}/api/v1/weather/forecast?district=${encodeURIComponent(currentDistrict)}`)
    .then(r => r.json())
    .then(data => {
      const cur = data.current || {};
      document.getElementById("currentTemp").innerText = toBnNum(Math.round(cur.temperature || 31)) + "°";
      document.getElementById("weatherCondition").innerText = cur.condition_bn || "স্বাভাবিক আবহাওয়া";
      document.getElementById("weatherHumidity").innerText = toBnNum(cur.humidity || 75) + "%";
      document.getElementById("weatherWind").innerText = toBnNum(Math.round(cur.wind_speed || 12)) + " কিমি/ঘ";

      const scroll = document.getElementById("forecastScroll");
      scroll.innerHTML = "";
      const daily = data.daily_forecast || [];
      if (daily.length > 0) {
        document.getElementById("weatherRain").innerText = toBnNum(daily[0].precipitation_sum || 0) + " মিমি";
      }

      daily.forEach((day, idx) => {
        const dayCard = document.createElement("div");
        dayCard.className = "forecast-day-card";
        const dayLabel = idx === 0 ? "আজ" : (idx === 1 ? "কাল" : `দিন ${toBnNum(idx+1)}`);
        
        let icon = "☀️";
        if (day.precipitation_sum > 10) icon = "🌧️";
        else if (day.precipitation_sum > 0) icon = "🌦️";
        else if (day.condition_bn.includes("মেঘ")) icon = "⛅";

        dayCard.innerHTML = `
          <span class="day-name">${dayLabel}</span>
          <span class="day-icon">${icon}</span>
          <span class="day-temp">${toBnNum(Math.round(day.temp_max))}°C</span>
          <div style="font-size:10px; color:#555;">${toBnNum(day.precipitation_sum)}mm</div>
        `;
        scroll.appendChild(dayCard);
      });
    })
    .catch(err => console.error("Error loading weather forecast:", err));

  const advKey = `kishan_cached_adv_${currentDistrict}`;
  const renderAdvisory = (res) => {
    const adv = res.advisory || {};
    document.getElementById("advisoryHeadline").innerText = adv.headline_bn || "আবহাওয়া সতর্কতা ও ফসলের যত্ন";

    const dosList = document.getElementById("advisoryDosList");
    dosList.innerHTML = "";
    (adv.dos_bn || []).forEach(d => {
      const li = document.createElement("li");
      li.innerText = d;
      dosList.appendChild(li);
    });

    const dontsList = document.getElementById("advisoryDontsList");
    dontsList.innerHTML = "";
    (adv.donts_bn || []).forEach(d => {
      const li = document.createElement("li");
      li.innerText = d;
      dontsList.appendChild(li);
    });

    document.getElementById("advisoryIrrigation").innerText = adv.irrigation_advice_bn || "মাটির আর্দ্রতা অনুযায়ী সেচ প্রদান করুন।";
  };

  fetch(API_BASE + "/api/v1/weather/advisory", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      district: currentDistrict,
      crops: selectedCrops
    })
  })
    .then(r => r.json())
    .then(res => {
      localStorage.setItem(advKey, JSON.stringify(res));
      renderAdvisory(res);
    })
    .catch(() => {
      const cached = localStorage.getItem(advKey);
      if (cached) {
        try {
          renderAdvisory(JSON.parse(cached));
        } catch (e) {}
      }
    });
}

// 9. Profile Form
function setupProfileForm() {
  const cropTags = document.querySelectorAll("#cropSelector .crop-tag");
  cropTags.forEach(tag => {
    tag.addEventListener("click", () => {
      tag.classList.toggle("active");
      updateSelectedCropsFromUI();
    });
  });

  const form = document.getElementById("profileForm");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("profName").value;
    const phone = document.getElementById("profPhone").value;
    const district = document.getElementById("profDistrict").value;
    const upazila = document.getElementById("profUpazila").value;
    const smsAlerts = document.getElementById("profSmsAlerts").checked;

    const payload = {
      device_id: deviceId,
      name: name,
      phone: phone,
      district: district,
      upazila: upazila,
      favorite_crops: selectedCrops.join(","),
      sms_alerts_enabled: smsAlerts
    };

    try {
      const res = await fetch(API_BASE + "/api/v1/profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      
      const statusEl = document.getElementById("profileSaveStatus");
      statusEl.innerText = "✓ তথ্য সফলভাবে সংরক্ষিত হয়েছে!";
      statusEl.style.color = "#2e7d32";
      setTimeout(() => { statusEl.innerText = ""; }, 3000);

      if (district !== currentDistrict) {
        currentDistrict = district;
        document.getElementById("districtSelect").value = district;
        loadBazarData();
        loadWeatherData();
        renderTrendSvg();
      }
    } catch (err) {
      console.error("Error saving profile:", err);
    }
  });
}

function updateSelectedCropsFromUI() {
  const activeTags = document.querySelectorAll("#cropSelector .crop-tag.active");
  selectedCrops = Array.from(activeTags).map(t => t.getAttribute("data-crop"));
  loadWeatherData();
}

function loadProfileData() {
  fetch(`${API_BASE}/api/v1/profile/${deviceId}`)
    .then(r => r.json())
    .then(p => {
      if (p.name) document.getElementById("profName").value = p.name;
      if (p.phone) document.getElementById("profPhone").value = p.phone;
      if (p.district) {
        document.getElementById("profDistrict").value = p.district;
        document.getElementById("districtSelect").value = p.district;
        currentDistrict = p.district;
      }
      if (p.upazila) document.getElementById("profUpazila").value = p.upazila;
      if (p.favorite_crops) {
        selectedCrops = p.favorite_crops.split(",");
        const tags = document.querySelectorAll("#cropSelector .crop-tag");
        tags.forEach(t => {
          const crop = t.getAttribute("data-crop");
          if (selectedCrops.includes(crop)) t.classList.add("active");
          else t.classList.remove("active");
        });
      }
    })
    .catch(err => console.log("Profile loading:", err));
}

// 10. Admin Controls
function setupAdminControls() {
  const btnSync = document.getElementById("btnTriggerSync");
  btnSync.addEventListener("click", async () => {
    btnSync.disabled = true;
    btnSync.innerText = "সিঙ্ক হচ্ছে...";
    const resEl = document.getElementById("syncResult");
    resEl.innerText = "সরকারি পোর্টাল, লাইভ ক্রলার ও এআই সিঙ্ক চলছে...";

    try {
      const res = await fetch(API_BASE + "/api/v1/admin/sync-now", { method: "POST" });
      const data = await res.json();
      resEl.innerText = `✓ ${data.message}`;
      resEl.style.color = "#2e7d32";
      loadBazarData();
      loadLiveCrawlerNews();
      loadStats();
    } catch (e) {
      resEl.innerText = "সিঙ্ক ব্যর্থ হয়েছে।";
      resEl.style.color = "red";
    } finally {
      btnSync.disabled = false;
      btnSync.innerText = "বাজারদর ও সংবাদ সিঙ্ক করুন";
    }
  });

  const btnAlert = document.getElementById("btnSendAlert");
  btnAlert.addEventListener("click", async () => {
    const title = document.getElementById("alertTitle").value;
    const body = document.getElementById("alertBody").value;
    const resEl = document.getElementById("alertResult");
    resEl.innerText = "বার্তা পাঠানো হচ্ছে...";

    try {
      const res = await fetch(API_BASE + "/api/v1/admin/send-alert", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title_bn: title,
          message_bn: body,
          target_district: currentDistrict,
          channel: "sms"
        })
      });
      const data = await res.json();
      resEl.innerText = `✓ ${data.message}`;
      resEl.style.color = "#2e7d32";
      loadStats();
    } catch (e) {
      resEl.innerText = "বার্তা পাঠাতে ব্যর্থ হয়েছে।";
      resEl.style.color = "red";
    }
  });
}

function loadStats() {
  fetch(API_BASE + "/api/v1/admin/stats")
    .then(r => r.json())
    .then(data => {
      document.getElementById("statsText").innerHTML = `
        মোট সক্রিয় পণ্য রেকর্ড: <strong>${toBnNum(data.total_commodities)}</strong> টি | 
        সক্রিয় জেলা: <strong>${toBnNum(data.active_districts)}</strong> টি | 
        নিবন্ধিত কৃষক: <strong>${toBnNum(data.registered_farmers)}</strong> জন | 
        মোট সতর্কবার্তা: <strong>${toBnNum(data.total_alerts_sent)}</strong> টি
      `;
    })
    .catch(e => console.error("Error loading stats:", e));
}
