const ipc = require('electron').ipcRenderer

// функция для изменения стиля
function changeStyleDiv()   {
    document.getElementById('body').style.filter = 'blur(0px)';
}

ipc.on('login', function (event, arg){
    console.log(arg);
    changeStyleDiv();
})