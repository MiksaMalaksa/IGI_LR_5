// static/js/script_class.js

// Базовый класс DateBase
class DateBase {
    constructor(day, month, year) {
        this._day = day;
        this._month = month;
        this._year = year;
    }

    // Геттеры и сеттеры для дня
    get day() {
        return this._day;
    }

    set day(day) {
        this._day = day;
    }

    // Геттеры и сеттеры для месяца
    get month() {
        return this._month;
    }

    set month(month) {
        this._month = month;
    }

    // Геттеры и сеттеры для года
    get year() {
        return this._year;
    }

    set year(year) {
        this._year = year;
    }

    // Метод отображения всех дат
    displayAllDates(array, containerId) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';
        array.forEach((date, index) => {
            const div = document.createElement('div');
            div.textContent = `Дата ${index + 1}: ${date.day}.${date.month}.${date.year}`;
            container.appendChild(div);
        });
    }

    // Метод отображения весенних дат
    displaySpringDates(array, containerId) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';
        const springDates = array.filter(date => date.month >= 3 && date.month <= 5);
        springDates.forEach((date, index) => {
            const div = document.createElement('div');
            div.textContent = `Весенняя Дата ${index + 1}: ${date.day}.${date.month}.${date.year}`;
            container.appendChild(div);
        });
    }
}

// Класс-наследник ExtendedDate добавляет параметр 'season'
class ExtendedDate extends DateBase {
    constructor(day, month, year) {
        super(day, month, year);
        this._season = this.getSeason(month);
    }

    // Геттер и сеттер для сезона
    get season() {
        return this._season;
    }

    set season(season) {
        this._season = season;
    }

    // Метод добавления даты в массив
    addDate(array) {
        this._season = this.getSeason(this.month);
        array.push(this);
    }

    // Метод определения сезона по месяцу
    getSeason(month) {
        if (month >= 3 && month <= 5) return 'Весна';
        if (month >= 6 && month <= 8) return 'Лето';
        if (month >= 9 && month <= 11) return 'Осень';
        return 'Зима';
    }
}

// Массив для хранения дат
const datesArray = [];

// Обработка формы добавления даты
document.getElementById('dateForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const day = parseInt(document.getElementById('day').value);
    const month = parseInt(document.getElementById('month').value);
    const year = parseInt(document.getElementById('year').value);

    const newDate = new ExtendedDate(day, month, year);
    newDate.addDate(datesArray);

    // Отображение всех дат и весенних дат
    newDate.displayAllDates(datesArray, 'allDates');
    newDate.displaySpringDates(datesArray, 'springDates');

    // Сохранение весенних дат в файл (скачивание файла)
    const springDates = datesArray.filter(date => date.month >= 3 && date.month <= 5);
    const fileContent = springDates.map(date => `${date.day}.${date.month}.${date.year}`).join('\n');
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
