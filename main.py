n=int(input('Enter the number of rows: '))
for i in range(n+1):
    for j in range(1,i):
        print(j,end=" ")
    print()   