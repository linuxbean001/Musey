N = int(input())
for i in range(1,N+1):
    for j in range(i):
        print("*",end=' ')
    print()

for k in range(N,0,-1):
    for l in range(k,0,-1):
        print("*",end=' ')    
    print()
"""
profile pattern function 

            . . .
          .       .         
         .  - | -  .    
         .  .   .  .
          .  . .  .
           .     .
     . . .         . . .
    .                   . 
    .                   .  
    .                   .
    . . . . . . . . . . .

"""


# Diamond program 
"""
  *
 * *
*   *
 * *
  *   
"""
for m in range(N):
    spaces = ' '*((N-1)-m) 
    # revspaces = ' '*(N-1))
    for n in range(m+1):
        if n == 0:
          print(spaces+"*",end=' ')
        else:
          print("*",end=' ') 
    print()
spacesrev = ' ' 
for o in range(N-1,0,-1):          
    for rev in range(o,0,-1):
        if rev == o:
         print(spacesrev+"*",end=' ') 
        else:
           print("*", end=' ')
    spacesrev = spacesrev+' '   
    print()

     


    