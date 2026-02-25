import sys
import re

with open('add-dashboard-filters-auth.py', 'r') as f:
    content = f.read()

content = content.replace('dashboard_id = 1', 'dashboard_id = 32')
content = content.replace('dashboard_id = 2', 'dashboard_id = 33')
content = content.replace('dashboard_id = 3', 'dashboard_id = 34')
content = content.replace('dashboard_id = 4', 'dashboard_id = 35')
content = content.replace('dashboard_id = 5', 'dashboard_id = 36')

with open('add-dashboard-filters-auth-fixed.py', 'w') as f:
    f.write(content)
