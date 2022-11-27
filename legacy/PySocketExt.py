# Extra Lib For Sockets
import socket
import sys
import time
import random
import threading

class Crypto:
    def __init__(Self):
        print()

class Server:
    def __init__(Self, SERVER):
        Self.Clients = {} # Collect Clients Connected
        Self.Alias = {} # Collect Aliases
        Self.Limits = 1024 # Byte Limit to Send
        Self.SERVER = SERVER
        Self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        Self.s.bind(SERVER)

    def LaunchServer(Self):
        Self.s.listen()
        print(f'Server is Listening on {Self.SERVER}')
        while True:
            client, addr = Self.s.accept()
            T = threading.Thread(target=Self.HandleClient, args=(client, addr))
            T.start()

    def HandleClient(Self, client, addr):
        try:
            print(f'{addr} connected to the server')
            Self.SendAtClientEntry(client)
            Self.Clients[client] = addr # Add To Clients
            Connected = True
            while Connected:
                msg = client.recv(Self.Limits).decode('utf-8') # Message Itself
                if msg == '<*Server_Discon*>':
                    Self.Clients.pop(client) # Remove To Clients
                    print(f'{addr} Disconnected')
                    Self.SendBack(addr, msg)
                    Connected = False
                else:
                    print(f'{addr}: {msg}')
                    Self.SendBack(addr, msg)
                    
        except:
            print(f'{addr} [X] Disconnected')
            Self.Clients.pop(client) # Remove To Clients

    def SendAtClientEntry(Self, client):
        msgToSend = 'Welcome To The Server, Change your name using $<NewName>$, See How Many Are Connected Using <$Len$>, And Disconnect Using <*Server_Discon*>'
        client.sendall(msgToSend.encode('utf-8'))

    def SendBack(Self, addr, msg):
        for client in Self.Clients.keys():
            # Check For Change Name
            if '$<NewName>$' in msg:
                ip, port = addr
                nName = msg.replace('$<NewName>$', '')
                Self.Alias[ip] = nName
                msgToSend = f'{ip} transformed to {nName}'
                client.sendall(msgToSend.encode('utf-8')) # Send Back To All
            # Check For Disconnection Request
            elif '<*Server_Discon*>' in msg:
                msgToSend = f'{addr} Disconnected From The Server'
                client.sendall(msgToSend.encode('utf-8')) # Send Back To All
            # Check For Length Request
            elif '<$Len$>' in msg:
                msgToSend = f'{addr} There are {len(Self.Clients)} Clients Connected'
                client.sendall(msgToSend.encode('utf-8')) # Send Back To All
            # Normal Message
            else:
                ip, port = addr
                # Check For Aliases
                if Self.Alias.get(ip) is not None:
                    ip = Self.Alias.get(ip)
                # Finalize Message
                msgToSend = str(ip) + ": " + msg
                client.sendall(msgToSend.encode('utf-8')) # Send Back To All

class Client:
    def __init__(Self, Host, Port):
        Self.Limits = 1024 # Byte Limit to Send
        Self.Host = Host
        Self.Port = Port
        Self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def ConnectToServer(Self):
        try:
            Self.s.connect((Self.Host, Self.Port))
            return True
        except:
            print('Connection Failed, Server is Down')
            time.sleep(1.5)
            sys.exit(0)

    def SendToServer(Self, Message):
        Message.strip()
        if len(Message) != 0:
            Message = Message.encode('utf-8')
            Self.s.sendall(Message)

    def ClientUpdate(Self):
        Data = Self.s.recv(Self.Limits).decode('utf-8')
        return Data


if __name__ == '__main__':
    print('Use this as a library or Debug Here')
    x = input()
    if x == 'SERVER':
        ADDR = (socket.gethostbyname(socket.gethostname()), 65432)
        S = Server(ADDR)
        S.LaunchServer()
    elif x == 'CLIENT':
        C = Client('169.254.249.97', 65432)
        Stats = C.ConnectToServer()
        while Stats:
            y = input('Message: ')
            C.SendToServer(y)
            C.ClientUpdate()
    else:
        exit(0)


