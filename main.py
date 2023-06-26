import socket
from random import choice, randint
from threading import Thread
import cv2
from time import sleep
import numpy
import pyaudio
import customtkinter as tk
from customtkinter import CTkButton, CTkImage, CTkFrame, CTkCanvas
from PIL import Image, ImageTk

SHAPE = 240, 320, 3
CHUNK = 1024
RATE = 44100
FORMAT = pyaudio.paInt16

CHARS = "".join(chr(i) for i in range(ord('0'), ord('9')+1)) + \
        "".join(chr(i) for i in range(ord('a'), ord('z')+1)) + \
        "".join(chr(i) for i in range(ord('A'), ord('Z')+1))



class VideoToDisplay:
    def __init__(self):
        self.user_video = None
        self.other_video = None


class Client:
    def __init__(self):
        self.client_video_socket = None
        self.client_audio_socket = None


class Audio:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.output_stream = self.audio.open(format=FORMAT, channels=1, rate=RATE, output=True, frames_per_buffer=CHUNK)
        self.input_stream = self.audio.open(format=FORMAT, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)


def programUI():
    BUTTON_SIZE= 50
    BUTTON_IMAGE_SIZE = 25
    root = tk.CTk()
    root.geometry("500x350")
    root.title("Goom")

    nav_bar = tk.CTkFrame(root, 300, 80, 10, 0, fg_color="#888888")
    nav_bar.pack(side=tk.BOTTOM)
    arr = numpy.zeros(SHAPE, dtype=numpy.uint8)

    vid_image = CTkImage(Image.fromarray(arr), size=(400, 280))

    user_vid = CTkButton(master=root, width=400, height=280, corner_radius=0,
                         image=vid_image, text="", fg_color="#333", hover_color="#333")
    user_vid.pack()


    def play_video(e):
        show_video_thread.start()
        return
        cap = cv2.VideoCapture(0)
        while True:
            print("getting video")
            ret, frame = cap.read()
            if not ret:
                continue
            user_vid.configure(image=CTkImage(Image.fromarray(frame), size=(400, 280)))
            user_vid.pack()



    vid_image = CTkImage(Image.open("vid.png"), size=(BUTTON_IMAGE_SIZE, BUTTON_IMAGE_SIZE))
    vid_btn = CTkButton(nav_bar, text="", width=BUTTON_SIZE, height=BUTTON_SIZE, image=vid_image)
    aud_image = CTkImage(Image.open("mic.png"), size=(BUTTON_IMAGE_SIZE, BUTTON_IMAGE_SIZE))
    aud_btn = CTkButton(nav_bar, text="", width=BUTTON_SIZE, height=BUTTON_SIZE, image=aud_image)
    red_image = CTkImage(Image.open("hang.png"), size=(BUTTON_IMAGE_SIZE, BUTTON_IMAGE_SIZE))
    red_btn = CTkButton(nav_bar,
                        text="", width=BUTTON_SIZE, height=BUTTON_SIZE,
                        image=red_image,
                        fg_color="#dd3333", hover_color="#c62e2e")

    vid_btn.place(rely=0.5, relx=0.20, anchor=tk.CENTER)
    aud_btn.place(rely=0.5, relx=0.50, anchor=tk.CENTER)
    red_btn.place(rely=0.5, relx=0.80, anchor=tk.CENTER)
    red_btn.bind("<Button 1>", exit)
    vid_btn.bind("<Button 1>", play_video)

    root.mainloop()


class screenUI(tk.CTk):
    def __init__(self):
        super().__init__()
        self.consts = self.initiate_consts()
        self.geometry("500x350")
        self.title("Goom")
        self.children = self.initiate_children()


    @staticmethod
    def initiate_consts():
        consts = {
            "BUTTON_SIZE": 50,
            "BUTTON_IMAGE_SIZE": 25
        }
        return consts

    def initiate_children(self):
        arr = numpy.zeros(SHAPE, dtype=numpy.uint8)
        for i in arr:
            for j in i:
                for k in range(3):
                    j[k] = randint(0, 255)
        user_vid_image = CTkImage(Image.fromarray(arr), size=(400, 280))
        vid_image = CTkImage(Image.open("vid.png"),
                             size=(self.consts["BUTTON_IMAGE_SIZE"], self.consts["BUTTON_IMAGE_SIZE"]))
        aud_image = CTkImage(Image.open("mic.png"),
                             size=(self.consts["BUTTON_IMAGE_SIZE"], self.consts["BUTTON_IMAGE_SIZE"]))
        red_image = CTkImage(Image.open("hang.png"),
                             size=(self.consts["BUTTON_IMAGE_SIZE"], self.consts["BUTTON_IMAGE_SIZE"]))

        nav_bar = tk.CTkFrame(self, 300, 80, 10, 0, fg_color="#888888")
        user_vid = tk.CTkLabel(master=self, width=400, height=280, corner_radius=0,
                               image=user_vid_image, text="", bg_color="#333")
        vid_btn = CTkButton(nav_bar, text="",
                            width=self.consts["BUTTON_SIZE"], height=self.consts["BUTTON_SIZE"],
                            image=vid_image)
        aud_btn = CTkButton(nav_bar, text="",
                            width=self.consts["BUTTON_SIZE"], height=self.consts["BUTTON_SIZE"],
                            image=aud_image)
        red_btn = CTkButton(nav_bar,
                            text="", width=self.consts["BUTTON_SIZE"], height=self.consts["BUTTON_SIZE"],
                            image=red_image,
                            fg_color="#dd3333", hover_color="#c62e2e")
        children = {
            'nav-bar': nav_bar,
            'user-vid': user_vid,
            "vid-btn": vid_btn,
            "red-btn": red_btn,
            "aud-btn": aud_btn
        }
        return children

    def place_children(self):
        self.children["user-vid"].pack()
        self.children["nav-bar"].pack(side=tk.BOTTOM)
        self.children["vid-btn"].place(rely=0.5, relx=0.20, anchor=tk.CENTER)
        self.children["aud-btn"].place(rely=0.5, relx=0.50, anchor=tk.CENTER)
        self.children["red-btn"].place(rely=0.5, relx=0.80, anchor=tk.CENTER)


        def red_click(e):
            global KILL_SOCKET
            KILL_SOCKET = True
            exit()
        self.children["red-btn"].bind("<Button 1>", red_click)


root = screenUI()
root.place_children()


videos = VideoToDisplay()
client = Client()
audio = Audio()

HOST = '10.100.102.8'
VIDEO_PORT = 12345
AUDIO_PORT = 12346


CLIENT_CONNECTED = False
AUDIO_CONNECTED  = False
KILL_SOCKET      = False


def encode_image(data):
    data = numpy.ndarray(SHAPE, dtype=numpy.uint8)
    enc = ''

    for i in range(9):
        enc += choice(CHARS)
    res = [("S"+enc).encode('utf8')]
    for part in data:
        res.append(part.tobytes())
    res.append(("E"+enc).encode('utf8'))
    return res


def video_socket_connection():
    global CLIENT_CONNECTED, KILL_SOCKET
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    s.bind((HOST, VIDEO_PORT))
    s.listen(1)
    print(f"Server listening on {HOST}:{VIDEO_PORT}")
    while not KILL_SOCKET:
        try:
            client.client_video_socket, _ = s.accept()
            break
        except TimeoutError:
            continue
    CLIENT_CONNECTED = True


def audio_socket_connection():
    global AUDIO_CONNECTED, KILL_SOCKET
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    s.bind((HOST, AUDIO_PORT))
    s.listen(1)
    print(f"Server listening on {HOST}:{AUDIO_PORT}")
    while not KILL_SOCKET:
        try:
            client.client_audio_socket, _ = s.accept()
            break
        except TimeoutError:
            continue
    AUDIO_CONNECTED = True


def get_video():
    global KILL_SOCKET, CLIENT_CONNECTED
    while not CLIENT_CONNECTED and not KILL_SOCKET:
        sleep(0.5)
    while not KILL_SOCKET:
        try:
            if client.client_video_socket.getpeername()[0] != '10.100.102.13':
                print("not equal")
                continue
        except (OSError, AttributeError) as e:
            print("some error")
            continue
        try:
            response = client.client_video_socket.recv(230600)
        except ConnectionResetError:
            KILL_SOCKET = True
            break
        if not response:
            KILL_SOCKET = True
            print("not res")
            break

        res = numpy.frombuffer(response, dtype=numpy.uint8)
        try:
            res = numpy.reshape(res, newshape=SHAPE)
        except ValueError:
            continue
        videos.other_video = res
        sleep(1/30)


def show_video():
    global KILL_SOCKET
    cap = cv2.VideoCapture(0)
    while not KILL_SOCKET:
        ret, frame = cap.read()
        if not ret:
            continue
        videos.user_video = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        # print(type(videos.other_video))
        if videos.other_video is not None:
            if type(videos.other_video) != numpy.ndarray:
                print('g')
                continue
            shape = list(videos.other_video.shape)
            shape[1] *= 2
            res_image = numpy.zeros(tuple(shape), numpy.uint8)
            res_image[:, :shape[1] // 2] = videos.user_video
            res_image[:, shape[1] // 2:] = videos.other_video
            cv2.imshow('Server', res_image[:, ::-1])
        else:
            cv2.imshow('Server', frame[:, ::-1])
        if cv2.waitKey(33) == ord("q"):
            KILL_SOCKET = True


def show_video_tk():
    global KILL_SOCKET
    cap = cv2.VideoCapture(0)
    while not KILL_SOCKET:
        ret, frame = cap.read()
        if not ret:
            continue
        videos.user_video = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        # print(type(videos.other_video))
        if videos.other_video is not None:
            if type(videos.other_video) != numpy.ndarray:
                print('g')
                continue
            shape = list(videos.other_video.shape)
            shape[1] *= 2
            res_image = numpy.zeros(tuple(shape), numpy.uint8)
            res_image[:, :shape[1] // 2] = videos.user_video
            res_image[:, shape[1] // 2:] = videos.other_video
            cv2.imshow('Server', res_image[:, ::-1])
        else:
            img = Image.fromarray(cv2.cvtColor(frame[:, ::-1], cv2.COLOR_BGR2RGB))
            # updating element
            root.children['user-vid'].configure(image=CTkImage(img, size=(400, 280)))

            # # replacing element
            # root.children['user-vid'].destroy()
            # user_vid_image = CTkImage(img, size=(400, 280))
            # root.children['user-vid'] = tk.CTkLabel(master=root, width=400, height=280, corner_radius=0,
            #                                         image=user_vid_image, text="", bg_color="#333")
            # root.children['user-vid'].pack()

            # cv2.imshow("server", s)
        if cv2.waitKey(33) == ord("q"):
            KILL_SOCKET = True


def send_video():
    global KILL_SOCKET
    while not KILL_SOCKET:
        client_video_socket = client.client_video_socket
        if client_video_socket is not None and videos.user_video is not None:
            try:
                # parts = encode_image(videos.user_video)
                client_video_socket.sendall(videos.user_video.tobytes())
            except ConnectionAbortedError:
                print("Server ended conversation")
                break
            except ConnectionResetError:
                print("Client ended conversation")
                KILL_SOCKET = True
        sleep(1/30)


def get_audio():
    global KILL_SOCKET, CLIENT_CONNECTED
    while not AUDIO_CONNECTED and not KILL_SOCKET:
        sleep(0.5)
    while not KILL_SOCKET:
        try:
            data = client.client_audio_socket.recv(CHUNK)
        except ConnectionResetError:
            KILL_SOCKET = True
            break
        audio.output_stream.write(data)


def send_audio():
    global KILL_SOCKET, CLIENT_CONNECTED
    while not AUDIO_CONNECTED and not KILL_SOCKET:
        sleep(0.5)
    while not KILL_SOCKET:
        data = audio.input_stream.read(CHUNK)
        client.client_audio_socket.sendall(data)




video_socket_thread = Thread(target=video_socket_connection)
get_video_thread    = Thread(target=get_video)
show_video_thread   = Thread(target=show_video_tk)
send_video_thread   = Thread(target=send_video)
audio_socket_thread = Thread(target=audio_socket_connection)
get_audio_thread    = Thread(target=get_audio)
send_audio_thread   = Thread(target=send_audio)

# video threads
# video_socket_thread.start()
# show_video_thread.start()
# send_video_thread.start()
# get_video_thread.start()
# # audio threads
#
# audio_socket_thread.start()
# send_audio_thread.start()
# get_audio_thread.start()
#
# # join
# get_audio_thread.join()
# send_audio_thread.join()
# get_video_thread.join()
# send_video_thread.join()
# show_video_thread.join()
# video_socket_thread.join()
# audio_socket_thread.join()

root.mainloop()


if client.client_video_socket is not None:
    client.client_video_socket.close()
if client.client_audio_socket is not None:
    client.client_audio_socket.close()


audio.output_stream.stop_stream()
audio.output_stream.close()
audio.input_stream.stop_stream()
audio.input_stream.close()
audio.audio.terminate()
