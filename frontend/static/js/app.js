/**
 * Safar v2 — Frontend Application
 * Improvements: confirmation flow, replace-place, suggestions,
 *               value badges, smart hints, dismissable warnings,
 *               city banner, budget health bar
 */
window.addEventListener(
    "pageshow",
    function(event){

        const token =
            localStorage.getItem("token") ||
            sessionStorage.getItem("token")

        if(!token){

            window.location.replace("/login")
        }
    }
)
const authPages = [
    "/login",
    "/signup"
]
function logout(){

    localStorage.clear()
    sessionStorage.clear()

    window.location.replace("/login")
}

function getToken(){

    return (
        localStorage.getItem("token")
        ||
        sessionStorage.getItem("token")
    )
}

function getUsername(){

    return (
        localStorage.getItem("username")
        ||
        sessionStorage.getItem("username")
    )
}

const currentPath =
    window.location.pathname

// Guest trying to access app
if (!getToken() && !authPages.includes(currentPath)) {
    window.location.href = "/login"
}

// Logged in user trying auth pages
if (getToken() && authPages.includes(currentPath)) {
    window.location.href = "/"
}

// ── State ──────────────────────────────────────────────────────────────────
const state = {
  sessionId:     null,
  lastItinerary: null,
};
const historyTrips = {}

// ── DOM ────────────────────────────────────────────────────────────────────
const chatWindow   = document.getElementById('chatWindow');
const chatInput    = document.getElementById('chatInput');
const sendBtn      = document.getElementById('sendBtn');
const menuBtn      = document.getElementById('menuBtn');
const sidebar      = document.getElementById('sidebar');
const sidebarClose = document.getElementById('sidebarClose');
const resetBtn     = document.getElementById('resetBtn');
const logoutBtn    =document.getElementById("logoutBtn")
const navBtns      = document.querySelectorAll('.nav-btn');
const panels       = document.querySelectorAll('.panel');


// ── Sidebar ────────────────────────────────────────────────────────────────
function openSidebar() {
  if(!sidebar) return;
  sidebar.classList.add('open');
  let ov =
    document.querySelector('.sidebar-overlay');
  if (!ov) {
    ov = document.createElement('div');
    ov.className = 'sidebar-overlay';
    ov.addEventListener('click', closeSidebar);
    document.body.appendChild(ov);
  }
  ov.classList.add('active');
}
function closeSidebar() {
  if(!sidebar) return;
  sidebar.classList.remove('open');
  document.querySelector('.sidebar-overlay')?.classList.remove('active');
  }
  if(menuBtn){
    menuBtn.addEventListener(
      'click',
      openSidebar
    );
  }

  if(sidebarClose){ 
  sidebarClose.addEventListener(
    'click',
    closeSidebar
  );
  }
  if(logoutBtn){
    logoutBtn.addEventListener(
        "click",
        logout
      )
    }
navBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    const t = btn.dataset.panel;
    navBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    // Clear badge on this tab
    btn.querySelector('.nav-badge')?.remove();
    panels.forEach(p => p.classList.remove('active'));
    document.getElementById('panel' + cap(t)).classList.add('active');
    if (window.innerWidth <= 768) closeSidebar();
  });
});

function cap(s) { return s.charAt(0).toUpperCase() + s.slice(1); }

function switchToPanel(name) {
  navBtns.forEach(b =>
    b.classList.toggle('active', b.dataset.panel === name.toLowerCase())
  );

  panels.forEach(p => p.classList.remove('active'));

  const activePanel =
    document.getElementById('panel' + cap(name));
  
  activePanel.classList.add('active');
  const inner = activePanel.querySelector('.panel-inner');
  if (inner) inner.scrollTop = 0;
  activePanel.scrollTop = 0;
}

function badgeTab(panelName) {
  const btn = [...navBtns].find(b => b.dataset.panel === panelName.toLowerCase());
  if (btn && !btn.classList.contains('active') && !btn.querySelector('.nav-badge')) {
    const dot = document.createElement('span');
    dot.className = 'nav-badge';
    btn.appendChild(dot);
  }
}

// ── Reset ──────────────────────────────────────────────────────────────────
if(resetBtn){
  resetBtn.addEventListener('click',async () => {
    try {
      await fetch(
        '/api/chat/reset',
        {
          method: 'POST',
          headers: {
            'Content-Type':'application/json',
            'Authorization':
            `Bearer ${getToken()}`
          },
          body: JSON.stringify({
            session_id: state.sessionId
          }),
        }
       );
      }catch(_) {}
      state.sessionId = null;
      state.lastItinerary = null;
      chatWindow
        ?.querySelectorAll('.msg:not(#welcomeMsg)')
        .forEach(m => m.remove());

      document
        .querySelector('.quick-hints')
        ?.style.removeProperty('display');

      const itineraryContent =
        document.getElementById('itineraryContent');

      if(itineraryContent){

        itineraryContent.innerHTML =
          emptyState(
            '🗺️',
            'Your itinerary will appear here once you generate a plan.'
          );
      }

      const budgetContent =
        document.getElementById('budgetContent');

      if(budgetContent){

        budgetContent.innerHTML =
          emptyState(
            '📊',
            'Budget details will appear here after your plan is generated.'
          );
      }

      updateContextPills({});

      switchToPanel('chat');
    }
  );
}



// ── Send message ───────────────────────────────────────────────────────────
async function sendMessage(text, extraData) {
  const msg = text ?? chatInput.value.trim();
  if (!msg) return;
  chatInput.value = '';
  resizeChatInput();

  document.querySelector('.quick-hints')?.style.setProperty('display','none');
  appendMessage(msg, 'user');
  sendBtn.disabled = true;

  const typingId = appendTyping();
  try {
    const body = { message: msg, session_id: state.sessionId, ...extraData };
    console.log("Sending request...");
    console.log(body);
    const res  = await fetch('/api/chat/message', {
        method: 'POST', headers: {'Content-Type':'application/json','Authorization':
          `Bearer ${getToken()}`
        },
        body: JSON.stringify(body),
      });
    removeTyping(typingId);
    if(res.status === 401){logout()
      return
    }
    if(!res.ok){
      throw new Error(res.status)
    } 
    const data = await res.json();
    console.log("FULL RESPONSE:");
    console.log(data);
    console.log("ITINERARY:");
    console.log(data.data);
    state.sessionId = data.session_id;

    // Bot reply with confirm buttons if CONFIRMING
    if (data.intent === 'CONFIRMING') {
      appendConfirmMessage(data.reply);
    } 
    else {
      appendMessage(data.reply, 'bot');
      scrollBottom();
    }

    if (data.data) {
      console.log("RENDER DATA:");
      console.log(data.data);
      state.lastItinerary = data.data;
      renderItinerary(data.data);
      scrollBottom();
      renderBudget(data.data);
      updateContextPills(data.data);
      badgeTab('itinerary');
      badgeTab('budget');
      switchToPanel('itinerary');
    }
  } 
  catch(err) {
    removeTyping(typingId);
    appendMessage('Sorry, something went wrong. Please try again.', 'bot');
    console.error(err);
  } 
  finally {
    sendBtn.disabled = false;
    chatInput.focus();
  }
}

window.sendHint = text => sendMessage(text);

// ── Confirm buttons ────────────────────────────────────────────────────────
function appendConfirmMessage(text) {
  const wrap = document.createElement('div');
  wrap.className = 'msg msg-bot';
  wrap.innerHTML = `
    <div class="msg-avatar">✦</div>
    <div class="msg-bubble">
      ${formatMessage(text)}
      <div class="confirm-actions">
        <button class="confirm-btn yes" onclick="sendMessage('yes')">✓ Yes, generate my plan</button>
        <button class="confirm-btn no"  onclick="sendMessage('no, let me change something')">✎ Change something</button>
      </div>
    </div>`;
  chatWindow.appendChild(wrap);
  scrollBottom();
}

// ── Replace place (called from itinerary buttons) ──────────────────────────
window.replacePlace = async function(dayNum, placeId, btnEl) {
  const placeItem = btnEl.closest('.place-item');
  placeItem.classList.add('replacing');
  btnEl.textContent = 'Finding…';
  btnEl.disabled = true;
  try {
    const res  = await fetch('/api/chat/message', {
      method: 'POST', headers: {'Content-Type':'application/json','Authorization':
        `Bearer ${getToken()}`
      },
      body: JSON.stringify({
        message:    'replace this place',
        session_id: state.sessionId,
        day_num:    dayNum,
        place_id:   placeId,
      }), 
    });
    const data = await res.json();
    if (data.data) {
      state.lastItinerary = data.data;
      renderItinerary(data.data);
      renderBudget(data.data);
      appendMessage(data.reply, 'bot');
    }
  } catch(e) {
    placeItem.classList.remove('replacing');
    btnEl.textContent = '↺ Replace';
    btnEl.disabled = false;
  }
};

window.removePlace = function(dayNum, placeId, btnEl) {
  const placeItem = btnEl.closest('.place-item');
  placeItem.classList.add('being-removed');
  setTimeout(() => {
    // Update local itinerary state
    if (state.lastItinerary) {
      const day = (state.lastItinerary.days || [])
        .find(d => d.day === dayNum);
      if(day && day.places){
        day.places = day.places.filter(p => p.id !== placeId);
      }
    }
    renderItinerary(state.lastItinerary);
    appendMessage('Removed! Your itinerary has been updated.', 'bot');
  }, 280);
};

// ── Input ──────────────────────────────────────────────────────────────────

  if(sendBtn && chatInput){
    sendBtn.addEventListener(
      'click',
      () => sendMessage()
    );
    chatInput.addEventListener(
      'input',
      resizeChatInput
    );
    chatInput.addEventListener(
      'keydown',
      (e) => {
        if (
          e.key === 'Enter'&&
          !e.shiftKey
        ) {
          e.preventDefault();
          sendMessage();
        }
      }
    )
  }

function resizeChatInput() {
  chatInput.style.height = 'auto';
  chatInput.style.height = Math.min(chatInput.scrollHeight, 130) + 'px';
}

// ── Message rendering ──────────────────────────────────────────────────────
function appendMessage(text, role) {
  const w = document.createElement('div');
  w.className = `msg msg-${role}`;
  if (role === 'bot') {
    w.innerHTML = `<div class="msg-avatar">✦</div>
      <div class="msg-bubble">${formatMessage(text)}</div>`;
  } else {
    w.innerHTML = `<div class="msg-bubble">${esc(text)}</div>`;
  }
  chatWindow.appendChild(w);
  setTimeout(() => {
  scrollBottom();
  }, 50);
  return w;
}

function appendTyping(customText = null) {
  const states = [
      "✦ Understanding your trip...",
      "🧠 Processing your request...",
      "📍 Collecting travel details...",
      "✈ Planning your journey..."
  ];
  const stateText =
      customText ||
      states[Math.floor(Math.random() * states.length)];

  const id = 'ty-' + Date.now();
  const w = document.createElement('div');
  w.className = 'msg msg-bot';
  w.id = id;

  w.innerHTML = `
      <div class="msg-avatar">✦</div>

      <div class="typing-bubble">
          ${stateText}
      </div>
  `;
  chatWindow.appendChild(w);
  setTimeout(() => {
  scrollBottom();
  }, 50); 
  return id;
}

function removeTyping(id) { document.getElementById(id)?.remove(); }
function scrollBottom() {
  requestAnimationFrame(() => {
    chatWindow.scrollTo({
      top: chatWindow.scrollHeight,
      behavior: 'smooth'
    });
  });
}

function formatMessage(t) {
    t = esc(t)

  return t
    
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/_(.*?)_/g, '<em>$1</em>')

    // BULLET POINTS
    .replace(/^• (.*)$/gm, '<li>$1</li>')

    // Wrap bullet items inside UL
    .replace(/(<li>.*<\/li>)/gs, '<ul class="ai-budget-list">$1</ul>')
    .replace(/\n\n/g,'</p><p>')
    .replace(/\n/g,'<br>')
    .replace(/^/,'<p>')
    .replace(/$/,'</p>');
}

function esc(t) {
  return String(t || '')
    .replace(/&/g,'&amp;')
    .replace(/</g,'&lt;')
    .replace(/>/g,'&gt;');
}

// ── Itinerary rendering ────────────────────────────────────────────────────────
function renderItinerary(itinerary) { 
  console.log("RENDERING ITINERARY:", itinerary);
   if (!itinerary) return;
  const b = itinerary.budget_breakdown || {
      total_budget:0,
      total_spent:0,
      leftover:0,
      people:1,
      days:1,
      hotel:{
          total_cost:0,
          label:"Not available",
          per_person_per_night:0
      },
      food:{
          total_cost:0,
          label:"Not available",
          per_person_per_day:0
      },
      transport:{
          total_cost:0,
          per_person_per_day:0
      },
      activities:{
          allocated:0,
          spent:0
      }
    };
  const c = document.getElementById('itineraryContent');
  const days = Array.isArray(itinerary.days)
    ? itinerary.days: [];
  const city = itinerary.city || "Unknown";
  const ai_explanation = itinerary.ai_explanation || "";
  const warnings = itinerary.warnings || [];
  const suggestions = itinerary.suggestions || [];
  let html = '';
  html +=`
  <div class="trip-hero">
  <div class="trip-hero-title">
  ✈ ${city}
  </div>
  <div class="trip-hero-sub">
  ${b.days} day trip •
  ${b.people} travelers •
  Rs ${fmt(b.total_budget)}
  </div>
  </div>
  `;

  // City banner
  html += `
    <div class="city-banner">
      <div>
        <div class="city-banner-name">📍 ${esc(city)}</div>
        <div style="font-size:12px;color:rgba(255,255,255,0.5);margin-top:2px">
          ${b.days} day${b.days>1?'s':''} · ${b.people} person${b.people>1?'s':''}
        </div>
      </div>
      <div class="city-banner-meta">
        Budget: Rs ${fmt(b.total_budget)}<br>
        Leftover: <span style="color:var(--sage)">Rs ${fmt(b.leftover)}</span>
      </div>
    </div>`;

  // AI explanation
  if (ai_explanation) {

  // Split explanation into lines
    const lines = ai_explanation
      .split('\n')
      .filter(line => line.trim() !== '');

    let formatted = '';

    let listStarted = false;

    lines.forEach(line => {

    // Budget bullet points
      if (line.trim().startsWith('•')) {

        if (!listStarted) {
          formatted += `<ul class="ai-summary-list">`;
          listStarted = true;
        }

        formatted += `
          <li>
            ${esc(line.replace('•', '').trim())}
          </li>
        `;
      } else {

      // Close list if needed
        if (listStarted) {
          formatted += `</ul>`;
          listStarted = false;
        }

        formatted += `<p>${esc(line)}</p>`;
      }
    });

    if (listStarted) {
      formatted += `</ul>`;
    }

    html += `
      <div class="ai-explanation-box">

        <div class="ai-label">
          ✦ AI Summary
        </div>
      ${formatted}
    </div>
  `;
}

  // Warnings (dismissable)
  (warnings || []).forEach((w,i) => {
    html += `<div class="warning-box" id="warn-${i}">
      <span>⚠️ ${esc(w)}</span>
      <button class="warning-dismiss" onclick="document.getElementById('warn-${i}').remove()">✕</button>
    </div>`;
  });

  // Day cards
  (days || []).forEach((day, di) => {   
     html += `<div class="day-card" style="animation-delay:${di*70}ms">
      <div class="day-header">
        <span class="day-number">Day ${day.day}</span>
        <span class="day-meta">
          ${(day.places || []).length} place${(day.places || []).length!==1?'s':''}
          ~${day.day_hours}h ·
          Rs ${fmt(day.day_activity_cost)} activities
        </span>
      </div>`;
      if (!(day.places || []).length) {
        html += `
        <div class="place-item">
          <p style="color:var(--mid);font-size:14px;padding:4px 0">
            No additional places needed — this is a travel or rest day.
          </p></div>`;
      } else {
        (day.places || []).forEach(p => {
          if (!p || typeof p !== 'object') return;
          console.log("PLACE:", p);
          const costBadge = p.cost === 0
          ? `<span class="place-cost free">Free</span>`
          : `<span class="place-cost">Rs ${fmt(p.cost)}</span>`;

        const tags = [];
        if (typeof p.category === "string" && p.category.trim()) {
          tags.push(`
            <span class="tag ${p.category.replace(/\s+/g, '-')}">
            ${esc(p.category)}
            </span>
            `);
          }
          if (p.popularity === "hidden") {
            tags.push(`
              <span class="tag hidden-gem">
              hidden gem
              </span>
              `);
            }
        const tagsHtml = tags.join('');

        const rating = p.rating
          ? `<span class="place-meta-item"><span class="rating-stars">★</span> ${p.rating}</span>`
          : '';
        const vScore = p.value_score
          ? `<span class="value-badge">⚡ ${p.value_score} value</span>`
          : '';

        html += `
          <div class="place-item">
          ${typeof p.image_url === 'string'
            && p.image_url.trim() !== ''
            && !p.image_url.includes('example.com') ? `
            <div class="place-image">
              <img src="${p.image_url}"
              loading="lazy"
              alt="${esc(p.name)}"
              onerror="this.parentElement.style.display='none'">
              </div>
              ` : ''}
              <div class="place-top">
              <span class="place-name">${esc(p.name)}</span>
              <div style="display:flex;gap:6px;align-items:center;flex-shrink:0">
                ${vScore}
                ${costBadge}
              </div>
              </div>
              <div class="place-tags">${tagsHtml}</div>
              ${p.description ? `<p class="place-desc">${esc(p.description)}</p>` : ''}
              <div class="place-footer">
              ${rating}
              <span class="place-meta-item">🕐 ~${p.time_required}h</span>
              ${p.best_time ? `<span class="place-meta-item">🌅 ${esc(p.best_time)}</span>` : ''}
              </div>
              ${p.explanation ? `<div class="place-explanation">${esc(p.explanation)}</div>` : ''}
              <div class="place-actions">
              <button class="place-action-btn"
              onclick="replacePlace(${day.day}, ${p.id}, this)">↺ Replace</button>
              <button class="place-action-btn removing"
              onclick="removePlace(${day.day}, ${p.id}, this)">✕ Remove</button>
            </div>
          </div>`;
      });
    }
    html += `</div>`;
  });

  // Suggestions
  if (suggestions && suggestions.length) {
    html += `<div class="suggestions-section">
      <div class="suggestions-title">💡 Suggestions</div>`;
    suggestions.forEach(s => {
      html += `<div class="suggestion-chip">
        <span class="sug-icon">${s.type==='upgrade'?'⬆️':s.type==='budget_tip'?'💰':s.type==='preference'?'🎯':'📅'}</span>
        <span>${esc(s.message)}</span>
      </div>`;
    });
    html += `</div>`;
  }
  try {
    c.innerHTML = html;
    console.log("ITINERARY HTML LENGTH:", html.length);
    console.log("ITINERARY RENDER SUCCESS");  } catch(err) {
    console.error("RENDER FAILED:", err);
  }}

// ── Budget rendering ───────────────────────────────────────────────────────
function renderBudget(itinerary) {
  if (!itinerary) return;
  const b = itinerary.budget_breakdown || {
    total_budget: 0,
    total_spent: 0,
    leftover: 0,
    people: 1,
    days: 1,
    hotel: {
      total_cost: 0,
      label: "Not available",
      per_person_per_night: 0
    },
    food: {
      total_cost: 0,
      label: "Not available",
      per_person_per_day: 0
    },
    transport: {
      total_cost: 0,
      per_person_per_day: 0
    },
    activities: {
      allocated: 0,
      spent: 0
    }
  };
  const c = document.getElementById('budgetContent');
  const pct = v => {
    if (!b.total_budget) return 0;
    return Math.min(
        100,
        Math.round((v / b.total_budget) * 100)
    );
  };  
  const usedPct = pct(b.total_spent);

  const healthClass = usedPct > 95 ? 'tight' : usedPct > 85 ? 'warn' : '';

  let html = `
    <div class="budget-health">
      <div class="budget-health-label">
        <span>Budget used</span>
        <span>${usedPct}% of Rs ${fmt(b.total_budget)}</span>
      </div>
      <div class="health-bar-track">
        <div class="health-bar-fill ${healthClass}" style="width:0%" id="healthFill"></div>
      </div>
    </div>

    <div class="budget-summary">
      ${metricCard('Total Budget', 'Rs '+fmt(b.total_budget), b.people+' person'+(b.people>1?'s':'')+', '+b.days+' day'+(b.days>1?'s':''))}
      ${metricCard('Total Spent',  'Rs '+fmt(b.total_spent),  usedPct+'% of budget')}
      ${metricCard('Leftover',     'Rs '+fmt(b.leftover),     'Safety buffer', '#2E7D4F')}
      ${metricCard('Per Person/Day','Rs ' + fmt(Math.round((b.total_budget || 0) /Math.max(1, (b.people || 1) * (b.days || 1)))),
        'Average daily cost')}
      </div>

    <div class="budget-bar-section">`;

  [
    {
      label:'Accommodation',
      v: b.hotel?.total_cost || 0,
      accent:'#6899C4'
    },
    {
      label:'Food & Drinks',
      v: b.food?.total_cost || 0,
      accent:'#8AAF80'
    },
    {
      label:'Transport',
      v: b.transport?.total_cost || 0,
      accent:'#7B6DAE'
    },
    {
      label:'Activities',
      v: b.activities?.spent || 0,
      accent:'#D4896A'
    },
  ]
  .forEach(bar => {
    const p = pct(bar.v);
    html += `<div style="margin-bottom:14px">
      <div class="budget-bar-label">
        <span>${bar.label}</span>
        <span>Rs ${fmt(bar.v)} (${p}%)</span>
      </div>
      <div class="budget-bar-track">
        <div class="budget-bar-fill" data-width="${p}"
             style="width:0%;background:${bar.accent}"></div>
      </div></div>`;
  });

  html += `</div>
    <table class="budget-table">
      <thead><tr><th>Category</th><th>Details</th><th style="text-align:right">Rs</th></tr></thead>
      <tbody>
        <tr><td>🏨 Hotel</td>
            <td>${esc(b.hotel?.label || 'Not available')} — Rs ${fmt(b.hotel?.per_person_per_night || 0)}/person/night</td>
            <td style="text-align:right">${fmt(b.hotel?.total_cost || 0)}</td>
        </tr>
        <tr><td>🍽️ Food</td>
            <td>${esc(b.food?.label || 'Not available')} — Rs ${fmt(b.food?.per_person_per_day || 0)}/person/day</td>
            <td style="text-align:right">${fmt(b.food?.total_cost || 0)}</td>       
        </tr>
        <tr><td>🚌 Transport</td>
            <td>Rs ${fmt(b.transport?.per_person_per_day || 0)}/person/day</td>
            <td style="text-align:right">${fmt(b.transport?.total_cost || 0)}</td></tr>
        <tr><td>🎯 Activities</td>
            <td>Rs ${fmt(b.activities?.allocated || 0)} allocated · Rs ${fmt(b.activities?.spent || 0)} used</td>
            <td style="text-align:right">${fmt(b.activities?.spent || 0)}</td></tr>
        <tr class="budget-total">
          <td colspan="2"><strong>Total</strong></td>
          <td style="text-align:right"><strong>${fmt(b.total_spent || 0)}</strong></td>
        </tr>
      </tbody>
    </table>`;

  c.innerHTML = html;

  // Animate bars after paint
  setTimeout(() => {
    document.getElementById('healthFill').style.width = usedPct + '%';
    c.querySelectorAll('.budget-bar-fill[data-width]').forEach(el => {
      requestAnimationFrame(() => { el.style.width = el.dataset.width + '%'; });
    });
  }, 80);
}

function metricCard(label, value, sub, valueColor) {
  return `<div class="budget-card">
    <div class="budget-card-label">${label}</div>
    <div class="budget-card-value"${valueColor ? ` style="color:${valueColor}"` : ''}>${value}</div>
    <div class="budget-card-sub">${sub}</div>
  </div>`;
}

// ── Context pills ──────────────────────────────────────────────────────────
function updateContextPills(itin) {
    itin = itin || {}
  const b = itin.budget_breakdown || {
    total_budget: 0,
    people: 1,
    days: 1
  };
  document.getElementById('ctxCity').textContent =
  `🏙️ City: ${itin.city || '—'}`;
  document.getElementById('ctxBudget').textContent =
  `💰 Budget: ${b.total_budget ? 'Rs '+fmt(b.total_budget) : '—'}`;
  document.getElementById('ctxDays').textContent =
  `📅 Days: ${b.days || '—'}`;
  document.getElementById('ctxPeople').textContent =
  `👥 People: ${b.people || '—'}`;
  
}

// ── Helpers ────────────────────────────────────────────────────────────────
function fmt(n){
    return Math.round(Number(n || 0))
        .toLocaleString('en-PK');
}

function emptyState(icon, text) {
  return `<div class="empty-state"><div class="empty-icon">${icon}</div><p>${text}</p></div>`;
}

async function loadHistory() {
  try {
    const res = await fetch(
      "/api/chat/history",
      {
        headers: {
          Authorization:
          `Bearer ${getToken()}`
        }
      }
    )
    if(res.status === 401){
      logout()
      return
    }
    if(!res.ok){throw new Error(res.status)}
    const data = await res.json()
    if(data.success){
      renderHistory(data.history)
    }
  } catch(err){
     console.error(err)
    }
  }

  function renderHistory(history) {
    const container =document.getElementById("historyContent")
    if(!history || !history.length){
      container.innerHTML = `
      <div class="empty-state">
      <div class="empty-icon">🕘</div>
      <p>No saved trips yet.</p>
      </div>
      `
      return
    }

    let html = ""

    history.forEach(trip => {
      historyTrips[trip.id] = trip.itinerary
      html += `
      <div class="history-card">
      <h3>${trip.city}</h3>
      <p>
      ${trip.days} days •
      ${trip.people} people
      </p>
      <p>
      Budget:
      Rs ${trip.budget}
      </p>
      <button
      class="history-open-btn"
      onclick="openHistoryTrip(${trip.id})">  
      Open Trip
      </button>
    </div>
    `
  })
  container.innerHTML = html
}

function openHistoryTrip(id){

    const itinerary =historyTrips[id]

    if(!itinerary) return

    state.lastItinerary =
    itinerary

    renderItinerary(itinerary)

    renderBudget(itinerary)

    updateContextPills(itinerary)

    switchToPanel("itinerary")
}
if(getToken()){
    loadHistory()
}