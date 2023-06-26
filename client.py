import socket
import pickle
import cv2
import numpy
from time import sleep
from threading import Thread


class Server:
    def __init__(self):
        self.socket = None


class VideoToDisplay:
    def __init__(self):
        self.user_video = None
        self.other_video = None




CLIENT_CONNECTED = False
KILL_SOCKET = False
server = Server()
videos = VideoToDisplay()



def main_flow(host='10.100.102.8', port=12345):
    global server, KILL_SOCKET, CLIENT_CONNECTED

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.socket = s
    while not KILL_SOCKET:
        print("Looking for server")
        try:
            s.connect((host, port))
        except TimeoutError:
            continue
        except Exception as e:
            raise e
        break
    server.socket = s
    print(f"Connected to server {host}:{port}")
    CLIENT_CONNECTED = True



def audio_handling():
    pass


def get_video():
    global KILL_SOCKET
    while not KILL_SOCKET:
        client_socket = server.socket
        if client_socket is not None:
            print("Receiving data from client")
            try:
                data = client_socket.recv(50000)
                print("got data")
                videos.other_video = pickle.loads(data)
            except ConnectionAbortedError as e:
                print("Server ended conversation")
                break
            except ConnectionResetError:
                print("Client ended conversation")
            break
        sleep(0.01)


def show_video():
    global KILL_SOCKET
    cap = cv2.VideoCapture(0)
    while not KILL_SOCKET:
        ret, frame = cap.read()
        if not ret:
            continue
        videos.user_video = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        if videos.other_video is not None:
            shape = list(videos.other_video.shpe)
            shape[0] *= 2
            res_image = numpy.zeros(tuple(shape), numpy.uint8)
            res_image[:shape[0] // 2][:] = videos.user_video
            res_image[shape[0] // 2:][:] = videos.other_video
            cv2.imshow('Server', res_image)
        else:
            cv2.imshow('Server', frame[:, ::-1])
        if cv2.waitKey(10) == ord("q"):
            KILL_SOCKET = True


def send_video():
    global KILL_SOCKET
    while not KILL_SOCKET:
        client_socket = server.socket
        if client_socket is not None and videos.user_video is not None:
            try:
                client_socket.sendall(pickle.dumps(videos.user_video))
            except ConnectionAbortedError:
                print("Server ended conversation")
                break
            except ConnectionResetError:
                print("Client ended conversation")
                KILL_SOCKET = True
        sleep(0.01)
    print(f"Send loop over, KILL_SOCKET={KILL_SOCKET}")


main_thread =       Thread(target=main_flow)
get_video_thread =  Thread(target=get_video)
show_video_thread = Thread(target=show_video)
send_video_thread = Thread(target=send_video)
audio_thread =      Thread(target=audio_handling)

main_thread.start()
show_video_thread.start()
send_video_thread.start()
get_video_thread.start()

get_video_thread.join()
send_video_thread.join()
show_video_thread.join()
main_thread.join()

if server.socket is not None:
    server.socket.close()

