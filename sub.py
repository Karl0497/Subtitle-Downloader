import sys
import requests, zipfile, io, os
from bs4 import BeautifulSoup
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
        #return self.link
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
def getFullPath():
    droppedFile = sys.argv[1]
    droppedFile=droppedFile.replace("\\","/")
    return droppedFile
def getSubtitle(name):
    url="https://subscene.com/subtitles/release?q="+name
    result = requests.get(url).content
    soup=BeautifulSoup(result, "html5lib")
    table=soup.find("tbody")
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
    print("Extracting subtitle")
    target_path = dir + name + ".srt"
    file= zip.read(zip.namelist()[0]) #Only extract the first file
    print(target_path)
    with open(target_path,"wb") as f:
        f.write(file)

def main():
    print("Processing file")
    path=getFullPath()
    dir,fileName= getFileName(path)
    if not fileName: 
        print("Invalid file")
        return
    
    print("Getting subtitles")
    subtitle = getSubtitle(fileName.lower())


    print("Downloading subtitle")
    downloadSubtitle(subtitle,fileName,dir)
if __name__ == '__main__':
    main()
