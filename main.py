# Imports
import sys
from PIL import Image
from tkinter import Menu
from tkinter.constants import *
from guizero import *
from pytube import YouTube
from urllib.request import urlopen
import threading
from pathlib import Path
from datetime import timedelta
import webbrowser


def main():
    # Functions and Callbacks
    def menu_file_paste():
        if yt_url.value == "":
            try:
                clipboard_text = app.tk.clipboard_get()
                if "youtu" in clipboard_text:
                    yt_url.value = clipboard_text
                    load_url_button.enable()
                    update_status_bar("")
                else:
                    update_status_bar("Not a valid YouTube URL")
            except:
                pass

    def menu_file_exit():
        app.destroy()

    def menu_help_about():
        pos_str = app.tk.geometry().split('+')
        pos = (int(pos_str[1]), int(pos_str[2]))
        about_window.tk.geometry(f"{about_window.width}x{about_window.height}+{pos[0] + APP_WIDTH // 2 - about_window.width // 2}+{pos[1] + APP_HEIGHT // 2 - about_window.height // 2}")
        about_window.show(wait=True)
        about_window.repeat(function=stay_modal, args=[about_window], time=100)

    def on_about_close():
        about_window.cancel(stay_modal)
        about_window.hide()

    def stay_modal(widget):
        widget.tk.lift()

    def show_context_menu(event):
        try:
            context_menu.tk_popup(event.display_x, event.display_y)
        finally:
            context_menu.grab_release()

    def url_update():
        if yt_url.value != "":
            load_url_button.enable()
        else:
            load_url_button.disable()

    def on_key_pressed(event):
        if event.key != "" and ord(event.key) == 13:
            on_click_load_button()

    def on_app_focus(event):
        if(event.widget == app.tk):
            app.tk.unbind("<FocusIn>")
            menu_file_paste()

    def on_click_load_button():
        stream_list.clear()
        streams.clear()
        downloads.clear()
        video_thumbnail.image = Image.new(mode="RGB", size=(VIDEO_PREVIEW_WIDTH,VIDEO_PREVIEW_HEIGHT), color="gray")
        video_title.value = ""
        video_duration.value = ""
        video_author.value = ""
        if (yt_url.value):
            url = yt_url.value
            t = threading.Thread(target=load_video_url, args=[url])
            t.start()
        else:
            update_status_bar("Paste a valid Youtube video url")

    def load_video_url(url):
        try:
            yt = YouTube(url, on_progress_callback=on_download_progress, on_complete_callback=on_download_complete)
            app.after(0, update_url_info, [yt.title, yt.length, yt.author])
            app.after(0, update_thumbnail, [yt.thumbnail_url])
            load_streams(yt)
        except:
            app.after(0, update_status_bar, ["Cant find a video at this url"])

    def stream_selected():
        download_button.enable()

    def on_download_progress(stream, chunk, remaining):
        percent = (100*(stream.filesize-remaining))/stream.filesize
        id = streams.index(stream)
        app.after(0, update_stream_list, [id, percent])

    def on_download_complete(stream, file_name):
        downloads[stream.itag] = True
        msg = f"Download {sum(downloads.values())}/{len(downloads)} completed"
        app.after(0, update_status_bar, [msg])

    def load_streams(yt):
        app.after(0, update_status_bar, ["Searching streams..."])
        yt_streams = yt.streams
        for s in yt_streams:
            streams.append(s)
            line = f"{s.mime_type:<10}"
            if s.resolution:
                line += f"{s.resolution:>8}"
            else:
                line += f"{'':>8}"
            try:
                line += f"{s.fps:>5}"
            except:
                line += f"{'':>5}"
            if s.abr:
                line += f"{s.abr:>10}"
            else:
                line += f"{'':>10}"
            line += f"{s.filesize_mb:>10.2f} Mb"
            if s.includes_audio_track:
                line += f"{'🎧':>16}"
            else:
                line += f"{'':>17}"
            if s.includes_video_track:
                line += f"{'🎬':>2}"
            # else:
            #     line += f"{'':>6}"
            stream_list.append(line)
            
        app.after(0, update_status_bar, ["Found streams"])

    def on_click_download_button():
        if stream_list.value != None:
            if len(stream_list.value) == 1:
                id = stream_list.items.index(stream_list.value[0])
                stream = streams[id]
                file_name = app.select_file(save=True, filename=f"{stream.itag}-{stream.default_filename}", folder=Path.home())
                if file_name:
                    t = threading.Thread(target=download_stream, args=[stream, file_name])
                    t.start()
            else:
                folder = app.select_folder(title="Select folder", folder=Path.home())
                if folder:
                    for item in stream_list.value:
                        id = stream_list.items.index(item)
                        stream = streams[id]
                        file_name = Path(folder).joinpath(f"{stream.itag}-{stream.default_filename}")
                        t = threading.Thread(target=download_stream, args=[stream, file_name])
                        t.start()

    def download_stream(stream, file_name):
        try:
            app.after(0, update_status_bar, ["Download in progress..."])
            downloads[stream.itag] = False
            stream.download(filename=file_name)
        except:
            app.after(0, update_status_bar, ["Cant download stream"])
    
    def update_url_info(title, duration, author):
        video_title.value = title
        video_duration.value = f"{timedelta(seconds=duration)}"
        video_author.value = author

    def update_stream_list(id, percent):
        base_string = stream_list.items[id]
        progress_string = f"{percent:>5.0f}%"
        updated_string = f"{base_string[:48]}{progress_string}{base_string[54:]}"
        stream_list.remove(stream_list.items[id])
        stream_list.insert(id, updated_string)

    def update_thumbnail(thumbnail_url):
        try:
            video_thumbnail.image = Image.open(urlopen(thumbnail_url))
        except:
            update_status_bar("Cant load video thumbnail")

    def update_status_bar(message):
        status_bar.value = message

    # Variables
    streams = []
    downloads = {}
    APP_WIDTH = 800
    APP_HEIGHT = 700
    VIDEO_PREVIEW_WIDTH = 160
    VIDEO_PREVIEW_HEIGHT = 120
    FONT = None

    match sys.platform:
        case "darwin":
            FONT = "Monaco"
        case "win32":
            FONT = "Consolas"
        case "linux":
            FONT = "DejaVu Sans Mono"

    # App
    app = App(title="YayTD", width=APP_WIDTH, height=APP_HEIGHT)
    app.icon = Path(__file__).resolve().with_name("yaytd_logo_64.png").as_posix()
    app.tk.minsize(APP_WIDTH, APP_HEIGHT)
    app.tk.bind("<FocusIn>", on_app_focus)

    # Widgets
    main_menu = MenuBar(app, toplevel=["File", "Help"], options=[[["Paste", menu_file_paste],["Exit", menu_file_exit]],[["About",menu_help_about]]])

    title_box_input = TitleBox(app, text="Youtube video link", width="fill")
    input_box = Box(title_box_input, align="top", width="fill")
    yt_url = TextBox(input_box, align="left", width="fill", command=url_update)
    yt_url.when_right_button_pressed = show_context_menu
    yt_url.when_key_pressed = on_key_pressed
    load_url_button = PushButton(input_box, on_click_load_button, text="Load", align="left", enabled=False)

    title_video_preview = TitleBox(app, text="Video info", width="fill")
    box_preview = Box(title_video_preview, layout="grid", align="left")
    video_thumbnail = Picture(box_preview, grid=[0,0,1,6], width=VIDEO_PREVIEW_WIDTH, height=VIDEO_PREVIEW_HEIGHT, image=Image.new(mode="RGB", size=(VIDEO_PREVIEW_WIDTH,VIDEO_PREVIEW_HEIGHT), color="gray"), align="top")
    spacer = Box(box_preview, grid=[1,0], width=15, height="fill")
    title_label = Text(box_preview, grid=[2,0], text="Title:", align="left", bg="grey", color="lightgray")
    video_title = Text(box_preview, grid=[2,1], align="left")
    author_label = Text(box_preview,grid=[2,2], text="Author:", align="left", bg="grey", color="lightgray")
    video_author = Text(box_preview,grid=[2,3], align="left")
    duration_label = Text(box_preview, grid=[2,4], text="Duration:", align="left", bg="grey", color="lightgray")
    video_duration = Text(box_preview, grid=[2,5], align="left")

    stream_list = ListBox(app, width="fill", height="fill", scrollbar=True, command=stream_selected, multiselect=True)
    stream_list.text_size = 12
    stream_list.font = FONT
    box_bottom = Box(app, align="bottom", width="fill")
    status_bar = Text(box_bottom, text="Yet Another YouTube Downloader", align="left")
    download_button = PushButton(box_bottom, command=on_click_download_button, text="Download", enabled=False, align="right")

    # TK Widgets
    context_menu = Menu(input_box.tk, tearoff = 0)
    context_menu.add_command(label ="Paste", command=menu_file_paste)

    # Windows
    about_window = Window(app, title="About", visible=False, width=320, height=240)
    about_window.tk.resizable(0,0)
    box = Box(about_window, align="left", width="fill")
    close_button = PushButton(box, command=lambda : about_window._close_window(), text="Close", align="bottom")
    pytube_logo = Picture(box, image=Path(__file__).resolve().with_name("yaytd_logo_64.png").as_posix())
    Text(box, "YayTD", size=12).tk.configure(font=("bold"))
    yaytd_gh_link = Text(box, "https://github.com/frenchfaso/yaytd", color="blue")
    yaytd_gh_link.when_clicked = lambda _ : webbrowser.open("https://github.com/frenchfaso/yaytd")
    yaytd_gh_link.tk.configure(cursor="hand2")
    Text(box, "Yet Another YouTube Downloader\nis a simple GUI built on top of 'pytube'\nwith 'guizero' and a little bit of 'tkinter'", size=10)
    box_links = Box(box)
    pytube_link = Text(box_links, text="pytube", color="blue", align="left")
    pytube_link.when_clicked = lambda _ : webbrowser.open("https://github.com/pytube/pytube")
    pytube_link.tk.configure(cursor="hand2")
    guizero_link = Text(box_links, "guizero", color="blue", align="left")
    guizero_link.when_clicked = lambda _ : webbrowser.open("https://lawsie.github.io/guizero/")
    guizero_link.tk.configure(cursor="hand2")
    tkinter_link = Text(box_links, "tkinter", color="blue", align="left")
    tkinter_link.when_clicked = lambda _ : webbrowser.open("https://docs.python.org/3/library/tkinter.html")
    tkinter_link.tk.configure(cursor="hand2")
    about_window.when_closed = on_about_close

    app.display()

if(__name__ == "__main__"):
    main()
