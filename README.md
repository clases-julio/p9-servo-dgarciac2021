# P9-Servo

On this exercise we will control a servo with the GPIO. Although there are a few types of servo out there, we are working with a 360º continous motion servo. More precisely, with the .

You might want to take a look on the [wiki](https://github.com/clases-julio/p8-fuerza-presencia-dgarciac2021/wiki), since there is info about everything involved on this exercise, from [FSR](https://github.com/clases-julio/p8-fuerza-presencia-dgarciac2021/wiki/FSR) to [PIR sensor](https://github.com/clases-julio/p8-fuerza-presencia-dgarciac2021/wiki/PIR)!

## Circuit Assembly

This excersise has three main parts, and they are:

|Nº|Part|
|---|---|
|1|Pressure sensor|
|2|PIR sensor|
|3|Illumination system|

For the pressure sensor, we are using a 1MΩ resistor attached just like the schematic shows below.

In the other hand, the PIR sensor is fully assembled and it is only need to power it and gather its signal wire to any pin of the Raspberry Pi. As for the Illumination system, we are pretending that a simple LED's represents it. 

This is an schematic made with [Fritzing](https://fritzing.org/):

![Schematic](./doc/img/schematic.png)

And this is the real circuit!

![aerial view](./doc/img/aerial-view.jpeg)

## Code

We used a similar code as in [p7](https://github.com/clases-julio/p7-humedad-dgarciac2021) with a bit of tweaking, so you can check out the details there.

This tweaks are also covered in previous exercises like [p5](https://github.com/clases-julio/p5-distanciaus-dgarciac2021) or [p6](https://github.com/clases-julio/p6-reedswitch-dgarciac2021), so there is no room to be concise here!

## Circuit testing

This is the result! Pretty nice, isn't it?

![Circuit Demo](./doc/img/demo.gif)
