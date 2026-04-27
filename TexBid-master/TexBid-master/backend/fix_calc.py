path = 'TexBid-master/TexBid-master/frontend/src/pages/supplier_dashboard.html'
content = open(path, encoding='utf-8').read()

form_tag = 'quoting-widget-form'
form_start = content.find('<form id="' + form_tag + '"')
form_end   = content.find('</form>', form_start) + len('</form>')

print(f'Form found: {form_start != -1}, chars {form_start} to {form_end}')

new_widget = '''                <div id="quoting-widget-form" class="p-5 space-y-4">

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

                <div>
                    <label class="block text-xs font-bold text-slate-600 mb-1">Estimated Lead Time (Days)</label>
                    <input type="number" id="lead_time"
                        class="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-primary focus:ring-1 focus:ring-brand-primary"
                        placeholder="e.g. 45">
                </div>

                <div id="quote-result" class="hidden p-3 rounded-lg text-sm font-semibold text-center"></div>

                <button type="button" id="calc-quote-btn"
                    class="w-full flex items-center justify-center gap-2 bg-brand-primary text-white font-bold py-3 rounded-lg shadow-sm hover:bg-brand-dark transition mt-2">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 11h.01M12 11h.01M15 11h.01M4 19h16a2 2 0 002-2V7a2 2 0 00-2-2H4a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                    </svg>
                    Calculate Quote
                </button>

                <a href="/ai/recommend"
                    class="w-full flex items-center justify-center gap-2 bg-indigo-600 text-white font-bold py-2.5 rounded-lg shadow-sm hover:bg-indigo-700 transition text-sm mt-1">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
                    </svg>
                    Get AI Bid Recommendation
                </a>

                </div>'''

content = content[:form_start] + new_widget + content[form_end:]

# Fix the JS - replace querySelector with getElementById and add Calculate button handler
old_js_marker = "document.querySelector('input[name=\"cm_cost\"]')"
new_js_marker  = "document.getElementById('cm_cost')"
content = content.replace(old_js_marker, new_js_marker)

old_js_marker2 = "document.querySelector('input[name=\"fabric_cost\"]')"
new_js_marker2  = "document.getElementById('fabric_cost')"
content = content.replace(old_js_marker2, new_js_marker2)

# Add the Calculate button handler after the existing calc() setup
calc_handler = """
        // Calculate Quote button handler
        const calcBtn = document.getElementById('calc-quote-btn');
        if (calcBtn) {
            calcBtn.addEventListener('click', () => {
                const cm = parseFloat(document.getElementById('cm_cost') ? document.getElementById('cm_cost').value : 0) || 0;
                const fab = parseFloat(document.getElementById('fabric_cost') ? document.getElementById('fabric_cost').value : 0) || 0;
                const leadEl = document.getElementById('lead_time');
                const lead = leadEl ? leadEl.value : '';
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
                resultEl.innerHTML = '&#x2705; Total: <strong>$' + total.toFixed(2) + '/unit</strong>' + (lead ? ' &bull; Lead: <strong>' + lead + ' days</strong>' : '');
                resultEl.classList.remove('hidden');
            });
        }
"""

# Insert after the existing drag/minimize widget logic
insert_after = "        if (cmInput && fabricInput) {\n            cmInput.addEventListener('input', calc);\n            fabricInput.addEventListener('input', calc);\n        }"
if insert_after in content:
    content = content.replace(insert_after, insert_after + calc_handler)
    print("Calculate button handler inserted")
else:
    print("WARNING: Could not find insertion point for calc handler — appending before </script>")
    # Find the first </script> after the quoting widget JS
    js_start = content.find("// Extremely basic auto-calc")
    script_end = content.find("</script>", js_start)
    content = content[:script_end] + calc_handler + content[script_end:]

open(path, 'w', encoding='utf-8').write(content)
print("Done — supplier_dashboard.html fixed.")
