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
from dirsync import sync
import json
import pickle

#all os directory operations were referred from this: https://docs.python.org/3/library/os.html

# Pathname manipulations: https://docs.python.org/2/library/os.path.html

latest_entry = 0 #to kepp track of whether username has been entered or not 
client_path = "C:\\Users\\patel\\Desktop\\DS_clients" #address to local directory storage
server_path = "C:\\Users\\patel\\Desktop\\DS\\" #address to server directory storage
identifier = 'a' #default value of identifier variable 

def receive(): #received messages from server come here and will print output accordingly on window
    global latest_entry,identifier
    while 1:
        message = client_socket.recv(buffer_size).decode(FORMAT)  #decoding received message
        # print("m",message)
        if message == "quit":
            client_socket.close() #if quit, client will be closed and disconnected
            init_window.quit()
        elif message == "Enter valid username ! Illegar characters are not allowed":
            latest_entry = 0
            message_box.insert(tkinter.END,message)
            message_box.insert(tkinter.END,"This username is not valid, try again !!!")
            latest_entry = 0
        elif message == "Client already there":
            latest_entry = 0 #so that client will be redirected to his inital status
            message_box.insert(tkinter.END,"Client with this username already logged in. Check your username and Try again !!! ")
            latest_entry = 0 #so that client will be redirected to his inital status
        elif message == 'A' and (len(message) == 1): #assigning identifiers to clients
            identifier = message
            print("Your client id is: ",identifier)
            message_box.insert(tkinter.END,identifier)
        elif message == 'B' and (len(message) == 1):
            identifier = message
            print("Your client id is: ",identifier)
            message_box.insert(tkinter.END,identifier)
        elif message == 'C' and (len(message) == 1):
            identifier = message
            print("Your client id is: ",identifier)
            message_box.insert(tkinter.END,identifier)
        elif message == "Available home directories on server":  
            message_box.insert(tkinter.END,"**********"+message+"**********")
            printing_dirs(server_path)
        else:
            message_box.insert(tkinter.END,message) #printing message on tkinter


def send(event=None): #send given text input to server via client socket
    global latest_entry
    message = input_txt.get()
    if (message != "quit" and latest_entry == 0):
        client_socket.send(bytes(message,FORMAT))
        init_window.title(message)  #printing title on window
        input_txt.set("")
        latest_entry = 1

    elif message == "quit":
        client_socket.send(bytes("quit", FORMAT))
        client_socket.close() #close client socket
        init_window.quit()
    elif latest_entry == 0:
        message_box.insert(tkinter.END,"Re enter your username")

    else:
        message_box.insert(tkinter.END,"You have logged in !!! Try CRUD operations")

def select(): #select home directory and give current present directories in it 
    message = input_txt.get()
    if latest_entry!=1 and message!="quit":
        message_box.insert(tkinter.END, "Enter your username first")
        message_box.see(tkinter.END)
    elif message == "quit":
        client_socket.send(bytes("quit", FORMAT))
        client_socket.close()
        init_window.quit()
    elif message == "home":
        client_socket.send(bytes("home,",FORMAT))
        message_box.insert(tkinter.END,"Your home directories are:")
    else:
        msg = "select,"+message
        client_socket.send(bytes(msg,FORMAT)) #sending encoded message string to client socket , from where, server will read it 


def create(): #creating directory
    message = input_txt.get()
    if latest_entry!=1 and message!="quit":
        message_box.insert(tkinter.END, "Enter your username first")
        message_box.see(tkinter.END)
    elif message == "quit":
        client_socket.send(bytes("quit", FORMAT))
        client_socket.close()
        init_window.quit()
    elif message == "":
        message_box.insert(tkinter.END,"Enter valid directory/ path to create one")
    else:
        print(message)
        msg = "create,"+message
        client_socket.send(bytes(msg,FORMAT)) #sending encoded message string to client socket , from where, server will read it 

def move(): #moving directory
    message = input_txt.get()
    if latest_entry!=1 and message!="quit":
        message_box.insert(tkinter.END, "Enter your username first")
        message_box.see(tkinter.END)
    elif message == "quit":
        client_socket.send(bytes("quit", FORMAT)) #sending encoded message string to client socket , from where, server will read it 
        client_socket.close()
        init_window.quit()
    elif message == "":
        message_box.insert(tkinter.END, "Enter directory's path to move")
    else:
        msg = "move,"+message
        client_socket.send(bytes(msg,FORMAT))


def delete(): #deleting directory
    message = input_txt.get()
    if latest_entry!=1 and message!="quit":
        message_box.insert(tkinter.END, "Enter your username first")
        message_box.see(tkinter.END)
    elif message == "quit":
        client_socket.send(bytes("quit", FORMAT))
        client_socket.close()
        init_window.quit()
    elif message == "":
        message_box.insert(tkinter.END, "Select any directory to delete")
    else:
        msg = "delete,"+message
        client_socket.send(bytes(msg,FORMAT))

def rename(): #renaming directory
    message = input_txt.get()
    if latest_entry!=1 and message!="quit":
        message_box.insert(tkinter.END, "Enter your username first")
        message_box.see(tkinter.END)
    elif message == "quit":
        client_socket.send(bytes("quit", FORMAT))
        client_socket.close()
        init_window.quit()
    elif message == "":
        message_box.insert(tkinter.END, "Enter directories' to rename")
    else:
        msg = "rename,"+message
        client_socket.send(bytes(msg,FORMAT))


def listall(): #listing all directories presented in client folder on server side
    message = input_txt.get()
    print("eer",latest_entry)
    if latest_entry!=1 and message!="quit":
        message_box.insert(tkinter.END, "Enter your username first")
        message_box.see(tkinter.END)
    elif message == "quit":
        client_socket.send(bytes("quit", FORMAT))
        client_socket.close()
        init_window.quit()
    elif latest_entry == 0:
        message_box.insert(tkinter.END,"Re enter your username")
    else:
        msg = "listall," +"dir"
        client_socket.send(bytes(msg,FORMAT))
        message_box.insert(tkinter.END,"All your directories are: ")


def getpath(): #get path of all directories in list format (so that we can have some help while renaming, moving and deleting directories)
    message = input_txt.get() 
    if latest_entry!=1 and message!="quit":
        message_box.insert(tkinter.END, "Enter your username first")
        message_box.see(tkinter.END)
    elif message == "quit":
        client_socket.send(bytes("quit", FORMAT))
        client_socket.close()
        init_window.quit()
    elif latest_entry == 0:
        message_box.insert(tkinter.END,"Re enter your username")
    else:
        msg = "getpath," +"dir"
        client_socket.send(bytes(msg,FORMAT))
        message_box.insert(tkinter.END,"Path to all of your directories are: ")

def close_window(event1=None): #closing window by clicking quit
    client_socket.send(bytes("quit", FORMAT))
    client_socket.close()
    init_window.quit()

def dirs_to_copy(): #function copies files from server end to client end 
    message = input_txt.get()
    if latest_entry!=1 and message!="quit":
        message_box.insert(tkinter.END, "Enter your username first")
        message_box.see(tkinter.END)
    elif message == "quit":
        client_socket.send(bytes("quit", FORMAT))
        client_socket.close()
        init_window.quit()
    elif latest_entry == 0 or message == "":
        message_box.insert(tkinter.END,"Enter directories you want on your local copy")
    else:
        msg = "copydirs,"+message
        client_socket.send(bytes(msg,FORMAT))

def serverhomedirs(): #this button will give server end home directories
    message = input_txt.get()
    if message == "serverhome":
        message_box.insert(tkinter.END,"Home directories on server are ... ")
        printing_dirs(server_path)
    else:
        message_box.insert(tkinter.END,"Enter string to get home directories")

def printing_dirs(path): #printing directories on client's end in pretty manner
    path = path
    # print(path)
    for root, dirs, files in os.walk(path): #https://stackoverflow.com/questions/9727673/list-directory-tree-structure-in-python
        level = root.replace(path, '').count(os.sep)
        indent = ' ' * 15 * (level)
        a = '{}{}/'.format(indent, os.path.basename(root))
        message_box.insert(tkinter.END,a)
        subindent = ' ' * 15 * (level + 1)
        for f in files:
            b = '{}{}'.format(subindent, f)
            message_box.insert(tkinter.END,b)

def desync(): #this function will desynchronize all local directories in the current client
    message = input_txt.get()
    if latest_entry!=1 and message!="quit":
        message_box.insert(tkinter.END, "Enter your username first")
        message_box.see(tkinter.END)
    elif message == "quit":
        client_socket.send(bytes("quit", FORMAT))
        client_socket.close()
        init_window.quit()
    elif latest_entry == 0:
        message_box.insert(tkinter.END,"Re enter your username")
    else:
        msg = "desync,"+"dir"
        client_socket.send(bytes(msg,FORMAT))
        # message_box.insert(tkinter.END,"Local copies are: ")
        printing_dirs(os.path.join(client_path,identifier))

def sync(): #synchronizes server side directories and LDs
    message = input_txt.get()
    if latest_entry!=1 and message!="quit":
        message_box.insert(tkinter.END, "Enter your username first")
        message_box.see(tkinter.END)
    elif message == "quit":
        client_socket.send(bytes("quit", FORMAT))
        client_socket.close()
        init_window.quit()
    elif latest_entry == 0:
        message_box.insert(tkinter.END,"Re enter your username")
    else:
        msg = "sync,"+"dir"
        client_socket.send(bytes(msg,FORMAT))
        message_box.insert(tkinter.END,"Local copies are: ")
        printing_dirs(os.path.join(client_path,identifier))


# how to use tkinter, I saw from this site and youtube video 
#https://realpython.com/python-gui-tkinter/

#https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170

#code starts here
if __name__ == "__main__":

    init_window = tkinter.Tk() #creating window from tkinter 
    init_window.title("Directory management | client side") #title of the window 
    msg_frame = tkinter.Frame(init_window) #intializing window frame
    input_txt = tkinter.StringVar()
    input_txt.set("Username...") #the string is used for giving hint to client 
    input_txt2 = tkinter.StringVar() # For the messages to be sent.
    input_txt2.set("New Name for file")
    scroll_nav = tkinter.Scrollbar(msg_frame) # To navigate through past messages.
    message_box = tkinter.Listbox(msg_frame, height=23, width=75, yscrollcommand=scroll_nav.set) #creating box size and dimensions 
    scroll_nav.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    message_box.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
    message_box.pack()
    msg_frame.pack()
    
    input_field = tkinter.Entry(init_window, textvariable=input_txt)
    input_field.bind("<Return>", send)
    input_field.pack()

    # input_field2 = tkinter.Entry(init_window, textvariable=input_txt2)
    # input_field2.bind("<Return>", rename)

    #tkinter.Button is used to create a button on window 
    #https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170
    
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
    send_button = tkinter.Button(init_window, text="home Directories on server",width= 25, command=serverhomedirs)
    send_button.pack()
    send_button = tkinter.Button(init_window,text = "Sync",width = 15,command = sync)
    send_button.pack()
    send_button = tkinter.Button(init_window,text = "Directories you want to copy on your local system",width = 45, command= dirs_to_copy)
    send_button.pack()
    send_button = tkinter.Button(init_window,text = "Desynchronize",width = 20, command= desync)
    send_button.pack()

    # ----Sockets Configuaration----
    HOST = "127.0.0.1"
    FORMAT = "utf-8"
    PORT = 3000

    buffer_size = 1024
    ADDR = (HOST, PORT)

    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect(ADDR)
    
    receive_thread = Thread(target=receive)
    receive_thread.start() #starting thread
    tkinter.mainloop() #starts GUI
