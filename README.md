<p align="center">
  <img src="https://i.ibb.co/0ypVVJGp/photo-2025-02-02-14-05-59-no-bg-preview-carve-photos.png" width="400" alt="Бот расписания ФКН ВГУ">
</p>

<h1 align="center">📅 Бот расписания ФКН ВГУ</h1>

<p align="center">
  <strong>Удобный доступ к расписанию занятий Факультета Компьютерных Наук Воронежского Государственного Университета</strong>
</p>

<p align="center">
  <a href="#о-проекте">О проекте</a> • 
  <a href="#быстрый-старт">Быстрый старт</a> • 
  <a href="#api-документация">API документация</a> • 
  <a href="#разработчики">Разработчики</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/версия-1.0.0-blue" alt="Версия">
  <img src="https://img.shields.io/badge/статус-активный-brightgreen" alt="Статус">
  <img src="https://img.shields.io/badge/API-доступно-orange" alt="API">
</p>

<br/>
<br/>

## О проекте

Бот предоставляет удобный доступ к расписанию занятий ФКН ВГУ через Telegram-интерфейс и REST API. Текущая версия поддерживает получение данных по API с возможностью фильтрации по курсу, группе, подгруппе и дню недели.

**Основные возможности:**
- 📊 Получение актуального расписания
- 🔍 Фильтрация по различным параметрам
- 🤖 Удобный Telegram-бот
- 🌐 REST API для интеграции с другими сервисами


<br/>
<br/>

## Быстрый старт

В этом разделе представлено краткое руководство по началу работы с API бота.

### Получение API-ключа

1. Перейдите в [Telegram-бот](https://t.me/fkn_vsu_schedule_bot)
2. Введите команду `/start` (если еще не делали этого)
3. Введите команду `/getapi` для получения ключа
4. Сохраните полученный ключ (включая знак '=' в конце)

### Пример использования API

Создайте папку `bot_api/` и добавьте в нее два файла:

#### index.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Пример</title>
</head>
<body>
<div style="display: grid; grid-column-gap: 1em; grid-template-columns: 1fr 1fr;">
    <form style="display: grid; grid-row-gap: 1em; grid-template-columns: 1fr;">
        <label> Курс:
            <input id="course" type="number" min="1" max="4">
        </label>

        <label> Группа:
            <input id="group" type="number" min="1" max="20">
        </label>

        <label> Подгруппа:
            <input id="sub-group" type="number" min="1" max="2">
        </label>

        <label> День недели:
            <select id="day">
                <option value="0">Понедельник</option>
                <option value="1">Вторник</option>
                <option value="2">Среда</option>
                <option value="3">Четверг</option>
                <option value="4">Пятница</option>
                <option value="5">Суббота</option>
            </select>
        </label>

        <button id="submit" style="width: 10em">Получить расписание</button>
    </form>
    <div id="output"></div>
</div>
<script src="index.js"></script>
</body>
</html>
```

#### index.js
```js
const button = document.querySelector('#submit');
const course = document.querySelector('#course');
const group = document.querySelector('#group');
const subGroup = document.querySelector('#sub-group');
const day = document.querySelector('#day');

button.addEventListener('click', async event => {
    event.preventDefault();
    let response = await fetch(
        `https://platovd.ru/api/schedule/<API ключ>/${course.value}/${group.value}/${subGroup.value}/${day.value}`,
        {
            method: 'POST',
            headers: {}
            }
    )

    let data = await response.json();
    displaySchedule(data)
})

function displaySchedule(data) {
    const outputDiv = document.querySelector('#output');
    outputDiv.innerHTML = '';
    let h = document.createElement("h2");
    h.innerText = data.day;
    outputDiv.appendChild(h);
    console.log(data.schedule)
    for (const [time, lesson] of Object.entries(data.schedule)) {
        let p = document.createElement("p")
        p.innerText = `${time} - ${lesson}`
        outputDiv.appendChild(p)
    }
}
```
> **Важно:** Замените `<API ключ>` на ваш действительный API-ключ.

Теперь Вы можете открыть свой html в браузере и выполнить запрос. Если все получилось, то вы увидите расписание, которое запросили у сервера.

<br/>
<br/>

## API документация

### Структура запроса

Сервер ожидает POST-запрос следующего формата:

```

https://platovd.ru/api/schedule/{token}/{course}/{group}/{subgroup}/{day}

```


#### Параметры:

| Параметр   | Тип    | Описание                                                                 | Допустимые значения         |
|------------|--------|-------------------------------------------------------------------------|-----------------------------|
| `token`    | string | Ваш уникальный API-ключ, полученный от бота                             | Ваш API ключ от бота        |
| `course`   | number | Номер курса, для которого нужно получить расписание                     | Цифры от 1 до 4             |
| `group`    | number | Номер группы, для которой нужно получить расписание                     | Числа от 1 до 20(зависит от курса)            |
| `subgroup` | number | Номер подгруппы                                                         | 1 или 2                     |
| `day`      | number | День недели (0 - понедельник, 1 - вторник, и т.д.)                      | Числа от 0 до 6             |

> **Примечание:** Тип недели (числитель/знаменатель) определяется автоматически на основе текущей учебной недели.

### Пример ответа API

```json
{
    "course": 1,
    "group": 6,
    "sub_group": 2,
    "day": "четверг",
    "schedule": {
        "8:00-9:35": null,
        "9:45-11:20": "Ин.яз. преп. Семенов В.П. 303П",
        "11:30-13:05": "АиСД асс. Проскуряков Е.Д. 291",
        "13:25-15:00": "Архитектура ВС (id=3) доц. Ветохин В.В. 291",
        "15:10-16:45": "Дискретная математика (id=20352) доц. Попов М.И. 305П",
        "16:55-18:30": null,
        "18:40-20:00": null,
        "20:10-21:30": null
    }
}
```


<br/>
<br/>

## Разработчики

Проект разработан студентами ФКН ВГУ:

- [**Меркулов Роман**](https://github.com/Merkury2006) 
- [**Платов Дмитрий**](https://github.com/PlatovD)


<br/>
<br/>

## Обратная связь

Мы открыты для предложений и сотрудничества! Если у вас есть:

- 💡 Идеи по улучшению функционала
- 🐛 Обнаружили ошибку в работе API
- 🤝 Предложения по сотрудничеству
- ❓ Вопросы по интеграции API

**Свяжитесь с нами:**
- Через Issues на GitHub
- Лично в Telegram: [Платов Дмитрий](https://t.me/DimaPlatov09)


<div align="center">

<br/>
<br/>

**Мы рады, что вы используете наше API!** 🎉

Пусть ваш код будет чистым, а расписание - удобным! 🚀

</div>

<p align="center">
  <sub>С любовью к кодерам от разработчиков ФКН ВГУ</sub>
</p>