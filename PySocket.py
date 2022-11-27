import sys
import time
import socket
import threading
from typing import Any, Callable

class ClientObject:
    def __init__(Self, Client, Addr):
        Self.Client = Client
        Self.Addr = Addr
        Self.Alias = str(Addr)
    
    def getClient(Self):
        return Self.Client
    
    def getAddr(Self):
        return Self.Addr

    def getAlias(Self) -> str:
        return Self.Alias

    def setAlias(Self, newAlias):
        Self.Alias = newAlias

class ServerCommands:
    def __init__(Self,
                OverrideMessageCommand: Callable[[ClientObject, ClientObject, str], None]=None,
                OverrideDisconnectCommand: Callable[[ClientObject, str], bool]=None,
                OverrideOtherCommand: Callable[[ClientObject, ClientObject, str, Any], bool]=None):
        Self.OverrideMessageCommand = OverrideMessageCommand
        Self.OverrideDisconnectCommand = OverrideDisconnectCommand
        Self.OverrideOtherCommand = OverrideOtherCommand

    def NormalMessage(Self, ClientSender: ClientObject, ClientReceiver: ClientObject, Message: str) -> None:
        if Self.OverrideMessageCommand is not None:
            return Self.OverrideMessageCommand(ClientSender, ClientReceiver, Message)
        else:
            msgToSend = ClientSender.getAlias() + ": " + Message
            ClientReceiver.getClient().sendall(msgToSend.encode('utf-8'))

    def DisconnectNotice(Self, ClientSender: ClientObject, Message: str) -> bool:
        if Self.OverrideDisconnectCommand is not None:
            return Self.OverrideDisconnectCommand(ClientSender, Message)
        else:
            if Message == "$Disconnect":
                return True
            return False

    def OtherCommands(Self, ClientSender: ClientObject, ClientReceiver: ClientObject, Message: str, ClassInstance) -> bool:
        if Self.OverrideOtherCommand is not None:
            return Self.OverrideOtherCommand(ClientSender, ClientReceiver, Message, ClassInstance)
        return False

class Server:
    def __init__(
        Self,
        ServerInfo: tuple[str, int],
        ClientLimit: int=None,
        ByteMessageLimit: int=1024
        ):

        Self.ClientObjs: list[ClientObject] = []    # Collect Client Objects
        Self.ClientLimit = ClientLimit              # Client Limit (will disregard if none)
        Self.CurrentClients = 0                     # Current Clients Connected
        Self.Limits = ByteMessageLimit              # Byte Limit to Send
        Self.ServerInfo = ServerInfo                # Set Server Info
        
        Self.Commands = ServerCommands()            # Set Commands; Default
        Self.ServerMessage = "Welcome to Server"    # Set Server Message

        Self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        Self.s.bind(ServerInfo)

    '''
    Intended as: Public

    Call this to start the server
    '''
    def LaunchServer(Self):
        Self.s.listen()
        print(f'Server is Listening on {Self.ServerInfo}')
        while True:
            client, addr = Self.s.accept()

            # Check Client Limit
            if (Self.ClientLimit is None) or (Self.CurrentClients < Self.ClientLimit):
                T = threading.Thread(target=Self.HandleClient, args=(client, addr))
                T.start()

            else:
                Self.ServerConsole('Server Already Full, Please try again later')

    '''
    Intended as: Private

    Args:
        Client -> Client from Conection
        Addr -> Address from Connection
    
    This is called when new client connects to server
    A new thread is also created
    '''
    def HandleClient(Self, Client, Addr):
        try:
            print(f'{Addr} connected to the server')

            # Add Client To List
            clientObj = ClientObject(Client, Addr)
            Self.ClientObjs.append(clientObj)

            # Send Server Announcement
            Self.ServerAnnouncement(clientObj)

            # Handle Client Responses
            Connected = True
            while Connected:
                # Receive Messages
                msg = clientObj.getClient().recv(Self.Limits).decode('utf-8')

                # Check if it is a message about disconnection
                if Self.Commands.DisconnectNotice(clientObj, msg):
                    Self.ClientObjs.remove(clientObj)
                    Self.ServerConsole(f'{clientObj.getAddr()} Disconnected By User')
                    Connected = False
                else:
                    Self.ServerConsole(f'{clientObj.getAlias()}: {msg}')
                
                Self.Broadcast(clientObj, msg)
        except Exception as e:
            print(e)
            Self.ServerConsole(f'{clientObj.getAddr()} Disconnected From Exception')
            Self.ClientObjs.remove(clientObj)

    '''
    Intended as: Private

    Args:
        Client -> To Receive Server Message

    This is called when a new client connects to server
    '''
    def ServerAnnouncement(Self, Client: ClientObject):
        # Send Server Message To Client At Enter
        Client.getClient().sendall(Self.ServerMessage.encode('utf-8'))

    '''
    Intended as: Private

    Args:
        clientSender -> Client to send messages on other clients through server
        message -> message to broadcast

    This is called when a new client connects to server
    '''
    def Broadcast(Self, clientSender: ClientObject, message: str):
        for clientObj in Self.ClientObjs:
            if Self.Commands.OtherCommands(clientSender, clientObj, message, Self):
                pass
            else:
                Self.Commands.NormalMessage(clientSender, clientObj, message)

    '''
    Intended as: Private

    Args:
        message -> message to be printed to console
    
    This is called when an event happens to the server
    '''
    def ServerConsole(Self, message: str):
        print(message)

    '''
    Intended as: Public

    Args:
        message -> set server message
    
    Call this to set a custom server message
    '''
    def SetServerMessage(Self, message: str):
        Self.ServerMessage = message
    
    '''
    Intended as: Public

    Args:
        commands -> set custom server commands
    
    Call this to set custom server commands
    '''
    def SetCommands(Self, commands: ServerCommands):
        Self.Commands = commands

class Client:
    def __init__(Self, ServerInfo: tuple[str, int]):
        Self.Limits = 1024 # Byte Limit to Send
        Self.ServerInfo = ServerInfo
        Self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    '''
    Intended as: Public
    
    Call this to connect to server
    '''
    def ConnectToServer(Self) -> bool:
        try:
            Self.s.connect(Self.ServerInfo)
            return True
        except:
            print('Connection Failed, Server is Down')
            time.sleep(1.5)
            sys.exit(0)

    '''
    Intended as: Public
    
    Call this to send message to server
    '''
    def SendToServer(Self, Message):
        Message.strip()
        if len(Message) != 0:
            Message = Message.encode('utf-8')
            Self.s.sendall(Message)

    '''
    Intended as: Public
    
    Call this to receive messages from server
    '''
    def ClientUpdate(Self):
        Data = Self.s.recv(Self.Limits).decode('utf-8')
        return Data


if __name__ == '__main__':
    print('Please import this library')