from Tkinter import *
from tkColorChooser import askcolor
import socket
import threading
import struct
from threading import Thread
import time
import random

threadShutdown = False

def run(theSocket):
	chan = 0
	comm = 0
	length = 0
	pixels = []
	numPixels = 25
	
	while threadShutdown is False:
		pixels = []
		for idx in range(numPixels):
			pixel = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
			#pixel = (255,0,0)
			pixels.append(pixel)
		length = len(pixels)*3
			
		message = struct.pack('B', chan)
		message += struct.pack('B', comm)
		message += struct.pack('!H', length)
		for pix in pixels:
			message += struct.pack('B', pix[0])
			message += struct.pack('B', pix[1])
			message += struct.pack('B', pix[2])
	
		try:
			theSocket.sendall(message)
			time.sleep(1) #TODO make this framerate
		except:
			print "Error in sending"
			break
			
	print "thread shutdown"
			
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
		self.theSocket = None
		self.theThread = None
		
		self.master = Tk()
		self.master.minsize(width=400, height=200)
		
		self.menubar = Menu(self.master)

		self.filemenu = Menu(self.menubar, tearoff=0)
		self.filemenu.add_command(label="Open    Ctl-O", command=test)
		self.menubar.add_cascade(label="File", menu=self.filemenu)

		self.brightnessSlider = Scale(self.master, from_=0, to=100, length=200, tickinterval=10, orient=HORIZONTAL)
		self.brightnessSlider.set(50)
		self.brightnessSlider.pack()
		
		var = StringVar(self.master)
		var.set("1")
		self.optionMenu = OptionMenu(self.master, var, "1","2","3","4","5","6","7","8")
		self.optionMenu.pack()

		#self.showbutton = Button(self.master, text='Show', command=lambda:show_values(self.brightnessSlider)).pack()
		self.colorbutton = Button(self.master, text='Select Color', command=getColor).pack()

		self.ipTextBox = Text(self.master, height=1, width=15)
		self.ipTextBox.insert(END, "192.168.120.136")
		self.ipTextBox.pack()

		self.portTextBox = Text(self.master, height=1, width=15)
		self.portTextBox.insert(END, "22368")
		self.portTextBox.pack()

		self.connectButton = Button(self.master, text='Connect', command=self.connectAction)
		self.connectButton.pack()
		
		self.testButton = Button(self.master, text='Test', command=self.runAction, state='disabled')
		self.testButton.pack()

		self.master.config(menu=self.menubar)

		self.master.bind('<Key>', keypressEvent)
		
	def connectAction(self):
		self.theSocket = connect(self.ipTextBox.get(1.0,END), self.portTextBox.get(1.0,END))
		if self.theSocket is not None:
			print "connection passed"
			self.connectButton['text'] = "Disconnect"
			self.connectButton['command'] = self.disconnectAction
			self.testButton['state'] = 'normal'
		else:
			print "not connected"
			
	def disconnectAction(self):
		disconnect(self.theSocket)
		self.connectButton['text'] = "Connect"
		self.connectButton['command'] = self.connectAction
		self.testButton['state'] = 'disabled'
		
	def runAction(self):
		global threadShutdown
		
		if self.testButton['text'] == "Test":
			threadShutdown = False
			self.theThread = Thread(target=run, args=(self.theSocket,))
			self.theThread.start()
			self.testButton['text'] = "Stop"
		else:
			if self.theThread is not None:
				threadShutdown = True
				self.theThread.join()
			self.testButton['text'] = "Test"
		
	def cleanup(self):
		global threadShutdown
		
		if self.theThread is not None:
			threadShutdown = True
			self.theThread.join()
	
		if self.theSocket is not None:
			self.theSocket.close()

def main():
	program = gui()
	mainloop()
	program.cleanup()

if __name__ == "__main__":
	main()