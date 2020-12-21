#Patel, Meetkumar
#UTA ID: 1001750000

#getting all required libraries
import socket
import tkinter
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from tkinter import *
from threading import *
import os 
import sys
import pickle
from pathlib import Path
import json
import shutil

#setting default Path for directory's CRUD operations
PATH = "C:\\Users\\patel\\Desktop\\DS"

#this function will handle all incoming clients by providing them different threads and printing appropriate message for their connection
def incoming_client_connections():
    while True:
        #server socket accepts all incoming client requests nd stores client's address and metadata
        client, client_address = SERVER.accept()
        print("\n%s:{} has connected with address: ".format(client_address)) #prints that client address
        client.send(bytes("\nWelcome! Enter your username and press enter... OR Type (quit) to exit!", FORMAT)) #Welcome message at client window after first client enters the name
        addresses[client] = client_address # client address is stored in addresses array
        Thread(target=handle_client, args=(client,)).start() # starts a new thread

def handle_client(client):  # Takes client socket as argument.
    while True:
        name = client.recv(buffer_size).decode(FORMAT) #decoding incoming request strings 
        if name == "quit": #if message is quit, client will be disonnected 
            current_client = clients[client]
            clients.pop(list(clients.keys())[list(clients.values()).index(current_client)]) #removing client from active_clients 
            message_list_box.insert(tkinter.END,"\nClient {} got offline...".format(current_client))

        elif ',' in name: #handle file operations
            command = name.split(',')[0]
            if (command == "create"):
                dir_name = name.split(',')[1]
                new_path = os.path.join(PATH,clients[client])
                if dir_name in os.listdir(new_path):
                    client.send(bytes("Directory with same name already exists",FORMAT))
                else:
                    try:            
                        os.mkdir(os.path.join(new_path,dir_name))
                        msg = "Directory {} created...".format(dir_name)
                        client.send(bytes(msg,FORMAT))
                    except:
                        client.send(bytes("Path does not exists",FORMAT))

            elif command == "home":
                path = os.path.join(PATH,clients[client])
                all_dirs = str(os.listdir(path))
                client.send(bytes(all_dirs,FORMAT))

            elif command == "delete":
                new_path = os.path.join(PATH,clients[client])
                dir_name = name.split(',')[1]
                check = os.path.exists(os.path.join(new_path,dir_name))
                if check == False: #directory does not exists
                    client.send(bytes("Directory with entered name does not exists... Try again...",FORMAT))
                else: #directory exists
                    try:
                        os.rmdir(os.path.join(new_path,dir_name))
                        client.send(bytes("Directory {} deleted...".format(dir_name),FORMAT))
                    except:
                        client.send(bytes("Directory contains subdirectories...",FORMAT))

            elif command == "rename":
                dir_names = name.split(',')[1]
                old_name = dir_names.split('-')[0]
                new_name = dir_names.split('-')[1]
                client_path = os.path.join(PATH,clients[client])
                old_path = os.path.join(os.path.join(PATH,clients[client]),old_name)
                new_path = os.path.join(os.path.join(PATH,clients[client]),new_name)
                if os.path.dirname(old_path) != os.path.dirname(new_path):
                    client.send(bytes("Directory must follow the same path... Try again",FORMAT))

                elif os.path.normpath(os.path.commonprefix([old_path,new_path]))!= client_path:
                    client.send(bytes("You can not rename another client's directory",FORMAT))

                else:
                    try:                
                        os.rename(old_path,new_path)
                        client.send(bytes("Directory renamed successfully...",FORMAT))
                    except:
                        client.send(bytes("Requested path or directory does not exists. Try again",FORMAT))
                        
            elif command == "move":
                dir_names = name.split(',')[1]
                client_path = os.path.join(PATH,clients[client])
                os.chdir(client_path)
                old_path = os.path.join(client_path,dir_names.split('-')[0])
                new_path = os.path.join(client_path,dir_names.split('-')[1])
                print(old_path)
                print(new_path)
                print(os.path.commonprefix([old_path,new_path]))
                print(Path(os.path.commonprefix([old_path,new_path])))
                if os.path.dirname(old_path) == os.path.dirname(new_path):
                    client.send(bytes("Directory must follow some different path...We can't move directory to same folder(path) Try again",FORMAT))
                
                elif os.path.normpath(os.path.commonprefix([old_path,new_path]))== PATH:
                    client.send(bytes("You can not move your directory to other client",FORMAT))
                else:
                    try:                
                        shutil.move(old_path,new_path)
                        client.send(bytes("Directory moved successfully...",FORMAT))
                    except:
                        client.send(bytes("Requested path or directory does not exists. Try again",FORMAT))

            elif command == "listall":
                all_dirs = str(listalldirectories(clients[client]))
                client.send(bytes(all_dirs,FORMAT))

            elif command == "getpath":
                path = str(getpathalldirs(clients[client]))
                client.send(bytes(path,FORMAT))

        else: #new client
            #check username characters 
            
            if not name.isalpha():
                client.send(bytes("\nEnter valid username ! Illegar characters are not allowed",FORMAT))
                active_clients()

            elif name in clients.values():
                client.send(bytes("Client already there",FORMAT))
                active_clients()

            else:
                #check whether given path exists or not
                # if given user name is present in system, log in the client and give access to directories
                check = os.path.exists(os.path.join(PATH,name))
                if check == True: # if client is already in system, he will be logged in and continue his operaions
                    msg = "\n%s has logged in again with HOST ADDRESS: %s and PORT-NUMBER: %s"%(name,HOST,PORT)
                    client.send(bytes("\nWelcome to server again...",FORMAT))
                    message_list_box.insert(tkinter.END,msg)
                    clients[client] = name
                    active_clients()
                else:     #client will be registered as new one 
                    clients[client] = name
                    client.send(bytes("\nWelcome to server!",FORMAT))
                    msg = "\n%s has joined with HOST ADDRESS:%s and PORT-NUMBER:%s" % (name, HOST, PORT)
                    message_list_box.insert(tkinter.END,msg)
                    os.mkdir(os.path.join(PATH,name))
                    active_clients()
        
def getpathalldirs(client):
    paths = []
    new_path = os.path.join(PATH,client)
    for path, subdirs, files in os.walk(new_path):
        for name in subdirs:
            paths.append(os.path.join(path,name))

    return paths

def listalldirectories(client):
    dirs = []
    # for i in os.listdir(os.path.join(PATH,client)):
    #     dirs.append(i)

    for a, subdirs, files in os.walk(os.path.join(PATH,client)):
        for name in subdirs:
            dirs.append(name)

    return dirs

def present_clients():
    dirs = []
    for i in os.listdir(PATH):
        dirs.append(i)
    msg = list(dirs)
    message_list_box.insert(tkinter.END,"All clients present in system: (Active and inactive both)\n\n",msg,"\n")

def active_clients():
    display_window =list(clients.values())
    message_list_box.insert(tkinter.END, "\n\n---------Currently active clients:---------\n\n",display_window,"\n")

# def disconnect_client(client):
    # handle_client()

def on_quit(root):
    SERVER.shutdown(socket.SHUT_RDWR)
    SERVER.close()
    root.quit()
    
#https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170
if __name__ == "__main__": #main code
    root = tkinter.Tk() #initialize window manager
    root.title("server window")
    msg_frame = tkinter.Frame(root)
    scroll_nav = tkinter.Scrollbar(msg_frame)
    # Following will contain the messages.
    message_list_box = tkinter.Listbox(msg_frame, height=23, width=75, yscrollcommand=scroll_nav.set)
    scroll_nav.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    message_list_box.pack(side=tkinter.LEFT, fill=tkinter.BOTH)

    message_list_box.insert(tkinter.END, "Waiting for clients to connect:")
    message_list_box.see(tkinter.END)

    message_list_box.pack()
    msg_frame.pack()
    root.protocol("DELETE_WINDOW", on_quit)

    send_button = tkinter.Button(root, text="Active Clients",width= 15, command=active_clients)
    send_button.pack()
    send_button = tkinter.Button(root, text="Present Clients(Active and inactive both)",width= 30, command=present_clients)
    send_button.pack()

    clients = {}
    addresses = {}

    HOST = "127.0.0.1"
    PORT = 3000
    FORMAT = "utf-8"
    buffer_size = 1024
    ADDR = (HOST, PORT)

    SERVER = socket(AF_INET, SOCK_STREAM)
    SERVER.bind(ADDR)

    SERVER.listen(7)#can concurrently run 7 clients
    ACCEPT_THREAD = Thread(target=incoming_client_connections)
    ACCEPT_THREAD.start()
    tkinter.mainloop()
    ACCEPT_THREAD.join()
    SERVER.close()

