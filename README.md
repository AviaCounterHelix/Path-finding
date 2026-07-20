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

Next steps:
1. We obtain a cross vector to create a pipe crossection. For this puprose we use points number 1 and 6 as start and finish of the vector for which we trying to find a cross vector.
   
2. We create a cross section be revolving cross vector along base vector.
  
3. We sweep circle cross section through the original spline.

______________________________________________________
We are working in CAE System and this code translated in VBA code to implement in Femap/Nastran like as Cross_point_Sweep_pipe.BAS.

The result is the shell geometry of the pipe

<img width="1410" height="611" alt="image" src="https://github.com/user-attachments/assets/caa9f180-c229-4124-8f5c-57f628f045be" />

______________________________________________________

In next steps we'll create a mesh, a load condition, a constraints, a property and materail characteristics

As a result of next steps an isotropic material and plate-shell property were added

The Young's Modul is equal 21000 kgf/mm^2 and Poisson ration is 0.3. These parameters is about steel alloys

The thickness of plate property is 1 mm

Finally mesh was created with size is default size / 8

<img width="996" height="614" alt="image" src="https://github.com/user-attachments/assets/1cf8a3ea-bf00-439a-8787-77adfbd2ead0" />

______________________________________________________

Next step we create a boundary condition - fixing of the ends of the tube like full constrains of six DOFs.

After that we loaded our pipe by internal pressure. The value of pressure is established by the user.

The result is shown below

<img width="697" height="561" alt="image" src="https://github.com/user-attachments/assets/15c33007-cb1e-463f-bcd5-42971b5539b6" />

Next step will be a nonlinear static analysy
______________________________________________________









