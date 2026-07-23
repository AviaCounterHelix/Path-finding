We have a spline with 5 control points:
<img width="1529" height="666" alt="image" src="https://github.com/user-attachments/assets/68d2d153-422b-4d56-b2e1-6f0ada0e3d66" />

Point number 6 is the end of the vector for creating of pipe cross-section. The location of point 6 is random and close to the start point. The pipe cross‑section is created in a plane perpendicular to the vector between points 1 and 6.

The coordinates of control points in Cartesian Coordinate System:

______________________________________________________
x1=-248.13; y1=-56.06; z1=0;

x2=-142.02; y2=34.39; z2=55.36;

x3=-84.62; y3=-14.61; z3=0;

x4=-2.86; y4=-10.89; z4=-11;

x5=78.9; y5=26.84; z5=0;

x6=-245.42; y6=-51.16; z6=3.7;

______________________________________________________

Next steps:
1. We obtain a cross vector to create a pipe crossection. For this purpose we use points number 1 and 6 as start and finish of the vector for which we are trying to find a cross vector.
   
2. We create a cross section by revolving cross vector along base vector.
  
3. We sweep circle cross section through the original spline.

______________________________________________________
We are working in CAE System and this code is translated in VBA code to implement in Femap/Nastran like Cross_point_Sweep_pipe.BAS.

The result is the shell geometry of the pipe

<img width="1410" height="611" alt="image" src="https://github.com/user-attachments/assets/caa9f180-c229-4124-8f5c-57f628f045be" />

______________________________________________________

In the next steps we'll create a mesh, a load condition, constraints, a property and material characteristics

As a result of next steps an isotropic material and plate-shell property were added

The Young's modulus is equal 21000 kgf/mm^2 and Poisson ratio is 0.3. These parameters are about steel alloys

The thickness of plate property is 1 mm

Finally mesh with a size equal to the default size divided by 8

<img width="996" height="614" alt="image" src="https://github.com/user-attachments/assets/1cf8a3ea-bf00-439a-8787-77adfbd2ead0" />

______________________________________________________

In the next step we create a boundary condition - fixing of the ends of the tube as full constraints of six DOFs.

After that we load our pipe by internal pressure. The value of pressure is established by the user.

The result is shown below

<img width="697" height="561" alt="image" src="https://github.com/user-attachments/assets/15c33007-cb1e-463f-bcd5-42971b5539b6" />

Next step will be a nonlinear static analysis
______________________________________________________

The final step is the creating of nonlinear static analysy parameters and pointing the output vectors.

We use Advanced Overrieds solution stategy with Modified Newton's Method.

We update the stiffness matrix after 5 iteraionts.

The total amout of analysis steps are 25.

Max iterattions per step are 50.

Convergence strategy is work + load convergence. The thesholds are 1e-7 and 1e-3 respectivetly.

As output vectors we get stress and displacments outputs.

The contribution of VonMises stress for top and bot layer of shell are shown below.

<img width="1916" height="816" alt="image" src="https://github.com/user-attachments/assets/c63cba85-3230-4547-9f32-d621f48b039a" />

<img width="1916" height="816" alt="image" src="https://github.com/user-attachments/assets/5a481dd6-7a54-4c2c-be1c-886b73f13373" />










