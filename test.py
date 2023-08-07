N = int(input())

for i in range(N):
    spaces = ''
    T = N-i
    while T>0:
      spaces +=' '
      T-=1
    for j in range(i+1):
        if j==0:
         print(spaces+"*",end=" ")
        else:
         print("*",end=" ")
    print()
  #Alphabets pattern
  #print A 


# height = 3
# width = (2 * height) - 1
# n = width // 2
# for i in range(0, height):
#     for j in range(0, width+1):  
#         #print(i,j,n,width-n,height//2)
#         if (j == n
#             or j == (width - n) 
#             or 
#             (i == (height // 2) 
#              and j > n 
#              and j < (width - n))):
#             print("*", end="")
            
#         else:
           
#             print(end=" ")
#     print()
#     n = n-1
    





