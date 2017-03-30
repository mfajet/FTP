# FTP
This is an FTP client and server I made as part of a course called Netcentric computing.
It uses TCP sockets to send messages and data back and forth between client and server.
Currently only supports active mode.

#Mark Fajet FTP Client and Server
In the base directory of ftpsoft, ftp_client.py is the name of the client.
The name of the server is ftp_server.py

1. Run the server in the background using
```
python3 ftp_server.py &
```

2. Run a client (or multiple) using
```
python3 ftp_client.py
```

3. You should be in an interactive environment asking for input
Do the following in order to connect to the server you started previously
```
open 127.0.0.1 2110
```

4. Complete list of commands to run can be viewed by entering
```
help
```

5. type ```quit``` to exit

6. test files can be run in two ways like so: In the command line:
```
cd tests
```
a. If you have bash installed
```
bash systemtestbash.txt
bash sunny1bash.txt
bash sunny2bash.txt
bash rainy1bash.txt
bash rainy2bash.txt
```
b. If you don't have bash installed
```
cat systemtestpipe.txt | python3 ../ftp_client.py
cat sunny1pipe.txt | python3 ../ftp_client.py
cat sunny2pipe.txt | python3 ../ftp_client.py -h 127.0.0.1 -fp 2110
cat rainy1pipe.txt | python3 ../ftp_client.py -h 127.0.0.1 -fp 2110
cat rainy2pipe.txt | python3 ../ftp_client.py -h 127.0.0.1 -fp 2110
```

7. To find a complete list of command line arguments
in the ftp client, type ```usage```
or python3 ftp_server.py -h
