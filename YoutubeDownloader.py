from datetime import datetime
from tkinter.ttk import Progressbar
import webbrowser
from Player import Player
import configparser
from tkinter import *
from tkinter import messagebox, filedialog
import tkinter.font as font
import os
import pytube
import requests
import speech_recognition as sr
import threading
from pytube import Search
config_file = "configuration_default.txt"
log_file = "logs.txt"

class YoutubeDownloader(Frame):
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(config_file, "UTF-8")
        self.parent = Tk()
        self.parent.geometry(self.config["DEFAULT"].get("geometry", "835x432+50+50"))
        self.parent.update()
        self.parent.title(" Youtube Downloader")
        self.parent.iconphoto(False, PhotoImage(file = "./icons/player.png"))
        self.parent.protocol("WM_DELETE_WINDOW", self.quit)
        Frame.__init__(self, self.parent)
        self.createMenuBar()
        self.parent.rowconfigure(0, weight = 9999)
        self.parent.rowconfigure(1, weight = 1)
        self.parent.columnconfigure(0, weight = 9999)
        self.parent.columnconfigure(1, weight = 1)
        self.createStatusBar()
        self.frame = Frame(self.parent, height = 250, width = 835)
        self.frame.place(x = 0, y = 0)
        self.createTools()
        self.foundVideoTittle = Label(self.frame)
        self.foundVideoViews = Label(self.frame)
        self.buttonPreview = Button(self.frame)
        self.buttonDownload = Button(self.frame)
        self.progressBar = Progressbar(self.frame, orient = HORIZONTAL, length = 100, mode = "determinate", value = 0)
        self.progressPercentage = Label(self.frame)
        self.player = None
        self.url = None
        self.mediaToDownload = None
        self.mediaTitle = None
        self.logs = ""
        self.currentKeyWord = None
        self.parent.mainloop()
    def createMenuBar(self):
        # File section
        self.menuBar = Menu(self.parent) 
        self.parent["menu"] = self.menuBar
        fileMenu = Menu(self.menuBar)
        for label, command, shortcut_text, shortcut in (
                ("Open media player", self.openPlayer, "Ctrl+O", "<Control-o>"),                
                (None, None, None, None),
                ("Quit", self.quit, "Ctrl+Q", "<Control-q>")):
            if label is None:
                fileMenu.add_separator()
            else:
                fileMenu.add_command(label=label, underline=0,
                        command=command, accelerator=shortcut_text)
                self.parent.bind(shortcut, command)
        self.menuBar.add_cascade(label="Open", menu=fileMenu, underline=0) 

        # Help section
        fileMenu = Menu(self.menuBar)
        for label, command, shortcut_text, shortcut in (
                ("Email...", self.sendEmail, "Ctrl+E", "<Control-e>"),
                (None, None, None, None),
                ("Quit", self.quit, "Ctrl+Q", "<Control-q>")):
            if label is None:
                fileMenu.add_separator()
            else:
                fileMenu.add_command(label=label, underline=0,
                        command=command, accelerator=shortcut_text)
                self.parent.bind(shortcut, command)
        self.menuBar.add_cascade(label="Help", menu=fileMenu, underline=0) 
    def createStatusBar(self):
        self.statusBar = Label(self.parent, text = "Welcome to Youtube Downloader!\tContact: 257795@student.pwr.edu.pl", bg = "#C0C0C0", anchor = W)
        self.statusBar.grid(row = 1, column = 0, sticky = EW)
    def sendEmail(self, event = None):
        webbrowser.open("mailto:?to=257795@student.pwr.edu.pl&subject=Youtube Downloader", new=1)        
    def openPlayer(self, event = None):
        self.player = Player()
    def quit(self, event = None):
        reply = messagebox.askyesno(
                        "Quit",
                        "Are you sure to quit?", parent=self.parent)
        if reply:
            # Saving new window's parameteres
            geometry = self.parent.winfo_geometry()
            self.config["DEFAULT"]["geometry"] = geometry
            with open(config_file, "w") as f:
                self.config.write(f)
            # Writing user logs
            with open (log_file, "a") as f:
                f.write(self.logs)
            self.parent.destroy()
    def createTools(self):
        self.buttonIcons = dict() # A dictionary to save button icons
        # Search bar of length 30
        self.searchBar = Entry(self.frame, width = 30)
        self.searchBar["font"] = font.Font(size = 25)
        self.searchBar.place(x = 100, y = 100)
        # Button Find
        buttonFind = Button(self.frame, text = "Find", command = self.addSearchThread)
        buttonFind["font"] = font.Font(size = 18)
        buttonFind.place(x = 655, y = 95)
        # Button Voice
        iconVoice = PhotoImage(file = "./icons/voice.png")
        self.buttonIcons["voice"] = iconVoice
        buttonVoice = Button(self.frame, image = self.buttonIcons["voice"], command = self.addVoiceThread)
        buttonVoice.place(x = 750, y = 95)
    def checkOnline(self):
        # Checking online by pinging to Youtube, using API request
        url = "https://www.youtube.com"
        timeout = 2
        try:
            request = requests.get(url, timeout=timeout)
        except (requests.ConnectionError, requests.Timeout) as exception:
            messagebox.showwarning("Internet", "No internet connection!")
            self.clearFoundMedia("")
            return False
        return True
    def clearFoundMedia(self, status):
        # Clearing currently found media before finding new one
        self.foundVideoTittle.place_forget()
        self.foundVideoViews.place_forget()
        self.buttonDownload.place_forget()
        self.buttonPreview.place_forget()
        self.progressBar.place_forget()
        self.progressPercentage.place_forget()
        self.foundVideoTittle.config(text = status)
        self.foundVideoTittle["font"] = font.Font(size = 15)
        self.foundVideoTittle.place(x = 100, y = 150)
    def searchYoutube(self):
        if self.searchBar.get() and self.checkOnline():
            self.clearFoundMedia("Searching...")
            keyword = self.searchBar.get()
            self.logs += datetime.now().strftime("%d-%m-%Y %H:%M:%S: ") + keyword + "\n"
            
            if keyword.find("http") != -1:
                # Setting url directly from keyword if it is a link
                self.url = keyword
            else:
                # If click again button find with the same keyword, another most matched video shows up
                if self.currentKeyWord == keyword:
                    self.url = "https://www.youtube.com/watch?v="  + self.currentIDs[self.currentIndex].video_id
                    self.currentIndex += 1
                else:
                    # If keyword is new, program searches for new videos matched with keyword
                    self.currentKeyWord = keyword
                    self.currentIDs = Search(keyword).results
                    self.currentIndex = 1
                    # The most matched video has offset 0
                    self.url = "https://www.youtube.com/watch?v="  + self.currentIDs[0].video_id

            # Using pytube API to get streams from a video
            yt = pytube.YouTube(self.url, on_progress_callback = self.on_progress)
            # Getting a highest resolution stream (video + audio)
            self.mediaToDownload = yt.streams.get_highest_resolution()
            self.mediaTitle = yt.title[0 : min(len(yt.title), 60)]
            self.foundVideoTittle.config(text = self.mediaTitle + " " + str(int(yt.length / 60)) + ":" + str(yt.length % 60))
            self.foundVideoTittle["font"] = font.Font(size = 15)
            self.foundVideoTittle.place(x = 100, y = 150)

            self.foundVideoViews.config(text = "(" + f"{yt.views:,}" + " views, " + f"{int(self.mediaToDownload.filesize * 10e-7)}" + " MB)")
            self.foundVideoViews["font"] = font.Font(size = 13)
            self.foundVideoViews.place(x = 100, y = 180)

            # Button preview to play a video online without downloading
            self.buttonPreview.config(text = "Preview", command = self.playYoutube)
            self.buttonPreview["font"] = font.Font(size = 10)
            self.buttonPreview.place(x = 100, y = 210)
            # Button download to save a video locally
            self.buttonDownload.config(text = "Download", command = self.addDownloadThread)
            self.buttonDownload["font"] = font.Font(size = 10)
            self.buttonDownload.place(x = 180, y = 210)
    def listenToKeywords(self):
        self.clearFoundMedia("Listening...")
        if not self.checkOnline(): 
            return
        self.searchBar.delete(0, END)        
        # Reading keywords using Google Speech Recognition API
        r = sr.Recognizer()
        mic = sr.Microphone()
        with mic as source:
            #r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
        keyword = None
        try:
            keyword = r.recognize_google(audio)
            #keyword = r.recognize_google(audio, language="pl")
        except sr.UnknownValueError:
            keyword = None
        self.searchBar.delete(0, END)
        self.clearFoundMedia("")
        if not keyword:
            messagebox.showinfo("Information", "Voice couldn't be recognized!")
        else:
            self.searchBar.insert(END, keyword)
    def addVoiceThread(self):
        # Due to synchronization issues, a thread is added to perform Speech Recognition
        t = threading.Thread(target = self.listenToKeywords)
        t.start()
    def addSearchThread(self):
        # Due to synchronization issues, a thread is added to perform Youtube video search
        t = threading.Thread(target = self.searchYoutube)
        t.start()
    def playYoutube(self):
        # Open media player with an URL passed
        self.player = Player(self.url)
    def on_progress(self, stream, chunk, bytesRemaining):      
        # Progress bar to display the downloading progress  
        totalSize = stream.filesize
        bytesDownloaded = totalSize - bytesRemaining
        percentageOfCompletion = bytesDownloaded / totalSize * 100
        self.progressBar["value"] = int(percentageOfCompletion)
        self.progressPercentage["text"] = str(round(percentageOfCompletion, 1)) + "%"
    def download(self):        
        # Asking a directory to save the downloaded video
        dir = filedialog.askdirectory(parent = self.parent, initialdir=os.getcwd(), title="Please select a location:")
        if dir:
            if not self.mediaToDownload.exists_at_path(dir +"/" + self.mediaToDownload.default_filename):
                self.progressBar["value"] = 0
                self.progressPercentage["text"] = "0%"
                self.progressBar.place(x = 270, y = 210)
                self.progressPercentage.place(x = 380, y = 210)
                self.mediaToDownload.download(dir)
            messagebox.showinfo("Information", "Video " + self.mediaTitle + " downloaded!")
    def addDownloadThread(self):
        # Due to synchronization issues, a thread is added to perform Youtube video downloading
        t = threading.Thread(target = self.download)
        t.start()

app = YoutubeDownloader()