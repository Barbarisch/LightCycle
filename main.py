from tkinter import *
from tkinter.colorchooser import askcolor
import socket
import threading
import struct
from threading import Thread
import time
import random
import math
import argparse
import cmd
from collections import deque

# local imports
import colorUtils


def cos(x, offset=0, period=1, minn=0, maxx=1):
    """A cosine curve scaled to fit in a 0-1 range and 0-1 domain by default.

    offset: how much to slide the curve across the domain (should be 0-1)
    period: the length of one wave
    minn, maxx: the output range

    """
    value = math.cos((x/period - offset) * math.pi * 2) / 2 + 0.5
    return value*(maxx-minn) + minn
	
def fade(pixels, start_time):
	""" Use cosine function to fade pixel list (in or out) """
	t = time.time() - start_time
	newPixels = []

	for idx in range(len(pixels)):
		r = cos(.1, offset=t/8, period=1) * pixels[idx][0]
		g = cos(.1, offset=t/8, period=1) * pixels[idx][1]
		b = cos(.1, offset=t/8, period=1) * pixels[idx][2]
		
		pixel = (int(r), int(g), int(b))
		newPixels.append(pixel)

	return newPixels
	
def shift(pixels, num):
	tempPixels = deque(pixels)
	tempPixels.rotate(num)
	return list(tempPixels)
	
	
def defaultFrameCreate(numPixels, pixelColor):
	pixels = []
	for idx in range(numPixels):
		pixels.append(pixelColor)
		
	return pixels
	
def shiftFrameCreate(numPixels, startPixel):
	pixels = []
	for idx in range(numPixels):
		val = idx/numPixels
		if val < .5:
			val = 0.5
		
		r = round(cos(val, offset=0, period=1) * startPixel[0])
		g = round(cos(val, offset=0, period=1) * startPixel[1])
		b = round(cos(val, offset=0, period=1) * startPixel[2])
	
		pixel = (r, g, b)
		pixels.append(pixel)
		
	return pixels

def changeBrightness(pixels, modifier):
	newPixels = []
	for pixel in pixels:
		newPixels.append((int(pixel[0]*modifier), int(pixel[1]*modifier), int(pixel[2]*modifier)))
	return newPixels

				
class gui:
	def __init__(self, lightcycle):
		self.lightcycle = lightcycle
		
		self.master = Tk()
		self.master.title("LightCycle")
		self.master.minsize(width=400, height=200)
		try:
			self.master.iconbitmap('lightcycle_16x16.ico')
		except:
			pass
		
		self.menubar = Menu(self.master)
		self.filemenu = Menu(self.menubar, tearoff=0)
		#self.filemenu.add_command(label="Open        Ctl-O")#, command=test)
		#self.filemenu.add_command(label="Connect     Ctl-N", command=self.startAction)
		self.menubar.add_cascade(label="File", menu=self.filemenu)

		self.brightnessSlider = Scale(self.master, from_=0, to=100, length=300, tickinterval=5, orient=HORIZONTAL, command=self.brightnessAction)
		self.brightnessSlider.set(50)
		self.brightnessSlider.pack()
		
		self.speedSlider = Scale(self.master, from_=1, to=10, length=200, tickinterval=1, orient=HORIZONTAL, command=self.speedAction)
		self.speedSlider.set(30)
		self.speedSlider.pack()
		
		var = StringVar(self.master)
		var.set('none')
		self.optionMenu = OptionMenu(self.master, var, *self.lightcycle.modes, command=self.modeAction)
		self.optionMenu.pack()

		self.colorbutton = Button(self.master, text='Select Color', command=self.colorAction)
		self.colorbutton.pack()

		self.ipTextBox = Text(self.master, height=1, width=15)
		self.ipTextBox.insert(END, self.lightcycle.ip)
		self.ipTextBox.pack()

		self.portTextBox = Text(self.master, height=1, width=15)
		self.portTextBox.insert(END, self.lightcycle.port)
		self.portTextBox.pack()

		self.startButton = Button(self.master, text='Start', command=self.startAction)
		self.startButton.pack()
		self.stopButton = Button(self.master, text='Stop', command=self.stopAction, state='disabled')
		self.stopButton.pack()

		self.master.config(menu=self.menubar)
		
	def startAction(self):
		self.lightcycle.start()
		if self.lightcycle.sock is not None:
			self.stopButton['state'] = 'normal'
			
	def stopAction(self):
		self.lightcycle.stop()
		self.stopButton['state'] = 'disabled'
		
	def modeAction(self, value):
		self.lightcycle.switchMode(value)
		
	def brightnessAction(self, event):
		self.lightcycle.brightness = self.brightnessSlider.get()
	
	def colorAction(self):
		color, colorString = askcolor(parent=self.master)
		self.lightcycle.color = color
	
	def speedAction(self, event):
		self.lightcycle.speed = self.speedSlider.get()
	
	def cleanup(self):
		self.lightcycle.stop()


class LightCycleCommandline(cmd.Cmd):
	def __init__(self, lightcycle):
		super().__init__()
		self.lightcycle = lightcycle
		self.prompt = '> '
		self.intro = 'LightCycle: LED controller'
		
	def do_help(self, line):
		usage = [
		'  help - print this help message',
		'  start - connect and start default animation logic',
		'  stop - disconnect and stop animation logic',
		'  mode - change current animation mode. ex: mode rainbowShift',
		'  exit - stop everything and close program',
		'  list - list available animation modes',
		'  on - turn all LEDs on',
		'  off - turn all LEDs off',
		'  brightness - change brightness level (0 - 100, default is 50)',
		'  speed - change speed of animations (1 is fastest, default is 5)',
		'  direction - change direction of linear animations (left or right)', 
		]
		for line in usage:
			print(line)
	
	def emptyline(self):
		""" Do nothing when empty line is input """
		pass
		
	def do_start(self, line):
		self.lightcycle.start()
		
	def do_stop(self, line):
		self.lightcycle.stop()
		
	def do_exit(self, line):
		self.lightcycle.stop()
		return True
		
	def do_list(self, line):
		for mode in self.lightcycle.modes:
			print(mode)
		
	def do_mode(self, line):
		self.lightcycle.switchMode(line.strip())
		
	def do_speed(self, line):
		self.lightcycle.speed = int(line.strip())
		
	def do_color(self, line):
		''' Change base color of animations '''
		self.lightcycle.color = colorUtils.selectColor(line.strip())
		
	def do_direction(self, line):
		self.lightcycle.switchDirection(line.strip())
		
	def do_brightness(self, line):
		self.lightcycle.brightness = int(line.strip())
		
	def do_on(self, line):
		self.lightcycle.on()
		
	def do_off(self, line):
		self.lightcycle.off()
		
	def complete_mode(self, text, line, start_index, end_index):
		# TODO
		pass

	
class LightCycle:
	def __init__(self):
		self.interface = LightCycleCommandline(self)
		self.ip = '127.0.0.1'
		self.port = 7890
		self.sock = None
		self.lightCycleThread = None
		self.stopRun = False
		self.stopMode = False
		self.numPixels = 0
		self.numChannels = 0
		self.mode = 'none'
		self.modes = ['none', 'test', 'flicker', 'flickerOn', 'rainbow', 'shift', 'rainbowShift', 'fill', 'fade']
		self.refreshRate = 60
		self.speed = 5
		self.color = (255,255,255)
		self.direction = 'right'
		self.brightness = 50
		
	def interactive_prompt(self):
		""" Start the interactive command prompt """
		self.interactive = True

		do_quit = False
		while do_quit is not True:
			try:
				self.interface.cmdloop()
				do_quit = True
			except KeyboardInterrupt:
				sys.stdout.write('\n')
	
	def start(self):
		self.stopRun = False
		self.stopMode = False
		self.connect()
		self.lightCycleThread = threading.Thread(target=self.run)
		self.lightCycleThread.start()
		
	def stop(self):
		self.stopMode = True
		self.stopRun = True
		if self.lightCycleThread is not None:
			self.lightCycleThread.join()
			self.lightCycleThread = None
		self.off()
		self.disconnect()
	
	def disconnect(self):
		if self.sock is not None:
			self.sock.close()
	
	def connect(self):
		# Create a TCP/IP socket
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
		# Connect the socket to the port where the server is listening
		try:
			print("connecting to", self.ip, self.port)
			server_address = (self.ip, self.port)
			self.sock.connect(server_address)
		except:
			print("failed to connect")
			self.sock = None
	
	def opcSend(self, pixels):
		""" Turn list of pixels into OPC format and send to server """
		pixels = changeBrightness(pixels, self.brightness/100)
		comm = 0
		for c in range(self.numChannels):
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
				self.sock.sendall(message)
			except:
				print("Error in sending")
				break
	
	def switchMode(self, mode):
		if mode in self.modes:
			print('new mode selected')
			self.mode = mode
			self.stopMode = True
		else:
			print('bad mode:', mode)
	
	def switchDirection(self, direction):
		if direction == 'right' or direction == 'left':
			self.direction = direction
		else:
			print('bad direction given. need "right" or "left"')
	
	def run(self):
		modeThread = None
		
		while self.stopRun is False:
			if self.mode != 'none':
				self.stopMode = False
				if self.mode == 'test':
					modeThread = threading.Thread(target=self.testMode)
				elif self.mode == 'flicker':
					modeThread = threading.Thread(target=self.flickerMode)
				elif self.mode == 'flickerOn':
					modeThread = threading.Thread(target=self.flickerOnMode)
				elif self.mode == 'rainbow':
					modeThread = threading.Thread(target=self.rainbowMode)
				elif self.mode == 'shift':
					modeThread = threading.Thread(target=self.shiftMode)
				elif self.mode == 'rainbowShift':
					modeThread = threading.Thread(target=self.rainbowshiftMode)
				elif self.mode == 'fill':
					modeThread = threading.Thread(target=self.fillMode)
				elif self.mode == 'fade':
					modeThread = threading.Thread(target=self.fadeMode)
				else:
					print('not a supported mode', self.mode)
			else:
				pass
	
			if modeThread is not None:
				self.mode = 'none'
				self.stopMode = False
				modeThread.start()
				modeThread.join()
				modeThread = None
				self.stopMode = True
			time.sleep(1)
			
	def off(self):
		pixels = defaultFrameCreate(self.numPixels, (0,0,0))
		self.opcSend(pixels)
	
	def on(self):
		pixels = defaultFrameCreate(self.numPixels, self.color)
		self.opcSend(pixels)
		
	def update(self):
		pass
	
	###################
	# mode functions
	###################
		
	def testMode(self):
		while self.stopMode is False:
			pixels = []
			for x in range(self.numPixels):
				pixels.append((random.randint(0,255),random.randint(0,255),random.randint(0,255)))
			self.opcSend(pixels)
			time.sleep((1/self.refreshRate) * self.speed)
		
	def flickerMode(self):
		on_pixels = defaultFrameCreate(self.numPixels, self.color)
		off_pixels = defaultFrameCreate(self.numPixels, (0,0,0))			
		self.opcSend(off_pixels)

		total = 1
		flicker_time = 0.1
		while self.stopMode is False:
			self.opcSend(on_pixels)
			time.sleep(flicker_time)
			self.opcSend(off_pixels)
			time.sleep(2 * random.uniform(0,0.5))
		self.opcSend(on_pixels)
		
	def flickerOnMode(self):
		on_pixels = defaultFrameCreate(self.numPixels, self.color)
		off_pixels = defaultFrameCreate(self.numPixels, (0,0,0))			
		self.opcSend(off_pixels)

		flicker_count = 3
		total = 1
		flicker_time = 0.1
		while flicker_count > 0:
			self.opcSend(on_pixels)
			time.sleep(flicker_time)
			self.opcSend(off_pixels)
			time.sleep(flicker_count * random.uniform(0,0.5))
			flicker_count = flicker_count -1
		self.opcSend(on_pixels)

	def rainbowMode(self):
		angle = 0		
		while self.stopMode is False:
			# get color from rainbow at current "angle"
			pixel = colorUtils.getRainbow2(angle)
			
			# create array of pixels of same color
			pixels = defaultFrameCreate(self.numPixels, pixel)
			
			# send pixels and sleep
			self.opcSend(pixels)
			time.sleep((1/self.refreshRate) * self.speed)
			
			# go to next angle in raindbow sequence
			angle = angle + 1
			if angle > 359:
				angle = 0
				
	def shiftMode(self):
		# make shift frame
		shiftnum = 0
		pixels = shiftFrameCreate(self.numPixels, self.color)

		# if left shift then reverse shift frame
		if self.direction == 'left':
			pixels = pixels[::-1]
			
		while self.stopMode is False:

			if self.direction == 'right':
				pixels = shift(pixels, 1)
			else:
				pixels = shift(pixels, -1)
				
			shiftnum = shiftnum +1
			if shiftnum > self.numPixels:
				shiftnum = 0
			
			# send pixels and sleep
			self.opcSend(pixels)
			time.sleep((1/self.refreshRate) * self.speed)
			
	def rainbowshiftMode(self):
		shiftnum = 0
		angle = 0
		while self.stopMode is False:
			# pick color from rainbow sequence
			pixel = colorUtils.getRainbow(angle)
			angle = angle + 1
			if angle > 359:
				angle = 0

			# create shift frame
			pixels = shiftFrameCreate(self.numPixels, pixel)
			if self.direction == 'left':
				tempNum = shiftnum - (shiftnum*2)
			else:
				tempNum = shiftnum
			pixels = shift(pixels, tempNum)
			
			shiftnum = shiftnum + 1
			if shiftnum > self.numPixels:
				shiftnum = 0
				
			# send pixels and sleep
			self.opcSend(pixels)
			time.sleep((1/self.refreshRate) * self.speed)

	def fillMode(self):
		pixels = defaultFrameCreate(self.numPixels, (0,0,0))
		pixels = []
		for x in range(self.numPixels):
			pixels.append((0,0,0))
		
		for idx in range(self.numPixels):
			pixels[idx] = self.color
			
			# send pixels and sleep
			self.opcSend(pixels)
			time.sleep((1/self.refreshRate) * self.speed)
			
	def fadeMode(self):
		startPixels = defaultFrameCreate(self.numPixels, self.color)
		start_time = time.time()
		
		while self.stopMode is False:
			pixels = fade(startPixels, start_time)
			
			# send pixels and sleep
			self.opcSend(pixels)
			time.sleep((1/self.refreshRate) * self.speed)


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-g", "--gui", action='store_true', help="enable the GUI")
	parser.add_argument("-i", "--ip", default="127.0.0.1", help="ip address of OPC server")
	parser.add_argument("-p", "--port", type=int, default=7890, help="port number for OPC server")
	
	args = parser.parse_args()
	
	lightcycle = LightCycle()
	lightcycle.ip = args.ip.strip()
	lightcycle.port = int(args.port)
	lightcycle.numPixels = 64 # pixels per channel..change this if your setup is different
	lightcycle.numChannels = 8 # fadecandy supports up to 8 channels
	
	if args.gui is True:
		program = gui(lightcycle)
		mainloop()
		program.cleanup()
	else:
		lightcycle.interactive_prompt()

if __name__ == "__main__":
	main()