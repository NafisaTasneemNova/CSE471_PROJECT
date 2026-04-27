"""
Resolves the 2 conflicts in TexBid-master/TexBid-master/backend/main.py:

Conflict 1 (imports):
  OURS:   our models import (without new Mehjabin models) + auth imports
  THEIRS: Mehjabin's models import (with PaymentModel, ContractModel, etc.) but no auth
  RESOLUTION: merge both import lines + keep auth imports

Conflict 2 (feature sections):
  OURS:   empty section marker (our features are appended at the end of the file)
  THEIRS: Mehjabin's rating system (duplicate of ours, already in our file)
  RESOLUTION: keep OURS (empty marker) — our full feature code is already at the end
"""
import re

path = 'TexBid-master/TexBid-master/backend/main.py'
content = open(path, encoding='utf-8').read()

pattern = re.compile(r'<{7}[^\n]*\n(.*?)={7}\n(.*?)>{7}[^\n]*\n', re.DOTALL)
conflicts = list(pattern.finditer(content))

print(f"Found {len(conflicts)} conflicts")

# --- Conflict 1: imports ---
c1 = conflicts[0]
ours_imports   = c1.group(1).strip()
theirs_imports = c1.group(2).strip()

# Extract the new model names Mehjabin adds that we don't have
# Our line ends at NotificationTypeEnum, theirs continues with more
# Find the extra models in theirs
our_models_line = [l for l in ours_imports.split('\n') if l.startswith('from models import')][0]
their_models_line = [l for l in theirs_imports.split('\n') if l.startswith('from models import')][0]

# Get the extra imports from theirs
our_models_end = our_models_line.rstrip()
their_models_end = their_models_line.rstrip()

# Find what theirs has that ours doesn't
our_names = set(n.strip() for n in our_models_end.replace('from models import', '').split(','))
their_names = set(n.strip() for n in their_models_end.replace('from models import', '').split(','))
extra_names = their_names - our_names
print(f"Extra model imports from Mehjabin: {extra_names}")

# Build merged import line
if extra_names:
    merged_models_line = our_models_end + ', ' + ', '.join(sorted(extra_names))
else:
    merged_models_line = our_models_end

# Build the merged imports block: merged models line + auth imports from ours
auth_imports = '\n'.join(l for l in ours_imports.split('\n') if 'auth' in l or 'from auth' in l)

merged_imports = merged_models_line + '\n' + auth_imports

print("Merged imports block:")
print(merged_imports[:300])

# --- Conflict 2: feature sections ---
# OURS is empty (our features are at the end of the file already)
# THEIRS has a duplicate rating system — keep OURS (empty)
c2 = conflicts[1]
ours_section   = c2.group(1)
theirs_section = c2.group(2)

# Keep ours (empty section marker), discard theirs (duplicate)
merged_section = ours_section

# Apply resolutions
result = content
# Replace conflict 2 first (work backwards to preserve positions)
result = result[:c2.start()] + merged_section + result[c2.end():]
# Now find conflict 1 again in the updated content
c1_new = list(re.finditer(r'<{7}[^\n]*\n(.*?)={7}\n(.*?)>{7}[^\n]*\n', result, re.DOTALL))[0]
result = result[:c1_new.start()] + merged_imports + '\n' + result[c1_new.end():]

remaining = result.count('<<<<<<<')
print(f"Remaining conflict markers: {remaining}")

open(path, 'w', encoding='utf-8').write(result)
print("main.py conflicts resolved")
