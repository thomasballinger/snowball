The Game
========
Snowball is a "dog eat dog" game. Players maneuver a snowball across the sky,
dodging larger snowballs, in an effort to be the last snowball standing.

![alt
text](https://github.com/stoneG/snowball/tree/master/images/TWO-1.png "Two players on
Ubuntu 12.04")  
![alt
text](https://github.com/stoneG/snowball/tree/master/images/TWO-2.png "Growing larger...")  
![alt
text](https://github.com/stoneG/snowball/tree/master/images/TWO-3.png "Looks like green
didn't make it")  
![alt
text](https://github.com/stoneG/snowball/tree/master/images/THREE-1.png "Three players on
OSX 10.8")  
![alt
text](https://github.com/stoneG/snowball/tree/master/images/THREE-2.png "Stoplight
formation")  
![alt
text](https://github.com/stoneG/snowball/tree/master/images/THREE-3.png "What's gonna
happen?")

Release
-------
(0.3) Optimized some server calculations, and the game now supports up to
5 players, though YMMV depending on your network connection.  
(0.2) Multiplayer is GO.  
(0.1) Currently you can play the game as a mutant green snowball that
terrorizes all the other snowflake denizens. That's about it though.

Installation
------------
What you need to run the server: python, git.  
What you additionally need to run the client: pygame.  

Ubuntu:
<pre>
sudo apt-get install python-pygame
</pre>

Clone 'snowball' repository into folder of choice:
<pre>
git clone https://github.com/stoneG/snowball.git
</pre>

Running the game
----------------
First run the server. You may give a specific IP address for the server to bind
to (ie if you want to run locally) or let it automatically attach to your outward IP address.  
<pre>
python server.py '127.0.0.1'
</pre>
or
<pre>
python server.py
</pre>
  
Please note the IP address that the server is binded and listening to:
<pre>
Listening at ('192.168.21.45', 1060)
</pre>
  
Then you want to run your client to point to the server's IP address.  
For example, if the server's IP is 192.168.21.45:
<pre>
python client.py '192.168.21.45'
</pre>
  
Then, clients connect to the server with SPACE. After all desired connections
are made, the master client (designated by the server) will have the option of
starting the game by hitting 's'.  

Controls
--------
ARROWS: Movement  
SPACE : Compress snowball for more speed, at the expense of size  
ESC   : Quit game

TODO
----
* Polish
* Better interface
* Scoring system/High scores
* Tons more
