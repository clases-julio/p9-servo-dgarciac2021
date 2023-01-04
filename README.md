# P9-Servo

On this exercise we will control a servo with the GPIO. Although there are a few types of servo out there, we are working with a 360º continous motion servo. More precisely, with the [Parallax feedback 360 high speed servo](https://www.parallax.com/product/parallax-feedback-360-high-speed-servo/).

All servos out there have always three wires, which are

|Nº|Wire|
|---|---|
|1|VCC|
|2|Control signal|
|3|GND|

But this model comes with a fourth wire, **which is a feedback signal**. That means that we can precisely know the position of the axle in any given moment. Cool!

You might want to take a look on the [wiki](https://github.com/clases-julio/p9-servo-dgarciac2021/wiki), since there is info about everything involved on this exercise, from [the servo itself](https://github.com/clases-julio/p9-servo-dgarciac2021/wiki/Parallax) to [PIGPIO](https://github.com/clases-julio/p9-servo-dgarciac2021/wiki/PIGPIO), a library used to manage PWM signal easily on the Raspberry Pi!

## Circuit Assembly

We got a little bit creative (and destructive) here. The assembly will be so simple if only the wire order of the connector meets the GPIO order! You see, there's three pins in a row in the RPI which are 5V, GND and GPIO14 respectively. [We have already talked about GPIO's here](https://github.com/clases-julio/p1-introrpi-pwm-dgarciac2021/wiki/GPIO). There we see that those pins are **(BOARD mode!) numbers 4, 6 and 8.**

However, the original connector of the servo comes in the following arrangement: VCC, Control Signal and GND. *Damnit*!

We will have to connect it to the protoboard and do the wiring there, just for one pin! Unless... We change the conector to our needs. Here's a picture of a similar connector:

![Dupont female header](https://www.pcboard.ca/image/cache/catalog/products/connectors/3-pin-dupont-connector-2-800x800.jpg)

Inside the plastic housing there is three small metal pieces which serve as contact points, fixing themselves in place by pressure. You can see this pieces here:ç

![Dupont female header disassembly](https://solectroshop.com/1364-medium_default/conector-dupont-254mm-hembra.jpg)

This metal pieces are held to the plastic housing by a tiny flange that can be manipulated with caution without breaking, and thus free the metal piece of each wire. Then is just as easy to put it back together in the right order. Here you can see a more detailed picture of where the plastic housing holds the metal piece:

![Dupont female header disassembly 2](https://techmattmillman.s3.dualstack.us-east-1.amazonaws.com/wp-content/uploads/2015/06/minipvreal-800x528.jpg)

Fortunately for us, the feedback wire comes in a separate housing and we can conncet it at any GPIO, but for a clean view we are connecting it to the next GPIO, the **GPIO15**.

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
