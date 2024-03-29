'''
Важно!!!

Краткая информация о комментариях:

!!! - То, что нужно сделать в близжайшее время
! - То, что тоже нужно сделать, однако имеет меньший приоритет и нет ограничений по времени

Обозначение окон:
================================ [Главное окно] ================================
Обозначение функций или подокон главных окон:
---------------- [Функция] ----------------

Прошу соблюдать эти условия, для того, чтобы было проще работать.
Так же советую соблюдать и длину ограничителей (слева и справа от надписи одинаковое кол-во)

Спасибо за прочтение

'''
import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk, messagebox, PhotoImage
from ttkthemes import ThemedStyle
from pystray import MenuItem as item
import pystray
import sys
import os
import sqlite3
import datetime
from datetime import timedelta, date
import time
import xlsxwriter
import threading
from tkcalendar import DateEntry
from tkinter import filedialog as fd
from PIL import ImageTk, Image
import playsound
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard
import socket

text = values = ''
self_main = self_info = self_book = self_main_book = self_main_not = self_book_info = 'close'
book_add = 0
prev_column = None

obj = ["Алгебра", "Геометрия", "Математика", "Русский язык", "Английский язык", "Французский язык", "Немецкий язык",
       "Физика", "Химия", "География", "Информатика", "Обществознание", "История", "Литература"]
open_win = []

easter_egg = 0


class MyTree(ttk.Treeview):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Элементам с тегом green назначить зеленый фон, элементам с тегом red
        # назначить красный фон

        self.tag_configure('A', background='green', foreground='white')
        self.tag_configure('B', background='red', foreground='white')
        self.tag_configure('C', background='yellow', foreground='black')

    def insert(self, parent_node, index, **kwargs):
        '''Назначение тега при добавлении элемента в дерево'''

        item = super().insert(parent_node, index, **kwargs)

        values = kwargs.get('values', None)

        if values:
            if "Сдана" in values:
                super().item(item, tag='A')
            elif "Просрочена" in values:
                super().item(item, tag='B')
            elif "На руках" in values:
                super().item(item, tag='C')

        return item


# ================================ Entry с Placeholder ===================

class Entry_Pl(ttk.Entry):
    def __init__(self, master=None, placeholder=None, width=20):
        self.entry_var = tk.StringVar()
        super().__init__(master, width=width, textvariable=self.entry_var)

        if placeholder is not None:
            self.placeholder = placeholder
            self.placeholder_color = 'grey'
            self.default_fg_color = self['foreground']
            self['font'] = 'Arial 11'
            self.placeholder_on = False
            self.put_placeholder()

            self.entry_var.trace("w", self.entry_change)

            # При всех перечисленных событиях, если placeholder отображается,
            # ставить курсор на 0 позицию

            self.bind("<FocusIn>", self.reset_cursor)
            self.bind("<KeyRelease>", self.reset_cursor)
            self.bind("<ButtonRelease>", self.reset_cursor)

    def entry_change(self, *args):
        if not self.get():
            self.put_placeholder()
        elif self.placeholder_on:
            self.remove_placeholder()
            self.entry_change()  # На случай, если после удаления placeholder остается пустое поле

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['foreground'] = self.placeholder_color
        self.icursor(0)
        self.placeholder_on = True

    def remove_placeholder(self):
        # Если был вставлен какой-то символ в начало, удаляем не весь текст, а
        # только placeholder:
        text = self.get()[:-len(self.placeholder)]
        self.delete('0', 'end')
        self['foreground'] = self.default_fg_color
        self.insert(0, text)
        self.placeholder_on = False

    def reset_cursor(self, *args):
        if self.placeholder_on:
            self.icursor(0)


# ================================ Главное окно ==========================
class Main(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, *kwargs)
        # Получение дэфолтного значения шрифта
        default_font = tkFont.nametofont("TkDefaultFont")
        # Изменение дэфолтного значения шрифта
        default_font.configure(size=11, family='Arial')

        self.option_add("*Font", default_font)  # Использование нашего шрифта

        self.title("Мини Библиотека 2020")  # Заголовок
        w = self.winfo_screenwidth() // 2 - 455  # ширина экрана
        h = self.winfo_screenheight() // 2 - 225  # высота экрана
        self.geometry('+{}+{}'.format(w, h))  # Размер
        self.resizable(False, False)  # Изменение размера окна

        threading.Thread(target=creat_table).start()
        theme = open(os.path.dirname(
            os.path.abspath(__file__)) + '/theme.txt', 'r')
        style = ThemedStyle()
        var_style = tk.StringVar()
        var_style.set(theme.read())
        theme.close()
        style.set_theme(var_style.get())

        # Изменение шрифта столбцов в Treeview

        style.configure("Treeview.Heading", font=('Arial', 11))
        style.configure('Treeview', font=('Arial', 11))
        style.configure('TButton', font=('Arial', 11))
        style.configure('TMenubutton', font=('Arial', 11))

        self.initMenus()
        self.initSearch()
        self.initTable()

    def initMenus(self):
        # ================================ Меню ===============================
        theme = open(os.path.dirname(
            os.path.abspath(__file__)) + '/theme.txt', 'r')
        style = ThemedStyle()
        var_style = tk.StringVar()
        var_style.set(theme.read())
        theme.close()
        style.set_theme(var_style.get())

        self.fr = ttk.Frame(self)
        self.fr.pack(fill='x')

        btn_file = ttk.Menubutton(self.fr, text='Файл')

        file_sohranit = tk.Menu(btn_file, tearoff=0)  # Запретить отделение
        first_and_last = first_and_last_day()
        file_sohranit.add_command(label="Статистика за месяц",
                                  command=lambda: threading.Thread(target=month_excel, args=[first_and_last, ]).start())
        file_sohranit.add_command(label="Статистика за год",
                                  command=lambda: threading.Thread(target=year_excel).start())
        file_sohranit.add_command(
            label="Статистика за выбранный срок", command=lambda: Excel())
        file_sohranit.add_separator()
        file_sohranit.add_command(label="Учёт регистраций",
                                  command=lambda: threading.Thread(target=excel_uchet_reg).start())
        file_sohranit.add_command(
            label="Учёт книг", command=lambda: threading.Thread(target=uchet_book).start())
        file_sohranit.add_separator()
        file_sohranit.add_command(
            label='Резервная копия БД', command=lambda: threading.Thread(target=BUP_DB).start())
        file_sohranit.add_command(label='Восстановление БД',
                                  command=lambda: threading.Thread(target=Recov_DB, args=[self, ]).start())

        btn_file.config(menu=file_sohranit)
        btn_file.grid(row=0, column=0, padx=5, pady=5)

        btn_style = ttk.Menubutton(self.fr, text='Темы')

        style_menu = tk.Menu(btn_style, tearoff=0, selectcolor='green')
        style_menu.add_radiobutton(label='Breeze - Светлая', variable=var_style, value='breeze',
                                   command=lambda: style_change(var_style.get()))
        style_menu.add_radiobutton(label='Breeze - Тёмная', variable=var_style, value='nightbreeze',
                                   command=lambda: style_change(var_style.get()))

        btn_uch = ttk.Button(self.fr, text='Учёт книг',
                             command=lambda: self_book_open(self))
        btn_uch.grid(row=0, column=1, padx=5, pady=5)

        btn_not = ttk.Button(self.fr, text='Уведомления',
                             command=lambda: self_not_open(self))
        btn_not.grid(row=0, column=2, padx=5, pady=5)

        btn_vk = ttk.Button(self.fr, text='ВК-Бот', command=lambda: VK_api())
        btn_vk.grid(row=0, column=3, padx=5, pady=5)

        btn_style.config(menu=style_menu)
        btn_style.grid(row=0, column=4, padx=5, pady=5)

        btn_inf = ttk.Menubutton(self.fr, text='Информация')

        file_infa = tk.Menu(btn_inf, tearoff=0)  # Запретить отделение
        file_infa.add_command(label="Просмотреть справку",
                              command=lambda: Spravka())
        file_infa.add_separator()
        file_infa.add_command(label="О программе",
                              command=lambda: Information())

        btn_inf.config(menu=file_infa)
        btn_inf.grid(row=0, column=5, padx=5, pady=5)

    def initSearch(self):
        # ================================= Поиск =============================
        self.frame_search1 = ttk.Frame(self)
        self.frame_search = ttk.Frame(self.frame_search1)

        self.search = Entry_Pl(self.frame_search, "Поиск")
        self.search.grid(row=0, column=0, padx=3, pady=3)

        self.bt_search = ttk.Button(self.frame_search, text='Найти',
                                    command=lambda: threading.Thread(target=search, args=[self, ]).start())
        self.bt_search.grid(row=0, column=1, padx=3, pady=3)

        self.bt_cancel = ttk.Button(self.frame_search, text='Отмена',
                                    command=lambda: threading.Thread(target=update_main, args=[self, ]).start())
        self.bt_cancel.grid(row=0, column=2, padx=3, pady=3)

        self.frame_search.pack()
        self.frame_search1.pack(fill='x')

        self.bind('<Return>', lambda event: search_enter(self))
        self.bt_search.bind('<Button-1>', lambda event: easter1())
        self.bt_cancel.bind('<Button-1>', lambda event: easter2())
        self.search.bind('<Button-1>', lambda event: easter3())

    def initTable(self):
        # ================================  Таблица  ==========================

        self.fr_watch_both = tk.Canvas(
            self, background='#e9e9e9', width=900, height=450)

        def fixed_map(option):
            return [elm for elm in style.map('Treeview', query_opt=option)
                    if elm[:2] != ('!disabled', '!selected') and elm[0] != '!disabled !selected']

        style = ttk.Style()
        style.map('Treeview', foreground=fixed_map(
            'foreground'), background=fixed_map('background'))

        # Создание скроллбара
        self.scroll = ttk.Scrollbar(self.fr_watch_both)
        self.scroll.pack(side='right', fill='y')

        # Таблица
        self.table = MyTree(self.fr_watch_both, columns=('BirthDay', 'Class', 'Litera', 'Adress', 'Phone'), height=21,
                            yscrollcommand=self.scroll.set)
        # Подключение скроллбара
        self.scroll.config(orient='vertical', command=self.table.yview)
        self.table.column('#0', minwidth=260, width=260, anchor=tk.CENTER)
        self.table.column('BirthDay', minwidth=110,
                          width=110, anchor=tk.CENTER)
        self.table.column('Class', minwidth=60, width=60, anchor=tk.CENTER)
        self.table.column('Litera', minwidth=60, width=60, anchor=tk.CENTER)
        self.table.column('Phone', minwidth=130, width=130, anchor=tk.CENTER)
        self.table.column('Adress', minwidth=260, width=260, anchor=tk.CENTER)

        self.table.heading(
            "#0", command=lambda: sort_0(self.table, "#0", False))

        columns = self.table['columns']

        for col in columns:
            self.table.heading(col, text=col, command=lambda _col=col:
            sort(self.table, _col, False))

        self.table.heading('#0', text='ФИО')
        self.table.heading('BirthDay', text='Дата рождения')
        self.table.heading('Class', text='Класс')
        self.table.heading('Litera', text='Литера')
        self.table.heading('Phone', text='Телефон')
        self.table.heading('Adress', text='Адрес')

        self.progress = ttk.Progressbar(self.table, mode='indeterminate')

        self.profile_menu = tk.Menu(self.table, tearoff=0)

        self.profile_menu.add_command(
            label="Добавить читателя", command=lambda: add_profile(self))
        self.profile_menu.add_command(
            label="Изменить читателя", command=lambda: edit_profile(self))
        self.profile_menu.add_command(label="Удалить читателя",
                                      command=lambda: threading.Thread(target=del_profile, args=[self, ]).start())
        self.profile_menu.add_command(
            label="Перевести в класс на 1 >", command=lambda: plus_class(self))
        self.profile_menu.add_command(
            label="Перевести в класс на 1 <", command=lambda: minus_class(self))

        self.table.pack(side='left')
        self.table.bind('<Double-Button-1>', lambda event: info(self))
        self.table.bind(
            '<Button-3>', lambda event: self.profile_menu.post(event.x_root, event.y_root))

        self.fr_watch_both.pack(side='bottom', fill='both')

        threading.Thread(target=update_main, args=[self, ]).start()
        self.focus_force()

        self.bind('<KeyPress>', lambda event: event_handler_main(event, self))
        self.bind('<<Key-43>>', lambda event: update_main(self))
        try:
            self.iconbitmap(os.path.dirname(
                os.path.abspath(__file__)) + "/lib.ico")
        except:
            self.tk.call('wm', 'iconphoto', self._w, ImageTk.PhotoImage(Image.open("./lib.ico")))


# ---------------- Добавить читателя ----------------
class Add_profile(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, *kwargs)
        open_win.append(self)
        self.title("Добавить читателя")  # Заголовок
        w = self.winfo_screenwidth() // 2 - 450  # ширина экрана
        h = self.winfo_screenheight() // 2 - 225  # высота экрана
        self.geometry('+{}+{}'.format(w, h))  # Размер
        self.resizable(False, False)  # Изменение размера окна
        self.protocol("WM_DELETE_WINDOW", lambda: self_main_null(self))
        self.attributes("-topmost", True)

        self.focus_force()

        # надпись "ФИО"
        self.lb_fio = ttk.Label(self, text='ФИО', font='Arial 11')
        self.lb_fio.grid(row=0, column=0, pady=3)

        # место ввода "ФИО"
        self.en_fio2 = ttk.Entry(self, width=49, font='Arial 11')
        self.en_fio2.grid_configure(row=0, column=1, columnspan=20, sticky='W')

        # надпись "Класс"
        self.lb_class = ttk.Label(self, text='Класс', font='Arial 11')
        self.lb_class.grid(row=1, column=0, pady=3)

        # место ввода "Класс"
        self.en_class2 = ttk.Combobox(
            self, values=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], width=3, font='Arial 11')
        self.en_class2.grid_configure(row=1, column=1, sticky='W')

        # надпись "Литера"
        self.lb_lit = ttk.Label(self, text='Литера', font='Arial 11')
        self.lb_lit.grid(row=1, column=2)

        # место ввода "Литера"
        self.en_lit2 = ttk.Combobox(
            self, values=['А', 'Б', 'В', 'Г'], width=3, font='Arial 11')
        self.en_lit2.grid_configure(row=1, column=3, sticky='W')

        # надпись "Телефон"
        self.lb_phone = ttk.Label(self, text='Телефон', font='Arial 11')
        self.lb_phone.grid(row=2, column=0, pady=3)

        # место ввода "Телефон"
        self.en_phone2 = ttk.Entry(self, width=14, font='Arial 11')
        self.en_phone2.grid_configure(row=2, column=1, sticky='W')

        # надпись "Адрес"
        self.lb_adr = ttk.Label(self, text='Адрес', font='Arial 11')
        self.lb_adr.grid(row=3, column=0, pady=3)

        # место ввода "Адрес"
        self.en_adr2 = ttk.Entry(self, width=49, font='Arial 11')
        self.en_adr2.grid_configure(row=3, column=1, columnspan=20, sticky='W')

        self.lb_client = ttk.Label(self, text='Категория', font='Arial 11').grid(
            row=4, column=0, pady=3)

        self.en_client = ttk.Combobox(self, values=["Ученик", "Учитель", "Другой посетитель"], width=18,
                                      font='Arial 11')
        self.en_client.grid_configure(
            row=4, column=1, columnspan=20, sticky='W')

        # надпись "Дата рождения"
        self.lb_db = ttk.Label(self, text='Дата рождения', font='Arial 11')
        self.lb_db.grid(row=5, column=3, pady=3)

        # место ввода "Дата рождения"
        self.en_db2 = Entry_Pl(self, 'dd.mm.YYYY', width=12)
        self.en_db2.grid_configure(row=5, column=4, sticky='W')

        # кнопка "Сохранить"
        self.btn_save = ttk.Button(self, text='Сохранить', command=lambda: threading.Thread(target=save_stud2, args=[
            self, ]).start())  # Пример многопоточности
        self.btn_save.grid(row=6, column=4, pady=3)
        try:
            self.iconbitmap(os.path.dirname(
            os.path.abspath(__file__)) + "/add.ico")
        except:
            self.tk.call('wm', 'iconphoto', self._w, ImageTk.PhotoImage(Image.open("./add.ico")))
        


# ---------------- Изменить читателя ----------------
class Edit_profile(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, *kwargs)
        open_win.append(self)
        self.title("Редактировать читателя")  # Заголовок
        w = self.winfo_screenwidth() // 2 - 450  # ширина экрана
        h = self.winfo_screenheight() // 2  # высота экрана
        self.geometry('+{}+{}'.format(w + 300, h - 125))  # Размер
        self.resizable(False, False)  # Изменение размера окна
        self.protocol("WM_DELETE_WINDOW", lambda: self_main_null(self))
        self.attributes("-topmost", True)

        self.focus_force()

        # надпись "ФИО"
        self.lb_fio = ttk.Label(self, text='ФИО', font='Arial 11')
        self.lb_fio.grid(row=0, column=0, ipady=3)

        # место ввода "ФИО"
        self.en_fio2 = ttk.Entry(self, width=49, font='Arial 11')
        self.en_fio2.grid_configure(row=0, column=1, columnspan=40, sticky='W')

        # надпись "Класс"
        self.lb_class = ttk.Label(self, text='Класс', font='Arial 11')
        self.lb_class.grid(row=1, column=0, ipady=3)

        # место ввода "Класс"
        self.en_class2 = ttk.Combobox(
            self, values=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], width=3, font='Arial 11')
        self.en_class2.grid_configure(row=1, column=1, sticky='W')

        # надпись "Литера"
        self.lb_lit = ttk.Label(self, text='Литера', font='Arial 11')
        self.lb_lit.grid(row=1, column=2, padx=5)

        # место ввода "Литера"
        self.en_lit2 = ttk.Combobox(
            self, values=['А', 'Б', 'В', 'Г'], width=3, font='Arial 11')
        self.en_lit2.grid_configure(row=1, column=3, sticky='W')

        # надпись "Телефон"
        self.lb_phone = ttk.Label(self, text='Телефон', font='Arial 11')
        self.lb_phone.grid(row=2, column=0, ipady=3)

        # место ввода "Телефон"
        self.en_phone2 = ttk.Entry(self, width=14, font='Arial 11')
        self.en_phone2.grid_configure(
            row=2, column=1, columnspan=10, sticky='W')

        # надпись "Адрес"
        self.lb_adr = ttk.Label(self, text='Адрес', font='Arial 11')
        self.lb_adr.grid(row=3, column=0, ipady=3)

        # место ввода "Адрес"
        self.en_adr2 = ttk.Entry(self, width=49, font='Arial 11')
        self.en_adr2.grid_configure(row=3, column=1, columnspan=20, sticky='W')

        # надпись "Дата рождения"
        self.lb_db = ttk.Label(self, text='Дата рождения', font='Arial 11')
        self.lb_db.grid(row=4, column=4, ipady=3)

        # место ввода "Дата рождения"
        self.en_db2 = Entry_Pl(self, 'dd.mm.YYYY', width=12)
        self.en_db2.grid_configure(row=4, column=5, sticky='W')

        # кнопка "Сохранить"
        self.btn_save = ttk.Button(self, text='Сохранить',
                                   command=lambda: threading.Thread(target=edit_stud, args=[self, ]).start())
        self.btn_save.grid(row=5, column=5, ipady=3)

        try:
            self.iconbitmap(os.path.dirname(
            os.path.abspath(__file__)) + "/edit.ico")
        except:
            self.tk.call('wm', 'iconphoto', self._w, ImageTk.PhotoImage(Image.open("./edit.ico")))


# ================================ Информация о читателе =================
class INFO(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, *kwargs)
        open_win.append(self)
        w = self.winfo_screenwidth() // 2 - 450  # ширина экрана
        h = self.winfo_screenheight() // 2 - 225  # высота экрана
        self.geometry('+{}+{}'.format(w + 300, h - 125))  # Размер
        self.resizable(False, False)  # Изменение размера окна
        self.focus_force()
        self.protocol("WM_DELETE_WINDOW", lambda: self_main_null(self))

        self.frame = ttk.Frame(self)
        self.frame.pack(fill='x')

        self.fr_watch_both = ttk.Frame(self, width=660, height=400)

        def fixed_map(option):
            return [elm for elm in style.map('Treeview', query_opt=option)
                    if elm[:2] != ('!disabled', '!selected') and elm[0] != '!disabled !selected']

        style = ttk.Style()
        style.map('Treeview', foreground=fixed_map(
            'foreground'), background=fixed_map('background'))

        # ttk.Style().configure("Treeview",fieldbackground="#e9e9e9")

        # Создание скроллбара
        self.scroll = ttk.Scrollbar(self.fr_watch_both)
        self.scroll.pack(side='right', fill='y')

        # Таблица
        self.info_table = MyTree(self.fr_watch_both, columns=('Author', 'Status', 'Col'), height=14,
                                 yscrollcommand=self.scroll.set)
        # Подключение скроллбара
        self.scroll.config(orient='vertical', command=self.info_table.yview)
        self.info_table.column('#0', width=250, minwidth=250, anchor=tk.CENTER)
        self.info_table.column('Author', width=250,
                               minwidth=250, anchor=tk.CENTER)
        self.info_table.column('Status', width=140,
                               minwidth=140, anchor=tk.CENTER)
        self.info_table.column('Col', width=50, minwidth=50, anchor=tk.CENTER)

        self.info_table.heading(
            "#0", command=lambda: sort_0(self.info_table, "#0", False))

        columns = self.info_table['columns']

        for col in columns:
            self.info_table.heading(col, text=col, command=lambda _col=col:
            sort(self.info_table, _col, False))

        self.info_table.heading('#0', text='Книга')
        self.info_table.heading('Author', text='Автор')
        self.info_table.heading('Status', text='Статус')
        self.info_table.heading('Col', text='Кол-во')

        self.info_table.pack(side='left')
        self.fr_watch_both.pack(side='bottom', fill='both')

        self.progress = ttk.Progressbar(self.info_table, mode='indeterminate')

        self.profile_menu = tk.Menu(self.info_table, tearoff=0)

        self.profile_menu.add_command(
            label="Добавить книгу", command=lambda: add_book(self))
        self.profile_menu.add_command(
            label="Изменить статус/дату сдачи книги", command=lambda: edit_lc(self))
        self.profile_menu.add_command(label="Удалить книгу",
                                      command=lambda: threading.Thread(target=delete_lc, args=[self, ]).start())

        self.bind('<KeyPress>', lambda event: event_handler_info(event, self))

        self.info_table.bind(
            '<Button-3>', lambda event: self.profile_menu.post(event.x_root, event.y_root))
        try:
            self.iconbitmap(os.path.dirname(
            os.path.abspath(__file__)) + "/profile.ico")
        except:
            self.tk.call('wm', 'iconphoto', self._w, ImageTk.PhotoImage(Image.open("./profile.ico")))


# ---------------- Добавить книгу читателю ----------------

class Add_lc(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, *kwargs)
        open_win.append(self)
        self.title("Добавить книгу в ЧБ")  # Заголовок
        w = self.winfo_screenwidth() // 2 - 450  # ширина экрана
        h = self.winfo_screenheight() // 2 - 225  # высота экрана
        self.geometry('+{}+{}'.format(w + 300, h - 125))  # Размер
        self.resizable(False, False)  # Изменение размера окна
        self.protocol("WM_DELETE_WINDOW", lambda: self_info_null(self))
        self.attributes("-topmost", True)

        self.focus_force()

        # надпись "Книга"
        self.bookname = ttk.Label(self, text='Книга', font='Arial 11')
        self.bookname.grid(row=0, column=0, ipady=3)

        # место ввода "Книга"
        self.en_bookname = ttk.Entry(self, width=49, font='Arial 11')
        self.en_bookname.grid_configure(
            row=0, column=1, columnspan=40, sticky='W')

        # надпись "Автор"
        self.lb_author2 = ttk.Label(self, text='Автор', font='Arial 11')
        self.lb_author2.grid(row=1, column=0, ipady=3)

        # место ввода "Автор"
        self.en_author2 = ttk.Entry(self, width=49, font='Arial 11')
        self.en_author2.grid_configure(
            row=1, column=1, columnspan=40, sticky='W')

        # надпись "кол-во"
        self.lb_col = ttk.Label(self, text='Кол-во', font='Arial 11')
        self.lb_col.grid(row=2, column=0, ipady=3)

        # место ввода "кол-во"
        self.en_col = ttk.Entry(self, width=10, font='Arial 11')
        self.en_col.grid_configure(row=2, column=1, columnspan=40, sticky='W')

        # кнопка "Сохранить"
        self.btn_save = ttk.Button(self, text='Сохранить',
                                   command=lambda: threading.Thread(target=save_lc2, args=[self, ]).start())
        self.btn_save.grid(row=3, column=1, padx=3, pady=3,
                           columnspan=40, sticky='E')

        try:
            self.iconbitmap(os.path.dirname(
            os.path.abspath(__file__)) + "/add.ico")
        except:
            self.tk.call('wm', 'iconphoto', self._w, ImageTk.PhotoImage(Image.open("./add.ico")))


# ---------------- Изменить книгу читателя ----------------

class Edit_lc(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, *kwargs)
        open_win.append(self)
        self.title("Изменить книгу в ЧБ")  # Заголовок
        w = self.winfo_screenwidth() // 2 - 450  # ширина экрана
        h = self.winfo_screenheight() // 2 - 225  # высота экрана
        self.geometry('+{}+{}'.format(w + 300, h - 125))  # Размер
        self.resizable(False, False)  # Изменение размера окна
        self.protocol("WM_DELETE_WINDOW", lambda: self_info_null(self))
        self.attributes("-topmost", True)

        self.focus_force()

        # надпись "Книга"
        self.bookname = ttk.Label(self, text='Книга', font='Arial 11')
        self.bookname.grid(row=0, column=0)

        # место ввода "Книга"
        self.en_bookname = ttk.Entry(self, width=49, font='Arial 11')
        self.en_bookname.grid_configure(
            row=0, column=1, columnspan=50, pady=3, sticky='W')

        # надпись "Автор"
        self.lb_author2 = ttk.Label(self, text='Автор', font='Arial 11')
        self.lb_author2.grid(row=1, column=0)

        # место ввода "Автор"
        self.en_author2 = ttk.Entry(self, width=49, font='Arial 11')
        self.en_author2.grid_configure(
            row=1, column=1, columnspan=50, pady=3, sticky='W')

        # надпись "Дата сдачи"
        self.lb_dc = ttk.Label(self, text='Дата сдачи',
                               font='Arial 11').grid(row=2, column=0)

        # место ввода "Дата сдачи"
        self.en_dc = DateEntry(self, width=12, background='darkblue',
                               foreground='white', borderwidth=2, font='Arial 11', date_pattern='dd.MM.yyyy')
        self.en_dc.grid_configure(
            row=2, column=1, columnspan=15, pady=3, sticky='W')

        # надпись "Статус"
        self.lb_stat = ttk.Label(
            self, text='Статус', font='Arial 11').grid(row=3, column=0)

        # место ввода "Статус"
        self.en_stat = ttk.Combobox(
            self, values=['На руках', 'Просрочена', 'Сдана'], width=15, font='Arial 11')
        self.en_stat.grid_configure(
            row=3, column=1, columnspan=15, pady=3, sticky='W')

        # кнопка "Сохранить"
        self.btn_save = ttk.Button(self, text='Сохранить',
                                   command=lambda: threading.Thread(target=save_stat, args=[self, ]).start())
        self.btn_save.grid(row=4, column=1, padx=3, pady=3,
                           columnspan=50, sticky='E')
        try:
            self.iconbitmap(os.path.dirname(
            os.path.abspath(__file__)) + "/edit.ico")
        except:
            self.tk.call('wm', 'iconphoto', self._w, ImageTk.PhotoImage(Image.open("./edit.ico")))


# ---------------- Удалить книгу у читателя ----------------

# ================================ Окно с учётом книг ===================
class Book(tk.Toplevel):

    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, *kwargs)
        open_win.append(self)
        self.title("Учёт книг")  # Заголовок
        w = self.winfo_screenwidth() // 2 - 450  # ширина экрана
        h = self.winfo_screenheight() // 2 - 225  # высота экрана
        self.geometry('+{}+{}'.format(w - 100, h - 150))  # Размер
        self.resizable(False, False)  # Изменение размера окна
        self.protocol("WM_DELETE_WINDOW", lambda: self_main_book_null(self))

        self.focus_force()

        # ================================ Поиск ==============================
        self.frame_search1 = ttk.Frame(self)
        self.frame_search = ttk.Frame(self.frame_search1)

        self.search = Entry_Pl(self.frame_search, "Поиск")
        self.search.grid(row=0, column=0, padx=3, pady=3)

        self.bt_search = ttk.Button(self.frame_search, text='Найти',
                                    command=lambda: threading.Thread(target=search_book, args=[self, ]).start())
        self.bt_search.grid(row=0, column=1, padx=3, pady=3)

        self.bt_cancel = ttk.Button(
            self.frame_search, text='Отмена', command=lambda: update_search(self))
        self.bt_cancel.grid(row=0, column=2, padx=3, pady=3)

        self.frame_search.pack()
        self.frame_search1.pack(fill='x')

        self.bind('<Return>', lambda event: search_b_enter(self))

        # ================================  Таблица  ==========================

        self.note = ttk.Notebook(self)

        # =========================== Учебники ================================
        self.fr_watch_both = tk.Canvas(
            self, background='#e9e9e9', width=900, height=450)

        def fixed_map(option):
            return [elm for elm in style.map('Treeview', query_opt=option)
                    if elm[:2] != ('!disabled', '!selected') and elm[0] != '!disabled !selected']

        style = ttk.Style()
        style.map('Treeview', foreground=fixed_map(
            'foreground'), background=fixed_map('background'))

        # ttk.Style().configure("Treeview",fieldbackground="#e9e9e9")

        # Создание скроллбара
        self.scroll = ttk.Scrollbar(self.fr_watch_both)
        self.scroll.pack(side='right', fill='y')

        # Таблица
        self.book_table = MyTree(self.fr_watch_both, columns=(
            'AUT', 'COL'), height=21, yscrollcommand=self.scroll.set)
        # Подключение скроллбара
        self.scroll.config(orient='vertical', command=self.book_table.yview)
        self.book_table.column('#0', minwidth=230, width=230, anchor=tk.CENTER)
        self.book_table.column('AUT', minwidth=230,
                               width=230, anchor=tk.CENTER)
        self.book_table.column('COL', minwidth=230,
                               width=230, anchor=tk.CENTER)

        self.book_table.heading(
            "#0", command=lambda: sort_0(self.book_table, "#0", False))

        columns = self.book_table['columns']

        for col in columns:
            self.book_table.heading(col, text=col, command=lambda _col=col:
            sort(self.book_table, _col, False))

        self.book_table.heading('#0', text='Название')
        self.book_table.heading('AUT', text='Автор(ы)')
        self.book_table.heading('COL', text='Кол-во')

        self.progress = ttk.Progressbar(self.book_table, mode='indeterminate')

        self.schbook_menu = tk.Menu(self.book_table, tearoff=0)

        self.schbook_menu.add_command(
            label="Добавить книги", command=lambda: schbook(self))
        self.schbook_menu.add_command(
            label="Изменить кол-во книг", command=lambda: edit_schbooks(self))
        self.schbook_menu.add_command(label="Удалить книги",
                                      command=lambda: threading.Thread(target=del_schbook, args=[self, ]).start())

        self.book_table.pack(side='left')
        self.book_table.bind(
            '<Button-3>', lambda event: self.schbook_menu.post(event.x_root, event.y_root))
        self.fr_watch_both.pack(side='bottom', fill='both')

        threading.Thread(target=update_schbook, args=[self, ]).start()

        # ============================ Литература =============================

        self.fr_lit = tk.Canvas(
            self, background='#e9e9e9', width=900, height=450)

        # ttk.Style().configure("Treeview",fieldbackground="#e9e9e9")

        # Создание скроллбара
        self.scroll1 = ttk.Scrollbar(self.fr_lit)
        self.scroll1.pack(side='right', fill='y')

        # Таблица
        self.book_table1 = MyTree(self.fr_lit, columns=(
            'AUT', 'COL'), height=21, yscrollcommand=self.scroll1.set)
        # Подключение скроллбара
        self.scroll1.config(orient='vertical', command=self.book_table1.yview)
        self.book_table1.column(
            '#0', minwidth=230, width=230, anchor=tk.CENTER)
        self.book_table1.column('AUT', minwidth=230,
                                width=230, anchor=tk.CENTER)
        self.book_table1.column('COL', minwidth=230,
                                width=230, anchor=tk.CENTER)

        self.book_table1.heading(
            "#0", command=lambda: sort_0(self.book_table1, "#0", False))

        columns = self.book_table1['columns']

        for col in columns:
            self.book_table1.heading(col, text=col, command=lambda _col=col:
            sort(self.book_table1, _col, False))

        self.book_table1.heading('#0', text='Название')
        self.book_table1.heading('AUT', text='Автор(ы)')
        self.book_table1.heading('COL', text='Кол-во')

        self.progress1 = ttk.Progressbar(
            self.book_table1, mode='indeterminate')

        self.book_menu = tk.Menu(self.book_table1, tearoff=0)

        self.book_menu.add_command(
            label="Добавить книги", command=lambda: lit(self))
        self.book_menu.add_command(
            label="Изменить кол-во книг", command=lambda: edit_lit(self))
        self.book_menu.add_command(label="Удалить книги",
                                   command=lambda: threading.Thread(target=del_book, args=[self, ]).start())

        self.book_table1.pack(side='left')
        self.book_table1.bind(
            '<Button-3>', lambda event: self.book_menu.post(event.x_root, event.y_root))
        self.fr_lit.pack(side='bottom', fill='both')

        threading.Thread(target=update_book, args=[self, ]).start()

        self.note.add(self.fr_watch_both, text='Учебники')
        self.book_table.bind("<Double-Button-1>",
                             lambda event: threading.Thread(target=schbook_info, args=[self, ]).start())
        self.book_table1.bind("<Double-Button-1>",
                              lambda event: threading.Thread(target=lit_info, args=[self, ]).start())

        self.book_table.bind(
            '<KeyPress>', lambda event: event_handler_schbook(event, self))
        self.book_table1.bind(
            '<KeyPress>', lambda event: event_handler_lit(event, self))

        self.note.add(self.fr_lit, text='Литература')
        self.note.bind("<<NotebookTabChanged>>",
                       lambda event: book_bind_add(self))
        self.note.pack(fill='both')

        try:
            self.iconbitmap(os.path.dirname(
            os.path.abspath(__file__)) + "/books.ico")
        except:
            self.tk.call('wm', 'iconphoto', self._w, ImageTk.PhotoImage(Image.open("./books.ico")))


# !---------------- Добавить книгу ----------------
class Add_book(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, *kwargs)
        open_win.append(self)
        self.title("Добавить книги")  # Заголовок
        w = self.winfo_screenwidth() // 2 - 450  # ширина экрана
        h = self.winfo_screenheight() // 2 - 225  # высота экрана
        self.geometry('+{}+{}'.format(w + 300, h - 125))  # Размер
        self.resizable(False, False)  # Изменение размера окна
        self.protocol("WM_DELETE_WINDOW", lambda: self_book_null(self))
        self.attributes("-topmost", True)

        self.focus_force()

        self.lb_name = ttk.Label(self, text='Название', font='Arial 11')
        self.lb_aut = ttk.Label(self, text='Автор', font='Arial 11')
        self.lb_col = ttk.Label(self, text='Кол-во', font='Arial 11')
        # поле ввода "Название"
        self.en_name = ttk.Entry(self, width=35, font='Arial 11')
        # поле ввода "Автор"
        self.en_aut = ttk.Entry(self, width=35, font='Arial 11')
        # поле ввода "Кол-во"
        self.en_col = ttk.Entry(self, width=10, font='Arial 11')
        #
        # кнопка "Сохранить"
        self.save = ttk.Button(self, text='Сохранить',
                               command=lambda: threading.Thread(target=save_book, args=[self, ]).start())
        self.save_sch = ttk.Button(self, text='Сохранить',
                                   command=lambda: threading.Thread(target=save_schbook, args=[self, ]).start())
        try:
            self.iconbitmap(os.path.dirname(
            os.path.abspath(__file__)) + "/add.ico")
        except:
            self.tk.call('wm', 'iconphoto', self._w, ImageTk.PhotoImage(Image.open("./add.ico")))


# !---------------- Изменить книгу ----------------
class Edit_books(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, *kwargs)
        open_win.append(self)
        self.title("Редактировать книги")  # Заголовок
        w = self.winfo_screenwidth() // 2 - 450  # ширина экрана
        h = self.winfo_screenheight() // 2 - 225  # высота экрана
        self.geometry('+{}+{}'.format(w + 300, h - 125))  # Размер
        self.resizable(False, False)  # Изменение размера окна
        self.protocol("WM_DELETE_WINDOW", lambda: self_book_null(self))
        self.attributes("-topmost", True)

        self.focus_force()

        self.lb_name = ttk.Label(
            self, text='Название', font='Arial 11').grid(row=0, column=0)
        self.lb_aut = ttk.Label(
            self, text='Автор', font='Arial 11').grid(row=1, column=0)
        self.lb_col = ttk.Label(self, text='Кол-во',
                                font='Arial 11').grid(row=2, column=0)
        # поле ввода "Название"
        self.en_name = ttk.Entry(self, width=35, font='Arial 11')
        self.en_name.grid_configure(
            row=0, column=1, columnspan=35, pady=3, sticky='W')
        # поле ввода "Автор"
        self.en_aut = ttk.Entry(self, width=35, font='Arial 11')
        self.en_aut.grid_configure(
            row=1, column=1, columnspan=35, pady=3, sticky='W')
        # поле ввода "Кол-во"
        self.en_col = ttk.Entry(self, width=10, font='Arial 11')
        self.en_col.grid_configure(
            row=2, column=1, columnspan=35, pady=3, sticky='W')
        # кнопка "Сохранить"
        self.save = ttk.Button(self, text='Сохранить',
                               command=lambda: threading.Thread(target=edit_book, args=[self, ]).start())
        self.save_sch = ttk.Button(self, text='Сохранить',
                                   command=lambda: threading.Thread(target=edit_schbook, args=[self, ]).start())
        try:
            self.iconbitmap(os.path.dirname(
            os.path.abspath(__file__)) + "/edit.ico")
        except:
            self.tk.call('wm', 'iconphoto', self._w, ImageTk.PhotoImage(Image.open("./edit.ico")))


class INFO_Book(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, *kwargs)
        open_win.append(self)
        self.title("Информация о книге")  # Заголовок
        w = ((self.winfo_screenwidth() // 2) - 450)  # ширина экрана
        h = ((self.winfo_screenheight() // 2) - 225)  # высота экрана
        self.geometry('830x450+{}+{}'.format(w + 300, h - 125))  # Размер
        self.resizable(False, False)  # Изменение размера окна
        self.protocol("WM_DELETE_WINDOW", lambda: self_book_inf_null(self))

        self.focus_force()

        # ============================= Контейнер информации =================

        self.fr_info = ttk.Frame(self)

        self.fr_info.pack(side='top', fill='x')

        # ================================ Таблица ===========================

        self.frame = ttk.Frame(self)

        self.scroll = ttk.Scrollbar(self.frame)
        self.scroll.pack(side='right', fill='y')

        self.table = MyTree(self.frame, columns=('DB', 'PHONE', 'DI', 'DC', 'STAT', 'COL'), height=21,
                            yscrollcommand=self.scroll.set)
        # Подключение скроллбара
        self.scroll.config(orient='vertical', command=self.table.yview)
        self.table.column('#0', minwidth=160, width=160, anchor=tk.CENTER)
        self.table.column('DB', minwidth=100, width=100, anchor=tk.CENTER)
        self.table.column('PHONE', minwidth=150, width=150, anchor=tk.CENTER)
        self.table.column('DI', minwidth=100, width=100, anchor=tk.CENTER)
        self.table.column('DC', minwidth=100, width=100, anchor=tk.CENTER)
        self.table.column('STAT', minwidth=150, width=150, anchor=tk.CENTER)
        self.table.column('COL', minwidth=50, width=50, anchor=tk.CENTER)

        self.table.heading(
            "#0", command=lambda: sort_0(self.table, "#0", False))

        columns = self.table['columns']

        for col in columns:
            self.table.heading(col, text=col, command=lambda _col=col:
            sort(self.table, _col, False))

        self.table.heading('#0', text='ФИО')
        self.table.heading('DB', text='Дата рождения')
        self.table.heading('PHONE', text='Телефон')
        self.table.heading('DI', text='Дата взятия')
        self.table.heading('DC', text='Дата сдачи')
        self.table.heading('STAT', text='Статус')
        self.table.heading('COL', text='Кол-во')

        self.table.pack(side='left', fill='both')
        try:
            self.iconbitmap(os.path.dirname(
            os.path.abspath(__file__)) + "/book.ico")
        except:
            self.tk.call('wm', 'iconphoto', self._w, ImageTk.PhotoImage(Image.open("./book.ico")))


# ================================ Уведомления ================================
class Not(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, *kwargs)
        open_win.append(self)

        self.title("Электронный читательский билет - Уведомления")  # Заголовок
        self.geometry("770x450+0+0")  # Размер окна
        self.resizable(False, False)  # Изменение размера окна
        self.configure(background='#e9e9e9')  # Фон окна
        self.focus_force()
        self.protocol("WM_DELETE_WINDOW", lambda: self_not_close(self))
        self.attributes("-topmost", True)

        # Контейнер уведомлений
        self.fr_watch_both = ttk.Frame(self)
        self.fr_watch_both.configure(width=750, height=456)
        self.fr_watch_both.pack(side='left', fill='both')

        # Создание скроллбара
        self.scroll = ttk.Scrollbar(self.fr_watch_both)
        self.scroll.pack(side='right', fill='y')

        # Таблица
        self.table = ttk.Treeview(self.fr_watch_both, columns=('FIO', 'Phone', 'Book', 'CompleteDate', 'Status'),
                                  height=21, show='headings', yscrollcommand=self.scroll.set)

        # Подключение скролбара
        self.scroll.config(orient='vertical', command=self.table.yview)

        self.table.column('FIO', width=150, anchor=tk.CENTER)
        self.table.column('Phone', width=150, anchor=tk.CENTER)
        self.table.column('Book', width=150, anchor=tk.CENTER)
        self.table.column('CompleteDate', width=150, anchor=tk.CENTER)
        self.table.column('Status', width=150, anchor=tk.CENTER)

        self.table.heading('FIO', text='ФИО')
        self.table.heading('Phone', text='Телефон')
        self.table.heading('Book', text='Книга')
        self.table.heading('CompleteDate', text='Дата сдачи')
        self.table.heading('Status', text='Статус')

        self.table.pack(side='left')

        threading.Thread(target=update_not, args=[self, ]).start()

        self.progress = ttk.Progressbar(self.table, mode='indeterminate')

        # Иконка
        try:
            self.iconbitmap(os.path.dirname(
            os.path.abspath(__file__)) + "/bell.ico")
        except:
            self.tk.call('wm', 'iconphoto', self._w, ImageTk.PhotoImage(Image.open("./bell.ico")))


class Excel(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, *kwargs)
        open_win.append(self)
        w = self.winfo_screenwidth() // 2 - 450  # ширина экрана
        h = self.winfo_screenheight() // 2 - 225  # высота экрана
        self.title("Сохранить в Excel")  # Заголовок
        self.protocol("WM_DELETE_WINDOW", lambda: closed_excel(self))
        self.geometry('200x150+{}+{}'.format(w + 300, h))
        self.resizable(False, False)  # Изменение размера окна
        self.configure(background='#e9e9e9')  # Фон окна
        self.focus_force()

        self.lb_excel = ttk.Label(
            self, text='Вывести отчёт в Excel', font='Arial 11')
        self.lb_excel.pack(fill='x')

        self.frame = ttk.Frame(self)
        self.lb_date1 = ttk.Label(self.frame, text='С:', font='Arial 11')
        self.lb_date1.grid(row=0, column=0)

        self.en_date1 = DateEntry(self.frame, width=12, background='blue',
                                  foreground='white', borderwidth=2, font='Arial 11', date_pattern='dd.MM.yyyy')
        self.en_date1.grid_configure(row=0, column=1, pady=3)

        self.lb_date2 = ttk.Label(self.frame, text='До:', font='Arial 11')
        self.lb_date2.grid(row=1, column=0)

        self.en_date2 = DateEntry(self.frame, width=12, background='darkblue',
                                  foreground='white', borderwidth=2, font='Arial 11', date_pattern='dd.MM.yyyy')
        self.en_date2.grid_configure(row=1, column=1, pady=3)

        self.btn = ttk.Button(self.frame, text='Сохранить отчёт',
                              command=lambda: threading.Thread(target=lub_period_excel, args=[self, ]).start())
        self.btn.grid(row=2, column=1, padx=3, pady=3, sticky='E')

        self.frame.pack(fill='both')


class Spravka(tk.Toplevel):

    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, *kwargs)
        open_win.append(self)
        self.title("Справка")  # Заголовок
        w = self.winfo_screenwidth() // 2 - 450  # ширина экрана
        h = self.winfo_screenheight() // 2 - 225  # высота экрана
        self.geometry('840x450+{}+{}'.format(w - 100, h - 150))  # Размер
        self.resizable(False, False)  # Изменение размера окна
        self.protocol("WM_DELETE_WINDOW", lambda: self_main_book_null(self))

        self.focus_force()

        self.frame = tk.Canvas(self)

        self.scroll = ttk.Scrollbar(
            self.frame, orient='vertical', comman=self.frame.yview)

        self.text = ttk.Frame(self.frame)

        file = open(os.path.dirname(
            os.path.abspath(__file__)) + "/spr.txt", 'r')
        lines = file.readlines()
        row = 0
        for line in lines:
            if line[0] == '/':
                line = line[:-1]
                ttk.Label(self.text, text=line[1:], font=('Arial Black', 13)).grid(row=row, column=0, columnspan=9999,
                                                                                   sticky='w')
            elif (line[0] == '*') and (line[1] == '*'):
                line = line[:-1]
                ttk.Label(self.text, text=line[2:], font=('Arial Black', 12)).grid(row=row, column=0, columnspan=9999,
                                                                                   sticky='w')
            else:
                line = line[:-1]
                ttk.Label(self.text, text=line, font='Arial 11').grid(row=row, column=0, columnspan=9999,
                                                                      rowspan=1, sticky='w')
            row += 1
        self.frame.create_window(0, 0, anchor='nw', window=self.text)
        self.frame.update_idletasks()

        self.frame.configure(scrollregion=self.frame.bbox(
            'all'), yscrollcommand=self.scroll.set)
        self.frame.pack(fill='both', expand=True, side='left')
        self.scroll.pack(fill='y', side='right')

        # Иконка
        try:
            self.iconbitmap(os.path.dirname(
            os.path.abspath(__file__)) + "/ask.ico")
        except:
            self.tk.call('wm', 'iconphoto', self._w, ImageTk.PhotoImage(Image.open("./ask.ico")))


class Information(tk.Toplevel):

    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, *kwargs)
        open_win.append(self)
        self.title("Информация")  # Заголовок
        w = self.winfo_screenwidth() // 2 - 450  # ширина экрана
        h = self.winfo_screenheight() // 2 - 225  # высота экрана
        self.geometry('+{}+{}'.format(w - 100, h - 150))  # Размер
        self.resizable(False, False)  # Изменение размера окна
        self.protocol("WM_DELETE_WINDOW", lambda: self_main_inf_null(self))

        self.focus_force()

        self.frame_logo = ttk.Frame(self)

        logo = os.path.dirname(os.path.abspath(__file__)) + "/logo.png"
        photo = ImageTk.PhotoImage(Image.open(logo))
        labimg = ttk.Label(self.frame_logo, image=photo)
        labimg.image = photo
        labimg.grid(row=0, column=1, padx=5)

        prog_logo = os.path.dirname(
            os.path.abspath(__file__)) + "/prog_logo.png"
        photo_prog = ImageTk.PhotoImage(Image.open(prog_logo))
        prog_logo = ttk.Label(self.frame_logo, image=photo_prog)
        prog_logo.image = photo_prog
        prog_logo.grid(row=0, column=0, padx=5)

        self.fr_inf = ttk.Frame(self)

        file = open(os.path.dirname(os.path.abspath(
            __file__)) + "/inf.txt", 'r')
        lines = file.readlines()
        row = 0
        self.text = ttk.Frame(self.fr_inf)
        self.contacts = ttk.Frame(self.fr_inf)
        for line in lines:
            if line == lines[0]:
                line = line[2:]
                line = line[:-3]
                ttk.Label(self.text, text=line, font=(
                    'Arial Black', 15)).pack(side='top')
            elif line[0] == '/':
                line = line[1:]
                ttk.Label(self.text, text=line, font=(
                    'Arial Black', 12)).pack()
            elif (line[0] == '|') and (line[1] != '|'):
                line = line[1:]
                if (line[0] not in ('Ш', 'К')) and (line[:3] != 'Поч'):
                    ttk.Label(self.contacts, text=line, font=('Arial Black', 10)).grid(
                        row=0, column=0, columnspan=1)
                elif line[0] == 'Ш':
                    ttk.Label(self.contacts, text=line, font=('Arial Black', 10)).grid(row=1, column=0, columnspan=1,
                                                                                       padx=5)
                elif line[0] == 'К':
                    ttk.Label(self.contacts, text=line, font=('Arial Black', 10)).grid(
                        row=2, column=0, columnspan=1)
                elif line[0] + line[1] + line[2] == 'Поч':
                    ttk.Label(self.contacts, text=line, font=('Arial Black', 10)).grid(
                        row=3, column=0, columnspan=1)
            elif (line[0] + line[1] == '||') and (line[2] != '|'):
                line = line[2:]
                if (line[0] not in ('Ш', 'К')) and (line[:3] != 'Поч'):
                    ttk.Label(self.contacts, text=line, font=('Arial Black', 10)).grid(
                        row=0, column=2, columnspan=1)
                elif line[0] == 'Ш':
                    ttk.Label(self.contacts, text=line, font=('Arial Black', 10)).grid(row=1, column=2, columnspan=1,
                                                                                       padx=5)
                elif line[0] == 'К':
                    ttk.Label(self.contacts, text=line, font=('Arial Black', 10)).grid(
                        row=2, column=2, columnspan=1)
                elif line[0] + line[1] + line[2] == 'Поч':
                    ttk.Label(self.contacts, text=line, font=('Arial Black', 10)).grid(
                        row=3, column=2, columnspan=1)
            elif line[0] + line[1] + line[2] == '|||':
                line = line[3:]
                if (line[0] not in ('Ш', 'К')) and (line[:3] != 'Поч'):
                    ttk.Label(self.contacts, text=line, font=('Arial Black', 10)).grid(
                        row=0, column=4, columnspan=1)
                elif line[0] == 'Ш':
                    ttk.Label(self.contacts, text=line, font=('Arial Black', 10)).grid(row=1, column=4, columnspan=1,
                                                                                       padx=5)
                elif line[0] == 'К':
                    ttk.Label(self.contacts, text=line, font=('Arial Black', 10)).grid(
                        row=2, column=4, columnspan=1)
                elif line[0] + line[1] + line[2] == 'Поч':
                    ttk.Label(self.contacts, text=line, font=('Arial Black', 10)).grid(
                        row=3, column=4, columnspan=1)
            else:
                ttk.Label(self.contacts, text=line, font=('Arial Black', 12)).grid(
                    row=4, column=2, columnspan=1)

        self.bottom = ttk.Frame(self.fr_inf)
        ttk.Label(self.bottom, text='* На момент написания программы', font=('Arial Black', 8)).grid(row=0, column=0,
                                                                                                     columnspan=1)

        self.frame_logo.pack(side='top')
        self.text.pack()
        self.contacts.pack()
        self.bottom.pack(fill='x')
        self.fr_inf.pack(side='bottom', fill='both')

        # Иконка
        try:
            self.iconbitmap(os.path.dirname(
            os.path.abspath(__file__)) + "/ask.ico")
        except:
            self.tk.call('wm', 'iconphoto', self._w, ImageTk.PhotoImage(Image.open("./ask.ico")))
        global easter_egg
        if easter_egg == 3:
            threading.Thread(target=easter4, args=[self, ]).start()


class VK_api(tk.Toplevel):

    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, *kwargs)
        open_win.append(self)
        self.title("Vk_Api")  # Заголовок
        w = self.winfo_screenwidth() // 2 - 450  # ширина экрана
        h = self.winfo_screenheight() // 2 - 225  # высота экрана
        self.geometry('+{}+{}'.format(w - 100, h - 150))  # Размер
        self.resizable(False, False)  # Изменение размера окна
        self.focus_force()
        self.protocol("WM_DELETE_WINDOW", lambda: vk_closed(self))

        self.frame = ttk.Frame(self)
        self.frame.pack(fill='both')

        self.token_lb = ttk.Label(self.frame, text='Токен:', width=10)
        self.token_lb.grid(row=0, column=0, pady=5, padx=5)

        self.token_en = ttk.Entry(self.frame, width=20)
        self.token_en.grid(row=0, column=1, padx=5)

        self.id_lb = ttk.Label(self.frame, text='Id:', width=10)
        self.id_lb.grid(row=1, column=0, pady=5, padx=5)

        self.id_en = ttk.Entry(self.frame, width=20)
        self.id_en.grid(row=1, column=1, padx=5)

        self.btn = ttk.Button(self.frame, text='Сохранить',
                              command=lambda: vk_api_save(self))
        self.btn.grid(row=2, column=1, pady=5, padx=5, sticky='E')


class BUP_DB:
    def __init__(self):
        con = sqlite3.connect(os.path.dirname(
            os.path.abspath(__file__)) + "/LC.db")
        ask = fd.asksaveasfilename(filetypes=(
            ('SQL', '*.sql'),), defaultextension=".sql")
        if ask != '':
            with open(ask, 'w') as f:
                for line in con.iterdump():
                    f.write('%s\n' % line)
            con.close()
            messagebox.showinfo(
                'Backup DB', "Резервная копия БД выполнена успешно")


class Recov_DB:
    def __init__(self, gl_window):
        path = os.path.dirname(os.path.abspath(__file__)) + "/LC.db"
        os.remove(path)
        con = sqlite3.connect(os.path.dirname(
            os.path.abspath(__file__)) + "/LC.db")
        ask = fd.askopenfilename(filetypes=(
            ('SQL', '*.sql'),), defaultextension=".sql")
        if ask != '':
            f = open(ask, 'r')
            sql = f.read()
            cur = con.cursor()
            cur.executescript(sql)
            con.commit()
            con.close()
            messagebox.showinfo('Восстановление БД',
                                "Восстановление БД выполнено успешно")
            gl_window.event_generate('<<Key-43>>')


# ================================ Работа с БД ================================
def creat_table():
    conn = sqlite3.connect(os.path.dirname(
        os.path.abspath(__file__)) + "/LC.db")
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS `BOOK` (
	        `NAME`	TEXT NOT NULL,
	        `AUT`	TEXT NOT NULL,
	        `COL`	INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS `LC` (
	        `FIO`	TEXT NOT NULL,
	        `DB`	TEXT NOT NULL,
	        `PHONE`	TEXT NOT NULL,
	        `DI`	TEXT NOT NULL,
	        `DC`	TEXT NOT NULL,
	        `AUT`	TEXT NOT NULL,
	        `BOOK`	TEXT NOT NULL,
	        `STAT`	TEXT NOT NULL,
	        `COL`	INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS `PROFILE` (
	        `FIO`	TEXT NOT NULL,
        	`DB`	TEXT NOT NULL,
        	`CLA`	INTEGER NOT NULL,
        	`LIT`	TEXT NOT NULL,
        	`ADR`	TEXT NOT NULL,
        	`PHONE`	TEXT NOT NULL,
        	`CLIENT`	TEXT NOT NULL,
            `DREG`	TEXT NOT NULL,
	        `VK_ID`	TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS `SCHBOOK` (
        	`NAME`	TEXT NOT NULL,
        	`AUT`	TEXT NOT NULL,
        	`COL`	INTEGER NOT NULL,
        	`OBJ`	TEXT NOT NULL
        );
    """
    )
    conn.commit()


def update_not(self):
    x = datetime.date.today().isoformat()  # Текущая дата в ISO формате
    # Подключение к БД
    conn = sqlite3.connect(os.path.dirname(
        os.path.abspath(__file__)) + "/LC.db")
    cur = conn.cursor()
    cur.execute('SELECT * FROM LC')  # Получение всех значений из таблицы LC БД
    rows = cur.fetchall()
    for _ in rows:
        cur.execute("UPDATE LC SET STAT = 'Просрочена' WHERE DC<(?) AND STAT = 'На руках'",
                    (x,))  # Обновление статуса если время сдачи < текущего
        conn.commit()
    cur.execute(
        "SELECT FIO, PHONE, BOOK, DC, STAT FROM LC WHERE STAT = 'Просрочена'")  # Выборка просроченных книг из БД
    rows = cur.fetchall()
    for row in rows:
        dc = datetime.datetime.strptime(row[3], '%Y-%m-%d')
        dc = dc.strftime('%d.%m.%Y')
        row = (row[0], row[1], row[2], dc, row[4])
        self.table.insert("", tk.END, values=row)  # Вывод в таблицу


def update_main(self):
    threading.Thread(target=progressbar_start, args=[self, ]).start()
    self.table.delete(*self.table.get_children())
    conn = sqlite3.connect(os.path.dirname(
        os.path.abspath(__file__)) + "/LC.db")
    cur = conn.cursor()

    # Вывовд всех учеников
    cur.execute("SELECT * FROM PROFILE")
    rows = cur.fetchall()
    self.uch = self.table.insert("", tk.END, text='Ученик')
    self.teach = self.table.insert("", tk.END, text='Учитель')
    self.dp = self.table.insert("", tk.END, text="Другой посетитель")
    for row in rows:
        if "Ученик" in row:
            db = row[1]
            if len(db) == 10:
                db = datetime.datetime.strptime(db, '%Y-%m-%d')
                db = db.strftime('%d.%m.%Y')
            row = (row[0], db, row[2], row[3], row[4], row[5])
            self.table.insert(self.uch, tk.END, text=row[0], values=row[1:])
        elif "Учитель" in row:
            db = row[1]
            if len(db) == 10:
                db = datetime.datetime.strptime(db, '%Y-%m-%d')
                db = db.strftime('%d.%m.%Y')
            row = (row[0], db, row[2], row[3], row[4], row[5])
            self.table.insert(self.teach, tk.END, text=row[0], values=row[1:])
        elif "Другой посетитель":
            db = row[1]
            if len(db) == 10:
                db = datetime.datetime.strptime(db, '%Y-%m-%d')
                db = db.strftime('%d.%m.%Y')
            row = (row[0], db, row[2], row[3], row[4], row[5])
            self.table.insert(self.dp, tk.END, text=row[0], values=row[1:])
    threading.Thread(target=progressbar_stop, args=[self, ]).start()


def update_schbook(self):
    threading.Thread(target=progressbar_start, args=[self, ]).start()
    global obj
    self.book_table.delete(*self.book_table.get_children())
    conn = sqlite3.connect(os.path.dirname(
        os.path.abspath(__file__)) + "/LC.db")
    cur = conn.cursor()
    self.obj = {}
    for less in obj:
        x = self.book_table.insert('', tk.END, text=less)
        self.obj[less] = x
        cur.execute(
            "SELECT NAME, AUT, COL FROM SCHBOOK WHERE OBJ = (?)", (less,))
        rows = cur.fetchall()
        col = 0
        for row in rows:
            cur.execute(
                "SELECT COL FROM LC WHERE BOOK = (?) AND AUT = (?) AND (STAT = 'На руках' OR STAT = 'Просрочена')",
                (row[0], row[1]))
            lines = cur.fetchall()
            if lines:
                for line in lines:
                    col += int(line[0])
                res = (row[0], row[1], row[2] - col)
                self.book_table.insert(x, tk.END, text=res[0], values=res[1:])
            else:
                self.book_table.insert(x, tk.END, text=row[0], values=row[1:])
    threading.Thread(target=progressbar_stop, args=[self, ]).start()


def update_book(self):
    threading.Thread(target=progressbar_start1, args=[self, ]).start()
    self.book_table1.delete(*self.book_table1.get_children())
    conn = sqlite3.connect(os.path.dirname(
        os.path.abspath(__file__)) + "/LC.db")
    cur = conn.cursor()

    # Вывовд всех учеников
    cur.execute("SELECT * FROM BOOK")
    rows = cur.fetchall()
    for row in rows:
        cur.execute("SELECT COl FROM LC WHERE BOOK = (?) AND AUT = (?) AND (STAT = 'На руках' OR STAT = 'Просрочена')",
                    (row[0], row[1]))
        lines = cur.fetchall()
        col = 0
        if lines:
            for line in lines:
                col += int(line[0])
            res = (row[0], row[1], row[2] - col)
            self.book_table1.insert('', tk.END, text=res[0], values=res[1:])
        else:
            self.book_table1.insert('', tk.END, text=row[0], values=row[1:])
    threading.Thread(target=progressbar_stop1, args=[self, ]).start()


def update_search(self):
    threading.Thread(target=update_book, args=[self, ]).start()
    threading.Thread(target=update_schbook, args=[self, ]).start()


def update_info(root):
    threading.Thread(target=progressbar_start, args=[root, ]).start()
    conn = sqlite3.connect(os.path.dirname(
        os.path.abspath(__file__)) + "/LC.db")
    cur = conn.cursor()

    root.fio = ttk.Label(root.frame, text=text, font='Arial 15').pack()
    root.db = ttk.Label(root.frame, text="Дата рождения: " +
                                         values[0], font='Arial 12').pack()
    if values[1] == '' and values[2] == '':
        root.adr = ttk.Label(root.frame, text='Адрес: ' +
                                              values[3], font='Arial 12').pack()
        root.phone = ttk.Label(
            root.frame, text='Телефон: ' + values[4], font='Arial 12').pack()
    else:
        root.clas = ttk.Label(root.frame, text='Класс: ' +
                                               values[1] + ' ' + values[2], font='Arial 12').pack()
        root.adr = ttk.Label(root.frame, text='Адрес: ' +
                                              values[3], font='Arial 12').pack()
        root.phone = ttk.Label(
            root.frame, text='Телефон: ' + values[4], font='Arial 12').pack()

    if len(values[0]) == 10:
        db = datetime.datetime.strptime(values[0], '%d.%m.%Y')  # Парсит дату
        db = db.strftime('%Y-%m-%d')  # Переводит дату в другой формат
    else:
        db = values[0]

    # Вывовд всех учеников
    cur.execute(
        "SELECT BOOK, AUT, STAT, COL FROM LC WHERE FIO=(?) AND DB=(?) AND PHONE=(?)", (text, db, values[4]))
    rows = cur.fetchall()
    for row in rows:
        root.info_table.insert('', tk.END, text=row[0], values=row[1:])

    root.title("Профиль: {}".format(text))  # Заголовок
    root.fr_watch_both.pack(side='bottom', fill='both')
    threading.Thread(target=progressbar_stop, args=[root, ]).start()


def info(self):
    global self_main
    global text
    global values
    selected_item = self.table.selection()
    # Получаем значения в выделенной строке
    values = self.table.item(selected_item, option="values")
    text = self.table.item(selected_item, option="text")
    if text not in ('Ученик', 'Учитель', 'Другой посетитель'):
        if self_main == 'close':
            if text:
                self_main = self
                root = INFO()
                threading.Thread(target=update_info, args=[root, ]).start()


def add_profile(self):
    global self_main
    if self_main == 'close':
        self_main = self
        Add_profile()


def save_stud2(self):
    global self_main
    null = ''
    fio = self.en_fio2.get()  # Присваивание переменным значение из полей ввода
    clas = self.en_class2.get()
    lit = self.en_lit2.get()
    phone = self.en_phone2.get()
    db = self.en_db2.get()
    try:
        db = datetime.datetime.strptime(db, '%d.%m.%Y')
        db = db.strftime('%Y-%m-%d')
    except:
        messagebox.showerror(
            'ОШИБКА!!!', 'Данные в поле "Дата рождения" имеют неверный формат', parent=self)
        return 0
    adr = self.en_adr2.get()
    client = self.en_client.get()
    dreg = datetime.date.today()
    line = [fio, db, clas, lit, adr, phone, client, dreg, '']
    if null in (fio, db, phone, adr):  # Проверка на пустоту полей
        messagebox.showerror(
            'ОШИБКА!!!', 'Ошибка! Поля не могут быть пустыми!', parent=self)  # Вывод ошибки
    else:
        # Занесение данных в базу данных
        conn = sqlite3.connect(os.path.dirname(
            os.path.abspath(__file__)) + "/LC.db")
        con_cur = conn.cursor()
        con_cur.execute('INSERT INTO PROFILE VALUES (?,?,?,?,?,?,?,?,?)', line)
        conn.commit()
        messagebox.showinfo('Успех!', 'Данные сохранены!', parent=self)
        prof = self_main.uch if client == 'Ученик' else self_main.teach if client == 'Учитель' else self_main.dp
        self_main.table.insert(prof, 'end', text=line[0], values=[datetime.datetime.strptime(line[1], '%Y-%m-%d').strftime('%d.%m.%Y')]+line[2:7])


def edit_profile(self):
    global self_main
    global text
    global values
    if self_main == 'close':
        self_main = self
        selected_item = self_main.table.selection()
        # Получаем значения в выделенной строке
        values = self_main.table.item(selected_item, option="values")
        text = self_main.table.item(selected_item, option="text")
        root = Edit_profile()
        root.en_fio2.insert(0, text)
        root.en_db2.insert(0, values[0])
        root.en_class2.insert(0, values[1])
        root.en_lit2.insert(0, values[2])
        root.en_adr2.insert(0, values[3])
        root.en_phone2.insert(0, values[4])


def edit_stud(self):
    global self_main
    global text
    global values
    null = ''
    fio = self.en_fio2.get()
    clas = self.en_class2.get()
    lit = self.en_lit2.get()
    phone = self.en_phone2.get()
    db = self.en_db2.get()
    try:
        db = datetime.datetime.strptime(db, '%d.%m.%Y')
        db = db.strftime('%Y-%m-%d')
    except:
        messagebox.showerror(
            'ОШИБКА!!!', 'Данные в поле "Дата рождения" имеют неверный формат', parent=self)
        return 0
    adr = self.en_adr2.get()
    fio2 = text
    db2 = datetime.datetime.strptime(values[0], '%d.%m.%Y')
    db2 = db2.strftime('%Y-%m-%d')
    phone2 = values[4]
    line = [fio, db, clas, lit, adr, phone, fio2, db2, phone2]

    if null in (fio, db, phone, adr):  # Проверка на пустоту полей
        messagebox.showerror(
            'ОШИБКА!!!', 'Ошибка! Поля не могут быть пустыми!', parent=self)  # Вывод ошибки
        self.focus_force()
    else:
        # Занесение данных в базу данных
        conn = sqlite3.connect(os.path.dirname(
            os.path.abspath(__file__)) + "/LC.db")
        con_cur = conn.cursor()
        con_cur.execute(
            'UPDATE PROFILE SET FIO = (?), DB = (?), CLA = (?), LIT = (?), ADR = (?), PHONE = (?) WHERE FIO = (?) AND DB = (?) AND PHONE = (?)',
            line)
        conn.commit()
        messagebox.showinfo('Успех!', 'Данные сохранены!', parent=self)
        self_main.table.item(self_main.table.selection(), text=line[0], values=[datetime.datetime.strptime(line[1], '%Y-%m-%d').strftime('%d.%m.%Y')]+line[2:6])


def del_profile(self):
    selected_item = self.table.selection()
    values = self.table.item(selected_item, option="values")
    text = self.table.item(selected_item, option="text")
    ask = messagebox.askyesno(
        'Удалить', 'Вы точно хотите удалить читателя {}?'.format(text), parent=self)

    if ask == True:
        self.focus_force()
        if len(values[0]) == 10:
            db = datetime.datetime.strptime(values[0], '%d.%m.%Y')
            db = db.strftime('%Y-%m-%d')
        else:
            db = values[0]
        line = (text, db, values[4])
        # Занесение данных в базу данных
        conn = sqlite3.connect(os.path.dirname(
            os.path.abspath(__file__)) + "/LC.db")
        con_cur = conn.cursor()
        con_cur.execute(
            'DELETE FROM PROFILE WHERE FIO = (?) AND DB = (?) AND PHONE = (?)', line)
        con_cur.execute(
            'DELETE FROM LC WHERE FIO = (?) AND DB = (?) AND PHONE = (?)', line)
        conn.commit()
        self.table.delete(selected_item)


def add_book(self):
    global self_info
    if self_info == 'close':
        self_info = self
        Add_lc()


def save_lc2(self):
    global self_info
    global text
    global values
    null = ''
    fio = text

    if len(values[0]) == 10:
        db = datetime.datetime.strptime(values[0], '%d.%m.%Y')
        db = db.strftime('%Y-%m-%d')
    else:
        db = values[0]

    phone = values[4]
    di = datetime.date.today()  # Присвоение текущей даты
    dc = di + timedelta(days=14)  # Определение срока сдачи книги
    book = self.en_bookname.get()  # Присваивание переменным значение из полей ввода
    aut = self.en_author2.get()
    stat = "На руках"
    col = self.en_col.get()
    if col == '':
        col = 1
    line = [fio, db, phone, di, dc, aut, book, stat, col]
    if null in (book, aut, col):  # Проверка на пустоту полей
        messagebox.showerror(
            'ОШИБКА!!!', 'Ошибка! Поля не могут быть пустыми!', parent=self)  # Вывод ошибки
    else:
        # Занесение данных в базу данных
        conn = sqlite3.connect(os.path.dirname(
            os.path.abspath(__file__)) + "/LC.db")
        con_cur = conn.cursor()
        con_cur.execute('INSERT INTO LC VALUES (?,?,?,?,?,?,?,?,?)', line)
        conn.commit()
        messagebox.showinfo('Успех!', 'Данные сохранены!', parent=self)
        self_info.info_table.insert('', 'end', text=line[-3], values=[line[-4], line[-2], line[-1]])


def edit_lc(self):
    global self_info
    global text
    global values

    if self_info == 'close':
        self_info = self
        selected_item = self_info.info_table.selection()
        # Получаем значения в выделенной строке
        values1 = self_info.info_table.item(selected_item, option="values")
        text1 = self_info.info_table.item(selected_item, option="text")
        if len(values[0]) == 10:
            db = datetime.datetime.strptime(values[0], '%d.%m.%Y')
            db = db.strftime('%Y-%m-%d')
        else:
            db = values[0]
        values2 = (db, values[1], values[2], values[3], values[4])
        root = Edit_lc()
        root.en_bookname.insert(0, text1)
        root.en_author2.insert(0, values1[0])
        root.en_stat.insert(0, values1[1])
        line = (text1, values1[0], values1[1], text, values2[0], values2[4])
        # Занесение данных в базу данных
        conn = sqlite3.connect(os.path.dirname(
            os.path.abspath(__file__)) + "/LC.db")
        con_cur = conn.cursor()
        con_cur.execute(
            'SELECT DC FROM LC WHERE BOOK = (?) AND AUT = (?) AND STAT = (?) AND FIO = (?) AND DB = (?) AND PHONE = (?)',
            line)
        rows = con_cur.fetchall()
        rows = datetime.datetime.strptime(rows[0][0], '%Y-%m-%d')
        row = rows.strftime('%d.%m.%Y')
        root.en_dc.set_date(row)
        conn.commit()


def save_stat(self):
    global self_info
    global text
    global values
    null = ''
    selected_item = self_info.info_table.selection()
    # Получаем значения в выделенной строке
    values1 = self_info.info_table.item(selected_item, option="values")
    text1 = self_info.info_table.item(selected_item, option="text")
    name = self.en_bookname.get()
    aut = self.en_author2.get()
    stat = self.en_stat.get()
    if len(values[0]) == 10:
        db = datetime.datetime.strptime(values[0], '%d.%m.%Y')
        db = db.strftime('%Y-%m-%d')
    else:
        db = values[0]
    dc = self.en_dc.get()
    dc = datetime.datetime.strptime(dc, '%d.%m.%Y')
    dc = dc.strftime('%Y-%m-%d')
    line = [name, aut, stat, dc, text, db,
            values[4], text1, values1[0], values1[1], values1[2]]
    if null in (name, aut, stat):  # Проверка на пустоту полей
        messagebox.showerror(
            'ОШИБКА!!!', 'Ошибка! Поля не могут быть пустыми!', parent=self)  # Вывод ошибки
    else:
        # Занесение данных в базу данных
        conn = sqlite3.connect(os.path.dirname(
            os.path.abspath(__file__)) + "/LC.db")
        con_cur = conn.cursor()
        con_cur.execute(
            'UPDATE LC SET BOOK=(?), AUT=(?), STAT=(?), DC=(?) WHERE FIO=(?) AND DB=(?) AND PHONE=(?) AND BOOK=(?) AND AUT=(?) AND STAT=(?) AND COL=(?)',
            line)
        conn.commit()

    messagebox.showinfo('Успех!', 'Данные сохранены!', parent=self)
    self_info.info_table.item(selected_item, text=line[0], values=line[1:3]+[line[-1]])


def delete_lc(self):
    global text
    global values
    selected_item = self.info_table.selection()
    # Получаем значения в выделенной строке
    values1 = self.info_table.item(selected_item, option="values")
    text1 = self.info_table.item(selected_item, option="text")
    ask = messagebox.askyesno(
        'Удалить', 'Вы точно хотите удалить книгу: {}?'.format(text1), parent=self)

    if ask:
        if len(values[0]) == 10:
            db = datetime.datetime.strptime(values[0], '%d.%m.%Y')
            db = db.strftime('%Y-%m-%d')
        else:
            db = values[0]
        line = (text, db, values[4], text1, values1[0], values1[1])
        # Занесение данных в базу данных
        conn = sqlite3.connect(os.path.dirname(
            os.path.abspath(__file__)) + "/LC.db")
        con_cur = conn.cursor()
        con_cur.execute(
            'DELETE FROM LC WHERE FIO = (?) AND DB = (?) AND PHONE = (?) AND BOOK = (?) AND AUT = (?) AND STAT = (?)',
            line)
        conn.commit()
        self.info_table.delete(selected_item)


def search(self):
    search = self.search.get()
    if search != 'Поиск':
        self.table.delete(*self.table.get_children())
        if len(search) > 1:
            search = search.lower().title()
        self.search.delete('0', 'end')
        conn = sqlite3.connect(os.path.dirname(
            os.path.abspath(__file__)) + "/LC.db")
        cur = conn.cursor()

        # Вывовд всех учеников
        cur.execute(
            "SELECT * FROM PROFILE WHERE FIO LIKE '%{0}%' OR '{0}%' OR '%{0}'".format(search))
        rows = cur.fetchall()
        for row in rows:
            db = row[1]
            if len(db) == 10:
                db = datetime.datetime.strptime(db, '%Y-%m-%d')
                db = db.strftime('%d.%m.%Y')
            row = (row[0], db, row[2], row[3], row[4], row[5])
            self.table.insert("", tk.END, text=row[0], values=row[1:])


def search_book(self):
    self.book_table.delete(*self.book_table.get_children())
    self.book_table1.delete(*self.book_table1.get_children())
    search = self.search.get()
    if search[0] != '"':
        if len(search) > 1:
            search = search.lower().title()
    self.search.delete('0', 'end')
    conn = sqlite3.connect(os.path.dirname(
        os.path.abspath(__file__)) + "/LC.db")
    cur = conn.cursor()

    # Вывовд всех учеников
    cur.execute(
        "SELECT * FROM BOOK WHERE (NAME LIKE '%{0}%' OR '{0}%' OR '%{0}') OR (AUT LIKE '%{0}%' OR '{0}%' OR '%{0}')".format(
            search))
    rows = cur.fetchall()
    for row in rows:
        cur.execute(
            "SELECT COUNT(*) FROM LC WHERE BOOK = (?) AND AUT = (?) AND (STAT = 'На руках' OR STAT = 'Просрочена')",
            (row[0], row[1]))
        line = cur.fetchall()
        res = (row[0], row[1], row[2] - line[0][0])
        self.book_table1.insert("", tk.END, text=res[0], values=res[1:])
    cur.execute(
        "SELECT * FROM SCHBOOK WHERE (NAME LIKE '%{0}%' OR '{0}%' OR '%{0}') OR (AUT LIKE '%{0}%' OR '{0}%' OR '%{0}')".format(
            search))
    rows = cur.fetchall()
    for row in rows:
        cur.execute(
            "SELECT COUNT(*) FROM LC WHERE BOOK = (?) AND AUT = (?) AND (STAT = 'На руках' OR STAT = 'Просрочена')",
            (row[0], row[1]))
        line = cur.fetchall()
        res = (row[0], row[1], row[2] - line[0][0])
        self.book_table.insert("", tk.END, text=res[0], values=res[1:])


def search_enter(self):
    if self.search.get() != 'Поиск':
        threading.Thread(target=search, args=[self, ]).start()
    else:
        threading.Thread(target=update_main, args=[self, ]).start()


def search_b_enter(self):
    if self.search.get() != 'Поиск':
        threading.Thread(target=search_book, args=[self, ]).start()
    else:
        threading.Thread(target=update_search, args=[self, ]).start()


def book(self):
    global self_book
    if self_book == 'close':
        self_book = self
        Add_book()


def save_book(self):
    global self_book
    null = ''
    name = self.en_name.get()
    aut = self.en_aut.get()
    col = self.en_col.get()
    line = (name, aut, col)
    if null in (name, aut, col):  # Проверка на пустоту полей
        messagebox.showerror(
            'ОШИБКА!!!', 'Ошибка! Поля не могут быть пустыми!', parent=self)  # Вывод ошибки
    else:
        # Занесение данных в базу данных
        conn = sqlite3.connect(os.path.dirname(
            os.path.abspath(__file__)) + "/LC.db")
        con_cur = conn.cursor()
        con_cur.execute('INSERT INTO BOOK VALUES (?,?,?)', line)
        conn.commit()
        messagebox.showinfo('Успех!', 'Данные сохранены!', parent=self)
        self_book.book_table1.insert('', 'end', text=line[0], values=line[1:3])



def edit_lit(self):
    global self_book
    if self_book == 'close':
        self_book = self
        root = Edit_books()
        selected_item = self_book.book_table1.selection()
        # Получаем значения в выделенной строке
        values1 = self_book.book_table1.item(selected_item, option="values")
        text1 = self_book.book_table1.item(selected_item, option="text")
        # Занесение данных в базу данных
        conn = sqlite3.connect(os.path.dirname(
            os.path.abspath(__file__)) + "/LC.db")
        con_cur = conn.cursor()
        line = (text1, values1[0])
        con_cur.execute(
            'SELECT COL FROM BOOK WHERE NAME=(?) AND AUT=(?)', line)
        col = con_cur.fetchall()
        root.en_name.insert(0, text1)
        root.en_aut.insert(0, values1[0])
        root.en_col.insert(0, col)
        root.save.grid(row=3, column=1, padx=3, pady=3,
                       columnspan=35, sticky='E')


def edit_schbooks(self):
    global self_book
    if self_book == 'close':
        self_book = self
        root = Edit_books()
        selected_item = self_book.book_table.selection()
        # Получаем значения в выделенной строке
        values1 = self_book.book_table.item(selected_item, option="values")
        text1 = self_book.book_table.item(selected_item, option="text")
        # Занесение данных в базу данных
        conn = sqlite3.connect(os.path.dirname(
            os.path.abspath(__file__)) + "/LC.db")
        con_cur = conn.cursor()
        line = (text1, values1[0])
        con_cur.execute(
            'SELECT COL FROM SCHBOOK WHERE NAME=(?) AND AUT=(?)', line)
        col = con_cur.fetchall()
        root.en_name.insert(0, text1)
        root.en_aut.insert(0, values1[0])
        root.en_col.insert(0, col)
        root.save_sch.grid(row=3, column=1, padx=3, pady=3,
                           columnspan=35, sticky='E')


def edit_book(self):
    global self_book
    selected_item = self_book.book_table1.selection()
    # Получаем значения в выделенной строке
    values1 = self_book.book_table1.item(selected_item, option="values")
    text1 = self_book.book_table1.item(selected_item, option="text")

    # Занесение данных в базу данных
    conn = sqlite3.connect(os.path.dirname(
        os.path.abspath(__file__)) + "/LC.db")
    con_cur = conn.cursor()
    con_cur.execute(
        'SELECT COL FROM BOOK WHERE NAME = (?) AND AUT = (?)', (text1, values1[0]))
    f = con_cur.fetchall()

    null = ''
    name = self.en_name.get()
    aut = self.en_aut.get()
    col = self.en_col.get()
    line = (name, aut, col, text1, values1[0], f[0][0])
    if null in (name, aut, col):  # Проверка на пустоту полей
        messagebox.showerror(
            'ОШИБКА!!!', 'Ошибка! Поля не могут быть пустыми!', parent=self)  # Вывод ошибки
    else:
        con_cur = conn.cursor()
        con_cur.execute(
            'UPDATE BOOK SET NAME=(?), AUT=(?), COL=(?) WHERE NAME=(?) AND AUT=(?) AND COL=(?)', line)
        conn.commit()
        messagebox.showinfo('Успех!', 'Данные сохранены!', parent=self)
        self_book.book_table1.item(selected_item, text=line[0], values=line[1:3])



def edit_schbook(self):
    global self_book
    selected_item = self_book.book_table.selection()
    # Получаем значения в выделенной строке
    values1 = self_book.book_table.item(selected_item, option="values")
    text1 = self_book.book_table.item(selected_item, option="text")

    # Занесение данных в базу данных
    conn = sqlite3.connect(os.path.dirname(
        os.path.abspath(__file__)) + "/LC.db")
    con_cur = conn.cursor()

    con_cur.execute(
        'SELECT COL FROM SCHBOOK WHERE NAME = (?) AND AUT = (?)', (text1, values1[0]))
    f = con_cur.fetchall()
    null = ''
    name = self.en_name.get()
    aut = self.en_aut.get()
    col = self.en_col.get()
    line = (name, aut, col, text1, values1[0], f[0][0])
    if null in (name, aut, col):  # Проверка на пустоту полей
        messagebox.showerror(
            'ОШИБКА!!!', 'Ошибка! Поля не могут быть пустыми!', parent=self)  # Вывод ошибки
    else:
        con_cur = conn.cursor()
        con_cur.execute(
            'UPDATE SCHBOOK SET NAME=(?), AUT=(?), COL=(?) WHERE NAME=(?) AND AUT=(?) AND COL=(?)', line)
        conn.commit()
        messagebox.showinfo('Успех!', 'Данные сохранены!', parent=self)
        self_book.book_table.item(selected_item, text=line[0], values=line[1:3])


def del_book(self):
    selected_item = self.book_table1.selection()
    # Получаем значения в выделенной строке
    values1 = self.book_table1.item(selected_item, option="values")
    text1 = self.book_table1.item(selected_item, option="text")
    ask = messagebox.askyesno(
        'Удалить', 'Вы точно хотите удалить книгу: {}?'.format(text1), parent=self)

    # Занесение данных в базу данных
    conn = sqlite3.connect(os.path.dirname(
        os.path.abspath(__file__)) + "/LC.db")
    con_cur = conn.cursor()

    if ask == True:
        line = (text1, values1[0], values1[1])
        con_cur.execute(
            'DELETE FROM BOOK WHERE NAME = (?) AND AUT = (?) AND COL = (?)', line)
        conn.commit()
        self.book_table1.delete(selected_item)


def del_schbook(self):
    selected_item = self.book_table.selection()
    # Получаем значения в выделенной строке
    values1 = self.book_table.item(selected_item, option="values")
    text1 = self.book_table.item(selected_item, option="text")
    ask = messagebox.askyesno(
        'Удалить', 'Вы точно хотите удалить книгу: {}?'.format(text1), parent=self)

    # Занесение данных в базу данных
    conn = sqlite3.connect(os.path.dirname(
        os.path.abspath(__file__)) + "/LC.db")
    con_cur = conn.cursor()

    if ask == True:
        line = (text1, values1[0], values1[1])
        con_cur.execute(
            'DELETE FROM SCHBOOK WHERE NAME = (?) AND AUT = (?) AND COL = (?)', line)
        conn.commit()
        self.book_table.delete(selected_item)


def save_schbook(self):
    global self_book
    null = ''
    name = self.en_name.get()
    aut = self.en_aut.get()
    col = self.en_col.get()
    less = self.en_less.get()
    line = (name, aut, col, less)
    if null in (name, aut, col):  # Проверка на пустоту полей
        messagebox.showerror(
            'ОШИБКА!!!', 'Ошибка! Поля не могут быть пустыми!', parent=self)  # Вывод ошибки
    else:
        # Занесение данных в базу данных
        conn = sqlite3.connect(os.path.dirname(
            os.path.abspath(__file__)) + "/LC.db")
        con_cur = conn.cursor()
        con_cur.execute('INSERT INTO SCHBOOK VALUES (?,?,?,?)', line)
        conn.commit()
        messagebox.showinfo('Успех!', 'Данные сохранены!', parent=self)
        self_book.book_table.insert(self_book.obj[line[-1]] , 'end', text=line[0], values=line[1:3])



def schbook(self):
    global obj
    global self_book
    self_book = self
    self = Add_book()
    w = ((self.winfo_screenwidth() // 2) - 450)  # ширина экрана
    h = ((self.winfo_screenheight() // 2) - 225)  # высота экрана
    self.geometry('+{}+{}'.format(w + 300, h - 125))  # Размер
    self.lb_name.grid(row=0, column=0)
    self.lb_aut.grid(row=1, column=0)
    self.lb_col.grid(row=2, column=0)
    self.en_name.grid_configure(
        row=0, column=1, columnspan=35, pady=3, sticky='W')
    self.en_aut.grid_configure(
        row=1, column=1, columnspan=35, pady=3, sticky='W')
    self.en_col.grid_configure(
        row=2, column=1, columnspan=35, pady=3, sticky='W')
    self.lb_less = ttk.Label(
        self, text='Урок', font='Arial 11').grid(row=3, column=0)
    self.en_less = ttk.Combobox(self, values=obj, width=17, font='Arial 11')
    self.en_less.grid_configure(
        row=3, column=1, columnspan=35, pady=3, sticky='W')
    self.save_sch.grid(row=4, column=1, padx=3, pady=3,
                       columnspan=40, sticky='E')


def lit(self):
    global self_book
    self_book = self
    self = Add_book()
    w = ((self.winfo_screenwidth() // 2) - 450)  # ширина экрана
    h = ((self.winfo_screenheight() // 2) - 225)  # высота экрана
    self.geometry('+{}+{}'.format(w + 300, h - 125))  # Размер
    self.lb_name.grid(row=0, column=0)
    self.lb_aut.grid(row=1, column=0)
    self.lb_col.grid(row=2, column=0)
    self.en_name.grid_configure(
        row=0, column=1, columnspan=35, pady=3, sticky='W')
    self.en_aut.grid_configure(
        row=1, column=1, columnspan=35, pady=3, sticky='W')
    self.en_col.grid_configure(
        row=2, column=1, columnspan=35, pady=3, sticky='W')
    self.save.grid(row=3, column=1, padx=3, pady=3, columnspan=35, sticky='E')


def self_main_null(self):
    global self_main
    open_win.remove(self)
    self_main = 'close'
    self.destroy()


def self_info_null(self):
    global self_info
    open_win.remove(self)
    self_info = 'close'
    self.destroy()


def self_book_null(self):
    global self_book
    open_win.remove(self)
    self_book = 'close'
    self.destroy()


def self_book_inf_null(self):
    global self_book_info
    open_win.remove(self)
    self_book_info = 'close'
    self.destroy()


def self_main_book_null(self):
    global book_add
    global self_main_book
    open_win.remove(self)
    self_main_book = 'close'
    book_add = 0
    self.destroy()


def self_main_inf_null(self):
    global book_add
    global self_main_book
    open_win.remove(self)
    self_main_book = 'close'
    book_add = 0
    self.destroy()


def self_book_open(self):
    global self_main_book
    if self_main_book == 'close':
        self_main_book = self
        Book()


def self_not_open(self):
    global self_main_not
    if self_main_not == 'close':
        self_main_not = self
        Not()


def self_not_close(self):
    global self_main_not
    open_win.remove(self)
    self_main_not = 'close'
    self.destroy()


def closed_excel(self):
    open_win.remove(self)
    self.destroy()


def vk_closed(self):
    open_win.remove(self)
    self.destroy()


def book_bind_add(self):
    global book_add
    if book_add == 0:
        self.bind(
            '<KeyPress>',
            lambda event: event_handler_schbook_a(
                event,
                self))
        book_add = 1
    elif book_add == 1:
        self.bind('<KeyPress>', lambda event: event_handler_lit_a(event, self))
        book_add = 0


def schbook_info(self):
    global self_book_info
    if self_book_info == 'close':
        self_book_info = self
        selected_item = self.book_table.selection()
        # Получаем значения в выделенной строке
        values = self.book_table.item(selected_item, option="values")
        text = self.book_table.item(selected_item, option="text")

        conn = sqlite3.connect(os.path.dirname(
            os.path.abspath(__file__)) + "/LC.db")
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM SCHBOOK WHERE NAME = (?) AND AUT =(?)", (text, values[0]))
        info = cur.fetchall()

        root = INFO_Book()

        root.aut = ttk.Label(root.fr_info, text=info[0][1], font='Arial 11')
        root.aut.pack()
        root.name = ttk.Label(root.fr_info, text=info[0][0], font='Arial 11')
        root.name.pack()
        root.col_v = ttk.Label(
            root.fr_info, text='Всего: ' + str(info[0][2]), font='Arial 11')
        root.col_v.pack()
        root.col_ost = ttk.Label(
            root.fr_info, text='Осталось: ' + str(values[1]), font='Arial 11')
        root.col_ost.pack()
        root.obj = ttk.Label(
            root.fr_info, text='Предмет: ' + info[0][3], font='Arial 11')
        root.obj.pack()
        root.frame.pack(side='bottom', fill='both')

        cur.execute(
            "SELECT FIO, DB, PHONE, DI, DC, STAT, COL FROM LC WHERE BOOK =(?) AND AUT=(?)", (text, values[0]))
        rows = cur.fetchall()
        for row in rows:
            if len(row[1]) == 10:
                db = datetime.datetime.strptime(row[1], '%Y-%m-%d')
                db = db.strftime('%d.%m.%Y')
            else:
                db = row[1]
            di = datetime.datetime.strptime(row[3], '%Y-%m-%d')
            di = di.strftime('%d.%m.%Y')
            dc = datetime.datetime.strptime(row[4], '%Y-%m-%d')
            dc = dc.strftime('%d.%m.%Y')
            row1 = [row[0], db, row[2], di, dc, row[5], row[6]]
            root.table.insert('', tk.END, text=row1[0], values=row1[1:])


def lit_info(self):
    global self_book_info
    if self_book_info == 'close':
        self_book_info = self
        selected_item = self.book_table1.selection()
        # Получаем значения в выделенной строке
        values = self.book_table1.item(selected_item, option="values")
        text = self.book_table1.item(selected_item, option="text")

        conn = sqlite3.connect(os.path.dirname(
            os.path.abspath(__file__)) + "/LC.db")
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM BOOK WHERE NAME = (?) AND AUT =(?)", (text, values[0]))
        info = cur.fetchall()

        root = INFO_Book()

        root.aut = ttk.Label(root.fr_info, text=info[0][1], font='Arial 11')
        root.aut.pack()
        root.name = ttk.Label(root.fr_info, text=info[0][0], font='Arial 11')
        root.name.pack()
        root.col_v = ttk.Label(
            root.fr_info, text='Всего: ' + str(info[0][2]), font='Arial 11')
        root.col_v.pack()
        root.col_ost = ttk.Label(
            root.fr_info, text='Осталось: ' + str(values[1]), font='Arial 11')
        root.col_ost.pack()
        root.frame.pack(side='bottom', fill='both')

        cur.execute(
            "SELECT FIO, DB, PHONE, DI, DC, STAT, COL FROM LC WHERE BOOK =(?) AND AUT=(?)", (text, values[0]))
        rows = cur.fetchall()
        for row in rows:
            if len(row[1]) == 10:
                db = datetime.datetime.strptime(row[1], '%Y-%m-%d')
                db = db.strftime('%d.%m.%Y')
            else:
                db = row[1]
            di = datetime.datetime.strptime(row[3], '%Y-%m-%d')
            di = di.strftime('%d.%m.%Y')
            dc = datetime.datetime.strptime(row[4], '%Y-%m-%d')
            dc = dc.strftime('%d.%m.%Y')
            row1 = [row[0], db, row[2], di, dc, row[5], row[6]]
            root.table.insert('', tk.END, text=row1[0], values=row1[1:])


# ================================ Сортировка ============================
def sort(tv, col, reverse_):
    global prev_column

    if prev_column == col:
        # Если предыдущая колонка та же что и сечас, то меняем направление
        # сортировки
        reverse_ = not reverse_
    else:
        # Если была другая колонка, то делаем прямую сортировку
        reverse_ = False

    prev_column = col

    l = [(tv.set(k, col), k) for k in tv.get_children()]
    l.sort(reverse=reverse_)

    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    tv.heading(col, command=lambda: sort(tv, col, reverse_))


def sort_0(tv, col, reverse):
    global prev_column

    if prev_column == col:
        reverse = not reverse
    else:
        reverse = False

    prev_column = col

    l = [(tv.item(k)["text"], k)
         for k in tv.get_children()]  # Display column #0 cannot be set
    l.sort(key=lambda t: t[0], reverse=reverse)

    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    tv.heading(col, command=lambda: sort_0(tv, col, reverse))


# ================================ Функции меню ==========================
def first_and_last_day():
    x = date.today()
    if x.month in (1, 3, 5, 7, 8, 10, 12):
        first = x.replace(day=1).isoformat()
        last = x.replace(day=31).isoformat()
    elif x.month == 2:
        if x.year % 4 != 0 or (x.year % 100 == 0 and x.year % 400 != 0):
            first = x.replace(day=1).isoformat()
            last = x.replace(day=28).isoformat()
        else:
            first = x.replace(day=1).isoformat()
            last = x.replace(day=29).isoformat()
    else:
        first = x.replace(day=1).isoformat()
        last = x.replace(day=30).isoformat()

    return first, last


def month_excel(x):
    y = date.today().isoformat()
    y = datetime.datetime.strptime(y, '%Y-%m-%d')
    y = y.strftime('%d_%m_%Y')
    ask = fd.asksaveasfilename(filetypes=(
        ('Excel', '*.xlsx'),), defaultextension=".xlsx")
    if ask:
        workbook = xlsxwriter.Workbook(ask)
        worksheet = workbook.add_worksheet()

        bold = workbook.add_format({'bold': True})

        worksheet.write('A1', 'ФИО', bold)
        worksheet.write('B1', 'Дата рождения', bold)
        worksheet.write('C1', 'Телефон', bold)
        worksheet.write('D1', 'Дата взятия книги', bold)
        worksheet.write('E1', 'Дата сдачи книги', bold)
        worksheet.write('F1', 'Автор', bold)
        worksheet.write('G1', 'Книга', bold)
        worksheet.write('H1', 'Статус', bold)
        worksheet.write('I1', 'Кол-во', bold)

        row = 1
        col = 0

        conn = sqlite3.connect(os.path.dirname(
            os.path.abspath(__file__)) + "/LC.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM LC WHERE DI BETWEEN (?) and (?)", x)
        rows = cur.fetchall()
        for fio, db, phone, di, dc, aut, book, stat, colvo in (rows):
            worksheet.write(row, col, fio)
            if len(db) == 10:
                db = datetime.datetime.strptime(db, '%Y-%m-%d')
                db = db.strftime('%d.%m.%Y')
            worksheet.write(row, col + 1, db)
            worksheet.write(row, col + 2, phone)
            di = datetime.datetime.strptime(di, '%Y-%m-%d')
            di = di.strftime('%d.%m.%Y')
            worksheet.write(row, col + 3, di)
            dc = datetime.datetime.strptime(dc, '%Y-%m-%d')
            dc = dc.strftime('%d.%m.%Y')
            worksheet.write(row, col + 4, dc)
            worksheet.write(row, col + 5, aut)
            worksheet.write(row, col + 6, book)
            worksheet.write(row, col + 7, stat)
            worksheet.write(row, col + 8, colvo)
            row += 1
        conn.commit()
        workbook.close()


def year_excel():
    x = date.today().replace(day=1, month=1).isoformat()
    y = date.today().isoformat()
    y = datetime.datetime.strptime(y, '%Y-%m-%d')
    y = y.strftime('%d_%m_%Y')
    z = date.today().replace(day=31, month=12).isoformat()
    ask = fd.asksaveasfilename(filetypes=(
        ('Excel', '*.xlsx'),), defaultextension=".xlsx")
    if ask:
        workbook = xlsxwriter.Workbook(ask)
        worksheet = workbook.add_worksheet()

        bold = workbook.add_format({'bold': True})

        worksheet.write('A1', 'ФИО', bold)
        worksheet.write('B1', 'Дата рождения', bold)
        worksheet.write('C1', 'Телефон', bold)
        worksheet.write('D1', 'Дата взятия книги', bold)
        worksheet.write('E1', 'Дата сдачи книги', bold)
        worksheet.write('F1', 'Автор', bold)
        worksheet.write('G1', 'Книга', bold)
        worksheet.write('H1', 'Статус', bold)
        worksheet.write('I1', 'Кол-во', bold)

        row, col = 1, 0

        conn = sqlite3.connect(os.path.dirname(
            os.path.abspath(__file__)) + "/LC.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM LC WHERE DI BETWEEN (?) and (?)", (x, z))
        rows = cur.fetchall()
        for fio, db, phone, di, dc, aut, book, stat, colvo in (rows):
            worksheet.write(row, col, fio)
            if len(db) == 10:
                db = datetime.datetime.strptime(db, '%Y-%m-%d')
                db = db.strftime('%d.%m.%Y')
            worksheet.write(row, col + 1, db)
            worksheet.write(row, col + 2, phone)
            di = datetime.datetime.strptime(di, '%Y-%m-%d')
            di = di.strftime('%d.%m.%Y')
            worksheet.write(row, col + 3, di)
            dc = datetime.datetime.strptime(dc, '%Y-%m-%d')
            dc = dc.strftime('%d.%m.%Y')
            worksheet.write(row, col + 4, dc)
            worksheet.write(row, col + 5, aut)
            worksheet.write(row, col + 6, book)
            worksheet.write(row, col + 7, stat)
            worksheet.write(row, col + 8, colvo)
            row += 1
        conn.commit()
        workbook.close()


def lub_period_excel(self):
    x = self.en_date1.get()
    x1 = datetime.datetime.strptime(x, '%d.%m.%Y')
    x1 = x1.strftime('%d_%m_%Y')

    y = self.en_date2.get()
    y1 = datetime.datetime.strptime(y, '%d.%m.%Y')
    y1 = y1.strftime('%d_%m_%Y')

    ask = fd.asksaveasfilename(filetypes=(
        ('Excel', '*.xlsx'),), defaultextension=".xlsx")
    if ask != '':
        workbook = xlsxwriter.Workbook(ask)
        worksheet = workbook.add_worksheet()

        bold = workbook.add_format({'bold': True})

        worksheet.write('A1', 'ФИО', bold)
        worksheet.write('B1', 'Дата рождения', bold)
        worksheet.write('C1', 'Телефон', bold)
        worksheet.write('D1', 'Дата взятия книги', bold)
        worksheet.write('E1', 'Дата сдачи книги', bold)
        worksheet.write('F1', 'Автор', bold)
        worksheet.write('G1', 'Книга', bold)
        worksheet.write('H1', 'Статус', bold)
        worksheet.write('I1', 'Кол-во', bold)

        row = 1
        col = 0

        x = datetime.datetime.strptime(x, '%d.%m.%Y')
        x = x.strftime('%Y-%m-%d')
        y = datetime.datetime.strptime(y, '%d.%m.%Y')
        y = y.strftime('%Y-%m-%d')

        conn = sqlite3.connect(os.path.dirname(
            os.path.abspath(__file__)) + "/LC.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM LC WHERE DI BETWEEN (?) and (?)", (x, y))
        rows = cur.fetchall()
        for fio, db, phone, di, dc, aut, book, stat, colvo in (rows):
            worksheet.write(row, col, fio)
            db = datetime.datetime.strptime(db, '%Y-%m-%d')
            db = db.strftime('%d.%m.%Y')
            worksheet.write(row, col + 1, db)
            worksheet.write(row, col + 2, phone)
            di = datetime.datetime.strptime(di, '%Y-%m-%d')
            di = di.strftime('%d.%m.%Y')
            worksheet.write(row, col + 3, di)
            dc = datetime.datetime.strptime(dc, '%Y-%m-%d')
            dc = dc.strftime('%d.%m.%Y')
            worksheet.write(row, col + 4, dc)
            worksheet.write(row, col + 5, aut)
            worksheet.write(row, col + 6, book)
            worksheet.write(row, col + 7, stat)
            worksheet.write(row, col + 8, colvo)
            row += 1
        conn.commit()
        workbook.close()


def month(num):
    months = {
        '01': 'Январь',
        '02': 'Февраль',
        '03': 'Март',
        '04': 'Апрель',
        '05': 'Май',
        '06': 'Июнь',
        '07': 'Июль',
        '08': 'Август',
        '09': 'Сентябрь',
        '10': 'Октябрь',
        '11': 'Ноябрь',
        '12': 'Декабрь'
    }
    return months[num]


def excel_uchet_reg():
    y = date.today().isoformat()
    y = datetime.datetime.strptime(y, '%Y-%m-%d')
    y1 = y.strftime('%d_%m_%Y')

    ask = fd.asksaveasfilename(filetypes=(
        ('Excel', '*.xlsx'),), defaultextension=".xlsx")
    if ask != '':
        workbook = xlsxwriter.Workbook(ask)
        worksheet = workbook.add_worksheet()

        bold = workbook.add_format({'bold': True})
        bold_wrap = workbook.add_format({'bold': True})
        bold_wrap.set_text_wrap()

        mon = y.strftime('%m')
        mon = month(mon)
        year = y.strftime('%Y')

        worksheet.merge_range('A1:P1', 'Учёт выдачи книг, брошюр и журналов за ____{0}____{1}г. '.format(mon, year),
                              bold)
        worksheet.merge_range('A2:A3', 'Числа месяца', bold_wrap)
        worksheet.merge_range('B2:B3', 'Всего', bold)
        worksheet.merge_range('C2:O2', 'В том числе', bold)
        worksheet.write('C3', '1 кл.', bold)
        worksheet.write('D3', '2 кл.', bold)
        worksheet.write('E3', '3 кл.', bold)
        worksheet.write('F3', '4 кл.', bold)
        worksheet.write('G3', '5 кл.', bold)
        worksheet.write('H3', '6 кл.', bold)
        worksheet.write('I3', '7 кл.', bold)
        worksheet.write('J3', '8 кл.', bold)
        worksheet.write('K3', '9 кл.', bold)
        worksheet.write('L3', '10 кл.', bold)
        worksheet.write('M3', '11 кл.', bold)
        worksheet.write('N3', 'Проч', bold)
        worksheet.write('O3', 'Учителя', bold)
        worksheet.write('P3', 'Число посещений', bold_wrap)
        x = 1
        row = 3
        col = 0
        while x <= 16:
            worksheet.write(row, col, x, bold)
            x += 1
            col += 1

        worksheet.write('A5', 'Состоит на начало месяца', bold_wrap)

        conn = sqlite3.connect(os.path.dirname(
            os.path.abspath(__file__)) + "/LC.db")
        cur = conn.cursor()

        chisl = list(range(1, 32))

        last = first_and_last_day()
        last_day = datetime.datetime.strptime(last[1], '%Y-%m-%d')
        last_day = int(last_day.strftime('%d'))

        first_day = y.replace(day=1)

        now_chisl = int(first_day.strftime('%d'))
        cl = 1
        ro = 5
        column = 0
        vsego = 0
        vsego_it = 0

        while (now_chisl <= last_day) and (now_chisl in chisl):
            worksheet.write(ro, column, now_chisl, bold)
            date_n = first_day.replace(day=now_chisl)
            date_n = date_n.strftime('%Y-%m-%d')
            column += 1
            col_vseg = column
            while cl <= 11:
                cur.execute("SELECT COUNT(*) FROM PROFILE WHERE DREG = (?) AND CLIENT =(?) AND CLA = (?)",
                            (date_n, 'Ученик', cl))
                rows = cur.fetchall()
                for row in rows:
                    if row[0] != 0:
                        worksheet.write(ro, column + 1, row[0])
                    else:
                        worksheet.write(ro, column + 1, '')
                    column += 1
                    cl += 1
                    vsego += int(row[0])
            cur.execute("SELECT COUNT(*) FROM PROFILE WHERE DREG = (?) AND CLIENT =(?)",
                        (date_n, 'Другой посетитель'))
            rows = cur.fetchall()
            for row in rows:
                if row[0] != 0:
                    worksheet.write(ro, column + 1, row[0])
                else:
                    worksheet.write(ro, column + 1, '')
                column += 1
                cl += 1
                vsego += int(row[0])
            cur.execute(
                "SELECT COUNT(*) FROM PROFILE WHERE DREG = (?) AND CLIENT =(?)", (date_n, 'Учитель'))
            rows = cur.fetchall()
            for row in rows:
                if row[0] != 0:
                    worksheet.write(ro, column + 1, row[0])
                else:
                    worksheet.write(ro, column + 1, '')
                column += 1
                cl += 1
                vsego += int(row[0])
            worksheet.write(ro, col_vseg, vsego, bold)
            vsego_it += vsego
            vsego = 0
            column = 0
            ro += 1
            cl = 1
            now_chisl += 1
        worksheet.write(ro, column, 'Всего за месяц', bold_wrap)
        column += 1
        worksheet.write(ro, column, vsego_it, bold)
        column = 0
        ro += 1
        worksheet.write(ro, column, 'Итого с начала', bold_wrap)
        conn.commit()
        workbook.close()


def uchet_book():
    y = date.today().isoformat()
    y = datetime.datetime.strptime(y, '%Y-%m-%d')
    y1 = y.strftime('%d_%m_%Y')

    ask = fd.asksaveasfilename(filetypes=(
        ('Excel', '*.xlsx'),), defaultextension=".xlsx")
    if ask != '':
        workbook = xlsxwriter.Workbook(ask)
        worksheet = workbook.add_worksheet()

        bold = workbook.add_format({'bold': True})
        bold_wrap = workbook.add_format({'bold': True})
        bold_wrap.set_text_wrap()

        mon = y.strftime('%m')
        mon = month(mon)
        year = y.strftime('%Y')

        worksheet.merge_range('A1:R1', 'Учёт выдачи книг, брошюр и журналов за ____{0}____{1}г. '.format(mon, year),
                              bold)
        worksheet.merge_range('A2:A3', 'Числа месяца', bold_wrap)
        worksheet.merge_range('B2:B3', 'Всего выдано', bold_wrap)
        worksheet.merge_range('C2:E2', 'ОПЛ', bold)
        worksheet.merge_range('F2:G2', 'ЕНЛ', bold)
        worksheet.write('C3', '1, 6, 86, 87', bold_wrap)
        worksheet.write('D3', '9', bold)
        worksheet.write('E3', '74', bold)
        worksheet.write('F3', '2', bold)
        worksheet.write('G3', '5', bold)
        worksheet.merge_range('H2:H3', '3', bold)
        worksheet.merge_range('I2:I3', '4', bold)
        worksheet.merge_range('J2:J3', '85', bold)
        worksheet.merge_range('K2:K3', '75', bold)
        worksheet.merge_range('L2:L3', '81, 82, 83', bold_wrap)
        worksheet.merge_range('M2:M3', '84', bold)
        worksheet.merge_range('N2:N3', 'Д', bold)
        worksheet.merge_range('O2:O3', 'Электр. изд', bold_wrap)
        worksheet.merge_range('P2:P3', 'Учебники', bold_wrap)
        worksheet.merge_range('Q2:Q3', 'Периодика', bold_wrap)
        worksheet.merge_range('R2:R3', 'Справки', bold_wrap)

        row = 3
        column = 0
        x = 1
        while x <= 18:
            worksheet.write(row, column, x, bold)
            x += 1
            column += 1

        row += 1
        column = 0
        worksheet.write(row, column, 'Кол-во предыдущих книговыд.', bold_wrap)
        ro = row + 1

        conn = sqlite3.connect(os.path.dirname(
            os.path.abspath(__file__)) + "/LC.db")
        cur = conn.cursor()

        chisl = (
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
            30,
            31)

        last = first_and_last_day()
        last_day = datetime.datetime.strptime(last[1], '%Y-%m-%d')
        last_day = int(last_day.strftime('%d'))

        first_day = y.replace(day=1)

        now_chisl = int(first_day.strftime('%d'))

        vsego = 0

        while (now_chisl <= last_day) and (now_chisl in chisl):
            worksheet.write(ro, column, now_chisl, bold)
            date_n = first_day.replace(day=now_chisl)
            date_n = date_n.strftime('%Y-%m-%d')
            column += 1
            cur.execute("SELECT COUNT(*) FROM LC WHERE DI = (?)", (date_n,))
            rows = cur.fetchall()
            for row in rows:
                if row[0] != 0:
                    worksheet.write(ro, column, row[0], bold)
                else:
                    worksheet.write(ro, column, '', bold)
                vsego += row[0]
            ro += 1
            column = 0
            now_chisl += 1

        worksheet.write(ro, column, 'Всего за месяц', bold_wrap)
        column += 1
        worksheet.write(ro, column, vsego, bold)
        column = 0
        ro += 1
        worksheet.write(ro, column, 'Итого с начала года', bold_wrap)

        conn.commit()
        workbook.close()


# ================================== Изменение темы ======================
def style_change(var_style):
    theme = open(os.path.dirname(
        os.path.abspath(__file__)) + '/theme.txt', 'w')
    theme.write(var_style)
    theme.close()
    ask = messagebox.askyesno('Перезапустить?',
                              'Чтобы изменения вступили в силу, необходимо перезапустить программу.\n \nПерезапустить программу прямо сейчас?\n(Перед этим действием убедитесь, что вы сохранили \nвсе изменения, иначе они будут утеряны)')
    if ask:
        os.execl(sys.executable, sys.executable, *sys.argv)

    # ================================= Обработчики событий ==================


def event_handler_main(event, self):
    if event.keycode == 65 and event.state == 4:  # Ctrl + A
        add_profile(self)
    elif event.keycode == 83 and event.state == 4:  # Ctrl + S
        edit_profile(self)
    elif event.keycode == 46:  # Delete
        threading.Thread(target=del_profile, args=[self, ]).start()


def event_handler_info(event, self):
    if event.keycode == 65 and event.state == 4:  # Ctrl + A
        add_book(self)
    elif event.keycode == 83 and event.state == 4:  # Ctrl + S
        edit_lc(self)
    elif event.keycode == 46:  # Delete
        threading.Thread(target=delete_lc, args=[self, ]).start()


def event_handler_schbook(event, self):
    if event.keycode == 83 and event.state == 4:  # Ctrl + S
        edit_schbooks(self)
    elif event.keycode == 46:  # Delete
        threading.Thread(target=del_schbook, args=[self, ]).start()


def event_handler_lit(event, self):
    if event.keycode == 83 and event.state == 4:  # Ctrl + S
        edit_lit(self)
    elif event.keycode == 46:  # Delete
        threading.Thread(target=del_book, args=[self, ]).start()


def event_handler_schbook_a(event, self):
    if event.keycode == 65 and event.state == 4:  # Ctrl + A
        schbook(self)


def event_handler_lit_a(event, self):
    if event.keycode == 65 and event.state == 4:  # Ctrl + A
        lit(self)


def easter1():
    global easter_egg
    easter_egg += 1


def easter2():
    global easter_egg
    if easter_egg == 1:
        easter_egg += 1
    else:
        easter_egg = 0


def easter3():
    global easter_egg
    if easter_egg == 2:
        easter_egg += 1
    else:
        easter_egg = 0


def easter4(self):
    filename = os.path.dirname(os.path.abspath(__file__)) + "/imper.mp3"
    playsound.playsound(filename)


def progressbar_start(self):
    self.progress.place(relx=0.8871, rely=0.95)
    self.progress.start()


def progressbar_stop(self):
    self.progress.place_forget()
    self.progress.stop()


def progressbar_start1(self):
    self.progress1.place(relx=0.8871, rely=0.95)
    self.progress1.start()


def progressbar_stop1(self):
    self.progress1.place_forget()
    self.progress1.stop()


def geometry(self):
    time.sleep(10)
    print(self.winfo_geometry())


def quit_window(icon, item):
    icon.stop()
    sys.exit(1)


def show_window(icon, item):
    icon.stop()
    app.after(0, app.deiconify)


def withdraw_window():
    for i in open_win:
        i.destroy()
    app.withdraw()
    image = Image.open(os.path.dirname(
        os.path.abspath(__file__)) + "/logo.ico")
    menu = pystray.Menu(item('Развернуть', show_window,
                             default=True), item('Закрыть', quit_window))
    icon = pystray.Icon("Мини библиотека 2020", image,
                        "Мини библиотека 2020", menu)
    icon.run()


def plus_class(self):
    conn = sqlite3.connect(os.path.dirname(
        os.path.abspath(__file__)) + "/LC.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM PROFILE WHERE CLIENT=(?)", ["Ученик", ])
    rows = cur.fetchall()
    for row in rows:
        clas = int(row[2]) + 1
        if clas <= 11:
            result = [clas, row[0], row[1], row[5]]
            cur.execute(
                "UPDATE PROFILE SET CLA = (?) WHERE FIO = (?) AND DB = (?) AND PHONE = (?)", result)
        elif clas > 11:
            line = [row[0], row[1], row[5]]
            cur.execute(
                'DELETE FROM PROFILE WHERE FIO = (?) AND DB = (?) AND PHONE = (?)', line)
            cur.execute(
                'DELETE FROM LC WHERE FIO = (?) AND DB = (?) AND PHONE = (?)', line)
    conn.commit()
    threading.Thread(target=update_main, args=[self, ]).start()


def minus_class(self):
    conn = sqlite3.connect(os.path.dirname(
        os.path.abspath(__file__)) + "/LC.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM PROFILE WHERE CLIENT=(?)", ["Ученик", ])
    rows = cur.fetchall()
    for row in rows:
        class_ = int(row[2]) - 1
        if class_ >= 1:
            result = [class_, row[0], row[1], row[5]]
            cur.execute(
                "UPDATE PROFILE SET CLA = (?) WHERE FIO = (?) AND DB = (?) AND PHONE = (?)", result)
        elif class_ < 1:
            line = [row[0], row[1], row[5]]
            cur.execute(
                'DELETE FROM PROFILE WHERE FIO = (?) AND DB = (?) AND PHONE = (?)', line)
            cur.execute(
                'DELETE FROM LC WHERE FIO = (?) AND DB = (?) AND PHONE = (?)', line)
    conn.commit()
    threading.Thread(target=update_main, args=[self, ]).start()


def vk_api_save(self):
    token = self.token_en.get()
    id_g = self.id_en.get()
    if token and id_g:
        file = open(os.path.dirname(
            os.path.abspath(__file__)) + "/vk_api.txt", 'w')
        file.write(token + '\n' + id_g)
        file.close()


def network():
    try:
        socket.gethostbyaddr('www.yandex.ru')
    except socket.gaierror:
        return False
    return True


def vk_bot_start(self):
    if os.path.exists('os.path.abspath(__file__)) + "/vk_api.txt"'):
        file = open(os.path.dirname(
            os.path.abspath(__file__)) + "/vk_api.txt", 'r')
        lines = file.readlines()
        if lines != []:
            if network() == True:
                threading.Thread(target=vk_bot, args=[
                    lines[0][:-1], lines[1], self]).start()


def vk_bot(token, id_g, self):
    vk_session = vk_api.VkApi(token=token, api_version='5.122')

    longpoll = VkBotLongPoll(vk_session, id_g)

    vk = vk_session.get_api()

    del_ac = 0

    keyboard_help = VkKeyboard(inline=False)
    keyboard_help.add_button(label='Продлить книгу', color='positive')
    keyboard_help.add_line()
    keyboard_help.add_button(label='Проверить наличие книги')
    keyboard_help.add_line()
    keyboard_help.add_button(label='Удалить аккаунт', color='negative')

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.obj['message']['text'] in ('Привет', 'Hello'):  # Если написали заданную фразу
                if event.from_user:  # Если написали в ЛС
                    key = VkKeyboard(one_time=True, inline=False)
                    key.add_button(label='Продолжить', color='primary')
                    vk.messages.send(  # Отправляем сообщение
                        user_id=event.obj['message']['from_id'],
                        random_id=event.obj['message']['random_id'],
                        keyboard=key.get_keyboard(),
                        message='Здравствуй! Я роботизированный помощник для школьной библиотеки. С моей помощью можно:\n\n1)Узнать статус взятой книги\n2)Продлить ее\n3)Узнать какие книги есть в наличии.'
                    )

            # Если написали заданную фразу
            elif event.obj['message']['text'] == 'Продолжить':
                if event.from_user:
                    key = VkKeyboard(one_time=True, inline=False)
                    key.add_button(label='Регистрация', color='primary')
                    key.add_line()
                    key.add_button(label='Связать аккаунты', color='default')
                    vk.messages.send(  # Отправляем сообщение
                        user_id=event.obj['message']['from_id'],
                        random_id=event.obj['message']['random_id'],
                        keyboard=key.get_keyboard(),
                        message='Я очень рад что ты заинтересовался мной) \nИ так, для начала работы со мной напиши "Связать аккаунты" если ты уже зарегестрирован в нашей библиотеке, иначе напиши "Регистрация"'
                    )

            elif event.obj['message']['text'] == 'Регистрация':
                if event.from_user:
                    vk.messages.send(  # Отправляем сообщение
                        user_id=event.obj['message']['from_id'],
                        random_id=event.obj['message']['random_id'],
                        message='И так, для регистрации мне нужны ваши данные.\nМне нужны ФИО, Дата рождения, Класс, Литера(буква класса), Адрес, Телефон и кто Вы(Ученик, Учитель или Другой посетитель)'
                    )
                    time.sleep(6)
                    vk.messages.send(  # Отправляем сообщение
                        user_id=event.obj['message']['from_id'],
                        random_id=event.obj['message']['random_id'],
                        message='Ваше следующее сообщение дожно быть вида: Регистрация: Фамилия Имя Отчество ДД.ММ.ГГГГ Класс Литера Улица дом, кв.номер Телефон Статус(кто Вы)'
                    )
                    time.sleep(6)
                    vk.messages.send(  # Отправляем сообщение
                        user_id=event.obj['message']['from_id'],
                        random_id=event.obj['message']['random_id'],
                        message='Пример: \nРегистрация: Париев Олег Евгеньевич 08.04.2002 10 А Советская 24, кв.60 88005553535 Ученик'
                    )
                    time.sleep(6)
                    vk.messages.send(  # Отправляем сообщение
                        user_id=event.obj['message']['from_id'],
                        random_id=event.obj['message']['random_id'],
                        message='Если вы Учитель или Другой посетитель, то вместо Класса и Литеры ставьте точку, иначе я вас не зарегистрирую'
                    )

            elif event.obj['message']['text'][:12] == 'Регистрация:':
                if event.from_user:
                    vk.messages.send(  # Отправляем сообщение
                        user_id=event.obj['message']['from_id'],
                        random_id=event.obj['message']['random_id'],
                        message='Ждите, я вас регистрирую'
                    )
                    text = event.obj['message']['text'][13:]
                    lst = text.split()
                    res_spis = []
                    i = 0
                    id_us = event.obj['message']['from_id']
                    conn = sqlite3.connect(os.path.dirname(
                        os.path.abspath(__file__)) + "/LC.db")
                    cur = conn.cursor()
                    while i < len(lst):
                        res = lst[i]
                        res_spis.append(res)
                        i += 1
                    fio = res_spis[0] + ' ' + res_spis[1] + ' ' + res_spis[2]
                    cur.execute('SELECT * FROM PROFILE WHERE FIO=(?) AND DB=(?) AND VK_ID =(?)',
                                [fio, datetime.datetime.strptime(res_spis[3], '%d.%m.%Y').strftime('%Y-%m-%d'),
                                 event.obj['message']['from_id']])
                    row = cur.fetchall()
                    if row != []:
                        vk.messages.send(  # Отправляем сообщение
                            user_id=event.obj['message']['from_id'],
                            random_id=event.obj['message']['random_id'],
                            message='Такой аккаунт существует!'
                        )
                    else:
                        cur.execute('SELECT * FROM PROFILE WHERE FIO=(?) AND DB=(?)',
                                    [fio, datetime.datetime.strptime(res_spis[3], '%d.%m.%Y').strftime('%Y-%m-%d')])
                        row = cur.fetchall()
                        if row != []:
                            key = VkKeyboard(one_time=True, inline=False)
                            key.add_button(
                                label='Связать аккаунты', color='positive')
                            vk.messages.send(  # Отправляем сообщение
                                user_id=event.obj['message']['from_id'],
                                random_id=event.obj['message']['random_id'],
                                keyboard=key.get_keyboard(),
                                message='Такой аккаунт существует! Проведите Связку аккаунтов'
                            )
                        else:
                            if (len(res_spis) == 11) and (res_spis[10] != 'Учитель') and (
                                    res_spis[4] != res_spis[5]) and (res_spis[5] != '.'):
                                result = [res_spis[0] + ' ' + res_spis[1] + ' ' + res_spis[2],
                                          datetime.datetime.strptime(
                                              res_spis[3], '%d.%m.%Y').strftime('%Y-%m-%d'),
                                          res_spis[4], res_spis[5],
                                          res_spis[6] + ' ' +
                                          res_spis[7] + ' ' + res_spis[8],
                                          res_spis[9], res_spis[10], datetime.date.today().isoformat(), id_us]
                                cur.execute(
                                    'INSERT INTO PROFILE VALUES (?,?,?,?,?,?,?,?,?)', result)
                                conn.commit()
                                self.event_generate('<<Key-43>>')
                                vk.messages.send(  # Отправляем сообщение
                                    user_id=event.obj['message']['from_id'],
                                    random_id=event.obj['message']['random_id'],
                                    message='Регистрация прошла успешно!'
                                )
                                time.sleep(2)
                                vk.messages.send(  # Отправляем сообщение
                                    user_id=event.obj['message']['from_id'],
                                    random_id=event.obj['message']['random_id'],
                                    keyboard=keyboard_help.get_keyboard(),
                                    message='Теперь вы можете пользоваться всеми моими функциями! Желаю вам Удачи и Хорошего чтения😄'
                                )
                            elif (len(res_spis) == 11) and (res_spis[10] == 'Учитель') and (
                                    res_spis[4] == res_spis[5]) and (res_spis[5] == '.'):
                                result = [res_spis[0] + ' ' + res_spis[1] + ' ' + res_spis[2],
                                          datetime.datetime.strptime(
                                              res_spis[3], '%d.%m.%Y').strftime('%Y-%m-%d'),
                                          res_spis[4].replace(
                                              '.', ''), res_spis[5].replace('.', ''),
                                          res_spis[6] + ' ' +
                                          res_spis[7] + ' ' + res_spis[8],
                                          res_spis[9], res_spis[10], datetime.date.today().isoformat(), id_us]
                                cur.execute(
                                    'INSERT INTO PROFILE VALUES (?,?,?,?,?,?,?,?,?)', result)
                                conn.commit()
                                self.event_generate('<<Key-43>>')
                                vk.messages.send(  # Отправляем сообщение
                                    user_id=event.obj['message']['from_id'],
                                    random_id=event.obj['message']['random_id'],
                                    message='Регистрация прошла успешно!'
                                )
                                time.sleep(2)
                                vk.messages.send(  # Отправляем сообщение
                                    user_id=event.obj['message']['from_id'],
                                    random_id=event.obj['message']['random_id'],
                                    keyboard=keyboard_help.get_keyboard(),
                                    message='Теперь вы можете пользоваться всеми моими функциями! Желаю вам Удачи и Хорошего чтения😄'
                                )
                            elif len(res_spis) == 12 and (
                                    res_spis[10] + ' ' + res_spis[11] == 'Другой посетитель') and (
                                    res_spis[4] != res_spis[5]) and (res_spis[5] != '.'):
                                result = [res_spis[0] + ' ' + res_spis[1] + ' ' + res_spis[2],
                                          datetime.datetime.strptime(
                                              res_spis[3], '%d.%m.%Y').strftime('%Y-%m-%d'),
                                          res_spis[4].replace(
                                              '.', ''), res_spis[5].replace('.', ''),
                                          res_spis[6] + ' ' +
                                          res_spis[7] + ' ' + res_spis[8],
                                          res_spis[9], res_spis[10] +
                                          ' ' + res_spis[11],
                                          datetime.date.today().isoformat(), id_us]
                                cur.execute(
                                    'INSERT INTO PROFILE VALUES (?,?,?,?,?,?,?,?,?)', result)
                                conn.commit()
                                self.event_generate('<<Key-43>>')
                                vk.messages.send(  # Отправляем сообщение
                                    user_id=event.obj['message']['from_id'],
                                    random_id=event.obj['message']['random_id'],
                                    message='Регистрация прошла успешно!'
                                )
                                time.sleep(2)
                                vk.messages.send(  # Отправляем сообщение
                                    user_id=event.obj['message']['from_id'],
                                    random_id=event.obj['message']['random_id'],
                                    keyboard=keyboard_help.get_keyboard(),
                                    message='Теперь вы можете пользоваться всеми моими функциями! Желаю вам Удачи и Хорошего чтения😄'
                                )
                            else:
                                vk.messages.send(  # Отправляем сообщение
                                    user_id=event.obj['message']['from_id'],
                                    random_id=event.obj['message']['random_id'],
                                    message='Ошибка! Посмотрети внимательнее, видимо вы где-то ошиблись'
                                )

            elif event.obj['message']['text'] == 'Связать аккаунты':
                if event.from_user:
                    vk.messages.send(  # Отправляем сообщение
                        user_id=event.obj['message']['from_id'],
                        random_id=event.obj['message']['random_id'],
                        message='Для связки аккаунтов мне потребуются ФИО, Дата рожденя и Номер телефона.'
                    )
                    time.sleep(1)
                    vk.messages.send(  # Отправляем сообщение
                        user_id=event.obj['message']['from_id'],
                        random_id=event.obj['message']['random_id'],
                        message='Ваше следующее сообщение должно быть вида:\nСвязать: Фамилия Имя Отчество ДД.ММ.ГГГГ Номер'
                    )
                    time.sleep(1)
                    vk.messages.send(  # Отправляем сообщение
                        user_id=event.obj['message']['from_id'],
                        random_id=event.obj['message']['random_id'],
                        message='Пример:\nСвязать: Париев Олег Евгеньевич 08.04.2002 88005553535'
                    )

            elif event.obj['message']['text'][:8] == 'Связать:':
                if event.from_user:
                    vk.messages.send(  # Отправляем сообщение
                        user_id=event.obj['message']['from_id'],
                        random_id=event.obj['message']['random_id'],
                        message='Ждите... Идёт привязка аккаунта. Это займёт не более 5 минут'
                    )
                    text = event.obj['message']['text'][9:]
                    lst = text.split()
                    res_spis = []
                    i = 0
                    id_us = event.obj['message']['from_id']
                    conn = sqlite3.connect(os.path.dirname(
                        os.path.abspath(__file__)) + "/LC.db")
                    cur = conn.cursor()
                    while i < len(
                            lst):  # Парсинг Данных и разбитие их в Массив
                        string = lst[i]
                        res_spis.append(string)
                        i += 1
                    if len(lst) == 5:
                        if len(res_spis[3]) == 10:
                            db = datetime.datetime.strptime(
                                res_spis[3], '%d.%m.%Y')
                            db = db.strftime('%Y-%m-%d')
                        else:
                            db = res_spis[3]
                        result = [id_us, res_spis[0] + ' ' +
                                  res_spis[1] + ' ' + res_spis[2], db, res_spis[4]]
                    elif len(lst) == 4:
                        if len(res_spis[2]) == 10:
                            db = datetime.datetime.strptime(
                                res_spis[3], '%d.%m.%Y')
                            db = db.strftime('%Y-%m-%d')
                        else:
                            db = res_spis[2]
                        result = [id_us, res_spis[0] + ' ' +
                                  res_spis[1], db, res_spis[3]]

                    cur.execute(
                        'SELECT * FROM PROFILE WHERE FIO = (?) AND DB = (?) AND PHONE = (?)', result[1:])
                    rows = cur.fetchall()
                    if rows != []:
                        cur.execute('UPDATE PROFILE SET VK_ID = (?) WHERE FIO = (?) AND DB = (?) AND PHONE = (?)',
                                    result)
                        conn.commit()
                        time.sleep(2)
                        vk.messages.send(  # Отправляем сообщение
                            user_id=event.obj['message']['from_id'],
                            random_id=event.obj['message']['random_id'],
                            message='Привязка прошла успешно!'
                        )
                        time.sleep(2)
                        vk.messages.send(  # Отправляем сообщение
                            user_id=event.obj['message']['from_id'],
                            random_id=event.obj['message']['random_id'],
                            keyboard=keyboard_help.get_keyboard(),
                            message='Теперь вы можете пользоваться всеми моими функциями! Желаю вам Удачи и Хорошего чтения😄'
                        )
                    else:
                        key = VkKeyboard(one_time=True, inline=False)
                        key.add_button(label='Регистрация', color='positive')
                        vk.messages.send(  # Отправляем сообщение
                            user_id=event.obj['message']['from_id'],
                            random_id=event.obj['message']['random_id'],
                            keyboard=key.get_keyboard(),
                            message='Такой пользователь не найден😢 Либо его нету в нашей Базе Данных, либо вы неверно ввели эти самые данные\n\nПроверьте их правильность, если снова не выйдет - пройдите Регистрацию'
                        )

            elif event.obj['message']['text'] in ('Помощь', 'Help', 'HELP', '/h'):
                if event.from_user:
                    vk.messages.send(
                        user_id=event.obj['message']['from_id'],
                        keyboard=keyboard_help.get_keyboard(),
                        random_id=event.obj['message']['random_id'],
                        message='Вот тебе рука помощи друг)\nУ тебя снизу появилась клавиатура, которая поможет тебе в общении со мной.\n\nЕсли ты тут впервые - напиши "Привет"'
                    )

            elif event.obj['message']['text'] == 'Удалить аккаунт':
                if event.from_user:
                    key = VkKeyboard(inline=False, one_time=True)
                    key.add_button(label='Да', color='positive')
                    key.add_button(label='Нет', color='negative')
                    vk.messages.send(
                        user_id=event.obj['message']['from_id'],
                        keyboard=key.get_keyboard(),
                        random_id=event.obj['message']['random_id'],
                        message='Вы уверены что хотите удалить свой билет из нашей библиотеки?\nЭто значит, что вы не сможете пользоваться функциями бота'
                    )
                    del_ac = 1

            elif event.obj['message']['text'] == 'Да':
                if event.from_user:
                    if del_ac != 0:
                        conn = sqlite3.connect(
                            os.path.dirname(os.path.abspath(__file__)) + "/LC.db")  # Занесение данных в базу данных
                        con_cur = conn.cursor()
                        con_cur.execute('SELECT * FROM PROFILE WHERE VK_ID = (?)',
                                        (str(event.obj['message']['from_id']),))
                        values = con_cur.fetchall()
                        line = (values[0][0], values[0][1], values[0][5])
                        con_cur.execute(
                            'DELETE FROM PROFILE WHERE FIO = (?) AND DB = (?) AND PHONE = (?)', line)
                        con_cur.execute(
                            'DELETE FROM LC WHERE FIO = (?) AND DB = (?) AND PHONE = (?)', line)
                        conn.commit()
                        vk.messages.send(
                            user_id=event.obj['message']['from_id'],
                            random_id=event.obj['message']['random_id'],
                            message='Очень жаль что вы нас покидаете😢\nАккаунт успешно удален'
                        )
                        del_ac = 0

            elif event.obj['message']['text'] == 'Нет':
                if event.from_user:
                    if del_ac != 0:
                        vk.messages.send(
                            user_id=event.obj['message']['from_id'],
                            random_id=event.obj['message']['random_id'],
                            message='Мы очень рады что вы решили остаться с нами😀'
                        )

            elif event.obj['message']['text'] == 'Продлить книгу':
                if event.from_user:
                    conn = sqlite3.connect(
                        os.path.dirname(os.path.abspath(__file__)) + "/LC.db")  # Занесение данных в базу данных
                    cur = conn.cursor()
                    cur.execute('SELECT * FROM PROFILE WHERE VK_ID = (?)',
                                (event.obj['message']['from_id'],))
                    values = cur.fetchall()
                    line = (values[0][0], values[0][1], values[0][5])
                    cur.execute(
                        'SELECT DC,AUT,BOOK,STAT FROM LC WHERE FIO = (?) AND DB = (?) AND PHONE = (?)', line)
                    rows = cur.fetchall()
                    mess = ''
                    k = 1
                    for i in rows:
                        date = datetime.datetime.strptime(i[0], '%Y-%m-%d')
                        date = date.strftime('%d.%m.%Y')
                        row = '{}) Автор: ' + i[1] + ' Название: ' + i[2] + ' Статус: ' + i[
                            3] + ' Сдать: ' + date + '\n'
                        row = row.format(k)
                        mess += row
                    vk.messages.send(
                        user_id=event.obj['message']['from_id'],
                        random_id=event.obj['message']['random_id'],
                        message='Вот список литературы, которую вы взяли:\n' +
                                mess + '\nКакую желаете продлить?'
                    )
                    time.sleep(3)
                    vk.messages.send(
                        user_id=event.obj['message']['from_id'],
                        random_id=event.obj['message']['random_id'],
                        message='Для продления напишите Автора и Название книги.'
                    )
                    time.sleep(1)
                    vk.messages.send(
                        user_id=event.obj['message']['from_id'],
                        random_id=event.obj['message']['random_id'],
                        message='Формат продления:\nПродлить: Фамилия И. О. "Название"'
                    )
                    time.sleep(1)
                    vk.messages.send(
                        user_id=event.obj['message']['from_id'],
                        random_id=event.obj['message']['random_id'],
                        message='Пример:\nПродлить: Пушкин А. С. "Евгений Онегин"'
                    )
                    conn.commit()

            elif event.obj['message']['text'][:9] == 'Продлить:':
                if event.from_user:
                    conn = sqlite3.connect(
                        os.path.dirname(os.path.abspath(__file__)) + "/LC.db")  # Занесение данных в базу данных
                    cur = conn.cursor()
                    values = event.obj['message']['text'][10:]
                    values = values.split()
                    aut = ''
                    book = ''
                    i = 0
                    while i < len(values):
                        if i < 2:
                            aut += values[i] + ' '
                            i += 1
                        elif i == 2:
                            aut += values[i]
                            i += 1
                        elif i < len(values) - 1:
                            book += values[i] + ' '
                            i += 1
                        else:
                            book += values[i]
                            i += 1
                    i = 0
                    cur.execute("SELECT FIO, DB, PHONE FROM PROFILE WHERE VK_ID = (?)",
                                (event.obj['message']['from_id'],))
                    values = cur.fetchall()
                    res = (values[0][0], values[0][1], values[0]
                    [2], aut, book, 'На руках', 'Просрочена')
                    cur.execute(
                        "SELECT DC FROM LC WHERE FIO = (?) AND DB=(?) AND PHONE = (?) AND AUT =(?) AND BOOK = (?) AND (STAT = (?) OR STAT = (?))",
                        res)
                    dc = cur.fetchone()
                    dc = datetime.datetime.strptime(dc[0], '%Y-%m-%d')
                    today = datetime.date.today()
                    today = str(today)
                    today = datetime.datetime.strptime(today, '%Y-%m-%d')
                    raz = dc - today
                    if raz.days > 6:
                        vk.messages.send(
                            user_id=event.obj['message']['from_id'],
                            random_id=event.obj['message']['random_id'],
                            message='Нельзя продливать книги, срок которых больше недели'
                        )
                    else:
                        dc = str(dc + timedelta(days=7))
                        dc = dc[:10]
                        res = (dc, values[0][0], values[0][1], values[0]
                        [2], aut, book, 'На руках', 'Просрочена')
                        cur.execute(
                            "UPDATE LC SET DC = (?) WHERE FIO = (?) AND DB=(?) AND PHONE = (?) AND AUT =(?) AND BOOK = (?) AND (STAT = (?) OR STAT = (?))",
                            res)
                        dc = str(dc)
                        dc = datetime.datetime.strptime(dc, '%Y-%m-%d')
                        dc = dc.strftime('%d.%m.%Y')
                        vk.messages.send(
                            user_id=event.obj['message']['from_id'],
                            random_id=event.obj['message']['random_id'],
                            keyboard=keyboard_help.get_keyboard(),
                            message='Книга успешно продлена до: {}'.format(dc)
                        )
                        conn.commit()

            elif event.obj['message']['text'] == 'Проверить наличие книги':
                if event.from_user:
                    vk.messages.send(
                        user_id=event.obj['message']['from_id'],
                        random_id=event.obj['message']['random_id'],
                        message='Какую(ие) книгу(и) хотите проверить на наличие в библиотеке?'
                    )
                    time.sleep(1)
                    vk.messages.send(
                        user_id=event.obj['message']['from_id'],
                        random_id=event.obj['message']['random_id'],
                        message='Напишите "Проверить: Слово/а'
                    )
                    time.sleep(1)
                    vk.messages.send(
                        user_id=event.obj['message']['from_id'],
                        random_id=event.obj['message']['random_id'],
                        message='Пример:\nПроверить: Евгений Онегин'
                    )
                    time.sleep(1)
                    vk.messages.send(
                        user_id=event.obj['message']['from_id'],
                        random_id=event.obj['message']['random_id'],
                        message='Возможно, Автор будет записан таким образом: "И. О. Фамилия" или же "Фаимилия И. О.".\nЕсли с первого раза Вы не нашли нужную книгу - попробуйте другой вариант)'
                    )

            elif event.obj['message']['text'][:10] == 'Проверить:':
                if event.from_user:
                    vk.messages.send(
                        user_id=event.obj['message']['from_id'],
                        random_id=event.obj['message']['random_id'],
                        message='Идёт поиск...'
                    )

                    conn = sqlite3.connect(
                        os.path.dirname(os.path.abspath(__file__)) + "/LC.db")  # Занесение данных в базу данных
                    cur = conn.cursor()
                    cur.execute("SELECT * FROM BOOK WHERE NAME LIKE '%{0}%' OR '{0}%' OR '%{0}'".format(
                        event.obj['message']['text'][12:]))
                    book = cur.fetchall()
                    cur.execute("SELECT * FROM SCHBOOK WHERE NAME LIKE '%{0}%' OR '{0}%' OR '%{0}'".format(
                        event.obj['message']['text'][12:]))
                    schbook = cur.fetchall()
                    cur.execute("SELECT * FROM SCHBOOK WHERE AUT LIKE '%{0}%' OR '{0}%' OR '%{0}'".format(
                        event.obj['message']['text'][12:]))
                    aut_schbook = cur.fetchall()
                    cur.execute("SELECT * FROM BOOK WHERE AUT LIKE '%{0}%' OR '{0}%' OR '%{0}'".format(
                        event.obj['message']['text'][12:]))
                    aut_book = cur.fetchall()

                    book_res = ''
                    schbook_res = ''
                    aut_book_res = ''
                    aut_schbook_res = ''

                    if (book == []) and (schbook == []) and (
                            aut_book == []) and (aut_schbook == []):
                        vk.messages.send(
                            user_id=event.obj['message']['from_id'],
                            random_id=event.obj['message']['random_id'],
                            message='Упс... Мы ничего не нашли.'
                        )
                    else:
                        for i in book:
                            for k in i:
                                book_res += str(k) + ' '
                            book_res += '\n'
                        for i in schbook:
                            for k in i:
                                schbook_res += str(k) + ' '
                            schbook_res += '\n'
                        for i in aut_book:
                            for k in i:
                                aut_book_res += str(k) + ' '
                            aut_book_res += '\n'
                        for i in aut_schbook:
                            for k in i:
                                aut_schbook_res += str(k) + ' '
                            aut_schbook_res += '\n'

                        vk.messages.send(
                            user_id=event.obj['message']['from_id'],
                            random_id=event.obj['message']['random_id'],
                            message='Результаты:\n\nПо названию среди книг:\n{0}\nПо названию среди учебников:\n{1}\nПо автору среди книг:\n{2}\nПо автору среди учебников:\n{3}'.format(
                                book_res, schbook_res, aut_book_res, aut_schbook_res)
                        )
            else:
                if event.from_user:
                    vk.messages.send(
                        user_id=event.obj['message']['from_id'],
                        random_id=event.obj['message']['random_id'],
                        message='Команда не найдена',
                        keyboard=keyboard_help.get_keyboard()
                    )


if __name__ == "__main__":
    app = Main()
    threading.Thread(target=vk_bot_start, args=[app, ]).start()
    app.protocol('WM_DELETE_WINDOW', withdraw_window)
    app.mainloop()