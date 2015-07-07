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
        File %s uploaded successfully.<br> 
    </body>
</html>"""%CurrentFile

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

        if 'filename_delete' in _GET:
            print "good try"
            file_delete = (_GET['filename_delete'])[0]
            target_delete = os.path.join(temp_base,file_delete)
            os.remove(target_delete)
            exit(-1)

          
   
        body = u"""





<html>
    <head><title>Upload</title>
        <script src="http://blog.niap3d.com/download/jsSimpleDatePickr/jsSimpleDatePickr.js"></script>
        <script src="http://blog.niap3d.com/download/jsSimpleDatePickr/jsSimpleDatePickrInit.js"></script>
        <script src="https://raw.githubusercontent.com/23/resumable.js/master/resumable.js"></script>
        <script src="http://code.jquery.com/jquery-2.1.4.js"></script>

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
            

            /* Uploader: Drag & Drop */
            .resumable-error {display:none; font-size:14px; font-style:italic;}
            .resumable-drop {padding:15px; font-size:13px; text-align:center; color:#666; font-weight:bold;background-color:#eee; border:2px dashed #aaa; border-radius:10px; margin-top:40px; z-index:9999; display:none;}
            .resumable-dragover {padding:30px; color:#555; background-color:#ddd; border:1px solid #999;}

            /* Uploader: Progress bar */
            .resumable-progress {margin:30px 0 30px 0; width:100%; display:none;}
            .progress-container {height:7px; background:#9CBD94; position:relative; }
            .progress-bar {position:absolute; top:0; left:0; bottom:0; background:#45913A; width:0;}
            .progress-text {font-size:11px; line-height:9px; padding-left:10px;}
            .progress-pause {padding:0 0 0 7px;}
            .progress-resume-link {display:none;}
            .is-paused .progress-resume-link {display:inline;}
            .is-paused .progress-pause-link {display:none;}
            .is-complete .progress-pause {display:none;}

            /* Uploader: List of items being uploaded */
            .resumable-list {overflow:auto; margin-right:-20px; display:none;}
            .uploader-item {width:148px; height:90px; background-color:#666; position:relative; border:2px solid black; float:left;     margin:0 6px 6px 0;}
            .uploader-item-thumbnail {width:100%; height:100%; position:absolute; top:0; left:0;}
            .uploader-item img.uploader-item-thumbnail {opacity:0;}
            .uploader-item-creating-thumbnail {padding:0 5px; font-size:9px; color:white;}
            .uploader-item-title {position:absolute; font-size:9px; line-height:11px; padding:3px 50px 3px 5px; bottom:0; left:0; right:0; color:white; background-color:rgba(0,0,0,0.6); min-height:27px;}
            .uploader-item-status {position:absolute; bottom:3px; right:3px;}

            /* Uploader: Hover & Active status */
            .uploader-item:hover, .is-active .uploader-item {border-color:#4a873c; cursor:pointer; }
            .uploader-item:hover .uploader-item-title, .is-active .uploader-item .uploader-item-title {background-color:rgba(74,135,60,0.8);}

            /* Uploader: Error status */
            .is-error .uploader-item:hover, .is-active.is-error .uploader-item {border-color:#900;}
            .is-error .uploader-item:hover .uploader-item-title, .is-active.is-error .uploader-item .uploader-item-title {background-   color:rgba(153,0,0,0.6);}
            .is-error .uploader-item-creating-thumbnail {display:none;}
            
            /* Delete file */
            .deleteFileCSS {display:none;}

            /* This is the style of our error messages */
            .error {
              width  : 100%;
              padding: 0;
 
              font-size: 80%;
              color: white;
              background-color: #900;
              border-radius: 0 0 5px 5px;
 
              -moz-box-sizing: border-box;
              box-sizing: border-box;
            }

            .error.active {
              padding: 0.3em;
            }            
        </style>

    </head>
    <body>
        <form  id= "example" name="test" method="post" action="">
            <label for="File">File:</label> <a href="#" id="browseButton">Select files</a><br>
            <div class="resumable-progress">
                <table>
                 <tr>
                   <td width="90%"><div class="progress-container"><div class="progress-bar"></div></div></td>
                   <td class="progress-text" nowrap="nowrap"></td>
                   <td class="progress-pause" nowrap="nowrap">
                     <a href="#" onclick="r.upload(); return(false);" class="progress-resume-link"><img src="https://lh6.ggpht.com/GUkQ_-dwSw6o-QwQwfJRSZgwzF-rSmcgW5TrBcmBMHtfP5mT52uZfYscELcqBIsPx40=w300" title="Resume upload"  height="42" width="42"/></a>
                     <a href="#" onclick="r.pause(); return(false);" class="progress-pause-link"><img src="http://uxrepo.com/static/icon-sets/elusive/svg/pause-circled.svg" title="Pause upload"  height="42" width="42"/></a>
                   </td>
                 </tr>
               </table>
             </div>
            <br>
             <ul class="resumable-list"></ul>
            <br>
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
            var date1 = document.getElementById('champ_date1');
            var date2 = document.getElementById('champ_date2');
            var form = document.getElementById('example');
            
            
            form.addEventListener("submit",function(event){
                console.log("submit event");
                if(!date1.value){
                    console.log("in the event and ");
                    alert("Please input the date publication")
                    event.preventDefault();
                    }

                if(!date2.value){
                    alert("Please input the date fin publication")
                    event.preventDefault();
                    }
                },false
            );

             function deleteFile(filename_delete)
            {
                var url = document.URL.replace("#","");
                var params ='filename_delete='+filename_delete;
                var http = new XMLHttpRequest();
                console.log("click delete");
                http.open("GET",url+"?"+params,true); 
                http.onreadystatechange = function()
                {
                     if(http.readyState == 4 && http.status == 200) {
                     alert(http.responseText);
                    }
                } 
                http.send(null);                        
              }

         
            
            r.assignBrowse(document.getElementById('browseButton'));

            r.on('fileAdded', function(file){
              // Show progress pabr
              $('.resumable-list').show();
              // Show pause, hide resume

              // Add the file to the list
              name_tmp = file.fileName;
              $('.resumable-list').append('<li class="resumable-file-'+file.uniqueIdentifier+'">Uploading <span class="resumable-file-name"></span> <progress id = "progress" value="100" max="100">100%</progress>');
              $('.resumable-file-'+file.uniqueIdentifier+' .resumable-file-name').html(file.fileName);
              // Actually start the upload
              r.upload();
            });
          r.on('pause', function(){
              // Show resume, hide pause
              $('.resumable-progress .progress-resume-link').show();
              $('.resumable-progress .progress-pause-link').hide();
            });
          r.on('uploadStart', function(){
              // Show resume, hide pause
              $('.resumable-progress .progress-resume-link').hide();
              $('.resumable-progress .progress-pause-link').show();
            });
          r.on('complete', function(){
              // Hide pause/resume when the upload has completed
              $('.resumable-progress').hide();
              $('.resumable-progress .progress-resume-link, .resumable-progress .progress-pause-link').hide();
              $('.deleteFileCSS').show();
            });
          r.on('fileSuccess', function(file,message){
              // Reflect that the file upload has completed
              $('.resumable-file-'+file.uniqueIdentifier+' .resumable-file-progress').html('(completed)');
            });
          r.on('fileError', function(file, message){
              // Reflect that the file upload has resulted in error
              $('.resumable-file-'+file.uniqueIdentifier+' .resumable-file-progress').html('(file could not be uploaded: '+message+')');
            });
          r.on('fileProgress', function(file){
              // Handle progress for both the file and the overall upload
              $('.resumable-file-'+file.uniqueIdentifier+' .resumable-file-progress').html(Math.floor(file.progress()*100) + '%');
              document.getElementById("progress").value = file.progress()*100;
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



