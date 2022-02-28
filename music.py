import os, sys, time, threading

ROOT = "/storage/emulated/0/"
songs = []
isAnimate = True


def red(s):
  return f"\033[1;31;40m{s}\033[1;37;40m"
  
def getName(path):
  return path.split("/")[-1]

def listAll(i, root, p):
  album = root.split("/")[-1]
  print(f"[{i}] {album} - {p}")
  
def listAlbums():
  os.system("clear")
  global songs
  j = 0
  albums = []
  
  for song in songs:
    album = song.split("/")[-2]
    
    if album not in albums:
      j += 1
      albums.append(album)
      print(f"{red('[')}{j}{red(']')} {album}")
   
  thisAlbum = []
  album = albums[int(input(">> ")) - 1]
  j = 0
  os.system("clear")
  
  for song in songs:
    if album == song.split("/")[-2]:
      j += 1
      thisAlbum.append(song)
      print(f"{red('[')}{j}{red(']')} {getName(song)}")
      
  song = thisAlbum[int(input(">> ")) - 1]
  
  os.system("clear")
  print()
  print(f"{getName(song)}")
  os.system(f"echo Duration: $(soxi -d '{song}')")
  os.system(f"echo Bitrate: $(soxi -r '{song}')Hz")
  os.system(f"play '{song}' -q")# &> /dev/null &")

def fetchAnimation():
  while True:
    for i in range(len(list("fetcheing all songs."))):
      string = list("fetcheing all songs.")
      string[i] = string[i].upper()
      string = ''.join(string)
      print(f"{string}", end="\r")
      time.sleep(0.5)
      
      if isAnimate == False:
        string = ""
        print("", end="\r")
        break
    
    if isAnimate == False:
      print("", end="\r")
      print(">> ")
      break
      
def visualizerAnimation():
  while True:
    print("", end="\r")

def fetchAll():
  global isAnimate
  for (root, dir, path) in os.walk(ROOT):
    for p in path:
      if p.endswith((".mp3") or (".m4a") or (".wav")):
        songs.append(f"{root}/{p}")
        
  isAnimate = False
      

thread = threading.Thread(target=fetchAnimation)
thread.start()

os.system("sox --version > /dev/null 2&>1 || apt install sox > /dev/null 2&>1")
fetchAll()
listAlbums()