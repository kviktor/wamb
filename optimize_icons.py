from pathlib import Path
import re

import httpx2

ICON_REGEX = re.compile(r"<i>([a-zA-Z0-9_]+)</i>")
URL_REGEX = re.compile(r"src: url\((.*)\) format")

templates = []
for root, _, files in Path("app/").walk():
    for name in files:
        if not name.endswith(".html"):
            continue
        templates.append(f"{root}/{name}")

#
icon_names = {
    "auto_stories",  # has some extra classes
    "photo",  # these 2 are from Python
    "table",
    "check",  # scan.js + yesno filter
    "close",
    "dangerous",  # scan.js
}
for template in templates:
    with open(template) as f:
        content = f.read()
        icon_names |= set(re.findall(ICON_REGEX, content))

print("Found the following icons in code", icon_names)

fonts = ["material-symbols-outlined", "material-symbols-rounded", "material-symbols-sharp"]

for font in fonts:
    print(font, end="")
    response = httpx2.get(
        "https://fonts.googleapis.com/css2",
        params={
            "family": " ".join([f"{p[0].upper()}{p[1:]}" for p in font.split("-")]),
            "icon_names": ",".join(list(icon_names)),
        },
    )
    response.raise_for_status()
    print(".", end="")

    font_url = re.search(URL_REGEX, response.text).group(1)

    font_response = httpx2.get(font_url)
    print(".", end="")

    with open(f"app/static/css/{font}.woff2", "wb") as f:
        f.write(font_response.read())
        print(".", end="")

    print("")
