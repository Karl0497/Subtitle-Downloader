import sys
import requests, zipfile, io
from bs4 import BeautifulSoup
from threading import Thread
import time
class Subtitle:
    def __init__(self,tag,name):
        spans = tag.find_all("span")

        self.tag=tag
        self.language = spans[0].text.strip().lower()
        self.title = spans[1].text.strip().lower()
        self.owner = tag.find("td","a5").text.strip().lower()
        self.point = calculatePoint(self.title,name)
        self.link = "https://subscene.com"+tag.find("a")["href"]
    def __repr__(self):
        return self.language+' '+self.title+' '+self.owner+' '+str(self.point)

def getFileName(path):
    dot = path.rfind(".")
    if dot==-1: return None
    slash = path.rfind("/")
    directory = path[:slash+1]
    return directory,path[slash+1:dot]

def calculatePoint(s1,s2): 
    def s(a,b):
        if a==b: return 1
        return -1
    gap_penalty = 1

    points = [[None for i in range(len(s1)+1)] for j in range(len(s2)+1)]
    for i in range(len(s1)+1):
        points[0][i]=-gap_penalty*i
    for i in range(len(s2)+1):
        points[i][0]=-gap_penalty*i

    for i in range(1,len(s2)+1):
        for j in range(1,len(s1)+1):
            points[i][j]=max(points[i-1][j-1]+s(s2[i-1],s1[j-1]),points[i-1][j]-gap_penalty,points[i][j-1]-gap_penalty)
    return points[len(s2)][len(s1)]

def getSubtitle(name, count=5):
    url="https://subscene.com/subtitles/release?q="+name
    result = requests.get(url).content
    soup=BeautifulSoup(result, "html5lib")

    #when the following div is found, it means there is no result for the current query
    search_result = soup.find("div",{"class":"search-result"})
    if search_result:
        return None

    table=soup.find("tbody")

    #if the table is not found, the website is blocking the script. Request again in 1 second
    if not table:
        time.sleep(1)
        return getSubtitle(name,count+1)


    tr_list=table.find_all("tr") 
    sub_list = [Subtitle(i,name) for i in tr_list]
    sub_list = [i for i in sub_list if i.language=="english"]
    return max(sub_list,key=lambda x: x.point)

def downloadSubtitle(s,name,dir):
    r = requests.get(s.link).content
    soup=BeautifulSoup(r,"html5lib")
    downloadLink = "https://subscene.com"+soup.find("a",{"id":"downloadButton"})["href"]
    r = requests.get(downloadLink).content
    zip = zipfile.ZipFile(io.BytesIO(r))

    #This is to rename the file
    #print("Extracting subtitle")
    target_path = dir + name + ".srt"
    file= zip.read(zip.namelist()[0]) #Only extract the first file
    print("Done",name)
    with open(target_path,"wb") as f:
        f.write(file)

def processPath(path):
    
    path=path.replace("\\","/")
    dir,fileName= getFileName(path)
    print("Processing file:",fileName)
    if not fileName: 
        print("Invalid file")
        return   
    #print("Getting subtitles")
    subtitle = getSubtitle(fileName.lower())
    if not subtitle:
        print("No subtitle found")
        return
    #print("Downloading subtitle")
    downloadSubtitle(subtitle,fileName,dir)
def main():
    pool = [Thread(target=processPath,kwargs={'path':path}) for path in sys.argv[1:]]
    for thread in pool:
        thread.start()
    for thread in pool:
        thread.join()
    input()
   
if __name__ == '__main__':
    main()
