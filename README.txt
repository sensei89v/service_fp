Данный сервер - является синхронным и однопоточным по той причине, 
что парсинг по условию задачи упирается только в процессор. Необходимость многопоточности
на данный момент не ясна, т.к. нет никакой информации о пользовательской нагрузке.
Многопоточность ради многопоточности ведет к усложнению кода и доп. расходам на синхронизацию.
Web приложение реализовано на Python-2.7.

Как разворачивать:
1) virtualenv <путь к окружению>
2) source <путь к окружению>/bin/activate
3) pip install -r requirement.txt

Как запускать:
./main.py <Путь к конфигурационному файлу>

Конфигурационный файл представляет собой JSON-объект со следующими полями
server_port - порт, который будет слушать сервер.
obsolete_time - время (в секундах) с момента последнего обращения, 
                при котором идентификатор документа считается устаревшим.
clean_period - частота (в секундах) запуска очистки хранилища от устаревших
               идентификаторов документов.
html - путь к директории с .html файлами.
css  - путь к директории с .css файлами.
js   - путь к директории с .js файлами.

Состав проекта:
main.py - входная точка приложения
options.py - файл, содержащий класс для парсинга конфигурационного файла
parser.py - файл, содержащий классы парсеров документов, а так же функции для работы с ними
server.py - файл, содержащий класс-сервер, а так же классы-обработчики запросов
storage.py - файл, содержащий классы для организации хранилища
config.json - пример конфигурационного файла
requirement.txt - текстовый файл с необходимыми для работы приложения модулями
html - директория с .html файлами
css  - директория с .css файлами
js   - директория с .js файлами

Сделать в первую очередь;
1. Разобраться как из Javascript получить доступ к ранее использовавшемуся файлу 
   не костыльным методом

Дальнейшие доработки;
1. Утвердить дизайн и сделать его не таким вырвиглазным.
2. Навести порядок в JS файле, текстовые сообщения вынести в константы, 
   провести унификацию запросров.
3. При увеличении нагрузки задуматься об асинхронности либо использовании нескольких ядер.
4. При увеличении нагрузки задуматься об использовании БД или иных внешних хранилищ.
5. Сделать тесты.
6. Сделать механизм деплоя.
7. Сделать отдельную страницу на ошибку 404.
8. Минификация JavaScript.
9. Переделать этот документ под MD-разметку.
