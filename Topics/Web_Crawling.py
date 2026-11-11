from fastapi import FastAPI
from bs4 import BeautifulSoup
import requests

app = FastAPI()

@app.get("/news")

def get_news():
    url = "https://indianexpress.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text,"html.parser")

    title = []

    for item in soup.find_all("aside",class_="topblockNews__sidebar"):
        title.append(item.text)

    return {
        "news":title[:5]
    }