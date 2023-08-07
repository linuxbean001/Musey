class Solution:
    # @param A : list of integers
    # @return an integer
    def solve(self, A):
        tempSpecialCount = 0
        inc = 0
        for i in A: 
            tempArr = A[:]
            print(A)
            isSpecialNumber = False
            isSpecialNumber = self.checkSpecial(inc,tempArr)
            inc = inc+1
            if isSpecialNumber == True or len(A)<3:
                tempSpecialCount = tempSpecialCount+1 
        return tempSpecialCount  

    def checkSpecial(self,i,tempArr):
         tempArr.pop(i)
         
         sumeven = 0
         sumodd = 0 
         inctemp = 1
         for j in tempArr:
             if inctemp%2==0:
                 sumeven = sumeven+j
             else:
                 sumodd = sumodd+j 
             inctemp = inctemp+1  
         if sumeven == sumodd and sumeven != 0:
             return True 
         else:
             return False             
             
ds = Solution()
print(ds.solve([10]))