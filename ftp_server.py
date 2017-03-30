from configparser import ConfigParser
from socket import *
import threading
import time
import sys
import traceback
import errno
import subprocess
import platform
import os
import argparse
import shutil
import uuid


## global variables
tList = []

CMD_QUIT = "QUIT"
CMD_HELP = "HELP"
CMD_LOGIN = "LOGIN"
CMD_LOGOUT = "LOGOUT"
CMD_LS = "LIST"
CMD_LIST = "LIST"
CMD_PWD = "PWD"
CMD_MKD = "MKD"
CMD_RMD = "RMD"
CMD_CWD = "CWD"
CMD_CDUP = "CDUP"
CMD_PORT = "PORT"
CMD_DELETE = "DELETE"
CMD_PUT = "PUT"
CMD_GET = "GET"
CMD_USER = "USER"
CMD_PASS = "PASS"
CMD_RETR = "RETR"
CMD_NOOP ="NOOP"
CMD_DELE = "DELE"
CMD_STOR = "STOR"
CMD_STOU = "STOU"
CMD_RNFR = "RNFR"
CMD_RNTO = "RNTO"
CMD_APPE = "APPE"
CMD_TYPE = "TYPE"
ftype="b"
RHELP="""214-The following commands are recognized:
214-QUIT\tHELP\tPWD\tMKD\tRMD
214-LIST\tCWD\tCDUP\tPORT\tUSER
214-PASS\tRETR\tNOOP\tDELE\tSTOR
214-STOU\tRNFR\tRNTO\tAPPE\tTYPE
"""
def clientThread(connectionSocket, addr):
    global base_dir
    global ftype
    global WELCOME_MSG
    ftype= "b" #"" for ascii
    user = ""
    password = ""
    logged_on  = False
    access_type = ""
    current_dir = base_dir
    data_port=""
    file_rename = ""
    wd = current_dir
    try:
        print ("Thread Client Entering Now...")
        connectionSocket.send(WELCOME_MSG.encode())
        print (addr)
        global pause_server
        while still_searching:
            while pause_server:
                continue
            msg = connectionSocket.recv(1024).decode()
            tokens = msg.split()
            if tokens:
                cmd = tokens[0].strip().upper()
            else:
                cmd = msg
            if(cmd ==CMD_USER):
                if len(tokens) > 1:
                    user = tokens[1]
                    connectionSocket.send(("331 Password required for " + tokens[1]).encode())
                else:
                    connectionSocket.send(("No username specified").encode())
            elif(cmd==CMD_QUIT):
                user =""
                password=""
                logged_on = False
                access_type = ""
                connectionSocket.send(("221 GOODBYE.").encode())
                connectionSocket.close()
                return
            elif(cmd==CMD_LOGOUT):
                user =""
                password=""
                logged_on = False
                access_type = ""
                connectionSocket.send(("221 GOODBYE.").encode())

            elif (cmd==CMD_PASS):
                if len(tokens) > 1 and user:
                    password = tokens[1]
                    access_type, message, logged_on = login(user,password)
                    if logged_on and access_type=="user":
                        current_dir = base_dir + user + "/"
                        if not os.path.isdir(current_dir):
                            os.makedirs(current_dir)
                    connectionSocket.send((message).encode())
                elif len(tokens) <= 1 :
                    connectionSocket.send(("No password specified").encode())
                else:
                    connectionSocket.send(("503 Login with USER first").encode())
            elif (cmd==CMD_CWD):
                if len(tokens)>1:
                    wd = current_dir
                    if tokens[1]==".." or tokens[1]=="../":
                        if wd != "/":
                            lastslash = wd.rfind("/")
                            secondslash  = wd[:lastslash].rfind("/")
                            wd = wd[:secondslash+1]
                        else:
                            connectionSocket.send("500 CWD command failed".encode())
                    else:
                        wd = wd + tokens[1] + "/"
                    if ((logged_on and access_type == 'admin') or (logged_on and (wd.startswith(base_dir + user + "/"))) and os.path.isdir(wd)):
                        current_dir = wd
                        connectionSocket.send("250 CWD command successful".encode())
                    else:
                        connectionSocket.send("500 CWD command failed".encode())

                else:
                    connectionSocket.send("500 CWD command failed".encode())
            elif (cmd==CMD_PWD):
                wd = current_dir.replace(base_dir,"/")
                connectionSocket.send(wd.encode())
            elif (cmd==CMD_CDUP):
                wd = current_dir
                if wd != "/":
                    lastslash = wd.rfind("/")
                    secondslash  = wd[:lastslash].rfind("/")
                    wd = wd[:secondslash+1]
                    if (logged_on and access_type == 'admin') or (logged_on and (wd.startswith(base_dir + user + "/"))):
                        current_dir = wd
                        connectionSocket.send("250 CWD command successful".encode())
                    else:
                        connectionSocket.send("500 CWD command failed".encode())
                else:
                    connectionSocket.send("500 CWD command failed".encode())
            elif cmd==CMD_NOOP:
                connectionSocket.send("200 NOOP command successful".encode())
            elif cmd==CMD_RETR:
                if (logged_on):
                    retr_ftp(tokens,connectionSocket,current_dir,data_port)
                else:
                    connectionSocket.send("530 Please log in and make sure you have the proper permissions".encode())
            elif cmd==CMD_PORT:
                if (logged_on ):
                    if len(tokens) >1:
                        data_port = tokens[1]
                        connectionSocket.send("200 PORT successful".encode())
                else:
                    connectionSocket.send("530 Please log in and make sure you have the proper permissions".encode())
            elif cmd==CMD_LIST:
                if (logged_on):
                    list_ftp(tokens,connectionSocket,current_dir,data_port,user,logged_on,access_type)
                else:
                    connectionSocket.send("530 Please log in and make sure you have the proper permissions".encode())
            elif cmd==CMD_STOR:
                if (logged_on):
                    store_ftp(tokens,connectionSocket,current_dir,data_port)
                else:
                    connectionSocket.send("530 Please log in and make sure you have the proper permissions".encode())
            elif cmd==CMD_APPE:
                if (logged_on):
                    append_ftp(tokens,connectionSocket,current_dir,data_port)
                else:
                    connectionSocket.send("530 Please log in and make sure you have the proper permissions".encode())
            elif cmd==CMD_DELE:
                if (logged_on):
                    delete_ftp(tokens,current_dir, connectionSocket)
                else:
                    connectionSocket.send("530 Please log in and make sure you have the proper permissions".encode())
            elif cmd==CMD_MKD:
                if (logged_on):
                    makedir_ftp(tokens,current_dir,connectionSocket)
                else:
                    connectionSocket.send("530 Please log in and make sure you have the proper permissions".encode())
            elif cmd==CMD_RMD:
                if (logged_on):
                    deletedir_ftp(tokens,current_dir,connectionSocket)
                else:
                    connectionSocket.send("530 Please log in and make sure you have the proper permissions".encode())
            elif cmd == CMD_STOU:
                if (logged_on):
                    stou_ftp(tokens,connectionSocket,current_dir,data_port)
                else:
                    connectionSocket.send("530 Please log in and make sure you have the proper permissions".encode())
            elif cmd == CMD_RNFR:
                if (logged_on):
                    if len(tokens) > 1:
                        if(os.path.isfile(current_dir + tokens[1]) or os.path.isdir(current_dir + tokens[1]) ):
                            file_rename = tokens[1]
                            connectionSocket.send("350 File or directory exists, ready for destination name".encode())
                        else:
                            connectionSocket.send("550 No such file or directory exists".encode())
                    else:
                        connectionSocket.send("no file name specified.".encode())
                else:
                    connectionSocket.send("530 Please log in and make sure you have the proper permissions".encode())
            elif cmd==CMD_RNTO:
                if (logged_on):
                    if len(tokens) > 1:
                        try:
                            os.rename(current_dir + file_rename, current_dir + tokens[1])
                            connectionSocket.send("250 Rename successful".encode())
                        except:
                            connectionSocket.send("Rename unsuccessful".encode())
                    else:
                        connectionSocket.send("no file name specified.".encode())
                else:
                    connectionSocket.send("530 Please log in and make sure you have the proper permissions".encode())
            elif cmd==CMD_TYPE:
                if (logged_on):
                    if len(tokens) > 1:
                        if tokens[1].upper() == "I":
                            ftype="b"
                            connectionSocket.send("200 Type set to I".encode())
                        elif tokens[1].upper() == "A":
                            ftype=""
                            connectionSocket.send("200 Type set to A".encode())
                        else:
                            connectionSocket.send(("504 TYPE not implemented for '" + tokens[1] + "' parameter").encode())
                else:
                    connectionSocket.send("530 Please log in and make sure you have the proper permissions".encode())
            elif cmd==CMD_HELP:
                global RHELP
                if not len(tokens) > 1:
                    connectionSocket.send(RHELP.encode())
                else:
                    helpwith = tokens[1].upper()
                    if helpwith==CMD_QUIT:
                        to_send = "214 Syntax: QUIT (close control connection)"
                    elif helpwith==CMD_HELP:
                        to_send = "214 Syntax: HELP [<sp> command]"
                    elif helpwith ==CMD_LIST:
                        to_send = "214 Syntax: LIST [<sp> pathname]"
                    elif helpwith==CMD_PWD:
                        to_send="214 Syntax: PWD (returns current working directory)"
                    elif helpwith==CMD_MKD:
                        to_send="214 Syntax: MKD <sp> pathname"
                    elif helpwith==CMD_RMD:
                        to_send = "214 Syntax: RMD <sp> pathname"
                    elif helpwith ==CMD_CWD:
                        to_send="214 Syntax: CWD <sp> pathname"
                    elif helpwith==CMD_CDUP:
                        to_send="214 Syntax: CDUP (up one directory)"
                    elif helpwith==CMD_PORT:
                        to_send="214 Syntax: PORT <sp> h1,h2,h3,h4,p1,p2"
                    elif helpwith==CMD_USER:
                        to_send="214 Syntax: USER <sp> username"
                    elif helpwith==CMD_PASS:
                        to_send="214 Syntax: PASS <sp> password"
                    elif helpwith==CMD_RETR:
                        to_send = "214 Syntax: RETR <sp> pathname"
                    elif helpwith==CMD_NOOP:
                        to_send = "214 Syntax: NOOP (no operation)"
                    elif helpwith==CMD_DELE:
                        to_send="214 Syntax: DELE <sp> pathname"
                    elif helpwith==CMD_STOR:
                        to_send= "214 Syntax: STOR <sp> pathname"
                    elif helpwith==CMD_STOU:
                        to_send="214 Syntax: STOU (store unique filename)"
                    elif helpwith==CMD_RNFR:
                        to_send="214 Syntax: RNFR <sp> pathname"
                    elif helpwith==CMD_RNTO:
                        to_send="214 Syntax: RNTO <sp> pathname"
                    elif helpwith == CMD_APPE:
                        to_send = "214 Syntax: APPE <sp> pathname"
                    elif helpwith==CMD_TYPE:
                        to_send = "214 Syntax: TYPE <sp> type-code (A, I)"
                    else:
                        to_send = "502 Unknown command '" + helpwith + "'"
                    connectionSocket.send(to_send.encode())
            else:
                strm = "2180at? " + msg
                print(strm)
                connectionSocket.send(strm.encode())
    except OSError as e:
        # A socket error
          print("Socket error:",e)



def login(username,password):
    global users
    for user in users:
        if len(user)==3:
            if user[0] == username and user[1] == password:
                if user[2] == "notallowed":
                    return user[2], "530 User not allowed", False
                elif user[2] =="blocked" or user[2] == "locked":
                    return user[2], "530 User blocked", False
                return user[2], "230 " + user[2] + " access granted, restrictions apply", True
        else:
            continue

    return "", "530 Login incorrect.", False

def delete_ftp(tokens,dirname, sock):
    if len(tokens) > 1:
        try:
            os.remove(dirname + tokens[1])
            sock.send("250 DELE command successful".encode())
        except:
            sock.send("550 File could not be deleted. Check to make sure it exists.".encode())
    else:
        sock.send("500 no file specified".encode())

def deletedir_ftp(tokens,dirname, sock):
    if len(tokens) > 1:
        try:
            shutil.rmtree(dirname + tokens[1])
            sock.send("250 RMD command successful".encode())
        except:
            sock.send("550 directory could not be deleted. Check to make sure it exists.".encode())
    else:
        sock.send("500 no directory specified".encode())

def makedir_ftp(tokens,dirname, sock):
    if len(tokens) > 1:
        try:
            os.makedirs(dirname + tokens[1])
            message = "257 " + (dirname + tokens[1]).replace(base_dir, "/") +" - Directory successfully created"
            sock.send(message.encode())
        except:
            sock.send("400 directorycould not be created".encode())

    else:
        sock.send("500 no directory name specified".encode())

def store_ftp(tokens,connectionSocket,dirname,data_port):
    if len(tokens) >1:
        # connectionSocket.send(("200 PORT command successful").encode())
        connectionSocket.send(("150 Opening ASCII mode data connection for " + tokens[1]).encode())

        data_socket = dataport_connecthost(data_port)

        filename=dirname + tokens[1]
        try:
            f = open(filename,'w' + ftype)
            data = data_socket.recv(1024)
            while data:
                f.write(data)
                data = data_socket.recv(1024)
            f.close()
            data_socket.close()
            connectionSocket.send('226 Transfer complete.\r\n'.encode())
        except Exception as e:
            data_socket.close()
            print (e)
            connectionSocket.send('Unable to Write file. Check that you have permissions\r\n'.encode())

def stou_ftp(tokens,connectionSocket,dirname,data_port):
    if len(tokens) >1:
        # connectionSocket.send(("200 PORT command successful").encode())
        newFileName = dirname + str(uuid.uuid4())

        connectionSocket.send(("150 FILE " + newFileName.replace(dirname,"/")).encode())

        data_socket = dataport_connecthost(data_port)

        filename= newFileName
        try:
            f = open(filename,'w' + ftype)
            data = data_socket.recv(1024)
            while data:
                f.write(data)
                data = data_socket.recv(1024)
            f.close()
            data_socket.close()
            connectionSocket.send('226 Transfer complete.\r\n'.encode())
        except:
            data_socket.close()
            connectionSocket.send('Unable to Write file. Check that you have permissions\r\n'.encode())


def append_ftp(tokens,connectionSocket,dirname,data_port):
    if len(tokens) >1:
        # connectionSocket.send(("200 PORT command successful").encode())
        connectionSocket.send(("150 Opening ASCII mode data connection for " + tokens[1]).encode())

        data_socket = dataport_connecthost(data_port)

        filename=dirname + tokens[1]
        try:
            f = open(filename,'a' + ftype)
            data = data_socket.recv(1024)
            while data:
                f.write(data)
                data = data_socket.recv(1024)
            f.close()
            data_socket.close()
            connectionSocket.send('226 Transfer complete.\r\n'.encode())
        except:
            data_socket.close()
            connectionSocket.send('Unable to Write file. Check that you have permissions\r\n'.encode())


def retr_ftp(tokens, connectionSocket, dirname, data_port):
    if len(tokens) >1:
        # connectionSocket.send(("200 PORT command successful").encode())
        connectionSocket.send(("150 Opening ASCII mode data connection for " + tokens[1]).encode())

        data_socket = dataport_connecthost(data_port)

        filename=dirname + tokens[1]
        try:
            f = open(filename,'r' + ftype)
            data = f.read(1024)
            while data:
                if(ftype==""):
                    data=data.encode()
                data_socket.send(data)
                data=f.read(1024)
            f.close()
            data_socket.close()
            connectionSocket.send('226 Transfer complete.\r\n'.encode())
        except Exception as e:
            data_socket.close()
            print (e)
            connectionSocket.send('Unable to retrieve file. Check that file exists (ls) or that you have permissions\r\n'.encode())

def list_ftp(tokens, connectionSocket, dirname, data_port, user, logged_on,access):
    if len(tokens) >1:
        # connectionSocket.send(("200 PORT command successful").encode())
        connectionSocket.send(("150 Opening ASCII mode data connection for " + tokens[1]).encode())
        global base_dir
        data_socket = dataport_connecthost(data_port)
        if (dirname + tokens[1]).startswith(base_dir + user) and logged_on or access=="admin":
            try:
                ls_output = subprocess.check_output(['ls', '-l', dirname + tokens[1]]).decode().splitlines()
                for x in range(0, len(ls_output)):
                    data_socket.send((ls_output[x] + "\n").encode())

            except:
                ls_output = "Error listing directory"
                data_socket.send(ls_output.encode())
        else:
            data_socket.send("500 You don't have the proper permissions".encode().encode())


        data_socket.close()
        connectionSocket.send('226 Transfer complete.\r\n'.encode())
    else:
        connectionSocket.send(("150 Opening ASCII mode data connection").encode())

        data_socket = dataport_connecthost(data_port)
        try:
            ls_output = subprocess.check_output(['ls', '-l', dirname ]).decode().splitlines()
            for x in range(0, len(ls_output)):
                data_socket.send((ls_output[x] + "\n").encode())


        except:
            ls_output = "Error listing directory"
            data_socket.send(ls_output.encode())

        data_socket.close()
        connectionSocket.send('226 Transfer complete.\r\n'.encode())


def dataport_connecthost(ip):
    print(ip)
    ip=ip.split(',')
    hostname = ".".join(ip[0:4])
    port = int(ip[4]) * 256 + int(ip[5])
    ftp_socket = socket(AF_INET, SOCK_STREAM)
    #to reuse socket faster. It has very little consequence for ftp client.
    ftp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    ftp_socket.connect((hostname, (port)))
    print (ftp_socket)
    return ftp_socket


def joinAll():
    global tList
    for t in tList:
        t.join()

users = []
def parseUserConfig():
    global users
    with open(user_data_file) as f:
        users = f.read().splitlines()
        for i in range(len(users)):
            users[i] = users[i].split()

base_dir = ""
user_data_file = "ftpserver/users.cfg"
#ftp_mode supports ACTIVE PASSIVE BOTH
ftp_mode = "ACTIVE"
#this applies for PASSIVE ONLY
DATA_PORT_RANGE_MIN = 20000
DATA_PORT_RANGE_MAX = 30000
DATA_PORT_FTP_SERVER =""# 21 is the common port
FTP_ENABLED = 1
MAX_USER_SUPPORT = 200
WELCOME_MSG = "Welcome to FTP Server Spring 2017"
FTP_LOG = "ftpserve/log"
SERVICE_PORT = 2180

def read_sys_config():
    parser = ConfigParser()
    parser.read('./ftpserver/conf/fsys.cfg')
    global base_dir
    global user_data_file
    #ftp_mode supports ACTIVE PASSIVE BOTH
    global ftp_mode
    #this applies for PASSIVE ONLY
    global DATA_PORT_RANGE_MIN
    global DATA_PORT_RANGE_MAX
    global DATA_PORT_FTP_SERVER # 21 is the common port
    global FTP_ENABLED
    global MAX_USER_SUPPORT
    global WELCOME_MSG
    global FTP_LOG
    global SERVICE_PORT
    base_dir = (parser.get('ftp', 'ftp_root'))
    user_data_file = (parser.get('ftp', 'user_data_file'))
    ftp_mode = (parser.get('ftp', 'ftp_mode'))
    DATA_PORT_RANGE_MIN = int(parser.get('ftp', 'DATA_PORT_RANGE_MIN'))
    DATA_PORT_RANGE_MAX = int(parser.get('ftp', 'DATA_PORT_RANGE_MAX'))
    DATA_PORT_FTP_SERVER = int(parser.get('ftp', 'DATA_PORT_FTP_SERVER'))
    FTP_ENABLED= (parser.get('ftp', 'FTP_ENABLED'))
    MAX_USER_SUPPORT = (parser.get('ftp', 'MAX_USER_SUPPORT'))
    WELCOME_MSG = (parser.get('ftp', 'WELCOME_MSG'))
    FTP_LOG = (parser.get('ftp', 'FTP_LOG'))
    SERVICE_PORT = int(parser.get('ftp', 'SERVICE_PORT'))

parser = argparse.ArgumentParser()
parser.add_argument("-port","--port",help="Sets FTP port",
                    type=int)
parser.add_argument("-configuration","--configuration",help="Sets configuration path",
                    type=str)
parser.add_argument("-max","--max",help="Sets max connections",
                    type=int)
parser.add_argument("-dpr","--dpr",help="Changes data port range",
                    type=int,nargs="*")
parser.add_argument("-userdb","--userd",help="Sets user file path",
                    type=str)
args = parser.parse_args()
serverPort = 2110
if args.port:
    serverPort = args.port

def servFunction(sock,idk):
    try:
        global still_searching
        global tList

        while still_searching:
            connectionSocket, addr = sock.accept()
            t = threading.Thread(target=start_stop,args=(connectionSocket,addr))
            t.start()
            tList.append(t)
    except:
        sock.close()
        joinAll()


pause_server = False
def start_stop(sock,addr):
    global pause_server
    msg = sock.recv(1024).decode().upper()
    if msg=="START":
        pause_server = False
    elif msg=="STOP":
        pause_server = True
    socket(AF_INET,SOCK_STREAM).connect(('127.0.0.1',serverPort))

    sock.close()

still_searching = True
def main():
    read_sys_config()
    parseUserConfig()
    conn=False
    global still_searching
    global tList
    global serverPort
    global pause_server
    try:
        if not serverPort:
            serverPort = 2110
        serverSocket = socket(AF_INET,SOCK_STREAM)
        serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        serverSocket.bind(('127.0.0.1',serverPort))
        serverSocket.listen(15)
        serviceSocket = socket(AF_INET,SOCK_STREAM)
        serviceSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        serviceSocket.bind(('127.0.0.1',SERVICE_PORT))
        serviceSocket.listen(15)
        t = threading.Thread(target=servFunction, args=(serviceSocket,""))
        t.start()
        tList.append(t)
        print('The server is ready to receive')

        while still_searching:
            while pause_server:
                sys.stdout.write("\rStopped")
                sys.stdout.flush()
                continue
            connectionSocket, addr = serverSocket.accept()
            conn = True
            t = threading.Thread(target=clientThread,args=(connectionSocket,addr))
            t.start()
            tList.append(t)
            print("Thread started")
            print("Waiting for another connection")


    except Exception as e:
        pause_server = False
        still_searching = False
        socket(AF_INET,SOCK_STREAM).connect(('127.0.0.1',serverPort))
        serverSocket.shutdown(SHUT_RDWR)
        serverSocket.close()
        socket(AF_INET,SOCK_STREAM).connect(('127.0.0.1',SERVICE_PORT))
        serviceSocket.shutdown(SHUT_RDWR)
        serviceSocket.close()
        if conn:
            connectionSocket.shutdown(SHUT_RDWR)
            connectionSocket.close()
        print ("Keyboard Interrupt. Time to say goodbye!!!" + e)
        joinAll()

    #except Exception:
     #   traceback.print_exc(file=sys.stdout)

    print("The end")
    sys.exit(0)

if __name__ == "__main__":
    # execute only if run as a script
    main()
