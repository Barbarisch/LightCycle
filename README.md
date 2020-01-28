# LightCycle
Code project controlling LED desk lights

## Background

I wanted to create a desk that had a similar look to it as Tron Legacy (https://i.imgur.com/Jww2gQt.jpg). So I embedded LEDs in the surface of my desk in a pattern that I thought looked Tron-like. The LEDs are hooked up to a fadecandy which in turn is connected to a raspberry pi. I needed custom software to control the LEDs so I made this project. My hope is that others could make use of this code in their own projects. It is slightly specific to this project, but shouldnt be too hard to modify.

I documented some of the desk build project here: https://imgur.com/a/l1eliAV

## Overview

The LED control software (LightCycle) is built around open pixel control protocol (OPC). It is written in python and can be run with latest versions of Python 3. It uses RGB pixel lists and simple TCP sockets to send pixel data to an OPC server running on my Raspberry PI. The OPC server is fcserver from the fadecandy github project (https://github.com/scanlime/fadecandy). It is simple to get running, and their readme and online tutorials are easy enough to follow to get your own LED projects up and running.

I initially tested the software using gl_server from the openpixelcontrol github project (https://github.com/zestyping/openpixelcontrol). This allowed me to test functionality without using physical LED hardware. It contains a LED simulator that you can customize to any shape you want.

Anyone who wants to see how I am creating OPC protocol messages should look at the opcSend function in the main.py file. It is fairly basic with a few bytes for channel and length followed by rgb values for each pixel.

## Usage

Basic usage:
  
    user@localhost:~/LightCycle$ python3 main.py -i <IP to OPC server> -p <Port to OPC server>
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
      list - list available animation modes
      on - turn all LEDs on
      off - turn all LEDs off
      brightness - change brightness level (0 - 100, default is 50)
      speed - change speed of animations (1 is fastest, default is 5)
      direction - change direction of linear animations (left or right)
