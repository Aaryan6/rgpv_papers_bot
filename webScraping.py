import requests
from bs4 import BeautifulSoup


async def getAllLinks(search_text, url):
    response = requests.get(url)
    if response.status_code != 200:
        print(
            f"Failed to fetch data from url. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a")

    if links:
        links_arr = []
        for link in links:
            fileUrl = link.get("href")
            if (fileUrl.startswith("https://www.rgpvonline.com/be") and fileUrl.endswith(".html")):
                links_arr.append(fileUrl.split(".")[2].split("/")[2])

        matching_items = [item for item in links_arr if all(
            word.lower() in item.lower() for word in search_text.split())]

        if len(matching_items) == 0:
            return "Not found!\nMaybe there is no file\ntry with any different name."
        else:
            return matching_items
    else:
        return "Not found!"
