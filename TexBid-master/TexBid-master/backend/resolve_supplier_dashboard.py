"""
Resolves all 6 conflicts in supplier_dashboard.html.
Strategy: keep both sides for all conflicts since they add different features.
Special handling for conflict 6 (endblock placement).
"""
import re

path = 'TexBid-master/TexBid-master/frontend/src/pages/supplier_dashboard.html'
content = open(path, encoding='utf-8').read()

pattern = re.compile(r'<{7}[^\n]*\n(.*?)={7}\n(.*?)>{7}[^\n]*\n', re.DOTALL)
conflicts = list(pattern.finditer(content))
print(f"Found {len(conflicts)} conflicts")

# Process conflicts in reverse order to preserve positions
result = content
for i, m in reversed(list(enumerate(conflicts))):
    ours   = m.group(1)
    theirs = m.group(2)

    if i == 5:
        # Conflict 6: ours = capacity panel, theirs = shipping modal include + endblock
        # Keep capacity panel BEFORE the shipping modal include and endblock
        # theirs ends with {% endblock %} — we need that
        merged = ours.rstrip('\n') + '\n\n' + theirs
    elif i == 4:
        # Conflict 5: ours = drag widget JS end, theirs = widget minimize/drag JS
        # Keep ours (drag end) then theirs (minimize/drag)
        merged = ours.rstrip('\n') + '\n\n' + theirs
    elif i == 3:
        # Conflict 4: ours = auto-calc JS, theirs = tab switching JS
        # Keep both JS blocks
        merged = ours.rstrip('\n') + '\n\n' + theirs
    elif i == 2:
        # Conflict 3: ours = Lead Time + Calculate button, theirs = Submit Bid button
        # Keep both
        merged = ours.rstrip('\n') + '\n\n' + theirs
    elif i == 1:
        # Conflict 2: ours = fabric_cost input, theirs = bid-price-input
        # Keep both inputs
        merged = ours.rstrip('\n') + '\n\n' + theirs
    else:
        # Conflict 1: ours = quoting widget div, theirs = same div with blue banner
        # Theirs has a blue info banner at top — prepend it to ours
        # Extract the banner from theirs
        banner_match = re.search(r'<div class="bg-blue-50.*?</div>', theirs, re.DOTALL)
        if banner_match:
            banner = banner_match.group(0)
            merged = '\n' + banner + '\n' + ours
        else:
            merged = ours.rstrip('\n') + '\n\n' + theirs

    result = result[:m.start()] + merged + result[m.end():]

remaining = result.count('<<<<<<<')
print(f"Remaining conflict markers: {remaining}")

open(path, 'w', encoding='utf-8').write(result)
print("supplier_dashboard.html resolved")
