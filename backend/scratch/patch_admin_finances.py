import re

path_html = r"c:\Users\Ibrahima Sory\Desktop\Sante\Sante_Numerique\frontend\src\app\features\admin\pages\finances\admin-finances.component.html"
with open(path_html, "r", encoding="utf-8") as f:
    content = f.read()

if '<div class="table-responsive">' not in content:
    def wrap_table(match):
        return f'<div class="table-responsive">\n        {match.group(0)}\n      </div>'
    content = re.sub(r'<table class="data-table">[\s\S]*?</table>', wrap_table, content)
    with open(path_html, "w", encoding="utf-8") as f:
        f.write(content)
    print("Wrapped table in admin-finances.component.html")

path_scss = r"c:\Users\Ibrahima Sory\Desktop\Sante\Sante_Numerique\frontend\src\app\features\admin\pages\finances\admin-finances.component.scss"
with open(path_scss, "r", encoding="utf-8") as f:
    scss = f.read()

if ".data-table {" in scss and "min-width:" not in scss:
    scss = scss.replace(".data-table {", ".data-table {\n  min-width: 680px;\n")
    with open(path_scss, "w", encoding="utf-8") as f:
        f.write(scss)
    print("Added min-width to data-table in admin-finances.component.scss")

