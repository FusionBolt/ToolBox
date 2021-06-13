import json
from bs4 import BeautifulSoup
import requests
import logging
import pandas as pd

logging.basicConfig(filename="YoutubeVideoListData.log", filemode="w+", level=logging.INFO)
proxies = {
"http":"http://127.0.0.1:1087",
"https":"https://127.0.0.1:1087"}

# Continuation
def findCToken(html:str):
    href = ""
    for i in BeautifulSoup(html, "html.parser").find_all("button", class_="yt-uix-button yt-uix-button-size-default yt-uix-button-default load-more-button yt-uix-load-more browse-items-load-more-button"):
        href = i["data-uix-load-more-href"]
    for i in href.split("&"):
        if i.startswith("continuation"):
            return i.replace("continuation=","")
    return ""

def processData(html:str):
    videoDatas = []
    for i in BeautifulSoup(html, "html.parser").find_all("li", class_="channels-content-item yt-shelf-grid-item"):
        videoData = {}
        node = i.find("div", class_="yt-lockup-thumbnail").span
        videoData["link"] = node.a["href"]
        videoData["duration"] = node.find("span", class_="video-time").span.get_text()
        contentNode = i.find("div", class_="yt-lockup-content")
        videoData["title"] = contentNode.h3.a["title"]
        info = contentNode.div.ul.li
        videoData["watchCount"] = info.get_text()
        videoData["pushTime"] = info.next_sibling.get_text()        
        videoDatas.append(videoData)
        # TODO: cover img
        # TODO: precision pushTime(enter play page get)
        # logging.info(f"link:{link}, duration:{duration}, title:{title}, watchCount:{watchCount}, pushTime:{pushTime}")
    return videoDatas

def computeSecondsByTimeStr(time:str):
    times = [int(i) for i in time.split(":")]
    if len(times) == 3:
        return times[0] * 3600 + times[1] * 60 + times[2]
    elif len(times) == 2:
        return times[0] * 60 + times[1]
    elif len(times) == 1:
        return times[0]
    else:
        raise "ErrorTimeFormat"

if __name__ == "__main__":
    videoDatas = []
    channelId = ""   
    resultText = requests.get("https://www.youtube.com/channel/" + channelId + "/videos", proxies=proxies).text

    videoDatas += processData(resultText)
    ctoken = findCToken(resultText)
    logging.info(resultText)

    while ctoken != "":
        print(ctoken)
        try:
            r = requests.get(f"https://www.youtube.com/browse_ajax?ctoken={ctoken}", proxies=proxies).text
            jsonData = json.loads(r)
            videoDatas += processData(jsonData["content_html"])
            # with open(f"newresult{count}.html", "w+") as f:
            #     f.write(jsonData["content_html"])
            ctoken = findCToken(jsonData["load_more_widget_html"])
            #TODO:fmt
        except Exception as e:
            logging.error("response info:%s, error info:%s"%(r, str(e)))

    pd.DataFrame(videoDatas).to_csv("videoDatas.csv")
    sumDuration = sum([computeSecondsByTimeStr(data["duration"]) for data in videoDatas])
    print(len(videoDatas))
    print(sumDuration/3600)