document.getElementById('btn').comm = 'login';
const ipc = require('electron').ipcRenderer
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
                ipc.send('login_access', ret);
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

function export2json() {
    const originalData = {
      user: [{
          login: localStorage.getItem('login'),
          region: localStorage.getItem('region'),
          city: localStorage.getItem('city'),
          address: localStorage.getItem('address')
        }
      ]
    };

    var fs = require('fs');

    fs.writeFile("./src/settings.json", JSON.stringify(originalData), function(error){

      if(error) throw error; // если возникла ошибка
      console.log("Асинхронная запись файла завершена. Содержимое файла:");
      let data = fs.readFileSync("./src/settings.json", "utf8");
      console.log(data);  // выводим считанные данные
    });
  }

// сохранение строк

function save() {
    var checkbox = document.getElementById('checkbox1zaal1');
    localStorage.setItem('checkbox1zaal1', checkbox.checked);

    var serialObj = document.getElementById('login');
    localStorage.setItem("login", serialObj.value);

    var serialObj = document.getElementById('password');
    localStorage.setItem("password", serialObj.value);

    var serialObj = document.getElementById('repass');
    localStorage.setItem("repass", serialObj.value);

    var serialObj = document.getElementById('email');
    localStorage.setItem("email", serialObj.value);

}

// вывод сохранённых строк снова в свои строки

function load() {    
    var checked = JSON.parse(localStorage.getItem('checkbox1zaal1'));
    document.getElementById("checkbox1zaal1").checked = checked;

    var returnObj = localStorage.getItem("login");
    document.getElementById("login").value = returnObj;

    var returnObj = localStorage.getItem("password");
    document.getElementById("password").value = returnObj;

    var returnObj = localStorage.getItem("repass");
    document.getElementById("repass").value = returnObj;

    var returnObj = localStorage.getItem("email");
    document.getElementById("email").value = returnObj;
}

document.getElementById('checkbox1zaal1').addEventListener('click', function () {
    var checked = this.checked;
      
    if (checked) {
        save();
    } else {
        wis()
    }
});

//var localValue = localStorage.getItem('login');
//var localValue2 = localStorage.getItem('password');
//var localValue3 = localStorage.getItem('repass');
//var localValue4 = localStorage.getItem('email');
//console.log(localValue,localValue2,localValue3,localValue4);

function wis()  {
    localStorage.clear()
}

load();

// нажал клавишу энтер и балдеешь
document.addEventListener("keydown", function onEvent(event) {
    if (event.key === "Enter") {
        export2json();
        document.getElementById("btn").click();
    }
});