import cgi
import cgitb
cgitb.enable()
import os
import sys

# extention: only the file who's extension is in this set "extention" can be identified
# eg:        LeMonde.pdf ----> LeMonde_07_07_2015.pdf       LeMonde.txt ----> LeMonde.txt_07_07_2015
extension = set(['pdf',])
# temp_base: we will store the file uploaded in this directory
temp_base = '/tmp/resumable_images/'
# CurrentFile: store the name of the file we have already uploaded, not success in the case of supervisor
CurrentFile = []


def app(environ, start_response):
    # when the method is POST, there are two case:
    # CASE 1: the RESUMABLE.js send the POST
    #           1.we receive the chunk sended by RESUMABLE.js
    #           2.we collect all of the chunk and delete those tempory directory 
    # CASE 2: we submit the form and send a POST
    #           1.we receive the date of publication of the file and change his name

    if environ['REQUEST_METHOD'] == 'POST':
        #import pdb
        #pdb.set_trace()
        _POST = cgi.FieldStorage(
            fp=environ['wsgi.input'],
            environ=environ,
            keep_blank_values=True
        )
        # CASE 1
        if "resumableChunkNumber" in _POST:
            # Receive the chunk information in the POST
            temp_dir = "{}{}".format(temp_base, _POST['resumableChunkNumber'].value)
            chunk_file = "{}/{}.part{}".format(temp_dir, _POST['resumableFilename'].value, _POST['resumableChunkNumber'].value)
            fileitem = _POST['file']
            print "this is the file name",fileitem.filename
            file_path = chunk_file

            counter = 0
            # If the path not exist, create a new one
            if not os.path.exists(file_path):
                os.makedirs(temp_dir)
            # Save the file in the tempory directory
            with open(file_path, 'wb') as output_file:
                while 1:
                    data = fileitem.file.read(1024)
                    if not data:
                        break
                    output_file.write(data)
                    counter += 1
                    if counter == 100:
                        counter = 0

            # calcul the current size and receive the file size
            currentSize =  int(_POST['resumableChunkNumber'].value) * (int(_POST['resumableChunkSize'].value)-1)
            filesize = int(_POST['resumableTotalSize'].value)

            # if all of the chunk were received, collect all of the chunk and create a new file
            if currentSize + int(_POST['resumableCurrentChunkSize'].value)>= filesize:
                print "entrez dans l'integration"
                print "*************************"
                target_file_name = "{}/{}".format(temp_base,_POST['resumableFilename'].value)
                with open(target_file_name, "ab") as target_file:
                    for i in range(1,int(_POST['resumableChunkNumber'].value)+1):
                        print i
                        stored_chunk_file_name = "{}{}/{}.part{}".format(temp_base,str(i), _POST['resumableFilename'].value,str(i))
                        stored_chunk_file = open(stored_chunk_file_name, 'rb')
                        target_file.write( stored_chunk_file.read() )
                        stored_chunk_file.close()
                        os.unlink(stored_chunk_file_name)
                        temp_dir = os.path.join(temp_base,str(i))
                        os.rmdir(temp_dir)

                target_file.close()
                # to remember the name of the file
                CurrentFile.append(target_file_name)
        # CASE 2: receive the date of publication and change the file name
        else:
            Date_p = _POST.getvalue("date_p")	
            Date_f_p = _POST.getvalue("date_f_p")
            for i in range(1,len(CurrentFile)+1):
                C_file = CurrentFile.pop()
                if not os.path.isfile(C_file ):
                    print "file can't be found"                    
                    exit(-1)			
                else: 
                    file_name_old = os.path.basename(C_file)
                    List = file_name_old.split('.')
                    Date_p_tmp = "_"+Date_p.replace('/','_')
                    if len(List) > 1 and (List[len(List)-1] in extension):
                        filename_tmp = ".".join(List[0:len(List)-1])
                        file_name_final = filename_tmp + Date_p_tmp + '.' + List[len(List)-1] 			
                    else: 
                        file_name_final = file_name_old + Date_p_tmp
                    path_old = os.path.join(temp_base,file_name_old)
                    path_final = os.path.join(temp_base,file_name_final)
                    os.rename(path_old,path_final)
   
       
        
       
    body = u"""

<html>
    <head><title>Fin upload</title>
        <style>
        /* Body */
            body 
            {
                background-image: url("http://egbinc.com/images/layout/background.png");
            }
        </style>
    </head>

    <body>
        File uploaded successfully.<br> 
    </body>
</html>"""

    if environ['REQUEST_METHOD'] == 'GET':
   
        _GET = cgi.parse_qs(environ['QUERY_STRING'])
        if 'resumableChunkNumber' in _GET:
            print "good", _GET['resumableChunkNumber']
            temp_dir = "{}{}".format(temp_base, (_GET['resumableIdentifier'])[0])
                #print "temp_dir is ",temp_dir
            chunk_file = "{}/{}.part{}".format(temp_dir, (_GET['resumableFilename'])[0],  (_GET['resumableChunkNumber'])[0])
                #print "chunk_file is", chunk_file
                #import pdb
                #pdb.set_trace()

            if not os.path.isfile(chunk_file):
                print "HTTP/1.0 404 Not Found"
                exit(-1)
            else:
                return 'ok'

          
   
        body = u"""





<html>
    <head><title>Upload</title>
        <script src="http://blog.niap3d.com/download/jsSimpleDatePickr/jsSimpleDatePickr.js"></script>
        <script src="http://blog.niap3d.com/download/jsSimpleDatePickr/jsSimpleDatePickrInit.js"></script>
        <script src="https://raw.githubusercontent.com/23/resumable.js/master/resumable.js"></script>

        <link rel="stylesheet" href="http://yui.yahooapis.com/pure/0.6.0/pure-min.css">

        <style>
            /* DEBUT calendrier JS : jsSimpleDatePickr */
            #calendarMain1, #calendarMain2{
                margin-left: 20%;
            }
            /* conteneur calendrier */
            .calendarWrap{
                display: none;
                position: absolute;
                z-index: 1000;
                width: 210px;
                padding: 5px 10px 10px 10px;
                background-color: #2e373f;
                /*background-color: rgba(46, 55, 63, 0.95);*/
                border-radius: 10px;
                -moz-box-shadow: 0 0 10px #555;
                -webkit-box-shadow: 0 0 10px #555;
                box-shadow: 0 0 10px #555;
                font-size: 12px;
            }
            /* bouton d'affichage*/
            #calendarMain1 > input, #calendarMain2 > input{
                display: block;
                width: 100px;
                height: 22px;
                padding-top: 2px;
                background-color: #2e373f;
                color: #fff;
                border-radius: 5px;
                border: none;
            }
            #calendarMain1 > input:hover, #calendarMain2 > input:hover{
                background-color: #2673cb;
            }
            /* navigation dans le calendrier */
            .calendarWrap ul{
                margin: 5px 0 10px 0;
                padding: 0;
            }
            .calendarWrap li{
                margin: 0;
                padding: 0;
                width: 20px;
                display: inline-block;
                *display: inline;
            }
            .calendarWrap li.calendarTitle{
                width: 170px;
                color: #ccc;
                text-align: center;
            }
            .calendarWrap li input{
                width: 20px;
                background-color: #5d6f7f;
                border: none;
                color: #fff;
            }           
            .calendarWrap li input:hover{
                background-color: #6f8598;
            }
            /* calendrier */
            .jsCalendar{
                color: #fff;
                border-collapse: collapse;
            }
            .jsCalendar th{
                color: #8ba7bf;
                font-size: 16px;
                font-weight: normal;
                text-align: center;
            }
            .jsCalendar td{
                padding: 0;
                border: none;
            }
            .jsCalendar a{
                display: block;
                width: 30px;
                padding: 3px 0 3px 0;
                color: #fff;
                font-weight: bold;
                text-decoration: none;
                text-align: center;
            }
            .jsCalendar .day:hover a{
                background-color: #2673cb;
                border-color: #2673cb;
            }
            .jsCalendar .selectedDay a{
                background-color: #c44d38;
                border-color: #c44d38;
            }
            /* FIN calendrier JS : jsSimpleDatePickr */
            
            /* Body */
            body {
                background-image: url("http://egbinc.com/images/layout/background.png");
            }
            
        </style>

    </head>
    <body>
        <form  name="test" method="post" action="">
            <label for="File">File:</label> <a href="#" id="browseButton">Select files</a><p id="dropTarget"></p><br><br>

            <label for="date_pu">Date publication:</label><br><input type="text" id="champ_date1" name="date_p" size="15">
            <div id="calendarMain1"></div>
                <script type="text/javascript">
                    calInit("calendarMain1", "", "champ_date1", "jsCalendar", "day", "selectedDay");
                </script>


            <label for="date_fin_pu">Date fin publication:</label><br><input type="text" id="champ_date2" name="date_f_p" size="15"></p>
            <div id="calendarMain2"></div>
                <script type="text/javascript">
                    calInit("calendarMain2", "", "champ_date2", "jsCalendar", "day", "selectedDay");
                </script>

            <button type="submit" class="pure-button pure-button-primary">Submit</button>
        </form>


        <script>
            var r = new Resumable({
              target:'',        
             chunkSize:1*256*1024,
            });
            
            r.assignBrowse(document.getElementById('browseButton'));
            r.assignDrop(document.getElementById('dropTarget'));

            r.on('fileSuccess', function(file){
                console.debug(file);
            });
            r.on('fileProgress', function(file){
                console.debug(file);
            });
            r.on('fileAdded', function(file, event){
                r.upload();
                //console.debug(file, event);
            });
            r.on('filesAdded', function(array){
                //console.debug(array);
            });
            r.on('fileRetry', function(file){
                //console.debug(file);
            });
            r.on('fileError', function(file, message){
                //console.debug(file, message);
            });
            r.on('uploadStart', function(){
                //console.debug();
            });
            r.on('complete', function(){
                //console.debug();
            });
            r.on('progress', function(){
                //console.debug();
            });
            r.on('error', function(message, file){
                //console.debug(message, file);
            });
            r.on('pause', function(){
                //console.debug();
            });
            r.on('cancel', function(){
                //console.debug();
            });
        </script>
    </body>
</html>

"""
    start_response(
        '200 OK', 
        [
            ('Content-type', 'text/html; charset=utf8'),
            ('Content-Length', str(len(body))),
        ]
    )
    return [body.encode('utf8')]



