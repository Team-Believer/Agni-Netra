import re

with open('backend/app/seed.py', 'r') as f:
    content = f.read()

replacements = {
    'ev_a': '"/agri_fire_1.jpg"',
    'ev_b': '"/ind_fire_korba.jpg"',
    'ev_c': '"/forest_fire_1.jpg"',
    'ev_d': '"/agri_fire_2.jpg"',
    'ev_f': '"/ind_anomaly.jpg"',
    'ev_g': '"/agri_fire_3.jpg"',
    'ev_h': '"/routine_flare.jpg"',
    'ev_i': '"/forest_fire_2.jpg"',
    'ev_j': '"/port_smoldering.jpg"',
    'ev_k': '"/coal_fire.jpg"',
    'ev_l': '"/landfill_fire.jpg"'
}

for var, img in replacements.items():
    pattern = r'(' + var + r'\s*=\s*Event\([\s\S]*?satellite_image_url=)(".*?"|None)'
    content = re.sub(pattern, r'\g<1>' + img, content)

with open('backend/app/seed.py', 'w') as f:
    f.write(content)

print('Updated seed.py')
