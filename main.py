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
import argparse
import signal

import colorUtils

threadShutdown = False
startingColor = (255,255,255)
framerate = 30
numPixels = 64.0
mode = "screensaver"
numChannels = 8
speed = 10
screensaver_cycle = True

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
		
		pixel = (r, g, b)
		newPixels.append(pixel)

	return newPixels
	
def rainbowCycle(numPixels, angle):
	#pixel = colorUtils.getRainbow(angle)#(r, g, b)
	pixel = colorUtils.getRainbow2(angle)#(r, g, b)
	
	newPixels = []
	for idx in range(int(numPixels)):
		newPixels.append(pixel)
	
	newAngle = angle + 1
	if newAngle > 359:
		newAngle = 0
	
	return newPixels, newAngle
	
def shift(pixels, num):
	tempPixels = deque(pixels)
	tempPixels.rotate(num)
	return list(tempPixels)
	
def fillup(pixels):
	tempPixels = deque(pixels)
	tempPixels.rotate(1)
	tempPixels = list(tempPixels)
	tempPixels[0] = tempPixels[1]
	return tempPixels
	
def testShift(pixels, offset):
	newPixels = []
	numPixels = len(pixels) * 1.0
	for idx in range(int(numPixels)):
		val = idx/numPixels
		if val < .5:
			r = 0
			g = 0
			b = 0
		else:
			r = round(cos(val, offset=offset/numPixels, period=1) * pixels[idx][0])
			g = round(cos(val, offset=offset/numPixels, period=1) * pixels[idx][1])
			b = round(cos(val, offset=offset/numPixels, period=1) * pixels[idx][2])
	
		#pixel = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
		pixel = (r, g, b)
		newPixels.append(pixel)
		
	return newPixels

def rainbowShift(pixels, angle=None):
	#find leading pixel
	retPixel = None
	for x in range(len(pixels)):
		num1 = 0
		num2 = 0
		
		if x+1 >= len(pixels):
			num1 = pixels[x][0]+pixels[x][1]+pixels[x][2]
			num2 = pixels[0][0]+pixels[0][1]+pixels[0][2]
		else:
			num1 = pixels[x][0]+pixels[x][1]+pixels[x][2]
			num2 = pixels[x+1][0]+pixels[x+1][1]+pixels[x+1][2]
			
		if int(num2) == 0 and int(num1) > 0:
			retPixel = (pixels[x][0], pixels[x][1], pixels[x][2])
			break
		
	if retPixel is None:
		print "did not find leading pixel"
		return
	
	if angle is None:
		nextAngle = colorUtils.getCurrentAngle(retPixel)+1
	else:
		nextAngle = angle+1
		
	nextPixel = colorUtils.getRainbow(nextAngle)
	
	print angle, nextAngle, retPixel, nextPixel
	
	rdiff = abs(retPixel[0]-nextPixel[0])
	gdiff = abs(retPixel[1]-nextPixel[1])
	bdiff = abs(retPixel[2]-nextPixel[2])
	
	newPixels = []
	for pix in pixels:
		rnew = 0
		gnew = 0
		bnew = 0
	
		if (pix[0]+pix[1]+pix[2]) > 0:
			rnew = pix[0]+rdiff
			gnew = pix[1]+gdiff
			bnew = pix[2]+bdiff
			
			if rnew > 255:
				rnew = rnew - 255
				
			if gnew > 255:
				gnew = gnew - 255
				
			if bnew > 255:
				bnew = bnew - 255
				
			#print "newpixel", rdiff, gdiff, bdiff
			
		newPixels.append((rnew, gnew, bnew))
	
	return newPixels, nextAngle
	
def defaultFrameCreate(numPixels, startPixel):
	pixels = []
	for idx in range(int(numPixels)):
		pixels.append(startPixel)
		
	return pixels
	
def fillupFrameCreate(numPixels, startPixel):
	pixels = []
	pixels.append(startPixel)
	for idx in range(int(numPixels)-1):
		pixels.append((0,0,0))
		
	return pixels
	
def shiftFrameCreate(numPixels, startPixel):
	pixels = []
	for idx in range(int(numPixels)):
		val = idx/numPixels
		if val < .5:
			val = 0.5
		
		r = round(cos(val, offset=0, period=1) * startPixel[0])
		g = round(cos(val, offset=0, period=1) * startPixel[1])
		b = round(cos(val, offset=0, period=1) * startPixel[2])
	
		#pixel = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
		pixel = (r, g, b)
		pixels.append(pixel)
		
	return pixels

def fillMode(pixels, iterations, numPixels, startingColor):
	if iterations == 0: #first iteration
		newPixels = fillupFrameCreate(numPixels, startingColor)
		iterations = iterations + 1
		updatedPixels = True
	elif iterations > numPixels: #last iteration
		newPixels = pixels
		updatedPixels = False
	else:
		newPixels = fillup(pixels)
		updatedPixels = True
		iterations = iterations + 1
		
	return newPixels, updatedPixels, iterations

def fadeMode(origPixels, iterations, numPixels, startingColor, start_time):
	if iterations == 0: #first iteration
		initPixels = defaultFrameCreate(numPixels, startingColor)
		pixels = origPixels
		iterations = iterations + 1
		updatedPixels = True
	else:
		initPixels = origPixels
		pixels = fade(initPixels, start_time)
		updatedPixels = True
		
	return initPixels, pixels, updatedPixels, iterations

def shiftMode(pixels, direction, iterations, numPixels, startingColor, shiftnum):
	if iterations == 0:
		pixels = shiftFrameCreate(numPixels, startingColor)
		iterations = iterations + 1
		updatedPixels = True
		if direction == "left":
			pixels = pixels[::-1]
	else:
		if direction == "right":
			pixels = shift(pixels, 1)
		else:
			pixels = shift(pixels, -1)
		shiftnum = shiftnum +1
		if shiftnum > numPixels:
			shiftnum = 0
		updatedPixels = True
		
	return pixels, updatedPixels, iterations, shiftnum

def rainbowshiftMode(directions, angle, numPixels, shiftnum):
	pixel = colorUtils.getRainbow(angle)
	angle = angle + 1
	if angle > 359:
		angle = 0
	pixels = shiftFrameCreate(numPixels, pixel)
	if directions == "left":
		tempNum = shiftnum - (shiftnum*2)
	else:
		tempNum = shiftnum
	pixels = shift(pixels, tempNum)
	shiftnum = shiftnum + 1
	if shiftnum > numPixels:
		shiftnum = 0
	updatedPixels = True
	
	return pixels, angle, updatedPixels, shiftnum

def rainbowMode(angle, numPixels):
	pixels, angle = rainbowCycle(numPixels, angle)
	updatedPixels = True
	
	return pixels, updatedPixels, angle

def opcSend(theSocket, pixels):
	global numChannels
	comm = 0

	for c in range(numChannels):
		chan = c
		length = len(pixels)*3
			
		message = struct.pack('B', chan)
		message += struct.pack('B', comm)
		message += struct.pack('!H', length)
		for pix in pixels:
			message += struct.pack('B', pix[0])
			message += struct.pack('B', pix[1])
			message += struct.pack('B', pix[2])
			
			#testing gamma correction
			#r1, g1, b1 = (pix[0]/255.0, pix[1]/255.0, pix[2]/255.0)
			#r, g, b = colorUtils.gamma((r1, g1, b1), 2.5)
			#message += struct.pack('B', r*255)
			#message += struct.pack('B', g*255)
			#message += struct.pack('B', b*255)
	
		try:
			theSocket.sendall(message)
		except:
			print "Error in sending"
			break
				
def run(theSocket):
	global startingColor
	global framerate
	global numPixels
	global numChannels
	global mode
	global speed
	global screensaver_cycle
	
	modes = ["fill","rainbow","fade","rshift","lshift","rainbow_rshift","rainbow_lshift"]

	origPixels = []
	pixels = []
	
	start_time = time.time()
	angle = 0
	
	#initial led frame
	if mode == "solid":
		origPixels = defaultFrameCreate(numPixels, startingColor)
	else:
		origPixels = defaultFrameCreate(numPixels, (0,0,0))
	
	pixels = origPixels
	last_time = time.time()
	modspeed = ((1.0/(speed))*framerate)
	shiftnum = 0
	updatedPixels = True
	iterations = 0
	
	while threadShutdown is False:
	
		if updatedPixels is True:
			opcSend(theSocket, pixels)
			updatedPixels = False
				
		#update pixels
		current_time = time.time()
		diff_time = current_time - last_time
		if diff_time > modspeed: #speed modifier
		
			if mode == "fill":
				pixels, updatedPixels, iterations = fillMode(pixels, iterations, numPixels, startingColor)
					
			elif mode == "rainbow":
				pixels, updatedPixels, angle = rainbowMode(angle, numPixels)
				
			elif mode == "fade":
				origPixels, pixels, updatedPixels, iterations = fadeMode(origPixels, iterations, numPixels, startingColor, start_time)
					
			elif mode == "rshift":
				pixels, updatedPixels, iterations, shiftnum = shiftMode(pixels, "right", iterations, numPixels, startingColor, shiftnum)
					
			elif mode == "lshift":
				pixels, updatedPixels, iterations, shiftnum = shiftMode(pixels, "left", iterations, numPixels, startingColor, shiftnum)
					
			elif mode == "rainbow_rshift":
				pixels, angle, updatedPixels, shiftnum = rainbowshiftMode("right", angle, numPixels, shiftnum)
				
			elif mode == "rainbow_lshift":
				pixels, angle, updatedPixels, shiftnum = rainbowshiftMode("left", angle, numPixels, shiftnum)

			last_time = time.time()
		time.sleep(1.0/framerate)
		
		if screensaver_cycle is True:
			cur_time = time.time()
			dif = cur_time - start_time
			if dif > 5:
				mode = random.choice(modes)
				start_time = cur_time
				pixels = defaultFrameCreate(numPixels, (0,0,0))
				updatedPixels = True
				shiftnum = 0
				updatedPixels = True
				iterations = 0
	
	#before exit turn off LEDs
	pixels = defaultFrameCreate(numPixels, (0,0,0))
	opcSend(theSocket, pixels)
			
	print "thread shutdown"
			
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
		#print "testing", x
		if x == 15: #ctr-O
			None
		else:
			print "testing:", x
			
class gui:
	def __init__(self, ip="127.0.0.1", port="22368"):
		self.theSocket = None
		self.theThread = None
		
		self.master = Tk()
		self.master.title("LightCycle")
		self.master.minsize(width=400, height=200)
		try:
			self.master.iconbitmap('lightcycle_16x16.ico')
		except:
			pass
		
		self.menubar = Menu(self.master)

		self.filemenu = Menu(self.menubar, tearoff=0)
		self.filemenu.add_command(label="Open        Ctl-O")#, command=test)
		self.filemenu.add_command(label="Connect     Ctl-N", command=self.connectAction)
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
		self.ipTextBox.insert(END, ip)
		self.ipTextBox.pack()

		self.portTextBox = Text(self.master, height=1, width=15)
		self.portTextBox.insert(END, port)
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
			
class nongui:
	def __init__(self, ip="127.0.0.1", port=22368):
		self.ip = ip
		self.port = port
		self.theSocket = None
		self.theThread = None
	
	def start(self):
		self.theSocket = connect(self.ip, self.port)
		
		if self.theSocket is not None:
			threadShutdown = False
			self.theThread = Thread(target=run, args=(self.theSocket,))
			self.theThread.start()
		else:
			if self.theThread is not None:
				threadShutdown = True
				self.theThread.join()
	
	def mainloop(self):
		global threadShutdown
		
		while threadShutdown is False:
			None
	
	def cleanup(self):
		global threadShutdown
		
		if self.theThread is not None:
			threadShutdown = True
			self.theThread.join()
	
		if self.theSocket is not None:
			self.theSocket.close()
			
def selectColor(color):
	pixel = (255, 255, 255)
	
	color = color.lower()
	
	if color == "red":
		pixel = (255, 0, 0)
	elif color == "green":
		pixel = (0, 255, 0)
	elif color == "blue":
		pixel = (0, 0, 255)
	elif color == "white":
		pixel = (255, 255, 255)
	elif color == "orange":
		pixel = (255,165,0)
	elif color == "yellow":
		pixel = (255, 255, 0)
	elif color == "purple":
		pixel = (160,32,240)
	elif color == "black":
		pixel = (0,0,0)

	return pixel

def signalCleanup(signum, frame):
	global threadShutdown
	threadShutdown = True
	
def main():
	global startingColor
	global framerate
	global mode
	global program
	global speed

	parser = argparse.ArgumentParser()
	parser.add_argument("-g", "--gui", action='store_true', help="enable the GUI")
	parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2], help="increase output verbosity")
	parser.add_argument("-c", "--color", default="white", help="select color to start")
	parser.add_argument("-f", "--framerate", default=framerate, help="starting framerate")
	parser.add_argument("-m", "--mode", default="screensaver", help="animation mode (i.e screensaver)")
	parser.add_argument("-i", "--ip", default="127.0.0.1", help="ip address of OPC server")
	parser.add_argument("-p", "--port", type=int, default=22368, help="port number for OPC server")
	parser.add_argument("-s", "--speed", type=int, default=10, help="animation speed setting")
	
	args = parser.parse_args()
	
	startingColor = selectColor(args.color)
	mode = args.mode
	speed = args.speed
	
	if args.gui is True:
		program = gui(ip=args.ip, port=str(args.port))
		mainloop()
		program.cleanup()
	else:
		signal.signal(signal.SIGINT, signalCleanup)
		program = nongui(args.ip, args.port)
		program.start()
		program.mainloop()
		program.cleanup()

if __name__ == "__main__":
	main()