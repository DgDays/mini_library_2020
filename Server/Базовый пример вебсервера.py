
# WS Сервер (базовый пример)

import asyncio # Библиотека стандартной архитектуры асинхронного ввода - вывода в Python
import websockets
import pymysql
import json
import datetime

async def hello(websocket, path): # На стороне сервера websocket выполняет 
    # сопрограмму обработчика hello один раз для каждого соединения
    ask = await websocket.recv()
    ask = json.loads(ask)
    if ask["comm"] == 'login':
        con = pymysql.connect(host='92.49.138.74', user='DGDays', 
            password='669202Qazwerty+', db='library')
        with con:
            cur = con.cursor()
            print(ask)
            cur.execute('''SELECT * FROM users WHERE Login=(%s) AND Password=(%s)''',(ask['login'],ask['password']))
            greeting = cur.fetchone()
            if greeting != None:
                greeting = {
                    "id": greeting[0],
                    "Login": greeting[1],
                    "Password": greeting[2],
                    "Name": greeting[3],
                    "Phone": greeting[4],
                    "Date_of_birthday": greeting[5].strftime("%d.%m.%Y"),
                    'res': "Good"
                }
            else:
                greeting = {'res': 'None'}
            greeting = json.dumps(greeting)
            print(greeting)
            await websocket.send(greeting)

start_server = websockets.serve(hello, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
# Закрывает соединение после возврата
# async/await -(специальный синтаксис для работы с промисами)
# Промис- это объект,
# представляющий возможное завершение передачи или сбой асинхронной операции
# В Python async гарантирует, что функция вернет промис и обернет в него не промисы. 