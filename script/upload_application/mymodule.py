import os
import sys

temp_base = '/tmp/resumable_images/'
CurrentFile = []


# handler: for trait the GET from resumable.js
def handler_rs_GET(_GET): 
    temp_dir = "{}{}".format(temp_base, (_GET['resumableIdentifier'])[0])
    chunk_file = "{}/{}.part{}".format(temp_dir, (_GET['resumableFilename'])[0],  (_GET['resumableChunkNumber'])[0])
    if not os.path.isfile(chunk_file):
        return False
    else:
        return True


# handler: for trait the POST from resumable.js
def handler_rs_POST(_POST):
    temp_dir = "{}{}".format(temp_base, _POST['resumableChunkNumber'].value)
    chunk_file = "{}/{}.part{}".format(temp_dir, _POST['resumableFilename'].value, _POST['resumableChunkNumber'].value)
    fileitem = _POST['file']
    file_path = chunk_file

    # If the path not exist, create a new one
    if not os.path.exists(file_path):
        os.makedirs(temp_dir)

    # Save the file in the tempory directory
    counter = 0
    with open(file_path, 'wb') as output_file:
        while 1:
            data = fileitem.file.read(1024)
            if not data:
                break
            output_file.write(data)
            counter += 1
            if counter == 100:
                counter = 0
    collect(_POST)



def collect(_POST):
    currentSize =  int(_POST['resumableChunkNumber'].value) * (int(_POST['resumableChunkSize'].value)-1)
    filesize = int(_POST['resumableTotalSize'].value)

    if currentSize + int(_POST['resumableCurrentChunkSize'].value)>= filesize:
        target_file_name = "{}/{}".format(temp_base,_POST['resumableFilename'].value)
        with open(target_file_name, "ab") as target_file:
            for i in range(1,int(_POST['resumableChunkNumber'].value)+1):
                stored_chunk_file_name = "{}{}/{}.part{}".format(temp_base,str(i), _POST['resumableFilename'].value,str(i))
                stored_chunk_file = open(stored_chunk_file_name, 'rb')
                target_file.write( stored_chunk_file.read() )
                stored_chunk_file.close()
                os.unlink(stored_chunk_file_name)
                temp_dir = os.path.join(temp_base,str(i))
                os.rmdir(temp_dir)
        target_file.close()
        CurrentFile.append(target_file_name)

