import cgi
import cgitb
cgitb.enable()
import logging
import os
import sys
import mymodule

def app(environ, start_response):


    try:

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
                mymodule.handler_rs_POST(_POST)
            # CASE 2: receive the date of publication and change the file name
            else:
                mymodule.handler_no_POST(_POST)
           
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
                if mymodule.handler_rs_GET(_GET) == True:
                    return 'ok'
                else:
                    print "HTTP/1.0 404 Not Found"
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
                }

                .error.active {
                  padding: 0.3em;
                } 




                /* style de Bruno */
                body {
                    font-family: arial;

                    padding: 50px 10% 50px 10%;
                }

                h1 {
                    padding-left: 50px;
                    margin-bottom: 100px;
                }

                div.editor_technical_contact_container {
                    position: relative;
                    z-index: 1;
                    top: 0;
                    width: 100%;
                }

                div.editor_technical_contact {
                    position: absolute;

                    right: 0;

                    text-align: left;

                    border: 1px solid grey;
                    border-radius: 5px;
                    padding: 10px;
                }

                div.main {
                    z-index: 0;
                }

                fieldset {
                    margin-top: 15px;
                    border-radius: 10px;
                }

                input.file_size {
                    background-color: green;
                    border-radius: 10px;
                }

                input.file_type {
                    background-color: red;
                    border-radius: 10px;
                }

                div.submit {
                    text-align: center;
      
                    margin-top: 50px;
                    margin-left: 100px;
                    margin-right: 100px;
                }

                div.submit input[type=submit] {
                    margin-left: 200px;
                }

                span.ref {
                    font-size: smaller;
                    color: blue;
                }
               
            </style>

        </head>
        <body>
            <div class="editor_technical_contact_container">
                <div class="editor_technical_contact">
	                <h3>Editor Technical Contact:</h3>
	                <p><span class="ref">(12)</span>&lt;&lt;Title&gt;&gt;<span class="ref">(13)</span>&lt;&lt;Name&gt;&gt;<span class="ref">(14)</span>&lt;&lt;Surname&gt;&gt;</p>
	                <p><span class="ref">(15)</span>&lt;&lt;Email&gt;&gt;</p>
	                <p><span class="ref">(16)</span>&lt;&lt;International phone number&gt;&gt;</p>
                </div>
            </div>
            <div class="main">
                <h1>Adaptive Upload</h1>
                <h2><span class="ref">(1)</span>&lt;&lt;Editor&gt;&gt; - <span class="ref">(2)</span>&lt;&lt;Publication Title&gt;&gt;</h2>
                <form  id= "example" name="test" method="post" action="">
                    <fieldset>
	                    <legend>File selection:</legend>
                        <a href="#" id="browseButton">Select files</a><ul class="resumable-list"></ul><br>
                    </fieldset>
                    <fieldset>
                    <legend>Publication:</legend>
                    <input type="text" id="champ_date1" name="date_p" size="25" value="<<Publication Start Date>>"><input type="text" value="<<Publication start time>>"/>
                    <div id="calendarMain1"></div>
                        <script type="text/javascript">
                            calInit("calendarMain1", "", "champ_date1", "jsCalendar", "day", "selectedDay");
                        </script>
                    
                    <input type="text" id="champ_date2" name="date_f_p" size="25" value="<<Publication End Date>>" ><br/>    
                    <div id="calendarMain2"></div>
                        <script type="text/javascript">
                            calInit("calendarMain2", "", "champ_date2", "jsCalendar", "day", "selectedDay");
                        </script>
                    <input type="text" value="<<Publication number>>" /><br/>
                    </fieldset>
                    <fieldset>
                        <legend>Status:</legend>
	                    <input type="button" class="file_size" value="File size" onclick = displaysize() /><span id = "filesize"></span><br/>
	                    <input type="button" class="file_type" value="File type" onclick = displayFiletype() /> <span id = "filetype"></span>
	                </fieldset>
            
                    <div class="submit">
	                    <input type="button" value="Cancel" />
	                    <input type="submit" />
	                </div>
                </form>
            </div>

            <script>
                var r = new Resumable({
                  target:'',        
                 chunkSize:1*256*1024,
                });
                var date1 = document.getElementById('champ_date1');
                var date2 = document.getElementById('champ_date2');
                var form = document.getElementById('example');
                
                var file_resumable;
                
                
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
                  function displaysize()
                {
                    var a = r.getSize();
                    var b = "B";
                    if (a/1000 >= 1)
                        {
                            a = a / 1000;
                            b = "KB";
                            if(a/1024 >= 1)
                                {
                                    a = a/1000;            
                                    b = "MB";
                                    if(a/1024 >=1)
                                        {
                                            a = a/1000;
                                            b = "GB";    
                                        }                    
                                }
                            
                        }
                    a = a * 10
                    a = Math.round(a);
                    a = a/10
                    size = a.toString() + b;
                    document.getElementById('filesize').innerHTML = size;       
                }  
                  function displayFiletype()
                {
                    extension = file_resumable.fileName.split('.').pop();
                    document.getElementById('filetype').innerHTML = extension;
                }
                
                r.assignBrowse(document.getElementById('browseButton'));

                r.on('fileAdded', function(file){
                  // Show progress pabr
                  $('.resumable-list').show();
                  // Show pause, hide resume

                  // Add the file to the list
                  name_tmp = file.fileName;
                  file_resumable = file;
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

    except Exception, e:
        logging.exception('!!! EXCEPTION !!!')
        start_response(
            '500 Internal Server Error', 
            [
                ('Content-type', 'text/html; charset=utf8'),
            ]
        )
        return None



