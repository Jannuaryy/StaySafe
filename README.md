# StaySafe
## Что делает StaySafe?
StaySafe - это программа для шифрования файлов.
На вход получает файл и шифрует/дешифрует его на мастер-пароле. Далее она его переписывает или копирует в указанную директорию.
К зашифрованным файлам программа добавляет расширение _.enc_  и, соответственно, уберает его при расшифровке.
## Инструкция по установке 
1. Распакуйте архив 
2. Запустите файл main.py 
3. Прогрмма готова к использованию
## Структура классов 
* **class StaySafe_Mainwindow(QMainWindow)** -  основное окно приложения. По умолчанию имеет кнопки:
  1. Выбор файла 
  2. Выбор пути сохранения 
  3. Кнопки шифровать/дешифровать (при нажатии открывается диалог пароля)
  4. Кнопка вызова диалога настроек
* **class Settings(QDialog)** - диалог настроек, имеет функционал
  1. Выбор темы (оформления приложения)
  2. Способ сохраниния результата: Сохранить копию файла или переписать уже имеющийся (При выборе скрывает/отображает выбор пути сохранения в основном окне приложения)
  3. Возможность выбора языка интерфейса (Планируется к выпуску в следующем релизе)

* **class Password_dialog(QDialog)** - диалог ввода пароля. Имеет возможность отображения пароля в открытом или скрытом от глаз виде. По нажатию на кнопку Ок вызывается процедура (рас)шифрования
## Используемые в проекте технологии
1. Библиотека PyQt6 - для создания пользовательского интерфейса 
2. Библиоткеа os - для работы с файловой системой
3. Библиотека sys - для запуска приложений
4. QStyleFactory - для управления темой приложения
5. оператор XOR -  для произведения (рас)шифрования файлов. В перспективе планруется выбор различных алгаритмов шифрования
6. sqlite3 - для ведения БД событий программы
7. csv.DictReader - для чтения файлов в формате csv
## Статус программы 
_Выпушен первый релиз программы. Некоторые функции запланированы к разработке в будущем_


