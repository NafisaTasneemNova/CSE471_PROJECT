with open(r'd:\TexBid_motiur\backend\main.py', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        s = line.strip()
        if s.startswith('@app.'):
            print(f'{i}: {s}')
