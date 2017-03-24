var TIMEOUT = 10000;

window.onload = function() {
    var uid = localStorage.getItem("uid");
    var filename = localStorage.getItem("filename");
    
    if (uid !== null)
    {                
        $.ajax({
            type: "GET",
            url: "/restore",
            timeout: TIMEOUT,
            headers: { 'uid': uid },
            // The key needs to match your method's input parameter (case-sensitive).            
            contentType: "application/json; charset=utf-8",
            dataType: "json",            
            
            success: function(data){
                pos = data["pos"];                                
                
                
                if (pos !== null)
                {
                    alert("Вы недавно пытались загрузить файл '" + filename + 
                    "'. Вы даже успели загрузить " + pos + " байт, но что-то пошло не так.\n" + 
                    "Вы можете снова указать на этот файл и начать отправку, но файл будет\n" +
                    "загружен заново, так как его содержимое между сессиями могло поменяться.");
                }                
            }, 
            async: false
        });
    }    
    localStorage.removeItem("uid");    
    localStorage.removeItem("filename");    
};

function Uploader(file, pos, chunk_size, uid) {    
    this.file = file;
    this.uid = uid;
    this.chunk_size = chunk_size;
    this.pos = pos;
    this.size = file.size;    
    
    if ('mozSlice' in this.file) {
        this.slice_method = 'mozSlice';
    }
    else if ('webkitSlice' in this.file) {
        this.slice_method = 'webkitSlice';
    }
    else {
        this.slice_method = 'slice';
    }
};

function onChunkLoad() {
    var owner = this.owner;
    owner.onChunkLoad();
};

function onTimeout() {
    var owner = this.owner;
    owner.onTimeout();
};

function onError() {
    var owner = this.owner;
    owner.onError();
};

Uploader.prototype = {
    upload: function() {        
        var pos_end = this.pos + this.chunk_size;
        
        if (pos_end > this.size) {
            pos_end = this.size;
        }        
        
        var chunk = this.file[this.slice_method](this.pos, pos_end);    
        this.request = new XMLHttpRequest();
        this.request.owner = this;
        this.request.onload = onChunkLoad;
        this.request.timeout = TIMEOUT; 
        this.request.ontimeout = onTimeout;
        this.request.onerror = onError;
        this.request.open('POST', '/upload', true);
        this.request.overrideMimeType('application/octet-stream');
        this.request.setRequestHeader('UID', this.uid);
        this.request.send(chunk);
    },    
    
    onTimeout: function() {
        alert("Сервер слишком долго не отвечает, загрузка отменена");
        if (this.onFinish)
            this.onFinish(null, false);
    }, 
    
    onError: function() {
        alert("Во время загрузки произошла ошибка, загрузка будет прервана");
        if (this.onFinish)
            this.onFinish(null, true);
    }, 
    
    updateProgress: function() {
        if (this.onUpdateProgress)
            this.onUpdateProgress(this.pos * 100 / this.size);            
    }, 
    
    onChunkLoad: function() {
        if (this.request.status != 200)
        {
            alert('При загрузке файла возникла ошибка');
            if (this.onFinish)
                this.onFinish(null, true);                
            return;
        }
        
        this.pos += this.chunk_size;
        
        if (this.pos > this.size)
        {
            this.pos = this.size;
        }        
        
        this.updateProgress();
        if (this.pos < this.size)       
        {             
            this.upload();            
        }
        else
        {
            this.finish_request();
        }
    },
    
    start: function() {
        this.upload();
    },
    
    finish_request: function() { 
        $.ajax({
            type: "POST",
            url: "/finish_send",
            timeout: TIMEOUT,
            headers: { 'uid': this.uid },            
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            owner: this,
            
            success: function(data){                
                if (this.owner.onFinish)
                    this.owner.onFinish(data, true);
            },
            
            error: function(xhr, req, thrown) {
                if (req == "timeout") {
                    alert("Сервер слишком долго не отвечает, загрузка отменена");
                    if (this.owner.onFinish)
                        this.owner.onFinish(null, false);
                }
                else {
                    alert("При обработке произошла ошибка");
                    if (this.owner.onFinish)
                        this.owner.onFinish(null, true);
                }
            }
        });
    }, 
    
    onUpdateProgress: null,
    onFinish: null    
};

function changeProgress(value) {
    var item = document.getElementById("progressbar-inner");
    item.style.width = value + '%';    
};

function buildTextResponse(data) {
    var parser = data['parser'];
    
    if (parser == 'counter')
        return 'Наиболее распространенные байты: ' + data['result'].join(',')
    else
        return 'Неподдерживаемый результат'
};

function finishSend(data, clean) {
    $('#submit_button').prop('disabled', false);    
    $('#fileupload').prop('disabled', false);    
    
    if (clean) {
        localStorage.removeItem("uid");  
        localStorage.removeItem("filename");                        
    }
    
    if (data === null) {
        $('#resulttext').val('');
    }
    else {              
        $('#resulttext').val(buildTextResponse(data));
    }
};

function startUpload(uid, file, pos) {
    var uploader = new Uploader(file, pos, 64 * 1024, uid);   
    uploader.onUpdateProgress = changeProgress;        
    uploader.onFinish = finishSend;
    uploader.updateProgress();
    uploader.start();
};

function onStartSend(obj) {        
    var uid = null;        
    var files = $('input[type=file]')[0].files;
    
    if (files.length == 0)
    {
        alert("Файл не выбран");        
        return;
    }    
    
    $('#submit_button').prop('disabled', true);    
    $('#fileupload').prop('disabled', true);    
    var file = files[0];    
    
    $.ajax({
            type: "POST",
            url: "/start_send",
            timeout: TIMEOUT,                      
            contentType: "application/json; charset=utf-8",
            dataType: "json",                      
            
            success: function(data){                
                uid = data['id'];                
                localStorage.setItem('uid', uid);
                localStorage.setItem("filename", file.name );    
                startUpload(uid, file, 0);
            },
            
            error: function(xhr, req, thrown) {
                alert('Невозможно начать отправку файла');
                changeProgress(0);
                finishSend(null, false);
            }
        });
};
