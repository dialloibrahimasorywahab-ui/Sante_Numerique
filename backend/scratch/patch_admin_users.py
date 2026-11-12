import re

path_html = r"c:\Users\Ibrahima Sory\Desktop\Sante\Sante_Numerique\frontend\src\app\features\admin\pages\users\admin-users.component.html"
with open(path_html, "r", encoding="utf-8") as f:
    content = f.read()

# Wrap tables with table-responsive if not already wrapped
# We can replace <table class="data-table"> with <div class="table-responsive"><table class="data-table">
# and </table> with </table></div> (carefully where not already closed with div)

if '<div class="table-responsive">' not in content:
    # Match each <table class="data-table">...</table> block
    def wrap_table(match):
        return f'<div class="table-responsive">\n        {match.group(0)}\n      </div>'
    
    content = re.sub(r'<table class="data-table">[\s\S]*?</table>', wrap_table, content)
    with open(path_html, "w", encoding="utf-8") as f:
        f.write(content)
    print("Wrapped tables in admin-users.component.html")
else:
    print("Tables already wrapped in admin-users.component.html")

# Now check admin-users.component.scss
path_scss = r"c:\Users\Ibrahima Sory\Desktop\Sante\Sante_Numerique\frontend\src\app\features\admin\pages\users\admin-users.component.scss"
with open(path_scss, "r", encoding="utf-8") as f:
    scss = f.read()

# Add responsive adjustments if needed
if ".data-table {" in scss and "min-width:" not in scss:
    scss = scss.replace(".data-table {", ".data-table {\n  min-width: 720px;\n")
    with open(path_scss, "w", encoding="utf-8") as f:
        f.write(scss)
    print("Added min-width to data-table in admin-users.component.scss")

