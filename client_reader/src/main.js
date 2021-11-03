const { app, BrowserWindow } = require('electron')
// const path = require("path")
// const url = require("url")

//создаём окно
function createWindow() {
  let mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 450,
    minHeight: 650,
    autoHideMenuBar: true,
    icon: __dirname + '/icon.ico'
  });
  let child = new BrowserWindow({
    width: 800, // задал ширину
    height: 700, // задал высоту
    parent: mainWindow, // указал родительское окно
    // closable: false,
    modal: true, // указал дочернее окно 
    autoHideMenuBar: true, // скрыл меню под 
    icon: __dirname + '/icon.ico',
  });
  child.loadURL(`file://${__dirname}/login.html`);
  // child.once('ready-to-show', () => {
  //   child.show()
  // })
  // appWindow.webContents.openDevTools();
  mainWindow.loadURL(`file://${__dirname}/index.html`);
};

app.on('ready', () => {
  createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

// // отправка отчёта об ошибках, url укажем в будущем
// const { crashReporter, globalShortcut } = require('electron')
// crashReporter.start({  compress: true, submitURL: '' })