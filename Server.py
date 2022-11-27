from PySocket import Server, ServerCommands, ClientObject
import socket
import tkinter
import time


# Functions
# Files
def ReadDataFromFile():
	with open('PORTS.txt', 'r') as rFile:
		return [line.rstrip() for line in rFile]        

	# Button Events        
def GetSelectedPort():
    global PORT
    PORT = int(Display.get(tkinter.ANCHOR))
    Window.destroy()


# Initialize Tkinter Window
Window = tkinter.Tk()
Window.title('Configure Server')
Window.configure(background='black')
Window.geometry('400x400')
Window.resizable(0, 0)

# Create Frame
Main_Frame = tkinter.Frame(Window)
Main_Frame.pack(padx=10, pady=50)

# Create Label
Header = tkinter.Label(Main_Frame, text='Choose Port', fg='green', font='arial 12 normal')
Header.pack(side='top', pady=10)

# Create Lists
ScrollBar = tkinter.Scrollbar(Main_Frame, orient=tkinter.VERTICAL)
Display = tkinter.Listbox(Main_Frame, width=50, yscrollcommand=ScrollBar.set)

# Configure ScrollBar
ScrollBar.config(command=Display.yview)
ScrollBar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

Display.pack() # After Config to iinclude whole GUI

for ports in ReadDataFromFile():
    Display.insert(tkinter.END, ports)

# Create Button
Submit = tkinter.Button(Main_Frame, text='Start Server', width=12, command=GetSelectedPort)
Submit.pack(padx=10, pady=10)


# Run Main Loop
Window.mainloop()

print('Starting Server...')
time.sleep(1.25)

# Server Commands
def OtherCommands(ClientSender: ClientObject, ClientReceiver: ClientObject, Message: str, ClassInstance: Server) -> bool:
    if '$Name$' in Message:
        nName = Message.replace('$Name$', '')
        msgToSend = f'{ClientSender.getAlias()} transformed to {nName}'
        ClassInstance.ClientObjs[ClassInstance.ClientObjs.index(ClientSender)].setAlias(nName)
        ClientReceiver.getClient().sendall(msgToSend.encode('utf-8'))
        ClassInstance.ServerConsole(msgToSend)
        return True
    elif '$Clients$' in Message:
        msgToSend = f'{ClientSender.getAlias()} There are {len(ClassInstance.ClientObjs)} Clients Connected'
        ClientReceiver.getClient().sendall(msgToSend.encode('utf-8'))
        ClassInstance.ServerConsole(msgToSend)
        return True
    return False

SC = ServerCommands(OverrideOtherCommand = OtherCommands)

# Server
S = Server((socket.gethostbyname(socket.gethostname()), PORT))
S.SetCommands(SC)
S.LaunchServer()