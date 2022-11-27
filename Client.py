from PySocket import Client
from tkinter import messagebox # Separate Import
import sys
import tkinter
import socket
import threading

MSG_LIMIT = 750

def WindowClosed():
    Window.destroy()
    sys.exit(0)

############################################# <PreLoad> #############################################

def ReadDataFromFile():
    with open('PORTS.txt', 'r') as rFile:
        return [line.rstrip() for line in rFile]

def OnClick():
    global HOST, PORT, IsChangeName, NewName
    IsChangeName = False
    if PortList.get(tkinter.ANCHOR) == '':
        PORT = 65432
    else:
        PORT = int(PortList.get(tkinter.ANCHOR))
    if len(H_Entry.get().strip()) != 0:
        IsChangeName = True
        NewName = str(H_Entry.get())
    HOST = socket.gethostbyname(socket.gethostname())
    T_Window.destroy()

# Initialization
T_Window = tkinter.Tk()
T_Window.title('Initialize Socket')
T_Window.geometry('400x400')
T_Window.configure(background='black')
T_Window.resizable(0, 0)

# Frames
F1 = tkinter.Frame(T_Window, bg='black')
F2 = tkinter.Frame(T_Window, bg='black')
F1.pack(pady=10)
F2.pack(pady=10)

# Label[Host]
H_Label = tkinter.Label(F1, text='Enter Intended Name <Leave Blank If Default>', bg='black', fg='white')
H_Label.pack()

# Entry[Host]
H_Entry = tkinter.Entry(F1, width=15)
H_Entry.pack()

# Label[Port]
P_Label = tkinter.Label(F2, text='Choose Port <Default If None is Chosen>', bg='black', fg='lightgreen')
P_Label.pack()

# ListBox[Port]
Scrollbar = tkinter.Scrollbar(F2, orient=tkinter.VERTICAL)
PortList = tkinter.Listbox(F2, width = 35, yscrollcommand=Scrollbar.set)
Scrollbar.config(command=PortList.yview)
Scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
PortList.pack()
for ports in ReadDataFromFile():
    PortList.insert(tkinter.END, ports)

# Submit Button
Submit = tkinter.Button(T_Window, text='Connect', width=10, command=OnClick)
Submit.pack()

# Main loop
T_Window.mainloop()

# Initialize Client
C = Client((HOST, PORT))
C.ConnectToServer()

# Request Change of Name
if IsChangeName:
    C.SendToServer('$<NewName>$' + NewName)

############################################# <MAIN> #############################################

def ReceiveMessages():
    while True:
        try:
            MessageBox.insert(tkinter.END, C.ClientUpdate())
        except:
            Window.destroy()
            sys.exit(0)

def OnSendClick():
    try:
        msg = str(EnterMessage.get())
        # Check If Nothing
        if len(msg.strip()) == 0:
            messagebox.showerror('Input Error', 'You Have No Input')
        elif len(msg.strip()) > MSG_LIMIT:
            messagebox.showerror('Size Error', 'Your Input Exceeds the Maximum amount')
        else:
            # Clear Entry
            EnterMessage.delete(0, tkinter.END)
            EnterMessage.insert(0, '')
            # Send To Server
            C.SendToServer(msg)
    except:
        Window.destroy()
        sys.exit(0)

# Create Window
Window = tkinter.Tk()
Window.title('[Chat System] <Client>')
Window.geometry('450x450')
Window.resizable(0, 0)
Window.configure(background='black')

# Create Frame
Top_Frame = tkinter.Frame(Window)
Middle_Frame = tkinter.Frame(Window)
Bottom_Frame = tkinter.Frame(Window, bg='black')

Top_Frame.pack(pady=25)
Middle_Frame.pack(pady=10)
Bottom_Frame.pack()


# Create Header
Header = tkinter.Label(Top_Frame, height=1, width=70, bg='#001018', fg='blue', text='Chat System', font=('Comic Sans MS', 20, 'normal'))
Header.pack()

# Create MessageBox
ScrollBar = tkinter.Scrollbar(Middle_Frame, orient=tkinter.VERTICAL)
MessageBox = tkinter.Listbox(Middle_Frame, height=7, width=52, yscrollcommand=ScrollBar.set, font=('Comic Sans MS', 10, 'normal'))
ScrollBar.config(command=MessageBox.yview)
ScrollBar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
MessageBox.pack()

# Create Label For Messages
SendMessageLabel = tkinter.Label(Bottom_Frame, width=20, bg='black', fg='white', text='Type Your Message:', font=('Comic Sans MS', 10, 'normal'))
SendMessageLabel.grid(row=1, column=1)

# Create Entry
EnterMessage = tkinter.Entry(Bottom_Frame, width=30, font=('Comic Sans MS', 10, 'normal'))
EnterMessage.grid(row=1, column=2)

# Create Button
BlankRow = tkinter.Label(Bottom_Frame, bg='black', width=63)
BlankRow.grid(row=2, column=1, columnspan=2)

SendButton = tkinter.Button(Bottom_Frame, text='Send', width=10, command=OnSendClick, font=('Comic Sans MS', 10, 'normal'), fg='green')
SendButton.grid(row=3, column=1, columnspan=2)

### -- Sockets -- ###

# Start Thread For Receiving Messages
thread = threading.Thread(target=ReceiveMessages)
thread.start()

# Check If Closed
Window.protocol('WM_DELETE_WINDOW', WindowClosed)

# Main Loop
Window.mainloop()


# Check If Used as Module
if __name__ == '__module__':
    print('Use this as a script')
