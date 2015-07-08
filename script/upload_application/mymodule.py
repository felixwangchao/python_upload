import os
import sys
import logging

CurrentListFile = 'CurrentFile.data'
CurrentFile = []

# extention: only the file who's extension is in this set "extention" can be identified
# eg:        LeMonde.pdf ----> LeMonde_07_07_2015.pdf       LeMonde.txt ----> LeMonde.txt_07_07_2015
extension = set(['pdf',])
# temp_base: we will store the file uploaded in this directory
temp_base = '/tmp/resumable_images/'
# CurrentFile: store the name of the file we have already uploaded, not success in the case of supervisor




# handler: for trait the GET from resumable.js
def handler_rs_GET(_GET): 
    '''This function is used to deal with the GET sended by resumable.js

        _GET = cgi.parse_qs(environ['QUERY_STRING'])'''
    temp_dir = "{}{}".format(temp_base, (_GET['resumableIdentifier'])[0])
    chunk_file = "{}/{}.part{}".format(temp_dir, (_GET['resumableFilename'])[0],  (_GET['resumableChunkNumber'])[0])
    if not os.path.isfile(chunk_file):
        return False
    else:
        return True


# handler: for trait the POST from resumable.js
def handler_rs_POST(_POST):
    ''' This function is used to deal with the POST sended by resumable.js

        the _POST = _POST = cgi.FieldStorage(...) '''
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
    ''' This function is used to collect all the small chunk and write them in a new file

        the _POST = _POST = cgi.FieldStorage(...) '''
 
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
        f = open('/tmp/CurrentFile.txt','a+')
        filename_target_tmp = temp_base + os.path.basename(target_file_name)
        f.write(filename_target_tmp+"\n")
        logging.warning(filename_target_tmp)
        f.close()
            


# handler for trait the POST from form
def handler_no_POST(_POST):
    ''' This function is used to deal with a normal request POST submit from "form"

        the _POST = _POST = cgi.FieldStorage(...) ''' 

    Date_p = _POST.getvalue("date_p")	
    Date_f_p = _POST.getvalue("date_f_p")
    
    update_CurrentFile()
        
    for i in range(1,len(CurrentFile)+1):
        C_file = CurrentFile.pop()
        logging.warning('WARNING! '+C_file)
        file_real = C_file.replace("\n","")
        if not os.path.isfile(file_real):               
            continue			
        else:
            rename_file(file_real, Date_p) 
            

def update_CurrentFile():
    '''This function is used to update the list CurrentFile, CurrentFile record the path of all the file uploaded

       It takes no arguments, because CurrentFile is a list global'''

    f2=open('/tmp/CurrentFile.txt','r+')
    line = f2.readline()

    while line !="":
        CurrentFile.append(line)
        line = f2.readline()
    f2.close()
    
    logging.warning('WARNING! remove the txt')
    os.remove('/tmp/CurrentFile.txt')

def rename_file(file_real, Date_p):
    '''This function is used to rename a file with his path and the publication date

       file_real is his path, Date publication is the date'''

    file_name_old = os.path.basename(file_real)
    List = file_name_old.split('.')
    Date_p_tmp = "_"+Date_p.replace('/','_')
    logging.warning('WARNING! extention probleme '+List[len(List)-1])
    if len(List) > 1 and (List[len(List)-1] == 'pdf'):
        filename_tmp = ".".join(List[0:len(List)-1])
        file_name_final = filename_tmp + Date_p_tmp + '.' + List[len(List)-1]
        path_old = os.path.join(temp_base,file_name_old)
        path_final = os.path.join(temp_base,file_name_final)
        os.rename(path_old,path_final) 			
    else: 
        file_name_final = file_name_old + Date_p_tmp
        path_old = os.path.join(temp_base,file_name_old)
        path_final = os.path.join(temp_base,file_name_final)
        os.rename(path_old,path_final)     

