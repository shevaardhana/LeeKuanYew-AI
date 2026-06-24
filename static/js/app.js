// Lee Kuan Yew Chatbot Frontend Controller

// Suggested Questions categorized by theme
const questionsMap = {
    Survival: [
        {
            label: "Separation from Malaysia",
            q: "What was your immediate reaction to the separation from Malaysia in 1965?"
        },
        {
            label: "Ensuring water security",
            q: "How did Singapore solve its critical water dependency on Malaysia?"
        },
        {
            label: "Building the military",
            q: "How did you build the Singapore Armed Forces when you had no resources?"
        }
    ],
    Leadership: [
        {
            label: "Philosophy on leadership",
            q: "What is your philosophy on political leadership and governing Singapore?"
        },
        {
            label: "Eliminating corruption",
            q: "How did you build a clean government and wipe out corruption?"
        },
        {
            label: "Toughness on opponents",
            q: "Why were you so tough on political opponents and media critics?"
        }
    ],
    Geopolitics: [
        {
            label: "Managing superpowers",
            q: "How should a small country like Singapore manage relations with superpowers like the US and China?"
        },
        {
            label: "On China's rise",
            q: "What was your relationship with Deng Xiaoping, and how do you view China's rise?"
        },
        {
            label: "Role in ASEAN",
            q: "What role did you play in the creation and stability of ASEAN?"
        }
    ],
    NationBuilding: [
        {
            label: "Public Housing & HDB",
            q: "Why did you prioritize public homeownership through HDB flats?"
        },
        {
            label: "Clean & Green City",
            q: "What was the strategic reason behind making Singapore a Clean and Green Garden City?"
        },
        {
            label: "Bilingualism Policy",
            q: "What was the rationale behind Singapore's bilingual education policy?"
        }
    ]
};

// Application State
let chatHistory = [];
let currentTheme = 'Survival';

// DOM Elements
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatFeed = document.getElementById('chat-feed');
const typingIndicator = document.getElementById('typing-indicator');

// Sidebar / Drawer Toggles (Mobile + Desktop)
const mobileSidebarToggle = document.getElementById('mobile-sidebar-toggle');
const mobileEvalToggle = document.getElementById('mobile-eval-toggle');
const desktopEvalToggle = document.getElementById('desktop-eval-toggle');
const evalClose = document.getElementById('eval-close');
const sidebar = document.getElementById('sidebar');
const evalDrawer = document.getElementById('eval-drawer');
const sidebarBackdrop = document.getElementById('sidebar-backdrop');

// Dashboard Elements
const avgRelevanceVal = document.getElementById('avg-relevance-val');
const avgRelevanceBar = document.getElementById('avg-relevance-bar');
const avgFaithfulnessVal = document.getElementById('avg-faithfulness-val');
const avgFaithfulnessBar = document.getElementById('avg-faithfulness-bar');
const totalQueriesLbl = document.getElementById('total-queries-lbl');
const evalTimeline = document.getElementById('eval-timeline');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    selectTheme('Survival');
    setupEventListeners();
    setupSettingListeners();
    updateDashboard(); // Load any existing evaluation stats
});

function setupSettingListeners() {
    const settingK = document.getElementById('setting-k');
    const settingKVal = document.getElementById('setting-k-val');
    if (settingK && settingKVal) {
        settingK.addEventListener('input', () => {
            settingKVal.textContent = settingK.value;
        });
    }
}

function setupEventListeners() {
    // Form Submission
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = userInput.value.trim();
        if (!message) return;

        // Append User Message
        appendMessage('user', message);
        userInput.value = '';
        userInput.blur();

        // Show Typing Indicator
        typingIndicator.classList.remove('hidden');
        chatFeed.scrollTop = chatFeed.scrollHeight;

        // Read RAG Options from settings
        const ragMode = document.getElementById('setting-rag-mode').value;
        const kVal = parseInt(document.getElementById('setting-k').value);
        const primaryProvider = document.getElementById('setting-primary-provider').value;

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    history: chatHistory,
                    options: {
                        rag_mode: ragMode,
                        k: kVal,
                        primary_provider: primaryProvider
                    }
                })
            });

            if (!response.ok) throw new Error('Failed to get response');
            const data = await response.json();

            // Hide Typing Indicator
            typingIndicator.classList.add('hidden');

            // Append Bot Message
            appendMessage('assistant', data.response, data.provider);

            // Save to local history
            chatHistory.push({ role: 'user', content: message });
            chatHistory.push({ role: 'assistant', content: data.response });

            // Update Metrics Dashboard
            updateDashboard();

        } catch (error) {
            console.error('Error fetching chat response:', error);
            typingIndicator.classList.add('hidden');
            appendMessage('assistant', 'System error: I cannot connect to the server. Survival requires resourcefulness, but currently the wires are down.');
        }
    });

    // Mobile Sidebar Toggles
    mobileSidebarToggle.addEventListener('click', () => {
        sidebar.classList.remove('-translate-x-full');
        sidebarBackdrop.classList.remove('hidden');
    });

    // Mobile Drawer Toggles
    mobileEvalToggle.addEventListener('click', () => {
        evalDrawer.classList.remove('translate-x-full');
        sidebarBackdrop.classList.remove('hidden');
    });

    desktopEvalToggle.addEventListener('click', () => {
        evalDrawer.classList.toggle('translate-x-full');
    });

    evalClose.addEventListener('click', () => {
        evalDrawer.classList.add('translate-x-full');
        sidebarBackdrop.classList.add('hidden');
    });

    // Click backdrop to close mobile panels
    sidebarBackdrop.addEventListener('click', () => {
        sidebar.classList.add('-translate-x-full');
        evalDrawer.classList.add('translate-x-full');
        sidebarBackdrop.classList.add('hidden');
    });
}

// Handle Theme Selection and update suggested inquiries
function selectTheme(theme) {
    currentTheme = theme;
    
    // Update theme button active state
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.classList.remove('active');
        // Simple check based on icon class to match button
        if (theme === 'Survival' && btn.innerHTML.includes('shield-halved')) btn.classList.add('active');
        if (theme === 'Leadership' && btn.innerHTML.includes('gavel')) btn.classList.add('active');
        if (theme === 'Geopolitics' && btn.innerHTML.includes('earth-asia')) btn.classList.add('active');
        if (theme === 'NationBuilding' && btn.innerHTML.includes('city')) btn.classList.add('active');
    });

    // Render Suggested Questions
    const questionsContainer = document.getElementById('suggested-questions');
    questionsContainer.innerHTML = '';
    
    const questions = questionsMap[theme] || [];
    questions.forEach(item => {
        const qDiv = document.createElement('div');
        qDiv.className = "p-3 bg-slate-950/40 border border-slate-800 rounded-lg hover:border-amber-600/40 cursor-pointer transition text-slate-300 hover:text-slate-100 hover:bg-slate-900/60";
        qDiv.onclick = () => fillInput(item.q);
        qDiv.innerHTML = `"${item.label}"`;
        questionsContainer.appendChild(qDiv);
    });

    // Close mobile sidebar if clicked
    sidebar.classList.add('-translate-x-full');
    if (evalDrawer.classList.contains('translate-x-full')) {
        sidebarBackdrop.classList.add('hidden');
    }
}

function fillInput(text) {
    userInput.value = text;
    userInput.focus();
}

// Append Chat Bubbles
function appendMessage(role, text, provider) {
    const messageContainer = document.createElement('div');
    
    if (role === 'user') {
        messageContainer.className = "flex gap-4 max-w-2xl ml-auto justify-end message-animate";
        messageContainer.innerHTML = `
            <div class="bg-slate-800 border border-slate-700 rounded-2xl rounded-tr-none p-4 text-slate-100 text-sm shadow-md leading-relaxed">
                <p class="font-semibold text-slate-400 mb-0.5 text-xs text-right">You</p>
                <p>${escapeHTML(text)}</p>
            </div>
            <div class="w-10 h-10 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-400 flex-shrink-0">
                <i class="fa-solid fa-user"></i>
            </div>
        `;
    } else {
        // assistant
        messageContainer.className = "flex gap-4 max-w-3xl mr-auto message-animate";
        
        // Render Markdown using marked.js
        const renderedHtml = marked.parse(text);

        const prov = provider || "Local Fallback";
        const providerBadge = `<span class="text-[9px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded border border-slate-700/80 ml-2 font-mono align-middle select-none">${prov}</span>`;

        messageContainer.innerHTML = `
            <div class="w-10 h-10 rounded-full bg-amber-600/10 border border-amber-600/30 flex items-center justify-center text-amber-500 flex-shrink-0">
                <i class="fa-solid fa-feather-pointed"></i>
            </div>
            <div class="bg-slate-900/60 border border-amber-900/20 rounded-2xl rounded-tl-none p-5 text-slate-300 leading-relaxed shadow-lg prose">
                <p class="font-semibold text-amber-500 mb-1 text-sm flex items-center">
                    <span>Lee Kuan Yew</span>
                    ${providerBadge}
                </p>
                <div class="text-sm space-y-2">${renderedHtml}</div>
            </div>
        `;
    }
    
    chatFeed.appendChild(messageContainer);
    // Scroll to bottom
    chatFeed.scrollTop = chatFeed.scrollHeight;
}

// Fetch Evaluation Scores and Update Dashboard
async function updateDashboard() {
    try {
        const response = await fetch('/api/eval');
        const data = await response.json();

        // Update progress stats
        const cr = data.average_context_relevance;
        const pf = data.average_persona_faithfulness;
        
        avgRelevanceVal.textContent = `${cr}%`;
        avgRelevanceBar.style.width = `${cr}%`;
        
        avgFaithfulnessVal.textContent = `${pf}%`;
        avgFaithfulnessBar.style.width = `${pf}%`;
        
        totalQueriesLbl.textContent = `Total Queries: ${data.total_queries}`;

        // Render timeline
        evalTimeline.innerHTML = '';
        if (data.history.length === 0) {
            evalTimeline.innerHTML = `
                <div class="text-center py-8 text-slate-600 text-xs">
                    <i class="fa-solid fa-receipt text-3xl mb-3 block opacity-30"></i>
                    Waiting for chatbot inquiries to evaluate...
                </div>
            `;
            return;
        }

        // Render timeline cards (show top 5 recent)
        const recentHistory = [...data.history].reverse().slice(0, 5);
        recentHistory.forEach((evalData, index) => {
            const card = document.createElement('div');
            card.className = "bg-slate-950/40 border border-slate-800 rounded-xl p-3 space-y-2.5 text-xs";
            card.innerHTML = `
                <div class="flex justify-between items-center pb-2 border-b border-slate-800/40">
                    <span class="font-semibold text-amber-500 font-['Outfit']">Query #${data.history.length - index}</span>
                    <span class="text-[10px] text-slate-500">LLM Evaluation</span>
                </div>
                <div class="grid grid-cols-2 gap-2 text-center">
                    <div class="bg-slate-900/60 p-1.5 rounded-lg border border-slate-800">
                        <p class="text-[10px] text-slate-500 uppercase">Context Rel</p>
                        <p class="font-bold text-amber-500 font-['Outfit'] text-sm mt-0.5">${evalData.context_relevance.score}%</p>
                    </div>
                    <div class="bg-slate-900/60 p-1.5 rounded-lg border border-slate-800">
                        <p class="text-[10px] text-slate-500 uppercase">Persona Faith</p>
                        <p class="font-bold text-amber-500 font-['Outfit'] text-sm mt-0.5">${evalData.persona_faithfulness.score}%</p>
                    </div>
                </div>
                <div class="space-y-1 text-slate-400 leading-relaxed text-[11px]">
                    <p><strong class="text-slate-300">Context:</strong> ${escapeHTML(evalData.context_relevance.reason)}</p>
                    <p><strong class="text-slate-300">Persona:</strong> ${escapeHTML(evalData.persona_faithfulness.reason)}</p>
                </div>
            `;
            evalTimeline.appendChild(card);
        });

    } catch (error) {
        console.error('Error loading dashboard stats:', error);
    }
}

// Reset Chat Session
async function resetChat() {
    chatHistory = [];
    
    // Clear chat feed DOM, keeping only the greeting
    chatFeed.innerHTML = `
        <div class="flex gap-4 max-w-3xl mr-auto">
            <div class="w-10 h-10 rounded-full bg-amber-600/10 border border-amber-600/30 flex items-center justify-center text-amber-500 flex-shrink-0">
                <i class="fa-solid fa-feather-pointed"></i>
            </div>
            <div class="bg-slate-900/60 border border-amber-900/20 rounded-2xl rounded-tl-none p-5 text-slate-300 leading-relaxed shadow-lg">
                <p class="font-semibold text-amber-500 mb-1 text-sm">Lee Kuan Yew</p>
                <p class="text-sm">I have spent a whole lifetime building Singapore. If you wish to understand the principles that governed our survival, ask your questions directly. Let us not waste time with pleasantries.</p>
            </div>
        </div>
    `;

    // Clear scores on backend
    try {
        await fetch('/api/eval/reset', { method: 'POST' });
        await updateDashboard();
    } catch (e) {
        console.error('Error resetting metrics:', e);
    }
}

// External Reset scores button
async function resetScores() {
    if (confirm("Reset all evaluation dashboard scores?")) {
        try {
            await fetch('/api/eval/reset', { method: 'POST' });
            await updateDashboard();
        } catch (e) {
            console.error('Error resetting metrics:', e);
        }
    }
}

// Helper to prevent HTML injections
function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag)
    );
}
