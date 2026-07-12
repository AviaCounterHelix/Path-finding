We have a spline with 5 control points:
<img width="1529" height="666" alt="image" src="https://github.com/user-attachments/assets/68d2d153-422b-4d56-b2e1-6f0ada0e3d66" />

Point number 6 is the end of the vector for createing of pipe crossection. The location of this point is randomly and close to start point
to cross to this vector we create a pipe crossection.

The coordinates of control points in Cartesion Coordinate System:

______________________________________________________
x1=-248.13; y1=-56.06; z1=0;

x2=-142.02; y2=34.39; z2=55.36;

x3=-84.62; y3=-14.61; z3=0;

x4=-2.86; y4=-10.89; z4=-11;

x5=78.9; y5=26.84; z5=0;

x6=-245.42; y6=-51.16; z6=3.7;

______________________________________________________

Next step we obtain a cross vector to create a pipe crossection. For thi puprose we use points number 1 and 6 as start and finish of the vector for which we trying to find a cross vector.

Code of this step in the cross_point.py

But we are working in CAE System and this code translated in VBA code to implement in Femap/Nastran like as Cross_point_Sweep_pipe.BAS.

