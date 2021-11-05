document.getElementById('btn').comm = 'login';
document.getElementById('signin').onclick = function() {
    document.getElementById('btn').comm = 'login';
};

document.getElementById('signup').onclick = function() {
    document.getElementById('btn').comm = 'signup';
};

document.getElementById('reset').onclick = function() {
    document.getElementById('btn').comm = 'reset';
};

document.getElementById('btn').onclick = function() {
    if (this.comm == 'login'){
        var log = document.getElementById('login').value;
        var password = document.getElementById('password').value;
        var ret;
        var ws = new WebSocket("ws://92.49.191.102:8765/")
        ws.onopen = function () {
            let data = {
                comm: 'login',
                login: log,
                password: password
            };
            let json = JSON.stringify(data);
            ws.send(json);
        };
        ws.onmessage = function (event) {
                ret = JSON.parse(event.data);
                  
                if(ret.res != "None") {
                // alert('Пароль верный'); 
                window.close();
                } else {
                    alert('Пароль неверный');
                    document.getElementById('login').value = '';
                    document.getElementById('password').value = '';
                    document.getElementById('repass').value = '';
                    document.getElementById('email').value = '';
                    }
                };
    } else if (this.comm == 'signup'){
        var log = document.getElementById('login').value;
        var password = document.getElementById('password').value;
        var email = document.getElementById('email').value;
        if (password == document.getElementById('repass').value){
            var ret;
            var ws = new WebSocket("ws://92.49.191.102:8765/")
            ws.onopen = function () {
                let data = {
                    comm: 'signup',
                    login: log,
                    password: password,
                    email: email
                };
                let json = JSON.stringify(data);
                ws.send(json);
            };
            ws.onmessage = function (event) {
                ret = JSON.parse(event.data);
                if(ret.res != "None" && ret.res != 'UserFound') {
                    alert('Новый пользователь добавлен!'); 
                    document.getElementById('signin').click();
                } else if (ret.res == 'UserFound'){
                    alert('Такой пользователь существует!');
                    document.getElementById('login').value = '';
                    document.getElementById('password').value = '';
                    document.getElementById('repass').value = '';
                    document.getElementById('email').value = '';
                } else {
                    alert('Использованы неверные символы в пароле, почте или логине.\r\n Проверьте их ещё раз');
                    document.getElementById('login').value = '';
                    document.getElementById('password').value = '';
                    document.getElementById('repass').value = '';
                    document.getElementById('email').value = '';
                };
            };
            }
    } else if (this.comm == 'reset') {
        var ret;
        var ws = new WebSocket("ws://92.49.191.102:8765/")
        var log = document.getElementById('login').value;
        ws.onopen = function () {
            let data = {
                comm: 'repass',
                login: log
            };
            let json = JSON.stringify(data);
            console.log(json)
            ws.send(json);
            };
    }
};

const ipc = require('electron').ipcRenderer

ipc.send('login_user', 'Какашка')
ipc.on('login', function (event, arg){
    console.log(arg)
})