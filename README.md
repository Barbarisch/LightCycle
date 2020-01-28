# LightCycle
Code project controlling LED desk lights

## Background

I embedded LEDs in the surface of my desk. The LEDs are hooked up to a fadecandy which in turn is connected to a raspberry pi. I needed custom software to control the LEDs so I made this project. My hope is that others could make use of this code in their own projects. It is slightly specific to this project, but shouldnt be too hard to modify.

The project name comes from Tron light cycles (https://i.imgur.com/Jww2gQt.jpg). The entire project was inspired by the look of Tron Legacy in general.

The code is written in python and can be run with latest versions of Python 3.

## Usage

I designed and tested it with the fcserver from fadecandy (https://github.com/scanlime/fadecandy). I also was able to test with gl_server in openpixelcontrol (https://github.com/zestyping/openpixelcontrol). The protocol is dead simple to understand and you should be able to look at the opcSend function in the main.py file to see how it is getting created. 

Basic usage:
  user@localhost# python3 main.py -i <IP to OPC server> -p <Port to OPC server>
  > start
  > color red
  > mode test
  > mode flickerOn
  > exit
  
The python script presents an interactive prompt (based off of Cmd.cmd python module). This allows control functionality during execution. This means that from the prompt changes can be made to animimation modes, colors, brightness, etc on the fly.

Help menu:
  help - print this help message
  start - connect and start default animation logic
  stop - disconnect and stop animation logic
  mode - change current animation mode. ex: mode rainbowShift
  exit - stop everything and close program
  on - turn all LEDs on
  off - turn all LEDs off
  brightness - change brightness level (0 - 100, default is 50)
  speed - change speed of animations (1 is fastest, default is 5)
  direction - change direction of linear animations (left or right)
