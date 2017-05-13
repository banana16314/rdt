# import numpy as np

def get_bits(s) :
	return "".join(map(lambda x: format(ord(x), 'b'), s))

s = 'HELLO'
binary_s = ' '.join(format(ord(x), 'b').zfill(8) for x in s)
byte_array = binary_s.split()

print(binary_s)
print(len(byte_array))

total_sum = 0
for i in range(0, len(byte_array)-1,2) :
	first_int = int(byte_array[i],2)
	print ("\tfirst:\t",first_int)
	second_int = int(byte_array[i+1],2)
	print ("\tsecond:\t",second_int)
	sum = first_int + second_int
	if sum > 255 :
		sum = sum - 256
		sum = sum + 1
	print("\tsum:\t",sum,"\n")
	total_sum = total_sum + sum
	if total_sum > 255 :
		total_sum = total_sum - 256
		total_sum = total_sum + 1
if (len(byte_array)%2 == 1) : # special case for odd 
	last_int = int(byte_array[len(byte_array)-1],2)
	total_sum = last_int + total_sum
	if total_sum > 255 :
		total_sum = total_sum - 256
		total_sum = total_sum + 1

total_sum = total_sum^255
print(total_sum)
cksum = '{0:08b}'.format(total_sum)
print (cksum)

