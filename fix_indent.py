
lines = []
with open('agents/orchestrator.py', 'r') as f:
    lines = f.readlines()

# Indent lines 64 to 245 (0-indexed: 63 to 244)
# Wait, line numbers in view_file were 1-indexed.
# try is at line 63.
# Line 64 is the first line inside try.
# Line 246 is 'finally:'.
# So we need to indent lines 64 to 245 (inclusive).
# In 0-index list: index 63 to 244.

start_idx = 63 # Line 64
end_idx = 245 # Line 246 (exclusive, so up to 245)

# Verify content before proceeding
if "try:" not in lines[62]:
     print(f"Error: Line 63 expected 'try:', found: {lines[62]}")
     exit(1)

if "finally:" not in lines[246]: # Line 247 in file (view_file showed finally at 246, but I might have miscounted if I didn't see context)
    # Let's check a range
    found_finally = False
    for i in range(240, 255):
        if "finally:" in lines[i]:
            found_finally = True
            end_idx = i
            break
    if not found_finally:
         print("Error: Could not find finally block")
         exit(1)

for i in range(start_idx, end_idx):
    if lines[i].strip(): # Don't indent empty lines if not needed, but consistency is good
        lines[i] = "    " + lines[i]

with open('agents/orchestrator.py', 'w') as f:
    f.writelines(lines)

print("Indentation fixed.")
