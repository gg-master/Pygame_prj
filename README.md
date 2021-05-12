# Pygame_prj
Вся информация анонимизирована.
<h3>Вступление</h3>
"TanksBattle" - Игра на pygame от 2-х creative developers. 

<br>Перед нами стояла цель разработать программный продукт с использованием библиотеки pygame, который позволит пользователю окунуться в бесконечный мир танковых боев, почувствовать себя настоящим танкистом, управляя собственным танком.

<h5>ТЗ:</h5>
1) Cоздать игру с использованием библиотеки Pygame<br>
2) Реализовать работоспособный код клиента игры и код меню игры.<br>
3) Реализовать изменение настроект игры пользователем.<br>

Ознакомиться с подробным описанием нашего проекта, а также его технической составляющей можно в пояснительный записке к проекту (см. файл PZ_dlya_irgry.docx).

<h3>Запуск</h3>
<h6><a href='https://drive.google.com/file/d/1dTjPf3GJn8iC5QDg-0xzShJfi_qaQ72O/view?usp=sharing'>Скачать запускаемый exe файл.</a></h6>

<h5>Запуск из кода</h5>Необходимые библиотеки (не идут вместе с python):
1) Pygame
2) pytmx

Все необходимые библиотеки описаны в requirements.txt.

<i><b>Чтобы запустить игру необходимо запустить файл main_menu.py из папки modules.</b></i>

<small>Имеется возможность отдельно запустить клиент игры (без меню) - запустить файл client.py из папки modules. 
В этом случае по-умолчанию запустится первый уровень игры на 1 человека. 

Можно изменить уровень и тип игры из самого кода. 
Для этого необходимо изменить первые две цифры в следующей строке: 

client = Client(1, 1, screen) 

в файл client.py,
 где первый параметр это тип игры - (1 - игра на одного, 2 - игра на двоих) и 
 второй параметр это уровень игры (всего доступно 20 различных уровней, если указан уровень другой, то 
 программа рандомно выберет один из 20 уровней).</small>

<a href='https://drive.google.com/file/d/1neXNqLHImhfI8Z2sXwp5gpoDOdQ4Fn5u/view?usp=sharing'><h3>Видео демонстрация</h3></a>
<h3>При запуске</h3>
<h5>Что вкратце происходит при запуске клиента игры</h5>
1) Загружаются настройки игры из json объекта.
2) Загружается вся музыка игры.
3) Создаются все объекты игры: загружается карта, картинки игровых объектов, 
создается менеджер ботов, объекты танков игроков, а также окна меню выхода и паузы.
4) Запускается основной игрвой цикл, 
в котором происходит перехват событий (нажатие клавиш на клавиатуре и пр.), 
обновление игрвого мира и его отрисовка. Кроме этого, 
в основном цикле можно перехватывать событие выхода в главное меню.
5) Далее уже клиент игры отвечает за обработку нажатых клавиш, 
обновление объекта игры, воспроизведение музыки и отрисовку игровых объектов.
6) Сам объект игры заставляет обновляться остальные игровые объекты, 
отвечает за передачу названий звуковых треков в объект клиента, 
проверяет состояние игры, и прочие действия при загрузке объектов.
7) Остальные объекты лишь обновляют свое состояние и изменяют его в 
зависимости от таймеров либо от действий игрока.

<h5>Что из себя представляет код меню и как он работает</h5>
* Каждое окно меню представляет из себя функцию. 
* Главная функция запускает стартовый экран, при переключении на другой экран, 
функция стартового экрана завершается и запускается функция другого окна.
* При переключении на другой экран, запускается функция соответствующего окна,
 а функция активного завершается.

<h3>Как создать свою карту?</h3>
1. Необходимо установить приложение Tiled Map Editor. 
<a href='https://www.mapeditor.org/'>Вот офф сайт</a>
2. Создать новую карту со следующими настройками:
    * Ориентация - Ортогональная
    * Формат слоя тайлов - Base64 (zlib сжатие)
    * Порядок отрисовки тайлов - Справа снизу
    * Размер тайлов тайлов:
        * Ширина и Высота - 80 точек
    * Размер карты. Может быть любым, но рекомендуемые:
        * Ширина и Высота - 13 тайлов
3. Добавить (если еще не добавлен) новый набор тайлов.<br>
Вот доступные картинки тайлов и их описание<br>
![alt tag](https://disk.yandex.ru/i/pepn8fJ4sUWvFg "Тайлы и их краткое описание")

    Вот настройки, который необходимо выставить в Tiled Map Editor
    * Тип - основано на изображении набора тайлов.
    * Источник - путь_к_корню_проекта/data/maps/tileds.png
    * Цвет прозрачности - по умолчанию
    * Ширина и Высота - 80 точек
    * Отступ и Промежуток - 0 точек
4. Игровая карта обязана содержать следующие слои и объекты: 
    *	Слои: ground (земля), spawn_players (клетки для спавна игрока),
spawn_bots (клетки для спавна бота)
    *	Объекты: eagle (орел)

5. Также карта может содержать следующие слои и объекты:
    *	Слои: trees (деревья)
    *	Объекты: walls (стены)

6. Новую карту необходимо сохранить под названием map{номер карты}.tmx в 
папке путь_к_корню_проекта\data\maps. Пример: map21.tmx

7. Теперь, поиграть на новой карте можно, запустив код из файла client.py, 
предварительно изменив строку <br><br>
client = Client(1, 1, screen), где вместо 2-го параметра необходимо указать номер нового уровня.

P.S. Если вдруг что-то стало непонятно по созданию уровня в Tiled Map Editor, 
то в нем можно открыть одну из доступных 
карт и ознакомиться с тем, какие слои содержат какие элементы,
 как нужно правильно подписать и расположить объекты и тд.