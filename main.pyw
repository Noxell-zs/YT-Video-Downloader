""""Application for downloading videos from YouTube"""

import os
import threading
import re
from tkinter import Tk
from tkinter.messagebox import showerror, showinfo
from tkinter.ttk import Style, Label, Entry, Button, Combobox
import ffmpeg
from pytube import YouTube


def load_video(
        streams,
        itag: int,
        output_path: str = "temp",
        filename: str = "video.mp4",
        callback=None
):
    """Loading video

    :type streams: pytube.StreamQuery
    :param itag: YouTube format identifier code
    :param output_path: The path to save the file
    :param filename: The name of output file with file extension
    :param callback: The function that is executed at the end
    """
    (
        streams
        .get_by_itag(itag)
        .download(output_path=output_path, filename=filename)
    )
    if callback:
        callback()


def load_audio(
        streams,
        output_path: str = "temp",
        filename: str = "audio.mp4",
        callback=None
):
    """Loading audio

    :type streams: pytube.StreamQuery
    :param output_path: The path to save the file
    :param filename: The name of output file with file extension
    :param callback: The function that is executed at the end
    """
    (
        streams
        .get_audio_only()
        .download(output_path=output_path, filename=filename)
    )
    if callback:
        callback()


def video_check(link: str, callback=None):
    """Checking the video

    :param link: Link to the video on YouTube
    :param callback: The function with one param that is executed at the end
    """
    result = None
    try:
        yt = YouTube(link)
        result = yt.streams, re.sub(r'[\\\/:\*\?"<>\|]', '', yt.title)
    except Exception as e:
        print(e)
    if callback:
        return callback(result)


def load_video_audio(
        streams,
        itag: int,
        title: str,
        callback=None
):
    """Loading video + audio

    :type streams: pytube.StreamQuery
    :param itag: YouTube format identifier code
    :param title: The title of video (without file extension)
    :param callback: The function that is executed at the end
    """
    thr1 = threading.Thread(target=load_video, kwargs={
        "streams": streams,
        "itag": itag
    })
    thr1.start()
    thr2 = threading.Thread(target=load_audio, args=(streams,))
    thr2.start()
    thr1.join()
    thr2.join()

    v_file = ffmpeg.input("temp/video.mp4")
    (
        ffmpeg
        .input("temp/audio.mp4")
        .output(v_file, f"out/{title}.mp4", shortest=None, vcodec='copy')
        .overwrite_output()
        .run()
    )

    os.remove("temp/video.mp4")
    os.remove("temp/audio.mp4")

    if callback:
        callback()


class App(Tk):
    """Toplevel widget of Tk"""
    def __init__(self):
        """Initialization of window"""
        super().__init__()
        if not os.path.isdir("temp"):
            os.mkdir("temp")
        if not os.path.isdir("out"):
            os.mkdir("out")

        self.streams = self.video_title = None
        PADY = 6
        PADX = 8

        self.title("Video loader")
        self.geometry("512x256")
        self.config(bg="#544B64", cursor="arrow")

        try:
            self.iconbitmap("icon.ico")
        except Exception as e:
            print(e)

        stl = Style()
        stl.configure('Button.TLabel', padding=6, anchor="center",
                      foreground='white', background='#544B64', relief='flat')
        stl.map('Button.TLabel', background=[
            ('!pressed', '!active', '#630DA7'),
            ('pressed', '#530097'),
            ('active', '#731DB7')
        ])
        stl.configure('E.TEntry', padding=6, foreground='#630DA7')
        stl.configure('C.TCombobox', padding=6, foreground='#630DA7')
        stl.configure('L.TLabel', foreground='white', background='#544B64')

        for c in range(4):
            self.columnconfigure(index=c, weight=1)
        for r in range(4):
            self.rowconfigure(index=r, weight=1)

        Label(text="URL of video:", style='L.TLabel').grid(
            row=0, column=0, columnspan=1, sticky="e", pady=PADY, padx=PADX)

        self.url_entry = Entry(style='E.TEntry')
        self.url_entry.grid(row=0, column=1, columnspan=3,
                            sticky="we", pady=PADY, padx=PADX)

        check_btn = Button(command=self.check_click, text="Check video",
                           style='Button.TLabel', cursor='hand2')
        check_btn.grid(row=1, column=0, columnspan=4,
                       sticky="we", pady=PADY, padx=PADX)

        self.audio_only_btn = Button(command=self.audio_only_click,
                                     text="Download audio only",
                                     style='Button.TLabel', cursor='hand2')
        self.audio_only_btn.grid(row=2, column=0, columnspan=1,
                                 sticky="we", pady=PADY, padx=PADX)
        self.audio_only_btn["state"] = "disabled"

        Label(text="Quality:", style='L.TLabel').grid(
            row=2, column=1, columnspan=1, sticky="e", pady=PADY, padx=PADX)

        self.q_combobox = Combobox(state="readonly", style="C.TCombobox",
                                   cursor='hand2')
        self.q_combobox.grid(row=2, column=2, columnspan=2,
                             sticky="we", pady=PADY, padx=PADX)
        self.q_combobox["state"] = "disabled"

        self.without_audio_btn = Button(command=self.without_audio_click,
                                        text="Download without audio",
                                        style='Button.TLabel', cursor='hand2')
        self.without_audio_btn.grid(row=3, column=0, columnspan=2,
                                    sticky="we", pady=PADY, padx=PADX)
        self.without_audio_btn["state"] = "disabled"

        self.video_audio_btn = Button(command=self.video_audio_click,
                                      text="Download video + audio",
                                      style='Button.TLabel', cursor='hand2')
        self.video_audio_btn.grid(row=3, column=2, columnspan=2,
                                  sticky="we", pady=PADY, padx=PADX)
        self.video_audio_btn["state"] = "disabled"

    def check_callback(self, result):
        """Callback for 'check_video' function"""
        if result:
            self.streams, self.video_title = result

            self.q_combobox["values"] = [
                f"Res: {i.resolution}, FPS: {i.fps}, Codec: {i.video_codec}; {i.itag}"
                for i in self.streams.filter(mime_type="video/mp4").order_by("resolution")
            ]

            self.audio_only_btn["state"] = "enabled"
            self.q_combobox["state"] = "enabled"
            self.without_audio_btn["state"] = "enabled"
            self.video_audio_btn["state"] = "enabled"
        else:
            self.streams = self.video_title = None

            self.audio_only_btn["state"] = "disabled"
            self.q_combobox["state"] = "disabled"
            self.without_audio_btn["state"] = "disabled"
            self.video_audio_btn["state"] = "disabled"

            self.q_combobox.set('')
            showerror("Error", "Couldn't find the video")
        self.config(cursor="arrow")

    def check_click(self):
        """Click event of check_btn"""
        self.config(cursor="watch")
        threading.Thread(target=video_check, kwargs={
            "link": self.url_entry.get(),
            "callback": self.check_callback,
        }).start()

    def audio_only_click(self):
        """Click event of audio_only_btn"""
        self.config(cursor="watch")
        threading.Thread(target=load_audio, kwargs={
            "streams": self.streams,
            "output_path": "out",
            "filename": self.video_title + ".mp4",
            "callback": self.loading_callback
        }).start()

    def without_audio_click(self):
        """Click event of without_audio_btn"""
        choice = self.q_combobox.get()
        if not choice:
            return
        self.config(cursor="watch")
        threading.Thread(target=load_video, kwargs={
            "streams": self.streams,
            "itag": int(re.search(r'\d+$', choice).group(0)),
            "output_path": "out",
            "filename": self.video_title + ".mp4",
            "callback": self.loading_callback
        }).start()

    def video_audio_click(self):
        """Click event of video_audio_btn"""
        choice = self.q_combobox.get()
        if not choice:
            return
        self.config(cursor="watch")
        threading.Thread(target=load_video_audio, kwargs={
            "streams": self.streams,
            "itag": int(re.search(r'\d+$', choice).group(0)),
            "title": self.video_title,
            "callback": self.loading_callback
        }).start()

    def loading_callback(self, *_):
        """Callback for loading function"""
        self.config(cursor="arrow")
        return showinfo("Success", "Downloaded in dir /out")


if __name__ == '__main__':
    app = App()
    app.mainloop()
