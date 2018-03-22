from Tkinter import *
from tkColorChooser import askcolor
import socket
import threading
import struct
from threading import Thread
import time
import random
import math
from collections import deque

#TODO figure out json for brightness control in fadecandy extension to OPC

threadShutdown = False
startingColor = (255,255,255)
framerate = 30

def cos(x, offset=0, period=1, minn=0, maxx=1):
    """A cosine curve scaled to fit in a 0-1 range and 0-1 domain by default.

    offset: how much to slide the curve across the domain (should be 0-1)
    period: the length of one wave
    minn, maxx: the output range

    """
    value = math.cos((x/period - offset) * math.pi * 2) / 2 + 0.5
    return value*(maxx-minn) + minn
	
def fade(pixels, start_time):
	t = time.time() - start_time
	newPixels = []
	for idx in range(len(pixels)):
		r = cos(.1, offset=t/8, period=1) * pixels[idx][0]
		g = cos(.1, offset=t/8, period=1) * pixels[idx][1]
		b = cos(.1, offset=t/8, period=1) * pixels[idx][2]
	
		#pixel = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
		#pixel = (255,0,0)
		pixel = (r, g, b)
		newPixels.append(pixel)
		
	return newPixels
	
def shift(pixels):
	tempPixels = deque(pixels)
	tempPixels.rotate(1)
	return list(tempPixels)

def defaultFrameCreate(numPixels, startPixel):
	pixels = []
	for idx in range(int(numPixels)):
		pixels.append(startPixel)
		
	return pixels
	
def shiftFrameCreate(numPixels, startPixel):
	pixels = []
	for idx in range(int(numPixels)):
		val = idx/numPixels
		if val < .5:
			val = 0.5
		
		r = cos(val, offset=0, period=1) * startPixel[0]
		g = cos(val, offset=0, period=1) * startPixel[1]
		b = cos(val, offset=0, period=1) * startPixel[2]
	
		#pixel = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
		pixel = (r, g, b)
		pixels.append(pixel)
		
	return pixels

def run(theSocket):
	global startingColor
	global framerate

	chan = 0
	comm = 0
	length = 0
	origPixels = []
	pixels = []
	numPixels = 64.0
	
	start_time = time.time()
	
	#initial led frame
	origPixels = defaultFrameCreate(numPixels, startingColor)
	#origPixels = shiftFrameCreate(numPixels, startingColor)
	
	pixels = origPixels
	while threadShutdown is False:
		length = len(origPixels)*3
			
		message = struct.pack('B', chan)
		message += struct.pack('B', comm)
		message += struct.pack('!H', length)
		for pix in pixels:
			message += struct.pack('B', pix[0])
			message += struct.pack('B', pix[1])
			message += struct.pack('B', pix[2])
	
		try:
			theSocket.sendall(message)
			time.sleep(1.0/framerate)
		except:
			print "Error in sending"
			break
			
		#update pixel
		#pixels = shift(pixels)
		pixels = fade(origPixels, start_time)
		
			
	print "thread shutdown"
			
def test():
	print "testing function call"
	
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
		self.filemenu.add_command(label="Open        Ctl-O", command=test)
		self.filemenu.add_command(label="Connect     Ctl-N", command=test)
		self.menubar.add_cascade(label="File", menu=self.filemenu)

		#self.brightnessSlider = Scale(self.master, from_=0, to=100, length=200, tickinterval=10, orient=HORIZONTAL)
		#self.brightnessSlider.set(50)
		#self.brightnessSlider.pack()
		
		self.framerateSlider = Scale(self.master, from_=0, to=60, length=200, tickinterval=5, orient=HORIZONTAL, command=self.framerateAction)
		self.framerateSlider.set(30)
		self.framerateSlider.pack()
		
		var = StringVar(self.master)
		var.set("1")
		self.optionMenu = OptionMenu(self.master, var, "1","2","3","4","5","6","7","8")
		self.optionMenu.pack()

		#self.showbutton = Button(self.master, text='Show', command=lambda:show_values(self.brightnessSlider)).pack()
		self.colorbutton = Button(self.master, text='Select Color', command=self.colorAction)
		self.colorbutton.pack()

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
	
	def colorAction(self):
		global startingColor
		startingColor, colorString = askcolor(parent=self.master)
		print startingColor, colorString
	
	def framerateAction(self, event):
		global framerate
		framerate = self.framerateSlider.get()
	
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