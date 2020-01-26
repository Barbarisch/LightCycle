import colorsys

rainbowSequence = [
  0,   0,   0,   0,   0,   1,   1,   2, 
  2,   3,   4,   5,   6,   7,   8,   9, 
 11,  12,  13,  15,  17,  18,  20,  22, 
 24,  26,  28,  30,  32,  35,  37,  39, 
 42,  44,  47,  49,  52,  55,  58,  60, 
 63,  66,  69,  72,  75,  78,  81,  85, 
 88,  91,  94,  97, 101, 104, 107, 111, 
114, 117, 121, 124, 127, 131, 134, 137, 
141, 144, 147, 150, 154, 157, 160, 163, 
167, 170, 173, 176, 179, 182, 185, 188, 
191, 194, 197, 200, 202, 205, 208, 210, 
213, 215, 217, 220, 222, 224, 226, 229, 
231, 232, 234, 236, 238, 239, 241, 242, 
244, 245, 246, 248, 249, 250, 251, 251, 
252, 253, 253, 254, 254, 255, 255, 255, 
255, 255, 255, 255, 254, 254, 253, 253, 
252, 251, 251, 250, 249, 248, 246, 245, 
244, 242, 241, 239, 238, 236, 234, 232, 
231, 229, 226, 224, 222, 220, 217, 215, 
213, 210, 208, 205, 202, 200, 197, 194, 
191, 188, 185, 182, 179, 176, 173, 170, 
167, 163, 160, 157, 154, 150, 147, 144, 
141, 137, 134, 131, 127, 124, 121, 117, 
114, 111, 107, 104, 101,  97,  94,  91, 
 88,  85,  81,  78,  75,  72,  69,  66, 
 63,  60,  58,  55,  52,  49,  47,  44, 
 42,  39,  37,  35,  32,  30,  28,  26, 
 24,  22,  20,  18,  17,  15,  13,  12, 
 11,   9,   8,   7,   6,   5,   4,   3, 
  2,   2,   1,   1,   0,   0,   0,   0, 
  0,   0,   0,   0,   0,   0,   0,   0, 
  0,   0,   0,   0,   0,   0,   0,   0, 
  0,   0,   0,   0,   0,   0,   0,   0, 
  0,   0,   0,   0,   0,   0,   0,   0, 
  0,   0,   0,   0,   0,   0,   0,   0, 
  0,   0,   0,   0,   0,   0,   0,   0, 
  0,   0,   0,   0,   0,   0,   0,   0, 
  0,   0,   0,   0,   0,   0,   0,   0, 
  0,   0,   0,   0,   0,   0,   0,   0, 
  0,   0,   0,   0,   0,   0,   0,   0, 
  0,   0,   0,   0,   0,   0,   0,   0, 
  0,   0,   0,   0,   0,   0,   0,   0, 
  0,   0,   0,   0,   0,   0,   0,   0, 
  0,   0,   0,   0,   0,   0,   0,   0, 
  0,   0,   0,   0,   0,   0,   0,   0 ]
  
def getRainbow(angle):
	#r = rainbowSequence[(angle+120)%360]
	r = rainbowSequence[(angle+120)%360]
	#g = rainbowSequence[angle]
	g = rainbowSequence[angle]
	#b = rainbowSequence[(angle+240)%360]
	b = rainbowSequence[(angle+240)%360]
	pixel = (r, g, b)
	return pixel
	
def getRainbow2(angle):
	red = 0
	green = 0
	blue = 0

	if angle<60:
		red = 255
		green = round(angle*4.25-0.01)
		blue = 0
	elif angle<120:
		red = round((120-angle)*4.25-0.01)
		green = 255
		blue = 0
	elif angle<180:
		red = 0
		green = 255
		blue = round((angle-120)*4.25-0.01)
	elif angle<240:
		red = 0
		green = round((240-angle)*4.25-0.01)
		blue = 255
	elif angle<300:
		red = round((angle-240)*4.25-0.01)
		green = 0
		blue = 255
	else:
		red = 255
		green = 0
		blue = round((360-angle)*4.25-0.01)
		
	pixel = (red, green, blue)
	return pixel

def getRainbow3(depth):
	maxd = 360
	(r, g, b) = colorsys.hsv_to_rgb(float(depth) / maxd, 1.0, 1.0)
	R, G, B = int(255 * r), int(255 * g), int(255 * b)
	
	return (R, G, B)
	
def getRainbow4(numPixels):
	h = 0
	v = 255
	s = 240
	
	pixels = []
	
	for x in range(255):
		h = h + 1
		(r, g, b) = colorsys.hsv_to_rgb(h/255.0, v/255.0, s/255.0)
		R, G, B = int(255 * r), int(255 * g), int(255 * b)
		pixels.append((R, G, B))
		
	print(pixels)
		
	return pixels

def getCurrentAngle(pixel):
	ret = 0
	
	for angle in range(360):
		r = rainbowSequence[(angle+120)%360]
		g = rainbowSequence[angle]
		b = rainbowSequence[(angle+240)%360]
		
		if r == pixel[0] and g == pixel[1] and b == pixel[2] and angle > 0:
			ret = angle
			break

	return ret
	
def gamma(color, gamma):
    """Apply a gamma curve to the color.  The color values should be in the range 0-1."""
    r, g, b = color
    return (max(r, 0) ** gamma, max(g, 0) ** gamma, max(b, 0) ** gamma)
	
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
	else:
		print('pixel color not available', color)

	return pixel