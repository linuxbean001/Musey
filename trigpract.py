N = int(input())
for a in range(N):
    if a == N-1 or a==N-2: 
      print("* ",end='* '*((N)-1))
    else:
      print(end=' '*N*2)    
    
    for b in range(a+1):
        print("*", end=' ')
    print()    
for c in range(N-1,0,-1):
    if c == N-1: 
      print("* ",end='* '*((N)-1))
    else:
      print(end=' '*N*2)
    for d in range(c,0,-1):
        print("*", end=' ')
    print()
