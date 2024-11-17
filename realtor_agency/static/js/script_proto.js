// static/js/script_proto.js

// Базовый класс DateBase
function DateBase(day, month, year) {
    this.day = day;
    this.month = month;
    this.year = year;
}

// Геттеры и сеттеры для дня
DateBase.prototype.getDay = function() {
    return this.day;
};

DateBase.prototype.setDay = function(day) {
    this.day = day;
};

// Геттеры и сеттеры для месяца
DateBase.prototype.getMonth = function() {
    return this.month;
};

DateBase.prototype.setMonth = function(month) {
    this.month = month;
};

// Геттеры и сеттеры для года
DateBase.prototype.getYear = function() {
    return this.year;
};

DateBase.prototype.setYear = function(year) {
    this.year = year;
};

// Метод отображения всех дат
DateBase.prototype.displayAllDates = function(array, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    array.forEach(function(date, index) {
        const div = document.createElement('div');
        div.textContent = `Дата ${index + 1}: ${date.getDay()}.${date.getMonth()}.${date.getYear()}`;
        container.appendChild(div);
    });
};

// Метод отображения весенних дат
DateBase.prototype.displaySpringDates = function(array, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    const springDates = array.filter(function(date) {
        return date.getMonth() >= 3 && date.getMonth() <= 5;
    });
    springDates.forEach(function(date, index) {
        const div = document.createElement('div');
        div.textContent = `Весенняя Дата ${index + 1}: ${date.getDay()}.${date.getMonth()}.${date.getYear()}`;
        container.appendChild(div);
    });
};

// Класс-наследник ExtendedDate добавляет параметр 'season'
function ExtendedDate(day, month, year) {
    DateBase.call(this, day, month, year);
    this.season = this.getSeason(month);
}

// Наследование прототипов
ExtendedDate.prototype = Object.create(DateBase.prototype);
ExtendedDate.prototype.constructor = ExtendedDate;

// Метод определения сезона по месяцу
ExtendedDate.prototype.getSeason = function(month) {
    if (month >= 3 && month <= 5) return 'Весна';
    if (month >= 6 && month <= 8) return 'Лето';
    if (month >= 9 && month <= 11) return 'Осень';
    return 'Зима';
};

// Геттер и сеттер для сезона
ExtendedDate.prototype.getSeasonProperty = function() {
    return this.season;
};

ExtendedDate.prototype.setSeason = function(season) {
    this.season = season;
};

// Метод добавления даты в массив
ExtendedDate.prototype.addDate = function(array) {
    this.season = this.getSeason(this.month);
    array.push(this);
};

// Массив для хранения дат
const datesArray = [];

// Обработка формы добавления даты
document.getElementById('dateForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const day = parseInt(document.getElementById('day').value);
    const month = parseInt(document.getElementById('month').value);
    const year = parseInt(document.getElementById('year').value);

    // Проверка корректности введенных данных
    if (isNaN(day) || isNaN(month) || isNaN(year)) {
        alert('Пожалуйста, введите корректные значения для дня, месяца и года.');
        return;
    }

    const newDate = new ExtendedDate(day, month, year);
    newDate.addDate(datesArray);

    // Отображение всех дат и весенних дат
    newDate.displayAllDates(datesArray, 'allDates');
    newDate.displaySpringDates(datesArray, 'springDates');
});

// Обработка нажатия на кнопку сохранения весенних дат
document.getElementById('downloadButton').addEventListener('click', function() {
    const springDates = datesArray.filter(function(date) {
        return date.getMonth() >= 3 && date.getMonth() <= 5;
    });

    if (springDates.length === 0) {
        alert('Нет весенних дат для сохранения.');
        return;
    }

    const fileContent = springDates.map(function(date) {
        return `${date.getDay()}.${date.getMonth()}.${date.getYear()}`;
    }).join('\n');

    downloadFile('g.txt', fileContent);
});

// Функция для скачивания файла
function downloadFile(filename, content) {
    const element = document.createElement('a');
    const file = new Blob([content], {type: 'text/plain'});
    element.href = URL.createObjectURL(file);
    element.download = filename;
    document.body.appendChild(element); // Для Firefox
    element.click();
    document.body.removeChild(element);
}
