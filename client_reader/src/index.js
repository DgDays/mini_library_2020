const ipc = require('electron').ipcRenderer


ipc.on('login', function (event, arg){
    console.log(arg);
    var blur = 10;
    let timer = setInterval(function(){
        blur = blur - 0.2
        if (blur <= 0){
            clearInterval(timer);
        }
        else{
            document.getElementById('body').style.filter = 'blur('+blur+'px)';
        }
    }, 20)
})