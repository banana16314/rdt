from file_handler import File_handler

byte_array = my_file.get_next_chunk()
print(byte_array)
my_file = File_handler('/tmp/test', 500)
print ("done ",len(byte_array))
