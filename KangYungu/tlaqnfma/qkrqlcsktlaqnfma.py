detail_urls = []

with open("message.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        if "→" in line:
            name, url = line.split("→", 1)
            name = name.strip()
            url = url.strip()
            if url.lower() == "none":
                url = None
            detail_urls.append((name, url))

print("detail_urls = [")
for item in detail_urls:
    print(f"    {item},")
print("]")