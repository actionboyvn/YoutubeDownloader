from tkinter import filedialog
import os
import vlc
import pytube
from tkinter import *
from tkinter import simpledialog
import webbrowser
class Player(Frame):
    def __init__(self, url = None):
        self.parent = Toplevel()
        self.parent.geometry("835x480")
        self.parent.resizable(0, 0)
        self.parent.title(" Media Player")
        self.parent.iconphoto(False, PhotoImage(file = "./icons/player.png"))
        self.parent.protocol("WM_DELETE_WINDOW", self.quit)
        Frame.__init__(self, self.parent)
        self.createMenuBar()
        self.createStatusBar()
        # Frame left where media are displayed
        self.frameLeft = Frame(self.parent, height = 432, width = 768, bg="#000000")
        self.frameLeft.place(x = 0, y = 0)
        # Frame right where control buttons are displayed
        self.frameRight = Frame(self.parent, height = 432, width = 50)
        self.frameRight.place(x = 775, y = 0)
        self.mediaPlayer = vlc.MediaPlayer()
        self.mediaSource = None
        self.createPlayerIcons()
        if url:
            self.setYoutubeMedia(url)
            self.playMedia()
        self.parent.mainloop()
    def createMenuBar(self):
        # File section
        self.menuBar = Menu(self.parent)
        self.parent["menu"] = self.menuBar
        fileMenu = Menu(self.menuBar)
        for label, command, shortcut_text, shortcut in (
                ("Open...", self.openFile, "Ctrl+O", "<Control-o>"),
                ("Play from URLs", self.playOnline, "Ctrl+U", "<Control-u>"),
                (None, None, None, None),
                ("Quit", self.quit, "Ctrl+Q", "<Control-q>")):
            if label is None:
                fileMenu.add_separator()
            else:
                fileMenu.add_command(label=label, underline=0,
                        command=command, accelerator=shortcut_text)
                self.parent.bind(shortcut, command)
        self.menuBar.add_cascade(label="File", menu=fileMenu, underline=0) 

        # Help section
        fileMenu = Menu(self.menuBar)
        for label, command, shortcut_text, shortcut in (
                ("Email...", self.openFile, "Ctrl+E", "<Control-e>"),
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
        self.statusBar = Label(self.parent, text = "Welcome to Media Player!", anchor = W)
        self.statusBar.place(x = 0, y = 436)
    def setStatusBar(self, title):
        # The status bar is used to display the playing video's title
        self.statusBar.config(text = title)
    def openFile(self, event = None):
        self.mediaSource = None
        self.playMedia()
    def sendEmail(self, event = None):
        webbrowser.open("mailto:?to=257795@student.pwr.edu.pl&subject=Youtube Downloader", new=1)
    def playOnline(self, event = None):
        # Users are asked to enter an URL if play an online video
        url = simpledialog.askstring(parent = self.parent, title = "Enter an URL", prompt = "Youtube URL:\t\t\t\t\t\t")
        if url:
            self.setYoutubeMedia(url)
            self.playMedia()            
    def quit(self, event = None):
        self.stopMedia()
        self.parent.destroy()
    def createPlayerIcons(self):
        self.buttonIcons = dict() # A dictionary to save icons
        # Basic buttons to control the media such as Play, Pause, Stop, Mute
        iconPlay = PhotoImage(file = "./icons/play.png")
        iconPause = PhotoImage(file = "./icons/pause.png")
        iconVolume = PhotoImage(file = "./icons/volume.png")
        iconMuted = PhotoImage(file = "./icons/muted.png")
        iconStop = PhotoImage(file = "./icons/stop.png")
        self.buttonIcons["play"] = iconPlay
        self.buttonIcons["pause"] = iconPause
        self.buttonIcons["volume"] = iconVolume
        self.buttonIcons["muted"] = iconMuted
        self.buttonIcons["stop"] = iconStop        
        self.buttonPlay = Button(self.frameRight, image = self.buttonIcons["play"], command = self.playMedia)
        self.buttonPlay.pack()
        buttonStop = Button(self.frameRight, image = self.buttonIcons["stop"], command = self.stopMedia)
        buttonStop.pack()
        self.buttonVolume = Button(self.frameRight, image = self.buttonIcons["volume"], command = self.volumeOff)
        self.buttonVolume.pack()

    def setYoutubeMedia(self, url):
        # Using pytube API to get streams from a video URL
        yt = pytube.YouTube(url)
        ys = yt.streams.get_highest_resolution()
        self.mediaSource = vlc.Media(ys.url)
        self.setStatusBar("Playing " + yt.title)
    def playMedia(self):
        # Selecting a media file on local disks
        fileDir = None
        if self.mediaSource == None:
            my_filetypes = [('video', '.mp4')]
            fileDir = filedialog.askopenfilename(parent=self.frameLeft, initialdir=os.getcwd(), title="Please select a media file:", filetypes=my_filetypes)
            if fileDir:
                self.mediaSource = vlc.Media(fileDir)
            else:
                return
        # Setting a media to play
        self.mediaPlayer.set_media(self.mediaSource)
        self.mediaPlayer.set_hwnd(self.frameLeft.winfo_id())
        self.mediaPlayer.play()
        # Button play changes it's icon when clicking
        self.buttonPlay.config(image = self.buttonIcons["pause"], command = self.pauseMedia)
        # Using os.path.basename to get the local video's title
        if fileDir:
            self.setStatusBar("Playing " + os.path.basename(fileDir))
            
    def pauseMedia(self):
        self.mediaPlayer.set_pause(1)
        self.buttonPlay.config(image = self.buttonIcons["play"], command = self.continueMedia)
    def continueMedia(self):
        if self.mediaPlayer.is_playing == 0:
            self.mediaPlayer.play()
        else:
            self.mediaPlayer.set_pause(0)
        self.buttonPlay.config(image = self.buttonIcons["pause"], command = self.pauseMedia)
    def stopMedia(self):
        self.mediaPlayer.stop()
        self.buttonPlay.config(image = self.buttonIcons["play"], command = self.playMedia)
        self.mediaSource = None
        self.setStatusBar("Welcome to Media Player!")
    def volumeOff(self):
        self.mediaPlayer.audio_set_volume(0)
        self.buttonVolume.config(image = self.buttonIcons["muted"], command = self.volumeOn)
    def volumeOn(self):
        self.mediaPlayer.audio_set_volume(100)
        self.buttonVolume.config(image = self.buttonIcons["volume"], command = self.volumeOff)
    