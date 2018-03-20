from Tkinter import *
from tkColorChooser import askcolor
import socket
import threading

threadShutdown = False

def run(theSocket):
	message = "test message"
	
	while threadShutdown is False:
	
		try:
			theSocket.sendall(message)
		except:
			break
			
def test():
	print "testing function call"
             
def getColor():
	color = askcolor() 
	print 

def show_values(w1):
	print (w1.get())
	
def connect(ip, port):
	# Create a TCP/IP socket
	theSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	# Connect the socket to the port where the server is listening
	try:
		print "connecting to", ip.strip(), port
		server_address = (ip.strip(), int(port))
		theSocket.connect(server_address)
		return theSocket
	except:
		print "failed to connect"
		return None
		
def disconnect(theSocket):
	if theSocket is not None:
		theSocket.close()
	
def keypressEvent(event):
	x = event.char
	if len(x) > 0:
		x = ord(x)
		print "testing", x
		if x == 15: #ctr-O
			test()
			
class gui:
	def __init__(self):
		self.master = Tk()
		self.master.minsize(width=400, height=200)
		
		self.menubar = Menu(self.master)

		self.filemenu = Menu(self.menubar, tearoff=0)
		self.filemenu.add_command(label="Open    Ctl-O", command=test)
		self.menubar.add_cascade(label="File", menu=self.filemenu)

		self.brightnessSlider = Scale(self.master, from_=0, to=100, length=200, tickinterval=10, orient=HORIZONTAL)
		self.brightnessSlider.set(50)
		self.brightnessSlider.pack()

		self.showbutton = Button(self.master, text='Show', command=lambda:show_values(self.brightnessSlider)).pack()
		self.colorbutton = Button(self.master, text='Select Color', command=getColor).pack()

		self.ipTextBox = Text(self.master, height=1, width=15)
		self.ipTextBox.insert(END, "192.168.2.52")
		self.ipTextBox.pack()

		self.portTextBox = Text(self.master, height=1, width=15)
		self.portTextBox.insert(END, "7890")
		self.portTextBox.pack()

		self.connectButton = Button(self.master, text='Connect', command=self.connectAction)
		self.connectButton.pack()

		self.master.config(menu=self.menubar)

		self.master.bind('<Key>', keypressEvent)
		
	def connectAction(self):
		self.theSocket = connect(self.ipTextBox.get(1.0,END), self.portTextBox.get(1.0,END))
		if self.theSocket is not None:
			print "connection passed"
			self.connectButton['text'] = "Disconnect"
			self.connectButton['command'] = self.disconnectAction
		else:
			print "not connected"
			
	def disconnectAction(self):
		disconnect(self.theSocket)
		self.connectButton['text'] = "Connect"
		self.connectButton['command'] = self.connectAction

def main():
	global theSocket
	program = gui()
	mainloop()
	
	if theSocket is not None:
		theSocket.close()

if __name__ == "__main__":
	main()