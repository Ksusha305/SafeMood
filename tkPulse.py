import tkinter as tk
import customtkinter as Ctk
from customtkinter import *
import cv2
import time
from PIL import Image, ImageTk
from fer import FER
from lib.device import Camera
from lib.interface import plotXY
from lib.processors_noopenmdao import findFaceGetPulse
import sys

serial = None
baud = None
send_serial = False
udp = None
send_udp = False
from lib.processors_noopenmdao import t


def key_handler():
    cv2.waitKey(10) & 255


def toggle_search():
    state = processor.find_faces_toggle()
    print("face detection lock =", not state)


def miss():
    global captured_emotions
    print("52")
    print(max(captured_emotions[0]['emotions'], key=captured_emotions[0]['emotions'].get))


def restart(self):
    self.refresh()
    self.controller.show_frame("StartPage")


def toggle_display_plot():
    print("bpm plot enabled")
    if processor.find_faces:
        toggle_search()
    make_bpm_plot()


win = None


def make_bpm_plot():
    global win
    plotXY([[processor.times,
             processor.samples],
            [processor.freqs,
             processor.fft]],
           labels=[False, True],
           showmax=[False, "bpm"],
           label_ndigits=[0, 0],
           showmax_digits=[0, 1],
           skip=[3, 3],
           bg=processor.slices[0])


if serial:
    send_serial = True

if not baud:
    baud = 9600

else:

    baud = int(baud)
    serial = Serial(port=serial,
                    baudrate=baud)

if udp:
    send_udp = True

    if ":" not in udp:
        ip = udp
        port = 5005

    else:
        ip, port = udp.split(":")
        port = int(port)

    udp = (ip, port)

cameras = []
selected_cam = 1

# for i in range(3):
#     camera = Camera(camera=i)  # first camera by default
#
#     if camera.valid or not len(cameras):
#         cameras.append(camera)
#
#     else:
#         break

w, h = 0, 0
pressed = 0
processor = findFaceGetPulse(bpm_limits=[50, 160], data_spike_limit=2500., face_detector_smoothness=10.)
cap = cv2.VideoCapture(1)


def Pulse():
    global cap, processor, selected_cam
    ret, frame = cap.read()

    if ret:
        processor.frame_in = frame
        processor.run(selected_cam)
        # while len(processor.samples) != 0:
        toggle_display_plot()
        key_handler()
        print(len(processor.samples))

app = Ctk.CTk()
width = app.winfo_screenwidth()
height = app.winfo_screenheight()
app.geometry("%dx%d" % (width, height))

window_menu = Ctk.CTkFrame(app,
                           width=width,
                           height=100,
                           fg_color="#c31b1c")
window_menu.pack(side=TOP)
window_menu_text = Ctk.CTkLabel(window_menu,
                                text="Детектор состояния человека",
                                width=width,
                                font=("emoji", 50, "bold"))
window_menu_text.pack(side=LEFT, pady=15)

window_footer = Ctk.CTkFrame(app,
                             width=width,
                             height=60,
                             fg_color="#c31b1c")
window_footer.pack(side=BOTTOM)
window_footer_text = Ctk.CTkLabel(window_footer,
                                  text="Российские железные дороги",
                                  text_color="white",
                                  width=width,
                                  font=("emoji", 25, "bold"))
window_footer_text.pack(side=LEFT, pady=5)

window_web = Ctk.CTkFrame(app,
                          width=200,
                          height=300)

window_web.pack(side=LEFT, padx=100, pady=50)
label = tk.Label(window_web, width=600, height=400)
label.pack()

# cap = cv2.VideoCapture(1)
emotion_detector = FER(mtcnn=True)
emotions_frame = []
emotions = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
ru_emotions = ['Злость', 'Отвращение', 'Страх', 'Радость', 'Грусть', 'Удивление', 'Нейтрально']
emotions_labels = []
procents_labels = []

index = -1


window_emotions_and_pulse = Ctk.CTkFrame(app,
                                         width=300,
                                         height=700,
                                         fg_color="gray13")

window_emotions_and_pulse.pack(side=RIGHT, padx=70, pady=70)

window_emotions = Ctk.CTkFrame(window_emotions_and_pulse,
                               width=300,
                               height=400,
                               fg_color="gray13")
window_emotions.pack(side=TOP, pady=50, padx=20)

window_button = Ctk.CTkFrame(window_emotions_and_pulse,
                             width=300,
                             height=250,
                             fg_color="gray13")
window_button.pack(side=BOTTOM, pady=50)

button_miss = Ctk.CTkButton(window_button, width=250,
                            height=70,
                            text="Задержать",
                            fg_color="gray33",
                            hover_color="gray43",
                            font=("Arial", 30, "bold"))
button_miss.grid(row=1, column=1, ipadx=6, ipady=6, padx=50, pady=4)

button_prohibit = Ctk.CTkButton(window_button, width=250,
                                height=70,
                                text="Пропустить",
                                fg_color="gray33",
                                hover_color="gray43",
                                font=("Arial", 30, "bold"))
button_prohibit.grid(row=1, column=2, ipadx=6, ipady=6, padx=50, pady=4)

# label_pul = tk.Label(window_pulse, width=300, height=250)
# label_pul.pack()

# captured_emotions = emotion_detector.detect_emotions(img)
# pr = -1
# for i in range(len(emotions)):
#     iii = str(emotions[i])
#     if pr < captured_emotions[0]['emotions'][iii]:
#         index = i
#         pr = captured_emotions[0]['emotions'][iii]

for i in range(len(emotions)):
    emotions_frame.append(Ctk.CTkFrame(window_emotions))
    emotions_frame[i]['height'] = 400
    emotions_frame[i]['width'] = 300
    emotions_frame[i].pack(side=TOP, padx=5, pady=5)
for i in range(len(emotions)):
    emotions_labels.append(tk.Label(emotions_frame[i]))
    emotions_labels[i]['text'] = ru_emotions[i]
    emotions_labels[i]['font'] = ("Arial", 25, "bold")
    # emotions_labels[i]['font'] = (borderwidth = 0)
    emotions_labels[i]['background'] = "gray17"
    emotions_labels[i]['foreground'] = "red" if i == index else "white"
    emotions_labels[i]['width'] = 10
    emotions_labels[i].pack(side=LEFT, padx=120)


def updateFrame():
    global z, captured_emotions, cap
    ret, frame = cap.read()
    if ret:
        frame = cv2.resize(frame, (600, 400))  # Уменьшенный размер
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        captured_emotions = emotion_detector.detect_emotions(img)
        # if len(captured_emotions) == 0:
        #     app.after(50, updateFrame)
        #     app.after(50, Pulse)
        #     return
        pr = -1
        for _ in range(len(captured_emotions)):
            for i in range(len(emotions)):
                iii = str(emotions[i])
                if pr < captured_emotions[0]['emotions'][iii]:
                    index = i
                    pr = captured_emotions[0]['emotions'][iii]
            for i in range(7):
                procents_labels.append(tk.Label(emotions_frame[i]))
                ii = str(emotions[i])
                procents_labels[i]['text'] = f'{captured_emotions[0]["emotions"][ii] * 100: .0f}%'
                procents_labels[i]['font'] = ("Arial", 25, "bold")
                procents_labels[i]['background'] = "gray17"
                procents_labels[i]['foreground'] = "#c31b1c" if i == index else "white"
                emotions_labels[i]['foreground'] = "#c31b1c" if i == index else "white"
                procents_labels[i]['width'] = 40
                procents_labels[i].pack(side=RIGHT, padx=120)

        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        label.imgtk = imgtk
        label.configure(image=imgtk)
    app.after(50, updateFrame)
    app.after(50, Pulse)


updateFrame()

app.mainloop()
