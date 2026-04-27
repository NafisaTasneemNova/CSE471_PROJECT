"""
Applies two fixes to supplier_dashboard.html in one clean pass:
1. Replaces the broken <form> bid calculator with a client-side div
2. Adds the capacity management panel before {% endblock %}
Run: python apply_dashboard_fixes.py  (from backend folder)
"""

path = '../frontend/src/pages/supplier_dashboard.html'
content = open(path, encoding='utf-8').read()

# ── FIX 1: Replace the form-based bid calculator ─────────────────────────────
OLD_FORM_START = '<form id="quoting-widget-form" action="/quote/submit" method="POST" class="p-5 space-y-4">'
OLD_FORM_END   = '</form>'

form_start = content.find(OLD_FORM_START)
form_end   = content.find(OLD_FORM_END, form_start) + len(OLD_FORM_END)

assert form_start != -1, "Could not find quoting-widget-form <form> tag"

NEW_CALCULATOR = '''<div id="quoting-widget-form" class="p-5 space-y-4">
                <!-- CM Cost -->
                <div>
                    <label class="block text-xs font-bold text-slate-600 mb-1">CM (Cut &amp; Make) Cost per piece</label>
                    <div class="relative">
                        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <span class="text-slate-500 sm:text-sm">$</span>
                        </div>
                        <input type="number" step="0.01" id="cm_cost"
                            class="pl-7 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-primary focus:ring-1 focus:ring-brand-primary"
                            placeholder="0.00">
                    </div>
                </div>

                <!-- Fabric Cost -->
                <div>
                    <label class="block text-xs font-bold text-slate-600 mb-1">Fabric/Material Cost per piece</label>
                    <div class="relative">
                        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <span class="text-slate-500 sm:text-sm">$</span>
                        </div>
                        <input type="number" step="0.01" id="fabric_cost"
                            class="pl-7 w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-primary focus:ring-1 focus:ring-brand-primary"
                            placeholder="0.00">
                    </div>
                </div>

                <hr class="border-slate-100">

                <!-- Auto-calculated total -->
                <div class="flex justify-between items-center bg-slate-50 p-2 rounded border border-slate-100">
                    <span class="text-sm font-bold text-slate-700">Total Unit Price</span>
                    <div class="relative w-24">
                        <div class="absolute inset-y-0 left-0 pl-2 flex items-center pointer-events-none">
                            <span class="text-slate-500 text-sm font-bold">$</span>
                        </div>
                        <input type="number" step="0.01" id="total_price" readonly
                            class="pl-6 w-full bg-transparent border-none text-right font-extrabold text-slate-900 text-lg focus:ring-0 p-0"
                            placeholder="0.00">
                    </div>
                </div>

                <!-- Lead Time -->
                <div>
                    <label class="block text-xs font-bold text-slate-600 mb-1">Estimated Lead Time (Days)</label>
                    <input type="number" id="lead_time"
                        class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-primary focus:ring-1 focus:ring-brand-primary"
                        placeholder="e.g. 45">
                </div>

                <!-- Result -->
                <div id="quote-result" class="hidden p-3 rounded-lg text-sm font-semibold text-center"></div>

                <!-- Calculate button -->
                <button type="button" id="calc-quote-btn"
                    class="w-full flex items-center justify-center gap-2 bg-brand-primary text-white font-bold py-3 rounded-lg shadow-sm hover:bg-brand-dark transition mt-2">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 11h.01M12 11h.01M15 11h.01M4 19h16a2 2 0 002-2V7a2 2 0 00-2-2H4a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                    </svg>
                    Calculate Quote
                </button>

                <!-- AI link -->
                <a href="/ai/recommend"
                    class="w-full flex items-center justify-center gap-2 bg-indigo-600 text-white font-bold py-2.5 rounded-lg shadow-sm hover:bg-indigo-700 transition text-sm mt-1">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
                    </svg>
                    Get AI Bid Recommendation
                </a>
            </div>'''

content = content[:form_start] + NEW_CALCULATOR + content[form_end:]
print("Fix 1 applied: bid calculator form replaced")

# ── FIX 2: Fix the existing JS to use getElementById ─────────────────────────
content = content.replace(
    "document.querySelector('input[name=\"cm_cost\"]')",
    "document.getElementById('cm_cost')"
)
content = content.replace(
    "document.querySelector('input[name=\"fabric_cost\"]')",
    "document.getElementById('fabric_cost')"
)

# Add Calculate button handler before closing </script>
CALC_HANDLER = """
        // Calculate Quote button
        const calcBtn = document.getElementById('calc-quote-btn');
        if (calcBtn) {
            calcBtn.addEventListener('click', () => {
                const cm  = parseFloat((document.getElementById('cm_cost') || {}).value) || 0;
                const fab = parseFloat((document.getElementById('fabric_cost') || {}).value) || 0;
                const lead = (document.getElementById('lead_time') || {}).value || '';
                const total = cm + fab;
                const resultEl = document.getElementById('quote-result');
                if (!resultEl) return;
                if (total <= 0) {
                    resultEl.className = 'p-3 rounded-lg text-sm font-semibold text-center bg-red-50 text-red-700 border border-red-200';
                    resultEl.textContent = 'Please enter CM and Fabric costs first.';
                    resultEl.classList.remove('hidden');
                    return;
                }
                resultEl.className = 'p-3 rounded-lg text-sm font-semibold text-center bg-emerald-50 text-emerald-800 border border-emerald-200';
                resultEl.innerHTML = '&#x2705; Total: <strong>$' + total.toFixed(2) + '/unit</strong>' +
                    (lead ? ' &bull; Lead: <strong>' + lead + ' days</strong>' : '');
                resultEl.classList.remove('hidden');
            });
        }
"""

# Insert before the drag widget closing </script>
DRAG_SCRIPT_END = "    });\n</script>"
assert DRAG_SCRIPT_END in content, "Could not find drag script end"
content = content.replace(DRAG_SCRIPT_END, CALC_HANDLER + "\n    });\n</script>")
print("Fix 2 applied: JS updated with getElementById + Calculate handler")

# ── FIX 3: Add capacity management panel before {% endblock %} ────────────────
CAPACITY_PANEL = """
<!-- ===== CAPACITY MANAGEMENT PANEL ===== -->
<div id="capacity-panel"
     class="fixed bottom-6 left-6 w-80 bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden z-40">

    <div class="px-5 py-3 bg-gradient-to-r from-[#1b4478] to-[#2563eb] flex items-center justify-between cursor-pointer select-none"
         id="capacity-panel-header">
        <div class="flex items-center gap-2">
            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
            </svg>
            <span class="text-white font-bold text-sm">My Factory Capacity</span>
        </div>
        <button type="button" id="capacity-panel-toggle" class="text-blue-200 hover:text-white transition">
            <svg id="capacity-chevron" class="w-4 h-4 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/>
            </svg>
        </button>
    </div>

    <div id="capacity-panel-body" class="p-5 space-y-4">
        <div id="capacity-summary" class="text-xs text-slate-400 text-center py-1">Loading...</div>
        <div class="space-y-3">
            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1">
                    Total Capacity <span class="text-slate-400 font-normal">(units/month)</span>
                </label>
                <input type="number" id="cap-total" min="1" placeholder="e.g. 50000"
                       class="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
            </div>
            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1">
                    Available Now <span class="text-slate-400 font-normal">(units free this month)</span>
                </label>
                <input type="number" id="cap-available" min="0" placeholder="e.g. 20000"
                       class="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
            </div>
            <p id="cap-error"   class="hidden text-xs text-red-600 font-medium"></p>
            <p id="cap-success" class="hidden text-xs text-emerald-600 font-medium"></p>
            <button type="button" id="cap-save-btn"
                    class="w-full py-2.5 bg-[#1b4478] text-white text-sm font-bold rounded-lg hover:bg-[#163a6b] transition disabled:opacity-50">
                Save Capacity
            </button>
        </div>
    </div>
</div>

<script>
(async () => {
    let myCompanyId = null;
    try {
        const r = await fetch('/api/me');
        if (r.ok) {
            const d = await r.json();
            myCompanyId = d.company && d.company.id ? d.company.id : null;
        }
    } catch (e) {}

    const toggleBtn = document.getElementById('capacity-panel-toggle');
    const panelBody = document.getElementById('capacity-panel-body');
    const chevron   = document.getElementById('capacity-chevron');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            panelBody.classList.toggle('hidden');
            chevron.style.transform = panelBody.classList.contains('hidden') ? 'rotate(180deg)' : '';
        });
    }

    async function loadCapacitySummary() {
        const summary = document.getElementById('capacity-summary');
        if (!myCompanyId) {
            if (summary) summary.innerHTML = '<span class="text-orange-500 font-semibold text-xs">Log in to manage capacity</span>';
            return;
        }
        try {
            const res  = await fetch('/capacity/' + myCompanyId);
            const data = await res.json();
            if (!data.success || !data.has_capacity_data) {
                summary.innerHTML = '<span class="text-orange-500 font-semibold text-xs">&#9888; No capacity set yet</span>';
                return;
            }
            const cap   = data.capacity;
            const total = cap.total_capacity || 0;
            const avail = cap.available_capacity || 0;
            const util  = data.utilization_pct || 0;
            const bar   = util >= 90 ? 'bg-red-500' : util >= 60 ? 'bg-orange-400' : 'bg-emerald-500';
            summary.innerHTML =
                '<div class="space-y-1.5">' +
                '<div class="flex justify-between text-xs">' +
                '<span class="text-slate-500">' + avail.toLocaleString() + ' free of ' + total.toLocaleString() + '</span>' +
                '<span class="font-bold text-slate-700">' + util + '% used</span></div>' +
                '<div class="w-full bg-slate-200 rounded-full h-2">' +
                '<div class="' + bar + ' h-2 rounded-full" style="width:' + Math.min(util,100) + '%"></div></div></div>';
            const capTotal = document.getElementById('cap-total');
            const capAvail = document.getElementById('cap-available');
            if (capTotal) capTotal.value = total;
            if (capAvail) capAvail.value = avail;
        } catch (e) {
            summary.innerHTML = '<span class="text-red-400 text-xs">Could not load capacity</span>';
        }
    }

    const saveBtn = document.getElementById('cap-save-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', async () => {
            const total     = parseInt((document.getElementById('cap-total') || {}).value);
            const available = parseInt((document.getElementById('cap-available') || {}).value);
            const errEl     = document.getElementById('cap-error');
            const okEl      = document.getElementById('cap-success');
            errEl.classList.add('hidden');
            okEl.classList.add('hidden');

            if (!total || total <= 0)        { errEl.textContent = 'Total capacity must be > 0.'; errEl.classList.remove('hidden'); return; }
            if (isNaN(available) || available < 0) { errEl.textContent = 'Available cannot be negative.'; errEl.classList.remove('hidden'); return; }
            if (available > total)           { errEl.textContent = 'Available cannot exceed total.'; errEl.classList.remove('hidden'); return; }

            saveBtn.disabled = true;
            saveBtn.textContent = 'Saving...';
            try {
                const res  = await fetch('/capacity/update', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'same-origin',
                    body: JSON.stringify({ total_capacity: total, available_capacity: available })
                });
                let data;
                try { data = await res.json(); } catch(_) { data = {}; }
                if (res.status === 401) { errEl.textContent = 'Session expired. Please log out and log back in.'; errEl.classList.remove('hidden'); return; }
                if (res.status === 403) { errEl.textContent = 'Access denied: ' + (data.error || 'Only suppliers can set capacity.'); errEl.classList.remove('hidden'); return; }
                if (data.success) {
                    okEl.textContent = '&#x2705; ' + data.message;
                    okEl.classList.remove('hidden');
                    if (!myCompanyId) {
                        const r2 = await fetch('/api/me');
                        if (r2.ok) { const d2 = await r2.json(); myCompanyId = d2.company && d2.company.id ? d2.company.id : null; }
                    }
                    await loadCapacitySummary();
                } else {
                    errEl.textContent = '&#x274C; ' + (data.error || 'Failed to save');
                    errEl.classList.remove('hidden');
                }
            } catch (e) {
                errEl.textContent = '&#x274C; Network error. Please try again.';
                errEl.classList.remove('hidden');
            } finally {
                saveBtn.disabled = false;
                saveBtn.textContent = 'Save Capacity';
            }
        });
    }

    loadCapacitySummary();
})();
</script>
"""

ENDBLOCK = "{% endblock %}"
last_endblock = content.rfind(ENDBLOCK)
assert last_endblock != -1, "Could not find {% endblock %}"
content = content[:last_endblock] + CAPACITY_PANEL + "\n" + ENDBLOCK
print("Fix 3 applied: capacity panel added")

open(path, 'w', encoding='utf-8').write(content)
print("Done. File length:", len(content))
