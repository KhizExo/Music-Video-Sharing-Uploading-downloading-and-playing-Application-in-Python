import socket
import tkinter as tk
from tkinter import filedialog
from threading import Thread
import os
import pygame
import cv2
from moviepy.editor import VideoFileClip

def is_audio(filename):
    _, file_extension = os.path.splitext(filename)
    return file_extension.lower() in ('.mp3','.wav')
def is_video(filename):
    _, file_extension = os.path.splitext(filename)
    return file_extension.lower() in ('.mp4', '.avi', '.mkv')

def play_audio(filename, quit_callback):
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    
    # New function to handle quitting
    def check_quit():
        pygame.mixer.music.stop()
        quit_callback()
    
    # Create a button to quit
    quit_button = tk.Button(root, text="Quit", command=check_quit)
    quit_button.pack()

def play_video(filename, quit_callback):
    pygame.init()
    video_clip = VideoFileClip(filename)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile("temp_audio.wav")

    # Load the converted audio file
    pygame.mixer.init()
    pygame.mixer.music.load("temp_audio.wav")

    # Play the audio
    pygame.mixer.music.play()

    # Play the video using OpenCV
    cap = cv2.VideoCapture(filename)
    def check_quit(): 
        quit_callback()

    quit_button = tk.Button(root, text="Quit", command=check_quit)
    quit_button.pack()
    while cap.isOpened():
        ret, frame = cap.read() 
        if not ret:
            break
        cv2.imshow("Video", frame)
        if cv2.waitKey(25) & 0xFF == ord("q"):
            break

    # Clean up
    cap.release()
    cv2.destroyAllWindows()
    pygame.mixer.quit()
    pygame.quit()


class FileTransferClient:
    def __init__(self, master):
        self.master = master
        master.title("File Transfer Client")

        self.label = tk.Label(master, text="Enter File name (with extension):")
        self.label.pack()

        self.entry = tk.Entry(master)
        self.entry.pack()

        self.transfer_button = tk.Button(master, text="Transfer File", command=self.transfer_file)
        self.transfer_button.pack()

        # Quit button to be added dynamically
        self.quit_button = None

    def transfer_file(self):
        filename = self.entry.get()
        if not filename:
            return

        # Disable the GUI elements during file transfer
        self.entry.config(state=tk.DISABLED)
        self.transfer_button.config(state=tk.DISABLED)

        # Start a new thread for file transfer to avoid freezing the GUI
        transfer_thread = Thread(target=self.transfer_file_thread, args=(filename,))
        transfer_thread.start()

    def transfer_file_thread(self, filename):
        try:
            # Connect to the server
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('127.0.0.1', 1234))

            # Send the filename to the server
            client_socket.send(filename.encode())

            # Receive the file data from the server and write it to a file
            with open(filename, 'wb') as file:
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    file.write(data)

            # Enable the GUI elements after file transfer is complete
            self.entry.config(state=tk.NORMAL)
            self.transfer_button.config(state=tk.NORMAL)

            # Play the audio or video file
            if is_audio(filename):
                # Pass the quit function to play_audio
                play_audio(filename,self.quit_callback)

            if is_video(filename):
                # Pass the quit function to play_video
                play_video(filename,self.quit_callback)

        except Exception as e:
            print(f"Error: {e}")

        finally:
            # Close the socket
            client_socket.close()

    def quit_callback(self):
        # Destroy the Quit button
        if self.quit_button:
            self.quit_button.destroy()

        # Enable the GUI elements after quitting
        self.entry.config(state=tk.NORMAL)
        self.transfer_button.config(state=tk.NORMAL)

if __name__ == '__main__':
    root = tk.Tk()
    client_app = FileTransferClient(root)
    root.mainloop()
