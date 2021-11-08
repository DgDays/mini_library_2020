const { app, BrowserWindow} = require('electron')
// Вывод инфы в консоль login.html 35-41
// const path = require("path")
// const url = require("url")
var child_window
var main_window
//создаём окно
function createWindow() {
  var mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 450,
    minHeight: 650,
    autoHideMenuBar: true,
    icon: __dirname + '/icon.ico'
  });
  var child = new BrowserWindow({
    width: 800, // задал ширину
    height: 750, // задал высоту
    parent: mainWindow, // указал родительское окно
    // closable: false,
    modal: true, // указал дочернее окно 
    autoHideMenuBar: true, // скрыл меню под 
    icon: __dirname + '/icon.ico',
  });
  child_window =  child;
  main_window = mainWindow;
  child.loadURL(`file://${__dirname}/login.html`);
  // child.once('ready-to-show', () => {
  //   child.show()
  // })
  // main_window.webContents.openDevTools();
  mainWindow.loadURL(`file://${__dirname}/index.html`);
};

app.on('ready', () => {
  createWindow();
  child_window.focus();
});

const ipc = require('electron').ipcMain

var logins_data;

ipc.on('login_access', function (event, arg){
  logins_data = arg;
  main_window.webContents.send('login', arg)
})

app.on('window-all-closed', () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

if (logins_data == ''){
  app.quit();
}

// // отправка отчёта об ошибках, url укажем в будущем
// const { crashReporter, globalShortcut } = require('electron')
// crashReporter.start({  compress: true, submitURL: '' })