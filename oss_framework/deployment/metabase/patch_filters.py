import sys
with open('add-dashboard-filters.py', 'r') as f:
    content = f.read()

content = content.replace(
    'if not client.login(args.email, args.password):',
    '''client.session_token = "d4a8a52b-0ec5-4091-af93-3dc6afaea019"
    client.headers["X-Metabase-Session"] = client.session_token
    print("Using provided session token")
    if False:'''
)

with open('add-dashboard-filters-auth.py', 'w') as f:
    f.write(content)
