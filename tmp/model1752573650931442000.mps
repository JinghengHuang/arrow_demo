* Source:     Pyomo MPS Writer
* Format:     Free MPS
*
NAME unknown
OBJSENSE
 MIN
ROWS
 N  x3
 E  c_e_x4_
 L  c_u_x5_
 L  c_u_x6_
COLUMNS
     x1 x3 1
     x1 c_e_x4_ 1
     x1 c_u_x5_ -1
     x2 x3 1
     x2 c_e_x4_ 1
     x2 c_u_x6_ -1
RHS
     RHS c_e_x4_ 1
     RHS c_u_x5_ 0
     RHS c_u_x6_ 0
BOUNDS
 LO BOUND x1 0
 UP BOUND x1 10
 LO BOUND x2 0
 UP BOUND x2 10
QUADOBJ
     x1 x1 2
     x2 x2 2
ENDATA
