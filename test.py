from Tkinter import *
from tkColorChooser import askcolor
import socket
import threading

def test():
	print "testing function call"
             
def getColor():
	color = askcolor() 
	print 

def show_values(w1):
	print (w1.get())
	
def keypressEvent(event):
	
	x = event.char
	if len(x) > 0:
		print ord(x)

def main():
	master = Tk()

	master.minsize(width=400, height=200)
	menubar = Menu(master)
	
	filemenu = Menu(menubar, tearoff=0)
	filemenu.add_command(label="Open", command=test)
	menubar.add_cascade(label="File", menu=filemenu)
	
	brightnessSlider = Scale(master, from_=0, to=100, length=200, tickinterval=10, orient=HORIZONTAL)
	brightnessSlider.set(50)
	brightnessSlider.pack()

	Button(master, text='Show', command=lambda:show_values(brightnessSlider)).pack()
	Button(text='Select Color', command=getColor).pack()
	
	master.config(menu=menubar)
	
	master.bind('<Key>', keypressEvent)

	mainloop()

if __name__ == "__main__":
	main()