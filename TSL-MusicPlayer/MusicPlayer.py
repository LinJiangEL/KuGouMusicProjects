import os
import ast
import time
import shutil
import base64
import threading
import eyed3
import ctypes
import glob
import tkinter.messagebox
from tkinter import *
from tkinter import filedialog
from typing import *
from win32com.client import Dispatch
from icon import iconbase
from mainmusic import musicbase

Temp_DIR = os.getenv('TEMP') + '\\TSL-MusicPlayer'

if os.path.exists(Temp_DIR):
    shutil.rmtree(Temp_DIR)

os.mkdir(Temp_DIR)

exeid = "'Explorer Network Lab.'.XV101.'1.3.7031"  # 这里可以设置任意文本
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(exeid)

musicnames: List[Any] = []
index = None
total = False

icon = open(f"{Temp_DIR}\\icon.ico", "wb+")
icon.write(base64.b64decode(iconbase))
icon.close()
musicgif = open(f"{Temp_DIR}\\mainmusic.gif", "wb+")
musicgif.write(base64.b64decode(musicbase))
musicgif.close()


def openfile() -> None:
    global total, musicname, index
    if index is None:
        index = [1]

    filenames = filedialog.askopenfilenames(title="打开音乐",
                                            filetypes=[("mp3文件", "*.mp3"),
                                                       ("WMA文件", "*.wma"),
                                                       ("WAV文件", "*.wav")
                                                       ]
                                            )

    if filenames != "":
        musicnames.append(filenames)
        btn_play.config(state="active")
        btn_playlist.config(state="active")
        list_name.config(state="normal")
        listdel_all.config(state="active")
        listexport.config(state="active")
        listdel_all.config(state="active")
        listdel_sel.config(state="active")
        savelist_btn.config(state="active")
        if len(musicnames) > 1:
            previous_play.config(state="active")
            next_play.config(state="active")

    if filenames:
        for i in range(len(filenames)):
            media = wmp.newMedia(filenames[i])
            wmp.currentPlaylist.appendItem(media)

            print(filenames[i])
            coco = eyed3.load(filenames[i])  # eyed3模块读取mp3信息
            total = int(coco.info.time_secs)
            minute = int(coco.info.time_secs) // 60
            sec = int(coco.info.time_secs) % 60

            musicname = filenames[i].split("/")

            i = index[0]
            list_name.insert(END, str(len(musicnames)) + "." + musicname[-1])
            list_name.insert(END, " " * 4)
            if minute < 10 and sec < 10:
                list_name.insert(END, "0%d:0%d" % (minute, sec))
            elif minute < 10 and sec >= 10:
                list_name.insert(END, "0%d:%d" % (minute, sec))
            elif minute >= 10 and sec < 10:
                list_name.insert(END, "%d:0%d" % (minute, sec))
            elif minute >= 10 and sec >= 10:
                list_name.insert(END, "%d:%d" % (minute, sec))
            else:
                pass
            list_name.insert(END, "\n")
            i = i + 1
            index.append(i)
        list_name.config(state="disabled")


def play(self=None) -> None:
    if total:
        per_thread = threading.Thread(target=per)
        per_thread.daemnon = True
        btn_stop.config(state="active")
        btn_pause.config(state="active")
        progress_scal.config(state="active")
        btn_continue.config(state="disabled")
        btn_play.config(state="disabled")
        listdel_all.config(state="disabled")
        wmp.controls.play()
        per_thread.start()


def per() -> None:
    global total
    while wmp.playState != 1 and total:
        progress_scal.set(int(wmp.controls.currentPosition))
        progress_scal.config(label=wmp.controls.currentPositionString)
        progress_scal.config(to=total, tickinterval=50)
        time.sleep(1)


def stop(self=None) -> None:
    wmp.controls.stop()
    btn_play.config(state="active")
    listdel_all.config(state="active")
    btn_playlist.config(state="active")
    progress_scal.config(state="disabled")
    btn_stop.config(state="disabled")
    btn_pause.config(state="disabled")
    btn_continue.config(state="disabled")


def pause(self=None) -> None:
    if total:
        wmp.controls.pause()
        btn_pause.config(state="disabled")
        btn_continue.config(state="active")


def btn_continue(self=None) -> None:
    wmp.controls.play()
    btn_continue.config(state="disabled")
    btn_pause.config(state="active")


def newlist(self=None) -> (List, List):
    wmp.currentPlaylist.clear()
    list_name.delete(1.0, END)
    btn_play.config(state="disabled")
    btn_stop.config(state="disabled")
    btn_pause.config(state="disabled")
    btn_continue.config(state="disabled")
    listdel_all.config(state="disabled")
    listexport.config(state="disabled")
    listdel_sel.config(state="disabled")
    savelist_btn.config(state="disabled")
    musicnames = []
    index = []
    return musicnames, index


def uselist(self=None) -> List[str]:
    musicnames = []
    ListFile = filedialog.askopenfile(filetypes=[("Text File", ".txt")])
    if ListFile != None:
        ListFilePath = ListFile.name
        with open(ListFilePath, "r", encoding='utf-8') as LP:
            for mname in LP.readlines():
                musicnames.append(mname)
        btn_play.config(state="active")
        btn_stop.config(state="disabled")
        btn_pause.config(state="disabled")
        btn_continue.config(state="disabled")
        listdel_all.config(state="active")
        listexport.config(state="active")
        listdel_sel.config(state="active")
        savelist_btn.config(state="active")
        return musicnames


def savelist(self=None) -> None:
    fileSave = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[("Text File", ".txt")])
    with open(fileSave, "w", encoding='utf-8') as ListFile:
        for musicnamet in musicnames:
            ListFile.write(musicnamet)
            ListFile.write("\n")

    tkinter.messagebox.showinfo(title="Info", message="Successfully save musicList!")


def saveaslist(self=None) -> None:
    fileSave = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[("Text File", ".txt")])
    with open(fileSave, "w") as ListFile:
        for musicname in musicnames:
            ListFile.write(musicname)
            ListFile.write("\n")

    tkinter.messagebox.showinfo(title="Info", message="Successfully save musicList!")


def delmusic(self=None) -> List[int]:
    global index
    delete_yesno = tkinter.messagebox.askyesno(title="Delete Music",
                                               message="This operation will delete the last music.\nContinue?"
                                               )
    if delete_yesno:
        list_name.config(state="normal")
        list_name.delete(1.0, END)
        try:
            musicnames.pop()
            wmp.currentPlaylist.clear()
        except IndexError:
            tkinter.messagebox.showerror(title="Error",
                                         message="Failed execute delete operation! MusicList was already empty!"
                                         )
        for n, i in enumerate(musicnames, start=1):
            media = wmp.newMedia(i[0])
            wmp.currentPlaylist.appendItem(media)
            minfo = eyed3.load(i[0])
            minute = int(minfo.info.time_secs) // 60
            sec = int(minfo.info.time_secs) % 60
            list_name.insert(END, f"{n}. {i[0].split('/')[-1]}")
            list_name.insert(END, " " * 4)
            if minute < 10 and sec < 10:
                list_name.insert(END, "0%d:0%d" % (minute, sec))
            elif minute < 10 and sec >= 10:
                list_name.insert(END, "0%d:%d" % (minute, sec))
            elif minute >= 10 and sec < 10:
                list_name.insert(END, "%d:0%d" % (minute, sec))
            elif minute >= 10 and sec >= 10:
                list_name.insert(END, "%d:%d" % (minute, sec))
            else:
                pass
            list_name.insert(END, "\n")
        list_name.config(state="disabled")
        index = index[:-1]
        if len(index) == 1:
            btn_play.config(state="disabled")
            btn_stop.config(state="disabled")
            btn_pause.config(state="disabled")
            btn_continue.config(state="disabled")
            listdel_all.config(state="disabled")
            listexport.config(state="disabled")
            listdel_sel.config(state="disabled")
            savelist_btn.config(state="disabled")
        return index


def exitit() -> None:
    shutil.rmtree(Temp_DIR)
    root.destroy()


def Previous_it() -> None:
    wmp.controls.previous()


def Next_it() -> None:
    wmp.controls.next()


def Volume_ctr(self=None) -> None:
    wmp.settings.Volume = vio_scale.get()


def Volume_add(i=None) -> None:
    try:
        if i is None:
            i = [0]
        wmp.settings.Volume = wmp.settings.Volume + 5
        i.append(wmp.settings.Volume)
        vio_scale.set(wmp.settings.Volume)
    except _tkinter.TclError:
        pass


def Volume_minus(i: List[int] = None) -> None:
    try:
        if i is None:
            i = [0]
        wmp.settings.Volume = wmp.settings.Volume - 5
        i.append(wmp.settings.Volume)
        vio_scale.set(wmp.settings.Volume)
    except _tkinter.TclError:
        pass


def Scale_ctr() -> None:
    wmp.controls.currentPosition = var_scale.get()
    # print(wmp.currentMedia.duration)


def Clear_list() -> (List, List):
    wmp.currentPlaylist.clear()
    list_name.config(state="normal")
    list_name.delete(1.0, END)
    btn_play.config(state="disabled")
    btn_stop.config(state="disabled")
    btn_pause.config(state="disabled")
    btn_continue.config(state="disabled")
    listdel_all.config(state="disabled")
    listexport.config(state="disabled")
    listdel_sel.config(state="disabled")
    savelist_btn.config(state="disabled")
    list_name.config(state="disabled")
    musicnames = []
    index = []
    return musicnames, index


def List_random() -> None:
    wmp.settings.setMode("shuffle", True)


def List_loop() -> None:
    wmp.settings.setMode("loop", True)


root = Tk()
root.title('音乐播放器 -- Made by LinJiang@Explorer Network Lab. -- QQ: 1633251707')
root.geometry("700x560")
root.resizable(0, 0)
root.wm_iconbitmap(f"{Temp_DIR}\\icon.ico")
root.protocol("WM_DELETE_WINDOW", exitit)
wmp = Dispatch("WMPlayer.OCX")

canvas = Canvas(root, width=170, height=250, bg="white")
img = PhotoImage(file=f'{Temp_DIR}\\mainmusic.gif')
canvas.create_image((87, 130), image=img)
canvas.place(x=80, y=10)
canvas.coords(img, 10, 10)
canvas.grid(row=0, column=0, sticky="nw", rowspan=1)

progress_lab = LabelFrame(root, text="播放进度")
progress_lab.grid(row=2, column=0, sticky="we", rowspan=2)
var_scale = DoubleVar()
progress_scal = Scale(progress_lab, orient=HORIZONTAL, showvalue=0, length=180, variable=var_scale, state="disabled")
progress_scal.bind("<Button-1>", pause)
progress_scal.bind("")
progress_scal.bind("<ButtonRelease-1>", play)
progress_scal.grid(row=3, column=0)

modee_lab = LabelFrame(root, text="播放模式")
modee_lab.grid(row=4, column=0, rowspan=4, sticky="ws")
var_mode = IntVar()
randomradio = Radiobutton(modee_lab, variable=var_mode, value=1, text="随机播放", command=List_random)
randomradio.grid(row=4, column=2)
inturnradio = Radiobutton(modee_lab, variable=var_mode, value=2, text="顺序播放")
inturnradio.grid(row=4, column=3)
alloop = Radiobutton(modee_lab, variable=var_mode, value=2, text="全部循环播放", command=List_loop)
alloop.grid(row=5, column=2)
sinloop = Radiobutton(modee_lab, variable=var_mode, value=3, text="单曲循环播放")
sinloop.grid(row=5, column=3)
previous_play = Button(modee_lab, text="上一曲", command=Previous_it, state="disabled")
previous_play.grid(row=6, column=2, rowspan=2, pady=10)
next_play = Button(modee_lab, text="下一曲", command=Next_it, state="disabled")
next_play.grid(row=6, column=3, rowspan=2, pady=10)

var_volume = IntVar()
vioce_lab = LabelFrame(root, text="音量控制")
vioce_lab.grid(row=8, column=0, sticky="wes")
vio_scale = Scale(vioce_lab, orient=HORIZONTAL, length=170, variable=var_volume, command=Volume_ctr)
vio_scale.set(30)
vio_scale.grid(row=8, column=0)
vio_plus = Button(vioce_lab, width=8, text="增加音量+", command=Volume_add)
vio_plus.grid(row=9, column=0, sticky="w")
vio_minus = Button(vioce_lab, width=8, text="减少音量-", command=Volume_minus)
vio_minus.grid(row=9, column=0, sticky="e")

ctr_lab = LabelFrame(root, text="播放控制", height=160)
ctr_lab.grid(row=0, column=1, rowspan=12, sticky="ns")
btn_open = Button(ctr_lab, text="打开音乐文件", width=10, command=openfile, state="active")
btn_open.grid(row=0, column=1)
btn_play = Button(ctr_lab, text="播放", width=10, command=play, state="disabled")
btn_play.grid(row=1, column=1, pady=5)
btn_stop = Button(ctr_lab, text="停止", width=10, command=stop, state="disabled")
btn_stop.grid(row=2, column=1, pady=5)
btn_pause = Button(ctr_lab, text="暂停", width=10, command=pause, state="disabled")
btn_pause.grid(row=3, column=1, pady=5)
btn_continue = Button(ctr_lab, text="继续", width=10, command=btn_continue, state="disabled")
btn_continue.grid(row=4, column=1, pady=5)

btn_playlist = Button(ctr_lab, text="新建播放列表", width=10, command=newlist, state="disabled")
btn_playlist.grid(row=5, column=1, pady=5)

listimport = Button(ctr_lab, width=10, text="导入列表", command=uselist, state="active")
listimport.grid(row=6, column=1, sticky="nw", pady=5)
listexport = Button(ctr_lab, width=10, text="导出列表", command=savelist, state="disabled")
listexport.grid(row=7, column=1, sticky="nw", pady=5)
listdel_all = Button(ctr_lab, width=10, text="清空列表", command=Clear_list, state="disabled")
listdel_all.grid(row=8, column=1, sticky="nw", pady=5)
listdel_sel = Button(ctr_lab, width=10, text="删除歌曲", command=delmusic, state="disabled")
listdel_sel.grid(row=12, column=1, sticky="nw", pady=5)
savelist_btn = Button(ctr_lab, text="保存为列表", command=saveaslist, state="disabled")
savelist_btn.grid(row=9, column=1)
min_btn = Button(ctr_lab, text="退出", command=exitit)
min_btn.grid(row=13, column=1)

list_name = Text(root, height=18, width=80, state="disabled")
list_name.grid(row=0, column=2, sticky="n", rowspan=6)

root.mainloop()
