#import necessary packages.
import os
import os.path
import errno
import traceback
import sys
from socket import *
import argparse
import subprocess
from configparser import ConfigParser
import logging
import threading

#Global constants
USAGE = "usage: Python ftp hostname [username] [password] -h [hostname] -u [username]\
 -w [password] -fp [ftp server port] -P (passive) -A (active)-D (debug mode on/off) \
  -d [on/off] (debug on/off) -V (verbose) -dpr [data port range (space separated)] \
-c [configuarion file] -t [test file] -T (run default test file) -L [log_file_name] \
-ALL (log all output to log file) -ONLY (log all output to log file without displaying)\
-version( prints version number of this client.) -info"
t_list=[]


CMD_FTP = "FTP"
CMD_OPEN = "OPEN"
CMD_QUIT = "QUIT"
CMD_BYE = "BYE"
CMD_CLOSE = "CLOSE"
CMD_EXIT = "EXIT"
CMD_DISC = "DISCONNECT"
CMD_HELP = "HELP"
CMD_QUESTION = "?"
CMD_LOGIN = "LOGIN"
CMD_LOGOUT = "LOGOUT"
CMD_LS = "LS"
CMD_LIST = "LIST"
CMD_DIR = "DIR"
CMD_PWD = "PWD"
CMD_MKD = "MKD"
CMD_MKDIR = "MKDIR"
CMD_RMD = "RMD"
CMD_RMDIR = "RMDIR"
CMD_CWD = "CWD"
CMD_CDUP = "CDUP"
CMD_PORT = "PORT"
CMD_DELETE = "DELETE"
CMD_PUT = "PUT"
CMD_SEND = "SEND"
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
CMD_APPEND = "APPEND"
CMD_TYPE = "TYPE"
CMD_IMAGE = "IMAGE"
CMD_BIN = "BINARY"
CMD_ASCII = "ASCII"
CMD_LPWD = "LPWD"
CMD_LCD = "LCD"
CMD_LLS = "LLS"
CMD_CD="CD"
CMD_USAGE = "USAGE"
CMD_VERBOSE = "VERBOSE"
CMD_SUNIQUE = "SUNIQUE"
CMD_DEBUG = "DEBUG"
CMD_RHELP = "RHELP"
CMD_RENAME = "RENAME"


unique_on = False
verbose_on = False
#global
global username
global password
username = ""
password = ""
hostname = ""
collection=""
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("supplied",nargs="*", help ="hostname, username, password")
parser.add_argument("-h", "--h", help="provide hostname",
                    type=str)
parser.add_argument("-u", "--u", help="provide username",
                    type=str)
parser.add_argument("-p", "--p", help="provide password",
                    type=str)
parser.add_argument("-w", "--w", help="provide password",
                    type=str)
parser.add_argument("-fp","--fp", help="provide ftp server port",
                    type=str)
parser.add_argument("-A","--A" ,help="Sets to active mode",
                    action="store_true")
parser.add_argument("-P", "--P",help="Sets to passive mode",
                    action="store_true")
parser.add_argument("-D", "--D",help="Sets to debug mode",
                    action="store_true")
parser.add_argument("-V", "--V",help="Sets to verbose mode",
                    action="store_true")
parser.add_argument("-dpr","--dpr",help="Changes data port range",
                    type=int,nargs="*")
parser.add_argument("-c","--c", help="Changes config file path", type=str)
parser.add_argument("-t", "--t",help="run test file", type=str)
parser.add_argument("-T", "--T", help="run default test file", action="store_true")
parser.add_argument("-L","--L", help="Changes files log name", type=str)
parser.add_argument("-ALL","--ALL", help="log all output to log file (and still display it) log_file_name", type=str)
parser.add_argument("-ONLY","--ONLY", help="log all output to log file", type=str)
parser.add_argument("-version", "--version",help="Prints version info", action="store_true")
parser.add_argument("-info", "--info",help="Prints student info", action="store_true")

debug_mode=0
logon_ready = False
args = parser.parse_args()
if args.h:
    hostname = args.h
if args.u:
    username = args.u
if args.p:
    password = args.p
if args.w:
    password = args.w
if args.u and args.w:
    logon_ready = True
if args.fp:
    FTP_PORT = int(args.fp)
if args.A:
    FTP_MODE = "ACTIVE"
if args.P:
    FTP_MODE = "PASSIVE"
if args.D:
    debug_mode = 1
if args.V:
    verbose_on = True
if args.dpr:
    DATA_PORT_MIN, DATA_PORT_MAX = args.dpr
if args.c:
    config_file_path = args.c
if args.t:
    #RUN args.t
    pass
if args.T:
    #RUN DEFAULT
    pass
if args.L:
    log_file_name = args.L
if args.ALL:
    log_file_name = args.ALL
    log_all_output = True
    print_and_log = True
if args.ONLY:
    log_file_name = args.ONLY
    log_all_output = True
    print_and_log =False
if args.version:
    print("FTP Client v2.0")
if args.info:
    print("FTP Client v2.0 was created by Mark Fajet.")

#entry point main()
def main():
    read_config()
    global username
    global password
    global log_file_name
    global hostname
    global args
    logged_on = False
    global logon_ready
    global debug_mode
    if not debug_mode:
        global default_debug_mode
        if default_debug_mode == "on":
            debug_mode = 1
        else:
            debug_mode = 0
    global verbose_on
    if not verbose_on:
        global default_verbose_mode
        if default_verbose_mode == "on":
            verbose_on = True
    logging.basicConfig(level=logging.DEBUG, filename=log_file_name,
                        format="%(asctime)-15s %(levelname)-8s %(message)s")
    print("FTP Client v2.0")
    if (len(args.supplied) < 1):
         print(USAGE)
    if (len(args.supplied) == 1):
        hostname = args.supplied[0]
    if (len(args.supplied) == 2):
        username = args.supplied[0]
        password = args.supplied[1]
        logon_ready = True
    if (len(args.supplied) == 3):
        username = args.supplied[1]
        password = args.supplied[2]
        logon_ready = True

    while not hostname:
        rinput = input("FTP>")
        if (rinput is None or rinput.strip() == ''):
            continue
        tokens = rinput.split()
        cmd = tokens[0].upper()
        if cmd == CMD_FTP or cmd ==CMD_OPEN:
            if len(tokens) == 2:
                hostname = tokens[1]
            elif len(tokens) == 3:
                hostname = tokens[1]
                global FTP_PORT
                FTP_PORT = int(tokens[2])
            else:
                print(cmd + " [hostname]")
        elif cmd==CMD_HELP:
            help_ftp()
        else:
            print("Not connected")
    print("********************************************************************")
    print("**                        ACTIVE MODE ONLY                        **")
    print("********************************************************************")
    print(("You will be connected to host:" + hostname))
    print("Type HELP for more information")
    print("Commands are NOT case sensitive\n")


    ftp_socket = ftp_connecthost(hostname)
    ftp_recv = ftp_socket.recv(RECV_BUFFER)
    ftp_code = ftp_recv[:3]
    #
    #note that in the program there are many .strip('\n')
    #this is to avoid an extra line from the message
    #received from the ftp server.
    #an alternative is to use sys.stdout.write
    print(msg_str_decode(ftp_recv,True))
    #
    #this is the only time that login is called
    #without relogin
    #otherwise, relogin must be called, which included prompts
    #for username
    #
    if(username and password):
        logon_ready = True
    if (logon_ready):
        logged_on = login(username,password,ftp_socket)
    keep_running = True

    while keep_running:
        try:
            rinput = input("FTP>")
            if (rinput is None or rinput.strip() == ''):
                continue
            tokens = rinput.split()
            cmdmsg , logged_on, ftp_socket = run_cmds(tokens,logged_on,ftp_socket)
            if (cmdmsg != ""):
                if log_all_output:
                    logging.info(cmdmsg)
                print(cmdmsg)
        except OSError as e:
        # A socket error
          print("Socket error:",e)
          strError = str(e)
          #this exits but it is better to recover
          if (strError.find("[Errno 32]") >= 0):
              sys.exit()

    #print ftp_recv
    try:
        ftp_socket.close()
        print("Thank you for using FTP 1.0")
    except OSError as e:
        print("Socket error:",e)
    sys.exit()

def run_cmds(tokens,logged_on,ftp_socket):
    global username
    global password
    global hostname
    global debug_mode
    global t_list
    cmd = tokens[0].upper()

    if (cmd == CMD_QUIT or cmd==CMD_EXIT or cmd == CMD_DISC or cmd==CMD_BYE or cmd ==CMD_CLOSE):
        quit_ftp(logged_on,ftp_socket)
        return "",logged_on, ftp_socket

    if (cmd == CMD_HELP or cmd == CMD_QUESTION):
        help_ftp(tokens)
        return "",logged_on, ftp_socket

    if (cmd == CMD_PWD):
        pwd_ftp(ftp_socket)
        return "",logged_on, ftp_socket
    if (cmd == CMD_STOU):
        data_socket = ftp_new_dataport(ftp_socket)
        if (data_socket is not None):
            stou_ftp(tokens, ftp_socket,data_socket)

            return "",logged_on, ftp_socket
        else:
            if log_all_output:
                logging.info("[STOU] Failed to get data port. Try again.")
            return "[STOU] Failed to get data port. Try again.",logged_on, ftp_socket
    if (cmd == CMD_LS or cmd == CMD_LIST or cmd == CMD_DIR):
        #FTP must create a channel to received data before
        #executing ls.
        #also makes sure that data_socket is valid
        #in other words, not None
        data_socket = ftp_new_dataport(ftp_socket)
        if (data_socket is not None):
            ls_ftp(tokens,ftp_socket,data_socket)
            return "",logged_on, ftp_socket
        else:
            if log_all_output:
                logging.info("[LS] Failed to get data port. Try again.")
            return "[LS] Failed to get data port. Try again.",logged_on, ftp_socket

    if (cmd == CMD_LOGIN):
        username, password, logged_on, ftp_socket \
        = relogin(username, password, logged_on, tokens, hostname, ftp_socket)
        return "",logged_on, ftp_socket

    if (cmd == CMD_LOGOUT):
        logged_on,ftp_socket = logout(logged_on,ftp_socket)
        return "",logged_on, ftp_socket

    if (cmd == CMD_DELETE or cmd == CMD_DELE or cmd=="DEL"):
        delete_ftp(tokens,ftp_socket)
        return "",logged_on, ftp_socket

    if (cmd == CMD_PUT or cmd==CMD_STOR or cmd==CMD_SEND):
        # FTP must create a channel to received data before
        # executing put.
        #  also makes sure that data_socket is valid
        # in other words, not None
        data_socket = ftp_new_dataport(ftp_socket)
        if (data_socket is not None):
            global unique_on
            if unique_on:
                stou_ftp(tokens,ftp_socket,data_socket)
            else:
                put_ftp(tokens,ftp_socket,data_socket)
            return "",logged_on, ftp_socket
        else:
            if log_all_output:
                logging.info("[PUT] Failed to get data port. Try again.")
            return "[PUT] Failed to get data port. Try again.",logged_on, ftp_socket
    if (cmd==CMD_STOR):
        # FTP must create a channel to received data before
        # executing put.
        #  also makes sure that data_socket is valid
        # in other words, not None
        data_socket = ftp_new_dataport(ftp_socket)
        if (data_socket is not None):
            put_ftp(tokens,ftp_socket,data_socket)
            return "",logged_on, ftp_socket
        else:
            if log_all_output:
                logging.info("[PUT] Failed to get data port. Try again.")
            return "[PUT] Failed to get data port. Try again.",logged_on, ftp_socket
    if (cmd == CMD_APPE or cmd == CMD_APPEND):
        # FTP must create a channel to received data before
        # executing put.
        #  also makes sure that data_socket is valid
        # in other words, not None
        data_socket = ftp_new_dataport(ftp_socket)
        if (data_socket is not None):
            appe_ftp(tokens,ftp_socket,data_socket)
            return "",logged_on, ftp_socket
        else:
            if log_all_output:
                logging.info("[APPE] Failed to get data port. Try again.")
            return "[APPE] Failed to get data port. Try again.",logged_on, ftp_socket

    if (cmd == CMD_GET or cmd ==CMD_RETR):
        # FTP must create a channel to received data before
        # executing get.
        # also makes sure that data_socket is valid
        # in other words, not None
        data_socket = ftp_new_dataport(ftp_socket)
        if (data_socket is not None):
            get_ftp(tokens,ftp_socket,data_socket)
            return "",logged_on, ftp_socket
        else:
            if log_all_output:
                logging.info("[GET] Failed to get data port. Try again.")
            return "[GET] Failed to get data port. Try again.",logged_on, ftp_socket
    if (cmd==CMD_USER):
        user_ftp(tokens,ftp_socket)
        return "",logged_on, ftp_socket

    if (cmd==CMD_PASS):
        logged_on = pass_ftp(tokens,ftp_socket)
        return "",logged_on, ftp_socket
    if (cmd==CMD_NOOP):
        noop_ftp(ftp_socket)
        return "",logged_on, ftp_socket
    if (cmd == CMD_CWD or cmd =="CD"):
        cwd_ftp(tokens,ftp_socket)
        return "",logged_on, ftp_socket

    if (cmd == CMD_MKD or cmd == CMD_MKDIR):
        mkd_ftp(tokens,ftp_socket)
        return "",logged_on, ftp_socket
    if (cmd == CMD_RMD or cmd == CMD_RMDIR):
        rmd_ftp(tokens,ftp_socket)
        return "",logged_on, ftp_socket
    if (cmd == CMD_CDUP):
        cdup_ftp(ftp_socket)
        return "",logged_on, ftp_socket
    if (cmd == CMD_RNFR):
        rnfr_ftp(tokens, ftp_socket)
        return "",logged_on, ftp_socket
    if (cmd == CMD_RNTO):
        rnto_ftp(tokens, ftp_socket)
        return "",logged_on, ftp_socket
    if (cmd == CMD_TYPE):
        type_ftp(tokens, ftp_socket)
        return "",logged_on, ftp_socket
    if cmd == CMD_IMAGE or cmd == CMD_BIN:
        image_ftp(tokens, ftp_socket)
        return "",logged_on, ftp_socket
    if cmd == CMD_ASCII:
        ascii_ftp(tokens, ftp_socket)
        return "",logged_on, ftp_socket
    if (cmd == CMD_PORT):
        port_ftp(tokens,ftp_socket)
        return "",logged_on, ftp_socket
    if (cmd==CMD_LPWD):
        return os.getcwd(),logged_on, ftp_socket
    if (cmd==CMD_LCD):
        if len(tokens) > 1:
            try:
                os.chdir(tokens[1])
                return os.getcwd(),logged_on, ftp_socket
            except:
                if log_all_output:
                    logging.info("LCD failed. Path does not exist")

                return "Path does not exist", logged_on, ftp_socket
        else:
            if log_all_output:
                logging.info("LCD failed. Path not specified")
            return "Path not specified", logged_on, ftp_socket
    if (cmd==CMD_LLS):
        if len(tokens) > 1:
            ls_output = subprocess.check_output(['ls', '-l', tokens[1]]).decode()
        else:
            ls_output = subprocess.check_output(['ls', '-l']).decode()
        return ls_output, logged_on, ftp_socket
    if (cmd==CMD_SUNIQUE):
        unique_on = not unique_on
        if unique_on:
            return "Unique storing on", logged_on, ftp_socket
        else:
            return "Unique storing off", logged_on, ftp_socket
    if (cmd == CMD_RENAME):
        rename_ftp(tokens, ftp_socket)
        return "",logged_on, ftp_socket
    if (cmd ==CMD_DEBUG):
        if len (tokens)>1:
            if tokens[1]>=1:
                debug_mode=tokens[1]
            elif tokens[1] == 0:
                debug_mode = 0
            else:
                return tokens[1] + ": bad debugging value.", logged_on, ftp_socket
        else:
            if debug_mode:
                debug_mode = 0
            else:
                debug_mode = 1
        if debug_mode:
            return "Debugging on (debug=" + str(debug_mode) + ")", logged_on,ftp_socket
        else:
            return "Debugging off (debug=0).", logged_on,ftp_socket
    if (cmd==CMD_VERBOSE):
        global verbose_on
        verbose_on = not verbose_on
        if verbose_on:
            return "Verbose mode on.", logged_on, ftp_socket
        else:
            return "Verbose mode on.", logged_on, ftp_socket
    if cmd == CMD_USAGE:
        global USAGE
        return USAGE, logged_on,ftp_socket
    if cmd == CMD_RHELP:
        rhelp_ftp(tokens,ftp_socket)
        return "",logged_on, ftp_socket

    return "Unknown command", logged_on, ftp_socket

def str_msg_encode(strValue):
    msg = strValue.encode()
    return msg

def msg_str_decode(msg,pStrip=False):
    #print("msg_str_decode:" + str(msg))
    strValue = msg.decode()
    if (pStrip):
        strValue.strip('\n')
    return strValue

def ftp_connecthost(hostname):

    ftp_socket = socket(AF_INET, SOCK_STREAM)
    #to reuse socket faster. It has very little consequence for ftp client.
    ftp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    ftp_socket.connect((hostname, FTP_PORT))
    print (ftp_socket)
    return ftp_socket

def ftp_new_dataport(ftp_socket):
    global next_data_port
    dport = next_data_port
    host = gethostname()
    host_address = gethostbyname(host)
    next_data_port = next_data_port + 1 #for next next
    dport = (DATA_PORT_MIN + dport) % DATA_PORT_MAX

    if verbose_on:
        print(("Preparing Data Port: " + host + " " + host_address + " " + str(dport)))
    data_socket = socket(AF_INET, SOCK_STREAM)
    # reuse port
    data_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    data_socket.bind((host_address, dport))
    data_socket.listen(DATA_PORT_BACKLOG)

    #the port requires the following
    #PORT IP PORT
    #however, it must be transmitted like this.
    #PORT 192,168,1,2,17,24
    #where the first four octet are the ip and the last two form a port number.
    host_address_split = host_address.split('.')
    high_dport = str(dport // 256) #get high part
    low_dport = str(dport % 256) #similar to dport << 8 (left shift)
    port_argument_list = host_address_split + [high_dport,low_dport]
    port_arguments = ','.join(port_argument_list)
    cmd_port_send = CMD_PORT + ' ' + port_arguments + '\r\n'
    if verbose_on:
        print(cmd_port_send)


    try:
        ftp_socket.send(str_msg_encode(cmd_port_send))
    except socket.timeout:
        print("Socket timeout. Port may have been used recently. wait and try again!")
        return None
    except socket.error:
        print("Socket error. Try again")
        return None
    msg = ftp_socket.recv(RECV_BUFFER)
    if verbose_on:
        print(msg_str_decode(msg,True))
    if not msg.decode()[0:3] == "200":
        return None
    return data_socket

def pwd_ftp(ftp_socket):
    message = str_msg_encode("PWD\r\n")
    global debug_mode
    if debug_mode:
        print("(DEBUG) --> " + message.decode())
    ftp_socket.send(message)
    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))

def rhelp_ftp(tokens, ftp_socket):
    if len(tokens)>1:
        message = str_msg_encode("HELP " + tokens[1] + "\r\n")
    else:
        message = str_msg_encode("HELP\r\n")
    global debug_mode
    if debug_mode:
        print("(DEBUG) --> " + message.decode())
    ftp_socket.send(message)
    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))

def port_ftp(tokens,ftp_socket):
    if (len(tokens) < 2):
        print("PORT [h1,h2,h3,h4,p1,p2]. Please specify address")
        return
    message = str_msg_encode("PORT " + tokens[1] + "\r\n")
    global debug_mode
    if debug_mode:
        print("(DEBUG) --> " + message.decode())
    ftp_socket.send(message)
    msg = ftp_socket.recv(RECV_BUFFER)
    if verbose_on:
        print(msg_str_decode(msg,True))


def type_ftp(tokens,ftp_socket):
    if (len(tokens) < 2):
        print("TYPE [type-code]. Please specify type-code")
        return

    message=str_msg_encode("TYPE " + tokens[1] + "\r\n")
    global debug_mode
    if debug_mode:
        print("(DEBUG) --> " + message.decode())
    ftp_socket.send(message)
    msg = ftp_socket.recv(RECV_BUFFER)
    if verbose_on:
        print(msg_str_decode(msg,True))

def image_ftp(tokens,ftp_socket):
    message = str_msg_encode("TYPE I\r\n")
    global debug_mode
    if debug_mode:
        print("(DEBUG) --> " + message.decode())
    ftp_socket.send(message)
    msg = ftp_socket.recv(RECV_BUFFER)
    if verbose_on:
        print(msg_str_decode(msg,True))

def ascii_ftp(tokens,ftp_socket):
    message = str_msg_encode("TYPE A\r\n")
    global debug_mode
    if debug_mode:
        print("(DEBUG) --> " + message.decode())
    ftp_socket.send(message)
    msg = ftp_socket.recv(RECV_BUFFER)
    if verbose_on:
        print(msg_str_decode(msg,True))

def rename_ftp(tokens,ftp_socket):
    if (len(tokens) < 3):
        print("RENAME [filename] [filename]. Please specify filename")
        return
    message = str_msg_encode("RNFR " + tokens[1] + "\r\n")
    global debug_mode
    if debug_mode:
        print("(DEBUG) --> " + message.decode())
    ftp_socket.send(message)

    msg = ftp_socket.recv(RECV_BUFFER)
    if verbose_on:
        print(msg_str_decode(msg,True))
    message = str_msg_encode("RNTO " + tokens[2] + "\r\n")
    if debug_mode:
        print("(DEBUG) --> " + message.decode())
    ftp_socket.send(message)
    msg = ftp_socket.recv(RECV_BUFFER)
    if verbose_on:
        print(msg_str_decode(msg,True))

def rnfr_ftp(tokens,ftp_socket):
    if (len(tokens) < 2):
        print("RNFR [filename]. Please specify filename")
        return
    message = str_msg_encode("RNFR " + tokens[1] + "\r\n")
    global debug_mode
    if debug_mode:
        print("(DEBUG) --> " + message.decode())
    ftp_socket.send(message)
    msg = ftp_socket.recv(RECV_BUFFER)
    if verbose_on:
        print(msg_str_decode(msg,True))

def rnto_ftp(tokens, ftp_socket):
    if (len(tokens) < 2):
        print("RNTO [filename]. Please specify filename")
        return
    message = str_msg_encode("RNTO " + tokens[1] + "\r\n")
    global debug_mode
    if debug_mode:
        print("(DEBUG) --> " + message.decode())
    ftp_socket.send(message)
    msg = ftp_socket.recv(RECV_BUFFER)
    if verbose_on:
        print(msg_str_decode(msg,True))

def stou_ftp(tokens, ftp_socket,data_socket):
        if (len(tokens) < 2):
            print("stou [filename]")
            return

        local_filename = tokens[1]
        if (len(tokens) == 3):
            filename = tokens[2]
        else:
            filename = local_filename

        if (os.path.isfile(local_filename) == False):
            print(("Filename does not exisit on this client. Filename: " + filename + " -- Check file name and path"))
            return
        filestat = os.stat(local_filename)
        filesize = filestat.st_size
        message = str_msg_encode("STOU " + filename + "\r\n")
        global debug_mode
        if debug_mode:
            print("(DEBUG) --> " + message.decode())
        ftp_socket.send(message)
        msg = ftp_socket.recv(RECV_BUFFER)
        if verbose_on:
            print(msg_str_decode(msg,True))
            print(("Attempting to send file. Local: " + local_filename + " - Remote:" + filename + " - Size:" + str(filesize)))
        def data_func():
            data_connection, data_host = data_socket.accept()
            file_bin = open(filename,"rb") #read and binary modes

            size_sent = 0
            #use write so it doesn't produce a new line (like print)
            while True:
                data = file_bin.read(RECV_BUFFER)
                if (not data or data == '' or len(data) <= 0):
                    file_bin.close()
                    break
                else:
                    data_connection.send(data)
                    size_sent += len(data)

            sys.stdout.write("\n")
            data_connection.close()
        global t_list
        t = threading.Thread(target = data_func)
        t.start()
        t_list.append(t)
        msg = ftp_socket.recv(RECV_BUFFER)
        if verbose_on:
            print(msg_str_decode(msg,True))

def user_ftp(tokens,ftp_socket):
    if (len(tokens) < 2):
        print("user [username]. Please specify username")
        return
    message = ("USER " + tokens[1] + "\n").encode()
    global debug_mode
    if debug_mode:
        print("(DEBUG) --> " + message.decode())
    ftp_socket.send(message)
    msg = ftp_socket.recv(RECV_BUFFER).decode()
    if verbose_on:
        print(msg.strip('\n'))

def pass_ftp(tokens,ftp_socket):
    if (len(tokens) < 2):
        print("pass [password]. Please specify password")
        return False
    message = ("PASS " + tokens[1] + "\n").encode()
    global debug_mode
    if debug_mode:
        print("(DEBUG) --> " + message.decode())
    ftp_socket.send(message)
    msg = ftp_socket.recv(RECV_BUFFER).decode()
    if verbose_on:
        print(msg.strip('\n'))
    if msg.split()[0]=="230":
        return True
    else:
        return False


def get_ftp(tokens, ftp_socket, data_socket):
    if (len(tokens) < 2):
        print("put [filename]. Please specify filename")
        return

    remote_filename = tokens[1]
    if (len(tokens) == 3):
        filename = tokens[2]
    else:
        filename = remote_filename
    message = str_msg_encode("RETR " + remote_filename + "\r\n")
    global debug_mode
    if debug_mode:
        print("(DEBUG) --> " + message.decode())
    ftp_socket.send(message)
    if verbose_on:
        print(("Attempting to write file. Remote: " + remote_filename + " - Local:" + filename))

    msg = ftp_socket.recv(RECV_BUFFER)
    strValue = msg_str_decode(msg)
    tokens = strValue.split()
    if (tokens[0] != "150" ):
        print("Unable to retrieve file. Check that file exists (ls) or that you have permissions")
        return
    if verbose_on:
        print(msg_str_decode(msg,True))
    def data_func():
        data_connection, data_host = data_socket.accept()
        file_bin = open(filename, "wb")  # read and binary modes
        print()
        size_recv = 0
        while True:
            data = data_connection.recv(RECV_BUFFER)

            if (not data or data == '' or len(data) <= 0):
                file_bin.close()
                break
            else:
                file_bin.write(data)
                size_recv += len(data)

        sys.stdout.write("\n")
        data_connection.close()
    global t_list
    t = threading.Thread(target = data_func)
    t.start()
    t_list.append(t)
    msg = ftp_socket.recv(RECV_BUFFER)
    if verbose_on:
        print(msg_str_decode(msg,True))

def appe_ftp(tokens, ftp_socket, data_socket):

        if (len(tokens) < 2):
            print("appe [filename]. Please specify filename")
            return

        local_filename = tokens[1]
        if (len(tokens) == 3):
            filename = tokens[2]
        else:
            filename = local_filename

        if (os.path.isfile(local_filename) == False):
            print(("Filename does not exisit on this client. Filename: " + filename + " -- Check file name and path"))
            return
        filestat = os.stat(local_filename)
        filesize = filestat.st_size
        message = str_msg_encode("APPE " + filename + "\r\n")
        global debug_mode
        if debug_mode:
            print("(DEBUG) --> " + message.decode())
        ftp_socket.send(message)
        msg = ftp_socket.recv(RECV_BUFFER)
        if verbose_on:
            print(msg_str_decode(msg,True))
            print(("Attempting to send file. Local: " + local_filename + " - Remote:" + filename + " - Size:" + str(filesize)))
        def data_func():
            data_connection, data_host = data_socket.accept()
            file_bin = open(filename,"rb") #read and binary modes

            size_sent = 0
            #use write so it doesn't produce a new line (like print)
            while True:
                data = file_bin.read(RECV_BUFFER)
                if (not data or data == '' or len(data) <= 0):
                    file_bin.close()
                    break
                else:
                    data_connection.send(data)
                    size_sent += len(data)

            sys.stdout.write("\n")
            data_connection.close()
        global t_list
        t = threading.Thread(target = data_func)
        t.start()
        t_list.append(t)
        msg = ftp_socket.recv(RECV_BUFFER)
        if verbose_on:
            print(msg_str_decode(msg,True))


### put_ftp
def put_ftp(tokens,ftp_socket,data_socket):

    if (len(tokens) < 2):
        print("put [filename]. Please specify filename")
        return

    local_filename = tokens[1]
    if (len(tokens) == 3):
        filename = tokens[2]
    else:
        filename = local_filename

    if (os.path.isfile(local_filename) == False):
        print(("Filename does not exisit on this client. Filename: " + filename + " -- Check file name and path"))
        return
    filestat = os.stat(local_filename)
    filesize = filestat.st_size

    message=str_msg_encode("STOR " + filename + "\r\n")
    global debug_mode
    if debug_mode:
        print("(DEBUG) --> " + message.decode())
    ftp_socket.send(message)
    msg = ftp_socket.recv(RECV_BUFFER)
    if verbose_on:
        print(msg_str_decode(msg,True))
        print(("Attempting to send file. Local: " + local_filename + " - Remote:" + filename + " - Size:" + str(filesize)))
    def data_func():
        data_connection, data_host = data_socket.accept()
        file_bin = open(filename,"rb") #read and binary modes

        size_sent = 0
        #use write so it doesn't produce a new line (like print)
        while True:
            data = file_bin.read(RECV_BUFFER)
            if (not data or data == '' or len(data) <= 0):
                file_bin.close()
                break
            else:
                data_connection.send(data)
                size_sent += len(data)

        sys.stdout.write("\n")
        data_connection.close()
    global t_list
    t = threading.Thread(target = data_func)
    t.start()
    t_list.append(t)
    msg = ftp_socket.recv(RECV_BUFFER)
    if verbose_on:
        print(msg_str_decode(msg,True))

#
def ls_ftp(tokens,ftp_socket,data_socket):
    if (len(tokens) > 1):
        message = str_msg_encode("LIST " + tokens[1] + "\r\n")
        global debug_mode
        if debug_mode:
            print("(DEBUG) --> " + message.decode())
        ftp_socket.send(message)
    else:
        message = str_msg_encode("LIST\r\n")
        if debug_mode:
            print("(DEBUG) --> " + message.decode())
        ftp_socket.send(message)

    msg = ftp_socket.recv(RECV_BUFFER)
    if verbose_on:
        print(msg_str_decode(msg,True))
    strValue = msg_str_decode(msg)
    tokens = strValue.split()
    if (tokens[0] != "200" and tokens[0]!="150"):
        print("Unable to list directory contents. Check that you have permissions")
        return
    def data_func():
        data_connection, data_host = data_socket.accept()
        print()
        msg = data_connection.recv(RECV_BUFFER)
        while (len(msg) > 0):
            print(msg_str_decode(msg,True))
            msg = data_connection.recv(RECV_BUFFER)

        data_connection.close()
    global t_list
    t = threading.Thread(target = data_func)
    t.start()
    t_list.append(t)
    msg = ftp_socket.recv(RECV_BUFFER)
    if verbose_on:
        print(msg_str_decode(msg,True))

    #data_connection.close()

def delete_ftp(tokens, ftp_socket):

    if (len(tokens) < 2):
        print("You must specify a file to delete")
    else:
        message = str_msg_encode("DELE " + tokens[1] + "\r\n")
        global debug_mode
        if debug_mode:
            print("(DEBUG) --> " + message.decode())
        if verbose_on:
            print(("Attempting to delete " + tokens[1]))

        ftp_socket.send(message)

    msg = ftp_socket.recv(RECV_BUFFER)
    if verbose_on:
        print(msg_str_decode(msg,True))

def logout(lin, ftp_socket):
    if (ftp_socket is None):
        print("Your connection was already terminated.")
        return False, ftp_socket
    global t_list
    for t in t_list:
        t.join()
    if (lin == False):
        print("You are not logged in. Logout command will be send anyways")
    if verbose_on:
        print("Attempting to logged out")
    msg = ""
    try:
        ftp_socket.send(str_msg_encode("QUIT\r\n"))
        msg = ftp_socket.recv(RECV_BUFFER)
    except socket.error:
        print ("Problems logging out. Try logout again. Do not login if you haven't logged out!")
        return False
    if verbose_on:
        print(msg_str_decode(msg,True))
    return False, ftp_socket #it should only be true if logged in and not able to logout

def quit_ftp(lin,ftp_socket):
    print ("Quitting...")
    logged_on, ftp_socket = logout(lin,ftp_socket)
    print("Thank you for using FTP")

    try:
        if (ftp_socket is not None):
            ftp_socket.close()
    except socket.error:
        print ("Socket was not able to be close. It may have been closed already")

    sys.exit()

def relogin(username,password,logged_on,tokens,hostname,ftp_socket):
    if (len(tokens) < 3):
        print("LOGIN requires more arguments. LOGIN [username] [password]")
        print("You will be prompted for username and password now")
        username = input("User:")
        password = input("Pass:")
    else:
        username = tokens[1]
        password = tokens[2]

    if (ftp_socket is None):
        ftp_socket = ftp_connecthost(hostname)
        ftp_recv = ftp_socket.recv(RECV_BUFFER)

        print(msg_str_decode(ftp_recv,True))

    logged_on = login(username, password, ftp_socket)
    return username, password, logged_on, ftp_socket


def help_ftp(tokens):
    printed=False
    if not len(tokens) > 1:
        print("FTP Help")
        print("Commands are not case sensitive")
        print("")
    if len(tokens) >1:
        tokens[1] = tokens[1].upper()
    if(not len(tokens) > 1 or tokens[1] == CMD_QUIT):
        print((CMD_QUIT + "\t\t Exits ftp and attempts to logout"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_LOGIN):
        print((CMD_LOGIN + "\t\t Logins. It expects username and password. LOGIN [username] [password]"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_LOGOUT):
        print((CMD_LOGOUT + "\t\t Logout from ftp but not client"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_LS):
        print((CMD_LS + "\t\t prints out remote directory content"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_DIR):
        print((CMD_DIR + "\t\t prints out remote directory content"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_PWD):
        print((CMD_PWD + "\t\t prints current (remote) working directory"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_GET):
        print((CMD_GET + "\t\t gets remote file. GET remote_file [name_in_local_system]"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_PUT):
        print((CMD_PUT + "\t\t sends local file. PUT local_file [name_in_remote_system]"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_DELETE):
        print((CMD_DELETE + "\t\t deletes remote file. DELETE [remote_file]"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_HELP):
        print((CMD_HELP + "\t\t prints help FTP Client. You can specify command."))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_MKDIR):
        print((CMD_MKDIR + "\t\t Creates (remote) directory. MKDIR [directory]"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_RMDIR):
        print((CMD_RMDIR + "\t\t Removes (remote) directory. RMDIR [directory]"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_CD):
        print((CMD_CD + "\t\t Change (remote) working directory. CD [directory]"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_PORT):
        print((CMD_PORT + "\t\t [host-port]"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_USER):
        print((CMD_USER + "\t\t Enter username. USER [username]"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_PASS):
        print((CMD_PASS + "\t\t Enter password. PASS [password]"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_NOOP):
        print((CMD_NOOP + "\t\t It specifies no action other than that the server send an OK reply."))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_IMAGE):
        print((CMD_IMAGE + "\t\t Sets mode to Image."))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_DISC):
        print((CMD_DISC + "\t\t Disconnects from the server."))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_LCD):
        print((CMD_LCD + "\t\t Changes local directory. LCD [pathname]"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_RHELP):
        print((CMD_RHELP + "\t\t get help from remote server. RHELP [command (optional)]"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_APPEND):
        print((CMD_APPEND + "\t\t Append to a file. APPEND [filename]"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_ASCII):
        print((CMD_ASCII + "\t\t set ASCII transfer type."))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_TYPE):
        print((CMD_TYPE + "\t\t Set file transfer type. TYPE [type-code]"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_EXIT):
        print((CMD_EXIT + "\t\t terminate ftp session and exit"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_LPWD):
        print((CMD_LPWD + "\t\t Prints local working directory"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_BIN):
        print((CMD_BIN + "\t\t Sets binary transfer type"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_SEND):
        print((CMD_SEND + "\t\t sends local file. SEND [local_file] [name_in_remote_system]"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_BYE):
        print((CMD_BYE + "\t\t terminate ftp session and exit"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_USAGE):
        print((CMD_USAGE + "\t\t Prints the usage information"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_VERBOSE):
        print((CMD_VERBOSE + "\t\t toggle verbose mode"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_CDUP):
        print((CMD_CDUP + "\t\t change remote working directory to parent directory"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_OPEN):
        print((CMD_OPEN + "\t\t connect to remote ftp"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_FTP):
        print((CMD_FTP + "\t\t connect to remote ftp"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_QUESTION):
        print((CMD_QUESTION + "\t\t prints help FTP Client. You can specify command."))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_CLOSE):
        print((CMD_CLOSE + "\t\t terminate ftp session and exit"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_DEBUG):
        print((CMD_DEBUG + "\t\t Toggle/set debug mode. DEBUG [0 or 1]"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_RENAME):
        print((CMD_RENAME + "\t\t Renames file. RENAME [remote_filename] [new_file_name]"))
        printed=True
    if(not len(tokens) > 1 or tokens[1] == CMD_SUNIQUE):
        print((CMD_SUNIQUE + "\t\t toggle store unique on remote machine"))
        printed=True
    if len(tokens) >1 and not printed:
        print("Command does not exist")



def noop_ftp(ftp_socket):
    message = "NOOP\n".encode()
    global debug_mode
    if debug_mode:
        print("(DEBUG) --> " + message.decode())
    ftp_socket.send(message)
    msg = ftp_socket.recv(RECV_BUFFER).decode()
    if verbose_on:
        print(msg.strip('\n'))

def login(user, passw, ftp_socket):
    if (user == None or user.strip() == ""):
        print("Username is blank. Try again")
        return False;

    if verbose_on:
        print(("Attempting to login user " + user))
    #send command user
    message = str_msg_encode("USER " + user + "\n")
    global debug_mode
    if debug_mode:
        print("(DEBUG) --> " + message.decode())
    ftp_socket.send(message)
    msg = ftp_socket.recv(RECV_BUFFER)
    if verbose_on:
        print(msg_str_decode(msg,True))
    message = str_msg_encode("PASS " + passw + "\n")
    if debug_mode:
        print("(DEBUG) --> " + message.decode())
    ftp_socket.send(message)
    msg = ftp_socket.recv(RECV_BUFFER)
    strValue = msg_str_decode(msg,False)
    tokens = strValue.split()
    if verbose_on:
        print(msg_str_decode(msg,True))
    if (len(tokens) > 0 and tokens[0] != "230"):
        print("Not able to login. Please check your username or password. Try again!")
        return False
    else:
        return True

def cwd_ftp(tokens,ftp_socket):
    if (len(tokens) < 2):
        print("cwd [dirname]. Please specify directory name")
        return
    message = ("CWD " + tokens[1] + "\n").encode()
    global debug_mode
    if debug_mode:
        print("(DEBUG) --> " + message.decode())
    ftp_socket.send(message)
    msg = ftp_socket.recv(RECV_BUFFER).decode()
    if verbose_on:
        print(msg.strip('\n'))

def mkd_ftp(tokens,ftp_socket):
    if (len(tokens) < 2):
        print("mkd [dirname]. Please specify directory name")
        return
    message = ("MKD " + tokens[1] + "\n").encode()
    global debug_mode
    if debug_mode:
        print("(DEBUG) --> " + message.decode())
    ftp_socket.send(message)
    msg = ftp_socket.recv(RECV_BUFFER).decode()
    if verbose_on:
        print(msg.strip('\n'))

def rmd_ftp(tokens,ftp_socket):
    if (len(tokens) < 2):
        print("rmd [dirname]. Please specify directory name")
        return
    message = ("RMD " + tokens[1] + "\n").encode()
    global debug_mode
    if debug_mode:
        print("(DEBUG) --> " + message.decode())
    ftp_socket.send(message)
    msg = ftp_socket.recv(RECV_BUFFER).decode()
    if verbose_on:
        print(msg.strip('\n'))

def cdup_ftp(ftp_socket):
    message = "CDUP\n".encode()
    global debug_mode
    if debug_mode:
        print("(DEBUG) --> " + message.decode())
    ftp_socket.send(message)
    msg = ftp_socket.recv(RECV_BUFFER).decode()
    if verbose_on:
        print(msg.strip('\n'))


RECV_BUFFER = 1024
FTP_MODE="ACTIVE"
DATA_PORT_MAX = 25599
DATA_PORT_MIN = 25500
DATA_PORT_BACKLOG = 1
next_data_port = 1
config_file_path = ""
log_file_name = ""
log_all_output = False
default_debug_mode  = "off"
default_verbose_mode = "off"
default_test_file = "test1.txt"
default_log_file = "ftpclient.log"
def read_config():
    parser = ConfigParser()
    parser.read('./ftp_client.cfg')
    global FTP_MODE
    FTP_MODE = (parser.get('ftp', 'default_mode'))
    global DATA_PORT_MIN
    DATA_PORT_MIN = int(parser.get('ftp', 'DATA_PORT_MIN'))
    global DATA_PORT_MAX
    DATA_PORT_MAX = int(parser.get('ftp', 'DATA_PORT_MAX'))
    global FTP_PORT
    if(not args.fp):
        FTP_PORT = int(parser.get('ftp', 'default_ftp_port'))
    global default_debug_mode
    default_debug_mode = (parser.get('ftp', 'default_debug_mode'))
    global default_log_file
    default_log_file = (parser.get('ftp', 'default_log_file'))
    global default_verbose_mode
    default_verbose_mode = (parser.get('ftp', 'default_verbose_mode'))

#Calls main function.
main()
