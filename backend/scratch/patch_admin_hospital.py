import re

path_html = r"c:\Users\Ibrahima Sory\Desktop\Sante\Sante_Numerique\frontend\src\app\features\admin\pages\hospital\admin-hospital.component.html"
with open(path_html, "r", encoding="utf-8") as f:
    content = f.read()

# Replace emojis with SVGs
svg_hospital = """<svg class="w-4 h-4 text-emerald-600 inline" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg>"""
svg_building = """<svg class="w-4 h-4 text-blue-600 inline" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z"/></svg>"""
svg_bed = """<svg class="w-4 h-4 text-teal-600 inline" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-9 2h18a1 1 0 001-1V5a1 1 0 00-1-1H3a1 1 0 00-1 1v14a1 1 0 001 1z"/></svg>"""

content = content.replace("🏥", svg_hospital)
content = content.replace("🏢", svg_building)
content = content.replace("🛏️", svg_bed)

if '<div class="table-responsive">' not in content:
    def wrap_table(match):
        return f'<div class="table-responsive">\n        {match.group(0)}\n      </div>'
    content = re.sub(r'<table class="data-table">[\s\S]*?</table>', wrap_table, content)
    print("Wrapped tables in admin-hospital.component.html")

with open(path_html, "w", encoding="utf-8") as f:
    f.write(content)

path_scss = r"c:\Users\Ibrahima Sory\Desktop\Sante\Sante_Numerique\frontend\src\app\features\admin\pages\hospital\admin-hospital.component.scss"
with open(path_scss, "r", encoding="utf-8") as f:
    scss = f.read()

if ".data-table {" in scss and "min-width:" not in scss:
    scss = scss.replace(".data-table {", ".data-table {\n  min-width: 680px;\n")
    with open(path_scss, "w", encoding="utf-8") as f:
        f.write(scss)
    print("Added min-width to data-table in admin-hospital.component.scss")

