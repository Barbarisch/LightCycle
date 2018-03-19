from Tkinter import *
from tkColorChooser import askcolor
import socket
             
def getColor():
	color = askcolor() 
	print 

def show_values(w1):
	print (w1.get())#, w2.get())	

def main():
	master = Tk()

	master.minsize(width=400, height=200)
	
	brightnessSlider = Scale(master, from_=0, to=100, length=200, tickinterval=10, orient=HORIZONTAL)
	brightnessSlider.set(50)
	brightnessSlider.pack()

	Button(master, text='Show', command=lambda:show_values(w1)).pack()
	Button(text='Select Color', command=getColor).pack()

	mainloop()

if __name__ == "__main__":
	main()