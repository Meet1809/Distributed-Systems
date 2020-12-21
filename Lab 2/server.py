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
from dirsync import sync
import distutils.dist
from distutils.core import setup

#setting default Path for directory's CRUD operations
PATH = "C:\\Users\\patel\\Desktop\\DS"
client_path = "C:\\Users\\patel\\Desktop\\DS_clients"
identifiers = ['A','B','C']
identifier_count = 0
client_bind_identifier = {}   #keeps track of which client has which identifier
allocated_dirs = {}          #keeps track of which identifier has which directories
try: 
    for i in range(len(identifiers)):
        allocated_dirs[identifiers[i]] = os.listdir(os.path.join(client_path,identifiers[i]))
except:
    for i in range(len(identifiers)):
        allocated_dirs[identifiers[i]] = os.mkdir(os.path.join(client_path,identifiers[i]))
    

#all os directory operations were referred from this: https://docs.python.org/3/library/os.html

# Pathname manipulations: https://docs.python.org/2/library/os.path.html

#this function will handle all incoming clients by providing them different threads and printing appropriate message for their connection
def incoming_client_connections():
    while True:
        #server socket accepts all incoming client requests nd stores client's address and metadata
        client, client_address = SERVER.accept()
        print("\n%s:{} has connected with address: ".format(client_address)) #prints that client address
        client.send(bytes("\nWelcome! Enter your username and press enter... OR Type (quit) to exit!", FORMAT)) #Welcome message at client window after first client enters the name
        addresses[client] = client_address # client address is stored in addresses array
        Thread(target=handle_client, args=(client,)).start() # starts a new thread

# extra function I wrote by mistake 
def sync_dirs(current_client,current_identifier,no_of_dirs_temp):
    no_of_dirs = no_of_dirs_temp
    
    for i in range(len(no_of_dirs)):
        #https://www.geeksforgeeks.org/python-os-path-join-method/
        src = os.path.join(PATH,no_of_dirs[i])
        dest = os.path.join(os.path.join(client_path,current_identifier),no_of_dirs[i])
        sync(src,dest,'sync')

def handle_client(client):  # Takes client socket as argument. then redirect to commands as per input 
    global identifier_count, client_bind_identifier,client_path,allocated_dirs
    while True:
        #https://pythonpedia.com/en/tutorial/8710/sockets-and-message-encryption-decryption-between-client-and-server
        name = client.recv(buffer_size).decode(FORMAT) #decoding incoming request strings 
        if name == "quit": #if message is quit, client will be disonnected 
            current_client = clients[client]
            #https://www.geeksforgeeks.org/python-get-key-from-value-in-dictionary/
            clients.pop(list(clients.keys())[list(clients.values()).index(current_client)]) #removing client from active_clients 
            message_list_box.insert(tkinter.END,"\nClient {} got offline...".format(current_client))

        elif ',' in name: #handle file operations
            command = name.split(',')[0] #https://www.w3schools.com/python/ref_string_split.asp
            if (command == "create"):
                dir_name = name.split(',')[1]
                new_path = os.path.join(PATH,clients[client])
                if dir_name in os.listdir(new_path):              #https://www.tutorialspoint.com/python/os_listdir.htm
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

                elif (os.path.dirname(old_path)!=os.path.dirname(new_path)) and (os.path.normpath(os.path.commonprefix([old_path,new_path]))!= client_path):  #https://www.geeksforgeeks.org/python-os-path-commonprefix-method/
                    #https://www.geeksforgeeks.org/python-os-path-normpath-method/
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
                # print(old_path)
                # print(new_path)
                # print(os.path.commonprefix([old_path,new_path]))
                # print(Path(os.path.commonprefix([old_path,new_path])))
                if os.path.dirname(old_path) == os.path.dirname(new_path):
                    client.send(bytes("Directory must follow some different path...We can't move directory to same folder(path) Try again",FORMAT))
                
                elif os.path.normpath(os.path.commonprefix([old_path,new_path]))== PATH:
                    client.send(bytes("You can not move your directory to other client",FORMAT))
                else:
                    try:                
                        shutil.move(old_path,new_path)         #https://www.geeksforgeeks.org/python-shutil-move-method/
                        client.send(bytes("Directory moved successfully...",FORMAT))
                    except:
                        client.send(bytes("Requested path or directory does not exists. Try again",FORMAT))

            elif command == "listall":
                all_dirs = str(listalldirectories(clients[client]))
                client.send(bytes(all_dirs,FORMAT))

            elif command == "getpath":
                path = str(getpathalldirs(clients[client]))
                client.send(bytes(path,FORMAT))

            elif command == "copydirs":
                no_of_dirs = (name.split(',')[1]).split('-')
                if set(no_of_dirs).issubset(set(os.listdir(PATH))): #https://www.w3schools.com/python/ref_set_issubset.asp
                    # try:
                    current_client = clients[client]
                    # print(client_bind_identifier)
                    current_identifier = list(client_bind_identifier.keys())[list(client_bind_identifier.values()).index(current_client)]
                    allocated_dirs[current_identifier] = no_of_dirs
                    for i in range(len(no_of_dirs)):

                        # os.mkdir(os.path.join(client_path,current_identifier)) #requested client's copy will be made at client side
                        src = os.path.join(PATH,no_of_dirs[i])   #set source path as requested clients' folders
                        # print(src)
                        dest = os.path.join(os.path.join(client_path,current_identifier),no_of_dirs[i]) #set destination path as local path -> identifier -> given name
                        # print(dest)
                        # shutil.copytree(src,dest)
                        distutils.dir_util.copy_tree(src, dest) #copying files from server to local directory
                        #https://stackoverflow.com/questions/1511808/python-distutils-copy-tree-with-filter

                    client.send(bytes("Files have been copied to local storage successfully ...",FORMAT))

                    # except:
                        # sync(current_client,current_identifier)
                        # client.send("Files have been synchronized successfully...",FORMAT)
                else:
                    client.send(bytes("Some files are not presented on server, check and try again",FORMAT))

            elif command == "sync":
                current_client = clients[client]
                # print("current_client",current_client)
                current_identifier = list(client_bind_identifier.keys())[list(client_bind_identifier.values()).index(current_client)]
                # print(current_client)
                # print("allocated",allocated_dirs)
                # print("current id",current_identifier)
                no_of_dirs_temp = allocated_dirs[current_identifier]
                # print("a",current_identifier)
                # print("b",allocated_dirs)
                # print("c",no_of_dirs_temp)
                for i in range(len(no_of_dirs_temp)):
                    src = os.path.join(PATH,no_of_dirs_temp[i])
                    dest = os.path.join(os.path.join(client_path,current_identifier),no_of_dirs_temp[i])
                    # print(src)
                    # print(dest)
                    #https://www.instructables.com/Syncing-Folders-With-Python/
                    #https://stackoverflow.com/questions/54688687/how-to-synchronize-two-folders-using-python-script
                    sync(src,dest,'sync',purge=True)

            elif command =="desync":
                current_client = clients[client]
                current_identifier = list(client_bind_identifier.keys())[list(client_bind_identifier.values()).index(current_client)]
                # https://stackoverflow.com/questions/13118029/deleting-folders-in-python-recursively'
                no_of_dirs_temp = allocated_dirs[current_identifier]
                # print("new",no_of_dirs_temp)
                for i in range(len(no_of_dirs_temp)):
                    shutil.rmtree(os.path.join(os.path.join(client_path,current_identifier),no_of_dirs_temp[i]))

                client.send(bytes("Your local directories are successfully desynchronized...",FORMAT))

        else: #new client
            #check username characters 
            if not name.isalpha(): #https://www.w3schools.com/python/ref_string_isalpha.asp
                client.send(bytes("Enter valid username ! Illegar characters are not allowed",FORMAT))
                active_clients()

            elif name in clients.values():
                client.send(bytes("Client already there",FORMAT))
                active_clients()

            else:
                #check whether given path exists or not
                # if given user name is present in system, log in the client and give access to directories
                check = os.path.exists(os.path.join(PATH,name))
                if check == True: # if client is already in system, he will be logged in and continue his operaions
                    msg = "\n\n%s has logged in again with HOST ADDRESS: %s and PORT-NUMBER: %s"%(name,HOST,PORT)
                    client.send(bytes("\nWelcome to server again...",FORMAT))
                    message_list_box.insert(tkinter.END,msg)
                    
                    id = identifiers[identifier_count]
                    # print("idd client",id)
                    client.send(bytes("\nYour new Identifier is...",FORMAT))
                    clients[client] = name
                    active_clients()
                    client.send(bytes(id,FORMAT))
                    active_clients()
                    # client.send(bytes("Available local directories",FORMAT))
                    client_bind_identifier[identifiers[identifier_count]] = name
                    message_list_box.insert(tkinter.END,"Clients registered with identifiers...")
                    message_list_box.insert(tkinter.END,client_bind_identifier)
                    client.send(bytes("Available home directories on server",FORMAT))               
                    try:
                        #creating local copy of client's identifier
                        os.mkdir(os.path.join(client_path,identifiers[identifier_count]))
                        identifier_count = identifier_count + 1
                    except:
                        # message_list_box.insert(tkinter.END,"Client has Local copy alredy exists..")
                        identifier_count = identifier_count + 1

                else:     #client will be registered as new one 
                    clients[client] = name
                    # print("idddd",identifier_count)
                    client.send(bytes("\nWelcome to server!",FORMAT))
                    msg = "\n%s has joined with HOST ADDRESS:%s and PORT-NUMBER:%s" % (name, HOST, PORT)
                    message_list_box.insert(tkinter.END,msg)
                    os.mkdir(os.path.join(PATH,name))

                    id = identifiers[identifier_count]
                    # print("idd client",id)
                    client.send(bytes("\nYour new Identifier is...",FORMAT))
                    active_clients()
                    client.send(bytes(id,FORMAT))

                    
                    client_bind_identifier[identifiers[identifier_count]] = name #https://stackoverflow.com/questions/20145154/dictinary-of-dictionary-in-python?rq=1
                    message_list_box.insert(tkinter.END,"Clients registered with identifiers...")
                    message_list_box.insert(tkinter.END,client_bind_identifier)
                    client.send(bytes("Available home directories on server",FORMAT))
                    try:
                        #creating local copy of client's identifier
                        os.mkdir(os.path.join(client_path,identifiers[identifier_count]))
                        identifier_count = identifier_count + 1
                    except:
                        # message_list_box.insert(tkinter.END,"Client has Local copy alredy exists..")
                        identifier_count = identifier_count + 1



def getpathalldirs(client): #returns list of path to all directories for current client
    paths = []
    new_path = os.path.join(PATH,client)
    #https://stackoverflow.com/questions/16953842/using-os-walk-to-recursively-traverse-directories-in-python
    for path, subdirs, files in os.walk(new_path):
        for name in subdirs:
            paths.append(os.path.join(path,name))

    return paths

def listalldirectories(client): #returns all directories at given path
    dirs = []
    #https://stackoverflow.com/questions/16953842/using-os-walk-to-recursively-traverse-directories-in-python
    for a, subdirs, files in os.walk(os.path.join(PATH,client)):
        for name in subdirs:
            dirs.append(name)
    return dirs

def present_clients(): #function used to print all active + inactive clients on server side 
    dirs = []
    for i in os.listdir(PATH):
        dirs.append(i)
    msg = list(dirs)
    message_list_box.insert(tkinter.END,"All clients present in system: (Active and inactive both)\n\n",msg,"\n")

def active_clients(): #function used to print all active clients right now at server 
    display_window =list(clients.values())
    message_list_box.insert(tkinter.END, "\n\n---------Currently active clients:---------\n\n",display_window,"\n")

# def disconnect_client(client):
    # handle_client()
def desync(): #desynchronizes directory and deletes the local directories
    print(allocated_dirs)
    for i in range(len(identifiers)):
        id = identifiers[i]
        no_of_dirs_temp = allocated_dirs[id]
        for j in range(len(no_of_dirs_temp)):
            shutil.rmtree(os.path.join(os.path.join(client_path,id),no_of_dirs_temp[j]))    

def on_quit(root): #to close down server 
    SERVER.shutdown(socket.SHUT_RDWR)
    SERVER.close()
    root.quit()
    

# how threads are created in while loop for all clietns, I took from this site
#https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170

# how to use tkinter, I saw from this site and youtube video 
#https://realpython.com/python-gui-tkinter/
#https://www.youtube.com/watch?v=YXPyB4XeYLA&ab_channel=freeCodeCamp.org

if __name__ == "__main__": #main code
    root = tkinter.Tk() #initialize window manager 
    root.title("Server window") #title of server window
    msg_frame = tkinter.Frame(root)
    scroll_nav = tkinter.Scrollbar(msg_frame)
    
    message_list_box = tkinter.Listbox(msg_frame, height=23, width=75, yscrollcommand=scroll_nav.set)
    scroll_nav.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    message_list_box.pack(side=tkinter.LEFT, fill=tkinter.BOTH)

    message_list_box.insert(tkinter.END, "Waiting for clients to connect:")
    message_list_box.see(tkinter.END)

    message_list_box.pack()
    msg_frame.pack()
    root.protocol("DELETE_WINDOW", on_quit)

    send_button = tkinter.Button(root, text="Active Clients",width= 15, command=active_clients) #button show which clients are active right now 
    send_button.pack() 
    send_button = tkinter.Button(root, text="Present Clients(Active and inactive both)",width= 30, command=present_clients) #button shows which clients are presented on server. they could be active or inactive
    send_button.pack() 
    send_button = tkinter.Button(root, text="Desynchronize all clients: ",width= 30, command=desync) #this will delete all local directories withour permission of clients
    send_button.pack() 


    clients = {} #client's dictionary. maintains, clients' information: client's address and his name
    addresses = {} #i created this dictionary to store addresses but never used it further 

    HOST = "127.0.0.1"
    PORT = 3000
    FORMAT = "utf-8"
    buffer_size = 1024
    ADDR = (HOST, PORT)

    SERVER = socket(AF_INET, SOCK_STREAM)
    SERVER.bind(ADDR) #bind server with his address

    SERVER.listen(3)#can concurrently run 3 clients
    ACCEPT_THREAD = Thread(target=incoming_client_connections)
    ACCEPT_THREAD.start() #starting thread 
    tkinter.mainloop() #starts GUI 
    ACCEPT_THREAD.join()
    SERVER.close()

