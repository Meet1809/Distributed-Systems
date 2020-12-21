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
import logging
import datetime

# logger = logging.getLogger(__name__)

# logger.setLevel(logging.INFO)
# formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')

#setting default Path for directory's CRUD operations

PATH = "C:\\Users\\patel\\Desktop\\DS"
client_path = "C:\\Users\\patel\\Desktop\\DS_clients"
identifiers = ['A','B','C']
identifier_count = 0
client_bind_identifier = {}   #keeps track of which client has which identifier
allocated_dirs = {}          #keeps track of which identifier has which directories
allocated_log_files = {}

log_client_A = []
log_client_B = []
log_client_C = []
files = [log_client_A,log_client_B,log_client_C]
allocated_log_files = dict(zip(identifiers,files)) #keep track of log files to each identifier
deleted_A = []
deleted_B = []
deleted_C = []
deleted_files_list = [deleted_A,deleted_B,deleted_C]
deleted_files = dict(zip(identifiers,deleted_files_list)) #to keep track of deleted files by each client

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


def sync_dirs():                         # synchronization function to sync local directories with server side directories
    # no_of_dirs = no_of_dirs_temp
    
    # for i in range(len(no_of_dirs)):
    #     #https://www.geeksforgeeks.org/python-os-path-join-method/
    #     src = os.path.join(PATH,no_of_dirs[i])
    #     dest = os.path.join(os.path.join(client_path,current_identifier),no_of_dirs[i])
    #     sync(src,dest,'sync',purge=True)

    for j in identifiers: #SYNC local directories with server directories
        no_of_dirs_temp = allocated_dirs[j]
        # print("id",j)
        # print("then ",no_of_dirs_temp)
        for i in range(len(no_of_dirs_temp)):
            src = os.path.join(PATH,no_of_dirs_temp[i])
            dest = os.path.join(os.path.join(client_path,j),no_of_dirs_temp[i])
            print("src",src)
            print("dest",dest)
            sync(src,dest,'sync',purge=True)

def handle_client(client):  # Takes client socket as argument. then redirect to commands as per input 
    global identifier_count, client_bind_identifier,client_path,allocated_dirs,allocated_log_files,deleted_files
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

            #getting log file for current client
            current_client = clients[client] #current client name 
            current_identifier = list(client_bind_identifier.keys())[list(client_bind_identifier.values()).index(current_client)] #current client identifier

            if (command == "create"): #this will be executed upon create command
                dir_name = name.split(',')[1]
                new_path = os.path.join(PATH,clients[client])
                if dir_name in os.listdir(new_path):              #https://www.tutorialspoint.com/python/os_listdir.htm
                    client.send(bytes("Directory with same name already exists",FORMAT))
                else:
                    try:
                        os.mkdir(os.path.join(new_path,dir_name))
                        msg = "Created {}".format(dir_name)
                        client.send(bytes("Directory {} created...".format(dir_name),FORMAT))

                        #showing log on server window 
                        message_list_box.insert(tkinter.END,"Log :: {} :: [Client {}]: ".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),current_identifier) + msg)
                        allocated_log_files.get(current_identifier).append(msg) ################## appending message as log to current identifier 

                        # for j in identifiers: #SYNC local directories with server directories
                        #     no_of_dirs_temp = allocated_dirs[j]
                        #     print("id",j)
                        #     print("then ",no_of_dirs_temp)
                        #     for i in range(len(no_of_dirs_temp)):
                        #         src = os.path.join(PATH,no_of_dirs_temp[i])
                        #         dest = os.path.join(os.path.join(client_path,j),no_of_dirs_temp[i])
                        #         sync(src,dest,'sync',purge=True)
                    
                    except:
                        client.send(bytes("Path does not exists",FORMAT))

                    sync_dirs() #synchronization local directories


            elif command == "home":
                path = os.path.join(PATH,clients[client])
                all_dirs = str(os.listdir(path))
                client.send(bytes(all_dirs,FORMAT))

            elif command == "delete": #this will be executed upon delete command
                new_path = os.path.join(PATH,clients[client])
                dir_name = name.split(',')[1]
                check = os.path.exists(os.path.join(new_path,dir_name))
                if check == False: #directory does not exists
                    client.send(bytes("Directory with entered name does not exists... Try again...",FORMAT))
                else: #directory exists
                    try:
                        os.rmdir(os.path.join(new_path,dir_name))
                        msg = "Deleted {}".format(dir_name)
                        client.send(bytes("Directory {} deleted...".format(dir_name),FORMAT))
                        allocated_log_files.get(current_identifier).append(msg) ##################appending log data to log file
                        #showing log on server window 
                        message_list_box.insert(tkinter.END,"Log :: {} :: [Client {}]: ".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),current_identifier) + msg)

                        deleted_files.get(current_identifier).append(msg)
                        print("deleted files ",deleted_files)

                    except: #exception so that program doesn't get stuck
                        client.send(bytes("Directory contains subdirectories...",FORMAT))

                    sync_dirs() #synchronization local directories

            elif command == "rename": #this will be executed upon rename command
                dir_names = name.split(',')[1]
                old_name = dir_names.split('-')[0]
                new_name = dir_names.split('-')[1]
                client_path_temp = os.path.join(PATH,clients[client])
                old_path = os.path.join(os.path.join(PATH,clients[client]),old_name)
                new_path = os.path.join(os.path.join(PATH,clients[client]),new_name)
                if os.path.dirname(old_path) != os.path.dirname(new_path):
                    client.send(bytes("Directory must follow the same path... Try again",FORMAT))

                elif (os.path.dirname(old_path)!=os.path.dirname(new_path)) and (os.path.normpath(os.path.commonprefix([old_path,new_path]))!= client_path_temp):  
                    #https://www.geeksforgeeks.org/python-os-path-commonprefix-method/
                    #https://www.geeksforgeeks.org/python-os-path-normpath-method/
                    client.send(bytes("You can not rename another client's directory",FORMAT)) #if client wants to move his directory to other client, this will pop up

                else:
                    try:                
                        os.rename(old_path,new_path)
                        msg = "Renamed {} to {}".format(old_name,new_name)
                        client.send(bytes("Directory renamed successfully...",FORMAT))
                        allocated_log_files.get(current_identifier).append(msg) ################## appending log data to log file
                        #showing log on server window 
                        message_list_box.insert(tkinter.END,"Log :: {} :: [Client {}]: ".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),current_identifier) + msg)

                    except: #exception so that program doesn't get stuck
                        client.send(bytes("Requested path or directory does not exists. Try again",FORMAT))

                    sync_dirs() #synchronization local directories
                        
            elif command == "move": #this will be executed upon move command
                dir_names = name.split(',')[1]
                client_path_temp = os.path.join(PATH,clients[client])
                os.chdir(client_path_temp)
                old_path = os.path.join(client_path_temp,dir_names.split('-')[0])
                new_path = os.path.join(client_path_temp,dir_names.split('-')[1])

                # if os.path.dirname(old_path) == os.path.dirname(new_path):
                #     client.send(bytes("Directory must follow some different path...We can't move directory to same folder(path) Try again",FORMAT))
                
                if os.path.normpath(os.path.commonprefix([old_path,new_path]))== PATH:
                    client.send(bytes("You can not move your directory to other client",FORMAT))
                else:
                    try:                
                        shutil.move(old_path,new_path)         #https://www.geeksforgeeks.org/python-shutil-move-method/
                        msg = "Moved {} to {}".format(dir_names.split('-')[0],dir_names.split('-')[1])
                        client.send(bytes("Directory moved successfully...",FORMAT))
                        allocated_log_files.get(current_identifier).append(msg) ################## appending log data to log file
                        #showing log on server window 
                        message_list_box.insert(tkinter.END,"Log :: {} :: [Client {}]: ".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),current_identifier) + msg)

                    except:
                        client.send(bytes("Requested path or directory does not exists. Try again",FORMAT))

                    sync_dirs() #synchronization local directories

            elif command == "listall":
                all_dirs = str(listalldirectories(clients[client]))
                client.send(bytes(all_dirs,FORMAT))

            elif command == "getpath":
                path = str(getpathalldirs(clients[client]))
                client.send(bytes(path,FORMAT))

            elif command == "copydirs":
                no_of_dirs = (name.split(',')[1]).split('-')
                if set(no_of_dirs).issubset(set(os.listdir(PATH))): #https://www.w3schools.com/python/ref_set_issubset.asp
                    current_client = clients[client]
                    current_identifier = list(client_bind_identifier.keys())[list(client_bind_identifier.values()).index(current_client)]
                    allocated_dirs[current_identifier] = no_of_dirs
                    # print("allocated dirs",allocated_dirs)
                    for i in range(len(no_of_dirs)):
                        src = os.path.join(PATH,no_of_dirs[i])   #set source path as requested clients' folders
                        dest = os.path.join(os.path.join(client_path,current_identifier),no_of_dirs[i]) #set destination path as local path -> identifier -> given name

                        distutils.dir_util.copy_tree(src, dest) #copying files from server to local directory
                        #https://stackoverflow.com/questions/1511808/python-distutils-copy-tree-with-filter

                    client.send(bytes("Files have been copied to local storage successfully ...",FORMAT))

                else:
                    client.send(bytes("Some files are not presented on server, check and try again",FORMAT))

            elif command == "sync":

                current_client = clients[client]
                current_identifier = list(client_bind_identifier.keys())[list(client_bind_identifier.values()).index(current_client)]
                no_of_dirs_temp = allocated_dirs[current_identifier]
                # sync_dirs(current_client,current_identifier,no_of_dirs_temp)
                sync_dirs()

                # for i in range(len(no_of_dirs_temp)):
                #     src = os.path.join(PATH,no_of_dirs_temp[i])
                #     dest = os.path.join(os.path.join(client_path,current_identifier),no_of_dirs_temp[i])
                #     #https://www.instructables.com/Syncing-Folders-With-Python/
                #     #https://stackoverflow.com/questions/54688687/how-to-synchronize-two-folders-using-python-script
                #     sync(src,dest,'sync',purge=True)

            elif command =="desync":
                current_client = clients[client]
                current_identifier = list(client_bind_identifier.keys())[list(client_bind_identifier.values()).index(current_client)]
                # https://stackoverflow.com/questions/13118029/deleting-folders-in-python-recursively'
                no_of_dirs_temp = allocated_dirs[current_identifier]
                # print("new",no_of_dirs_temp)
                for i in range(len(no_of_dirs_temp)):
                    shutil.rmtree(os.path.join(os.path.join(client_path,current_identifier),no_of_dirs_temp[i]))

                client.send(bytes("Your local directories are successfully desynchronized...",FORMAT))

            elif command == "logs": #this function will return logs of a client on his window in a list format
                logs = str(allocated_log_files.get(current_identifier))
                client.send(bytes(logs,FORMAT)) 
            
            elif command == "undo": #this will handle UNDO operations from client 
                sub_command = name.split(',')[1] 
                new_command = sub_command.split(" ")[0].lower() #first string of command will decide which operation to perform

                #we will check given command exists in log file or not
                logs = allocated_log_files.get(current_identifier)
                if sub_command not in logs: #on entering invalid command, error will be given to client 
                    client.send(bytes("Enter valid log operations to UNDO it....",FORMAT))
                
                elif sub_command != logs[-1]:  #if the command is not on last position in the log file
                    # client.send(bytes("Enter latest operation from logs to UNDO it, UNDO must be done sequential ",FORMAT))
                    #performing all operations reversely turn by turn | though, I never used this list
                    operations_to_perform = logs[logs.index(sub_command):] #https://www.geeksforgeeks.org/python-remove-all-values-from-a-list-present-in-other-list/
                    print("operations: ",operations_to_perform)
                    
                    if new_command == "created": #if the command is created, we will delete the same directory to UNDO the operation
                        try:
                            a = undo_created(clients[client],sub_command.split(" ")[1],allocated_log_files.get(current_identifier),sub_command.split(" ")[1])
                            allocated_log_files[current_identifier] = a #UPDATE the log file
                            client.send(bytes("Director(y)ies deleted...",FORMAT))
                            msg = "Director(y)ies deleted..."
                            #showing log on server window
                            message_list_box.insert(tkinter.END,"Log :: {} :: [Client {}]: ".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),current_identifier) + msg)

                        except:
                            client.send(bytes("Try again...",FORMAT))
                        sync_dirs() #synchronization local directories
                    
                    elif new_command == "deleted": #we need to create the requested directory for this command to UNDO the operation
                        dir_name = sub_command.split(" ")[1]
                        new_path = os.path.join(PATH,clients[client])
                        if dir_name in os.listdir(new_path):
                            client.send(bytes("Directory with same name already exists",FORMAT))
                        else:
                            try:
                                os.mkdir(os.path.join(new_path,dir_name))
                                msg = "Directory {} created...".format(dir_name)
                                client.send(bytes("Directory {} created...".format(dir_name),FORMAT))
                                
                                a = [i for i in allocated_log_files.get(current_identifier) if i not in sub_command]
                                allocated_log_files[current_identifier] = a#UPDATE the log file
                                #showing log on server window
                                message_list_box.insert(tkinter.END,"Log :: {} :: [Client {}]: ".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),current_identifier) + msg)

                            except:
                                client.send(bytes("ERROR UNDOing operation! Try again",FORMAT))
                            sync_dirs() #synchronization local directories

                    elif new_command == "renamed":
                        # client.send(bytes("Enter latest operation from logs to UNDO-Rename it",FORMAT))
                        client_path_temp = os.path.join(PATH,clients[client])
                        os.chdir(client_path_temp)
                        old_name = sub_command.split(" ")[3]
                        new_name = sub_command.split(" ")[1]
                        old_path = os.path.join(client_path_temp,old_name)
                        new_path = os.path.join(client_path_temp,new_name)
                        try:                
                            os.rename(old_path,new_path)
                            msg = "Renamed {} to {}".format(old_name,new_name)
                            client.send(bytes("Directory renamed successfully...",FORMAT))
                            a = [i for i in allocated_log_files.get(current_identifier) if i not in sub_command]
                            allocated_log_files[current_identifier] = a#UPDATE the log file
                            message_list_box.insert(tkinter.END,"Log :: {} :: [Client {}]: ".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),current_identifier) + msg)
                            
                        except:
                            client.send(bytes("ERROR UNDOing operation! Try again",FORMAT))
                        sync_dirs() #synchronization local directories

                    elif new_command == "moved": #we need to move the requested directory to original place for this command to UNDO the operation
                        client_path_temp = os.path.join(PATH,clients[client])
                        os.chdir(client_path_temp)
                        new_path = os.path.join(client_path_temp,sub_command.split(" ")[1])
                        old_path = os.path.join(client_path_temp,os.path.join(sub_command.split(" ")[3],sub_command.split(" ")[1]))
                        # print("old: ",old_path)
                        # print("new: ",new_path)

                        try:                
                            shutil.move(old_path,new_path)
                            # msg = "Moved {} to {}".format(new_path,old_path)
                            msg = "Moved successfully..."
                            client.send(bytes("Directory moved successfully...",FORMAT))
                            a = [i for i in allocated_log_files.get(current_identifier) if i not in sub_command]
                            allocated_log_files[current_identifier] = a ###################UPDATE the log file
                            message_list_box.insert(tkinter.END,"Log :: {} :: [Client {}]: ".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),current_identifier) + msg)

                        except:
                            client.send(bytes("ERROR UNDOing operation! Try again",FORMAT))
                        sync_dirs() #synchronization local directories

                else: #if the command is last position in the log file 
                    if new_command == "created": #we need to delete the requested directory for this command to UNDO the operation
                        new_path = os.path.join(PATH,clients[client])
                        dir_name = sub_command.split(" ")[1]
                        try:
                            os.rmdir(os.path.join(new_path,dir_name))
                            msg = "Directory {} deleted...".format(dir_name)
                            client.send(bytes("Directory {} deleted...".format(dir_name),FORMAT))
                            #remove log operation from log file
                            allocated_log_files.get(current_identifier).pop()
                            message_list_box.insert(tkinter.END,"Log :: {} :: [Client {}]: ".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),current_identifier) + msg)

                        except:
                            client.send(bytes("ERROR UNDOing operation! Try again",FORMAT))
                        sync_dirs() #synchronization local directories

                    elif new_command == "deleted": #we need to create the requested directory for this command to UNDO the operation
                        dir_name = sub_command.split(" ")[1]
                        new_path = os.path.join(PATH,clients[client])
                        if dir_name in os.listdir(new_path):
                            client.send(bytes("Directory with same name already exists",FORMAT))
                        else:
                            try:
                                os.mkdir(os.path.join(new_path,dir_name))
                                msg = "Directory {} created...".format(dir_name)
                                client.send(bytes("Directory {} created...".format(dir_name),FORMAT))
                                allocated_log_files.get(current_identifier).pop()
                                message_list_box.insert(tkinter.END,"Log :: {} :: [Client {}]: ".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),current_identifier) + msg)

                            except:
                                client.send(bytes("ERROR UNDOing operation! Try again",FORMAT))
                            sync_dirs() #synchronization local directories


                    elif new_command == "moved": #we need to move the requested directory to original place for this command to UNDO the operation
                        client_path_temp = os.path.join(PATH,clients[client])
                        os.chdir(client_path_temp)
                        new_path = os.path.join(client_path_temp,sub_command.split(" ")[1])
                        old_path = os.path.join(client_path_temp,os.path.join(sub_command.split(" ")[3],sub_command.split(" ")[1]))

                        try:                
                            shutil.move(old_path,new_path)
                            msg = "Directory moved successfully..."
                            client.send(bytes("Directory moved successfully...",FORMAT))
                            allocated_log_files.get(current_identifier).pop() ##################
                            message_list_box.insert(tkinter.END,"Log :: {} :: [Client {}]: ".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),current_identifier) + msg)

                        except:
                            client.send(bytes("ERROR UNDOing operation! Try again",FORMAT))

                        sync_dirs() #synchronization local directories
                    
                    elif new_command == "renamed": #if command is renamed
                        client_path_temp = os.path.join(PATH,clients[client])
                        os.chdir(client_path_temp)
                        old_name = sub_command.split(" ")[3]
                        new_name = sub_command.split(" ")[1]

                        old_path = os.path.join(client_path_temp,old_name)
                        new_path = os.path.join(client_path_temp,new_name)

                        try:                
                            os.rename(old_path,new_path)
                            msg = "Renamed {} to {}".format(old_name,new_name)
                            client.send(bytes("Directory renamed successfully...",FORMAT))
                            allocated_log_files.get(current_identifier).pop() ##################
                            message_list_box.insert(tkinter.END,"Log :: {} :: [Client {}]: ".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),current_identifier) + msg)
                            
                        except:
                            client.send(bytes("ERROR UNDOing operation! Try again",FORMAT))
                        sync_dirs() #synchronization local directories

                    else: 
                        client.send(bytes("ERROR UNDOing operation! Try again",FORMAT))

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


def undo_created(name,x,ls,prefix_dir): #this function will help in sequence dependent operations
    temp_client_path = os.path.join(os.path.join(PATH,name),x)
    temp_subdirs = os.listdir(temp_client_path)
    if len(temp_subdirs)==0:
        os.rmdir(temp_client_path)
        ls.remove("Created "+prefix_dir)
    else:
        for i in temp_subdirs:
            ls = undo_created(name+"//"+x,i,ls,prefix_dir+"/"+i)
        os.rmdir(temp_client_path)
        ls.remove("Created "+prefix_dir)
    return ls

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

def client_logs_a(): #if server wants log file of client A 
    logs = str(allocated_log_files.get('A'))
    message_list_box.insert(tkinter.END, "\n\n---------Logs of Client A:---------\n\n",logs,"\n")

def client_logs_b(): #if server wants log file of client B
    logs = str(allocated_log_files.get('B'))
    message_list_box.insert(tkinter.END, "\n\n---------Logs of Client B:---------\n\n",logs,"\n")

def client_logs_c(): #if server wants log file of client C
    logs = str(allocated_log_files.get('C'))
    message_list_box.insert(tkinter.END, "\n\n---------Logs of Client C:---------\n\n",logs,"\n")


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

    send_button = tkinter.Button(root, text="Active Clients",width= 30, command=active_clients) #button show which clients are active right now 
    send_button.pack() 
    send_button = tkinter.Button(root, text="Present Clients(Active and inactive both)",width= 30, command=present_clients) #button shows which clients are presented on server. they could be active or inactive
    send_button.pack() 
    send_button = tkinter.Button(root, text="Desynchronize all clients: ",width= 30, command=desync) #this will delete all local directories withour permission of clients
    send_button.pack() 
    send_button = tkinter.Button(root, text="Logs of Client A: ",width= 30, command=client_logs_a)
    send_button.pack() 
    send_button = tkinter.Button(root, text="Logs of Client B: ",width= 30, command=client_logs_b)
    send_button.pack() 
    send_button = tkinter.Button(root, text="Logs of Client C: ",width= 30, command=client_logs_c)
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

