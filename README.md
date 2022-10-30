# praktikum_new_diplom
Сайт с проектом: http://51.250.110.182/
Работает всё кроме страниц: 
* http://51.250.110.182/subscriptions
* http://51.250.110.182/user/1

Получилось настроить механизм подписок. Пермишены скорректировал. Комментарии .
По прежнему не работают 2 вышеуказанных урла.
Данные для входа в админку:
email: admin@admin.com
password: admin
Логи по ошибкам в контейнере бэка выглядят минималистично:
igorkalchenko-web-1  | Not Found: /api/users/subscriptions/
igorkalchenko-web-1  | Bad Request: /api/recipes/
В консоле разработчика:

http://51.250.110.182/user/1:
{author: Array(1)}
author
: 
['Выберите корректный вариант. 1 нет среди допустимых значений.']
[[Prototype]]
: 
Object

http://51.250.110.182/subscriptions:
/subscriptions:1 Uncaught (in promise) 
{detail: 'Страница не найдена.'}
detail
: 
"Страница не найдена."
[[Prototype]]
: 
Object
