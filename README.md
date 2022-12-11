# jeddah

Upciti is a company that places sensors on light poles. As it his very tidious to find the lightpoles manually, I have developped a solution that does it automatically. 

Here how it works : 
* You enter the coordinates of a point and a radius 
* The program queries all the roads in the given area using the OpenStreetMap API
* The program then strategically places points along these roads and queries the Street View images from the Google Street View API
* These images are then saved into a database 
* A CNN then performs an instance segmentation on these images to detect light poles and predict theur coordinates
* The coordinates of light poles are displayed on a map

Unfortunately, the CNN needed further tuning and is not available in this github repository. It will only save these images in a PostgreSQL database.


Code is in src/jeddah

further instructions will be given later !
