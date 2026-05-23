import re
import json

with open("templates/courses/dashboard.html", "r") as f:
    content = f.read()

# Extract Style
style_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
style_content = style_match.group(1) if style_match else ""

# Extract Script
script_match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
script_content = script_match.group(1) if script_match else ""

# Extract Body elements (excluding script)
# First strip script tag from content
content_no_script = re.sub(r'<script>.*?</script>', '', content, flags=re.DOTALL)
body_match = re.search(r'<body>(.*?)</body>', content_no_script, re.DOTALL)
body_content = body_match.group(1) if body_match else ""

# Replace Hardcoded data in body
body_content = body_content.replace(
    '<h1>Welcome back, Arjun</h1>', 
    '<h1>Welcome back, {{ user.first_name|default:user.username }}</h1>'
)

body_content = body_content.replace(
    '<span style="font-family:var(--ff-mono);font-size:11px;color:var(--text3)">Updated 18:42</span>',
    '<span style="font-family:var(--ff-mono);font-size:11px;color:var(--text3)">Updated {{ last_updated|date:"H:i" }}</span>'
)

body_content = body_content.replace(
    '<p class="tagline">Keep up the momentum · 3 courses in progress</p>',
    '<p class="tagline">Keep up the momentum · {{ total_courses }} courses in progress</p>'
)

# In script, replace COURSES = [...] with Django JSON integration
script_content = re.sub(
    r'const COURSES = \[.*?\];',
    'const COURSES = JSON.parse(\'{{ courses_json|escapejs }}\');',
    script_content,
    flags=re.DOTALL
)

# Replace countTo default targets in JS, wait, the script does:
# countTo(document.getElementById('kpi-streak'), 19, 0, '', 900);
# countTo(document.getElementById('kpi-courses'), 5, 0, '', 1000);
# countTo(document.getElementById('kpi-hours'), 14, 1, '<span class="unit">h</span>', 1100);
# countTo(document.getElementById('kpi-mastered'), 2, 0, '', 1200);
script_content = re.sub(
    r"countTo\(document\.getElementById\('kpi-streak'\), \d+,",
    r"countTo(document.getElementById('kpi-streak'), {{ profile.streak_count }},",
    script_content
)
script_content = re.sub(
    r"countTo\(document\.getElementById\('kpi-courses'\), \d+,",
    r"countTo(document.getElementById('kpi-courses'), {{ total_courses }},",
    script_content
)
script_content = re.sub(
    r"countTo\(document\.getElementById\('kpi-hours'\), \d+,",
    r"countTo(document.getElementById('kpi-hours'), {{ weekly_hours }},",
    script_content
)
script_content = re.sub(
    r"countTo\(document\.getElementById\('kpi-mastered'\), \d+,",
    r"countTo(document.getElementById('kpi-mastered'), {{ completed_courses }},",
    script_content
)

# Heatmap replacement
# In JS, the heatmap data is currently generated randomly/statically.
# The user's heatmap from views.py is `streak_grid`. We should inject this.
script_content = re.sub(
    r'const levels = \[.*?\];',
    'const streakGrid = JSON.parse(\'{{ streak_grid_json|escapejs }}\');\n            const levels = streakGrid.map(d => d.level);',
    script_content,
    flags=re.DOTALL
)

new_template = f"""{{% extends 'courses/base.html' %}}

{{% block extra_head %}}
<link
    href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=Syne:wght@400;500;600;700;800&display=swap"
    rel="stylesheet">
<style>
{style_content}
</style>
{{% endblock %}}

{{% block content %}}
{body_content}
{{% endblock %}}

{{% block extra_js %}}
<script>
{script_content}
</script>
{{% endblock %}}
"""

with open("templates/courses/dashboard.html", "w") as f:
    f.write(new_template)

print("dashboard.html successfully transformed!")
