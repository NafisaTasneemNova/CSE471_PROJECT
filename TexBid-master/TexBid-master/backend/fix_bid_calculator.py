"""
Fix script: replaces the broken form-based bid calculator with a
pure client-side calculator that never submits/reloads the page.
"""
import re

path = "../frontend/src/pages/supplier_dashboard.html"
content = open(path, encoding="utf-8").read()

# Find the form start and end
form_start = content.find('<form id="quoting-widget-form"')
form_end   = content.find("</form>", form_start) + len("</form>")

if form_start == -1:
    print("Form not found — already fixed or different markup.")
    exit(0)

print(f"Found form at chars {form_start}–{form_end}")

new_widget = '''                <!-- Bid Calculator — pure client-side, no form submission -->
                <div id="quoting-widget-form" class="p-5 space-y-4">

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

                <!-- Result message -->
                <div id="quote-result" class="hidden p-3 rounded-lg text-sm font-semibold text-center"></div>

                <!-- Calculate Button -->
                <button type="button" id="calc-quote-btn"
                    class="w-full flex items-center justify-center gap-2 bg-brand-primary text-white font-bold py-3 rounded-lg shadow-sm hover:bg-brand-dark transition mt-2">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 11h.01M12 11h.01M15 11h.01M4 19h16a2 2 0 002-2V7a2 2 0 00-2-2H4a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                    </svg>
                    Calculate Quote
                </button>

                <!-- AI Recommendation link -->
                <a href="/ai/recommend"
                    class="w-full flex items-center justify-center gap-2 bg-indigo-600 text-white font-bold py-2.5 rounded-lg shadow-sm hover:bg-indigo-700 transition text-sm mt-1">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
                    </svg>
                    Get AI Bid Recommendation
                </a>

                </div><!-- end quoting-widget-form div -->'''

content = content[:form_start] + new_widget + content[form_end:]

# Also fix the JS that references the old form inputs (name= → id=)
# The existing JS already uses querySelector by name, update to use getElementById
old_js = '''        const cmInput = document.querySelector('input[name="cm_cost"]');
        const fabricInput = document.querySelector('input[name="fabric_cost"]');
        const totalInput = document.getElementById('total_price');

        function calc() {
            const cm = parseFloat(cmInput.value) || 0;
            const fab = parseFloat(fabricInput.value) || 0;
            totalInput.value = (cm + fab).toFixed(2);
        }

        if (cmInput && fabricInput) {
            cmInput.addEventListener('input', calc);
            fabricInput.addEventListener('input', calc);
        }'''

new_js = '''        const cmInput = document.getElementById('cm_cost');
        const fabricInput = document.getElementById('fabric_cost');
        const totalInput = document.getElementById('total_price');

        function calc() {
            const cm = parseFloat(cmInput ? cmInput.value : 0) || 0;
            const fab = parseFloat(fabricInput ? fabricInput.value : 0) || 0;
            totalInput.value = (cm + fab).toFixed(2);
        }

        if (cmInput && fabricInput) {
            cmInput.addEventListener('input', calc);
            fabricInput.addEventListener('input', calc);
        }

        // Calculate Quote button
        const calcBtn = document.getElementById('calc-quote-btn');
        if (calcBtn) {
            calcBtn.addEventListener('click', () => {
                const cm = parseFloat(cmInput ? cmInput.value : 0) || 0;
                const fab = parseFloat(fabricInput ? fabricInput.value : 0) || 0;
                const lead = document.getElementById('lead_time') ? document.getElementById('lead_time').value : '';
                const total = cm + fab;
                const resultEl = document.getElementById('quote-result');

                if (total <= 0) {
                    resultEl.className = 'p-3 rounded-lg text-sm font-semibold text-center bg-red-50 text-red-700 border border-red-200';
                    resultEl.textContent = 'Please enter CM and Fabric costs.';
                    resultEl.classList.remove('hidden');
                    return;
                }

                resultEl.className = 'p-3 rounded-lg text-sm font-semibold text-center bg-emerald-50 text-emerald-800 border border-emerald-200';
                resultEl.innerHTML = `✅ Total Unit Price: <strong>$${total.toFixed(2)}</strong>${lead ? ` &bull; Lead Time: <strong>${lead} days</strong>` : ''}`;
                resultEl.classList.remove('hidden');
            });
        }'''

if old_js in content:
    content = content.replace(old_js, new_js)
    print("JS updated successfully")
else:
    # Try to find and replace just the querySelector lines
    content = content.replace(
        "document.querySelector('input[name=\"cm_cost\"]')",
        "document.getElementById('cm_cost')"
    )
    content = content.replace(
        "document.querySelector('input[name=\"fabric_cost\"]')",
        "document.getElementById('fabric_cost')"
    )
    print("JS partially updated (querySelector replaced)")

open(path, "w", encoding="utf-8").write(content)
print("Done — supplier_dashboard.html updated.")
