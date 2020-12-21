#Patel, Meetkumar
#UTA ID: 1001750000

import socket
import tkinter
import _tkinter
from datetime import datetime
from tkinter import *
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from tkinter import simpledialog    
import os 
import sys
import json
import pickle

clt_act = ""
latest_entry = 0

def receive():
    global latest_entry, clt_act
    while 1:
        message = clt_tcp_socket.recv(buffer_size).decode(FORMAT)
        if message == "quit":
            clt_tcp_socket.close()
            init_window.quit()
        elif message == "Enter valid username ! Illegar characters are not allowed":
            message_box.insert(tkinter.END,message)
            message_box.insert(tkinter.END,"This username is not valid, try again !!!")
        elif message == "Client already there":
            latest_entry = 0 #so that client will be redirected to his inital status
            message_box.insert(tkinter.END,"Client with this username already logged in. Check your username and Try again !!! ")
        else:
            message_box.insert(tkinter.END,message)


def send(event=None):
    global latest_entry
    message = input_txt.get()

    if (message != "quit" and latest_entry == 0):
        clt_tcp_socket.send(bytes(message,FORMAT))
        init_window.title(message)
        input_txt.set("")
        latest_entry = 1

    elif message == "quit":
        clt_tcp_socket.send(bytes("quit", FORMAT))
        clt_tcp_socket.close()
        init_window.quit()
    
    else:
        message_box.insert(tkinter.END,"You have logged in !!! Try CRUD operations")

def select():
    message = input_txt.get()
    if latest_entry!=1 and message!="quit":
        message_box.insert(tkinter.END, "Enter your username first")
        message_box.see(tkinter.END)
    elif message == "quit":
        clt_tcp_socket.send(bytes("quit", FORMAT))
        clt_tcp_socket.close()
        init_window.quit()
    elif message == "home":
        clt_tcp_socket.send(bytes("home,",FORMAT))
        message_box.insert(tkinter.END,"Your home directories are:")
    else:
        msg = "select,"+message
        clt_tcp_socket.send(bytes(msg,FORMAT))


def create():
    message = input_txt.get()
    if latest_entry!=1 and message!="quit":
        message_box.insert(tkinter.END, "Enter your username first")
        message_box.see(tkinter.END)
    elif message == "quit":
        clt_tcp_socket.send(bytes("quit", FORMAT))
        clt_tcp_socket.close()
        init_window.quit()
    elif message == "":
        message_box.insert(tkinter.END,"Enter valid directory/ path to create one")
    else:
        print(message)
        msg = "create,"+message
        clt_tcp_socket.send(bytes(msg,FORMAT))

def move():
    message = input_txt.get()
    if latest_entry!=1 and message!="quit":
        message_box.insert(tkinter.END, "Enter your username first")
        message_box.see(tkinter.END)
    elif message == "quit":
        clt_tcp_socket.send(bytes("quit", FORMAT))
        clt_tcp_socket.close()
        init_window.quit()
    elif message == "":
        message_box.insert(tkinter.END, "Enter directory's path to move")
    else:
        msg = "move,"+message
        clt_tcp_socket.send(bytes(msg,FORMAT))


def delete():
    message = input_txt.get()
    if latest_entry!=1 and message!="quit":
        message_box.insert(tkinter.END, "Enter your username first")
        message_box.see(tkinter.END)
    elif message == "quit":
        clt_tcp_socket.send(bytes("quit", FORMAT))
        clt_tcp_socket.close()
        init_window.quit()
    elif message == "":
        message_box.insert(tkinter.END, "Select any directory to delete")
    else:
        msg = "delete,"+message
        clt_tcp_socket.send(bytes(msg,FORMAT))

def rename():
    message = input_txt.get()
    if latest_entry!=1 and message!="quit":
        message_box.insert(tkinter.END, "Enter your username first")
        message_box.see(tkinter.END)
    elif message == "quit":
        clt_tcp_socket.send(bytes("quit", FORMAT))
        clt_tcp_socket.close()
        init_window.quit()
    elif message == "":
        message_box.insert(tkinter.END, "Enter directories' to rename")
    else:
        msg = "rename,"+message
        clt_tcp_socket.send(bytes(msg,FORMAT))


def listall():
    message = input_txt.get()
    if latest_entry!=1 and message!="quit":
        message_box.insert(tkinter.END, "Enter your username first")
        message_box.see(tkinter.END)
    elif message == "quit":
        clt_tcp_socket.send(bytes("quit", FORMAT))
        clt_tcp_socket.close()
        init_window.quit()
    elif latest_entry == 0:
        message_box.insert(tkinter.END,"Re enter your username")
    else:
        msg = "listall," +"dir"
        clt_tcp_socket.send(bytes(msg,FORMAT))
        message_box.insert(tkinter.END,"All your directories are: ")


def getpath():
    message = input_txt.get()
    if latest_entry!=1 and message!="quit":
        message_box.insert(tkinter.END, "Enter your username first")
        message_box.see(tkinter.END)
    elif message == "quit":
        clt_tcp_socket.send(bytes("quit", FORMAT))
        clt_tcp_socket.close()
        init_window.quit()
    elif latest_entry == 0:
        message_box.insert(tkinter.END,"Re enter your username")
    else:
        msg = "getpath," +"dir"
        clt_tcp_socket.send(bytes(msg,FORMAT))
        message_box.insert(tkinter.END,"Path to all of your directories are: ")

def close_window(event1=None):
    clt_tcp_socket.send(bytes("quit", FORMAT))
    clt_tcp_socket.close()
    init_window.quit()

#https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170
if __name__ == "__main__":

    init_window = tkinter.Tk()
    init_window.title("Directory management | client side")
    msg_frame = tkinter.Frame(init_window)
    input_txt = tkinter.StringVar()
    input_txt.set("Username...")
    input_txt2 = tkinter.StringVar()
    input_txt2.set("New Name for file")
    scroll_nav = tkinter.Scrollbar(msg_frame)
    message_box = tkinter.Listbox(msg_frame, height=23, width=75, yscrollcommand=scroll_nav.set)
    scroll_nav.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    message_box.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
    message_box.pack()
    msg_frame.pack()
    
    input_field = tkinter.Entry(init_window, textvariable=input_txt)
    input_field.bind("<Return>", send)
    input_field.pack()

    # input_field2 = tkinter.Entry(init_window, textvariable=input_txt2)
    # input_field2.bind("<Return>", rename)

    send_button = tkinter.Button(init_window, text="Enter username",width= 15, command=send)
    send_button.pack()
    send_button = tkinter.Button(init_window, text="Select directory",width= 15, command=select)
    send_button.pack()
    send_button = tkinter.Button(init_window, text="Create directory",width= 15, command=create)
    send_button.pack()
    send_button = tkinter.Button(init_window, text="Delete directory",width= 15, command=delete)
    send_button.pack()
    send_button = tkinter.Button(init_window, text="Move directory",width= 15, command=move)
    send_button.pack()
    send_button = tkinter.Button(init_window, text="Rename directory",width= 15, command=rename)
    # input_field2.pack()
    send_button.pack()
    send_button = tkinter.Button(init_window, text="List all directories",width= 15, command=listall)
    send_button.pack()
    send_button = tkinter.Button(init_window, text="Get path to all directories",width= 25, command=getpath)
    send_button.pack()

    # ----Sockets Configuaration----
    HOST = "127.0.0.1"
    FORMAT = "utf-8"
    PORT = 3000

    buffer_size = 1024
    ADDR = (HOST, PORT)

    clt_tcp_socket = socket(AF_INET, SOCK_STREAM)
    clt_tcp_socket.connect(ADDR)
    
    receive_thread = Thread(target=receive)
    receive_thread.start()
    tkinter.mainloop()
