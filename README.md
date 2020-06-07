# Orbit simulator
Python programm using the 2nd law of Newton to simulate in real time gravitational interactions between two or more celestial bodies with a decicated UI. This program is our work for our informatic class final project.
## Operating process
For each frame, the system compute the position of each object in the next frame considering a movement vector to which the variation of the speed vector has been added considering the following formulas : <br>
![Newton 2nd Law](https://wikimedia.org/api/rest_v1/media/math/render/svg/ce5a34efdcbe454a69e8b879e0005c809b0439ee) <br>
![acceleration formula](https://wikimedia.org/api/rest_v1/media/math/render/svg/941bc4c58dbc6f6716ce1d0024ff29e2ee82a0c9)

## Installation
### Windows
This guide was tested on Windows 10
1. Install the latest release [here](https://github.com/jupiter2653/orbit-simulator/releases/latest) or clone this repository with git. *If you want to, you can also clone this repository but the content might not be production ready*
2. Extract all the files from the compressed folder.
3. Install the dependencies by typing ``py -m pip install -r requirements.txt`` in the directory in which you exctracted the files
4. Launch ``main.py``.
5. Enjoy !

## Usage
Once launched, you can add a spacial object by clicking on "Add Spacial Object". You can the choose to use a preset or a personalized object but you will have to specify the movement vector (the movement in x and y in m/s), and the x and y coordinates.<br>
When the spacial object is added, it will start moving following the vector you specified and the forced which are applied to it. You can pause it by pressing the Play/Pause logo.<br>
You can also change the parameters of the object on the fly thanks to the left panel. If you want to change the speed you need to pause the live updating by clicking the "Pause" button. Then, like all the other parameters, you will have to press "Ok" to apply changes. You can also change the position of the object by dragging and dropping the object.


## Credits
- @Everheartt 
- @jupiter2653
