const ipc = require('electron').ipcRenderer

ipc.on('login', function (event, arg){
    console.log(arg);
})