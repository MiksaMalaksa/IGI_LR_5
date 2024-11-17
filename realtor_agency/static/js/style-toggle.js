// static/js/style-toggle.js

document.addEventListener('DOMContentLoaded', () => {
    const styleToggleCheckbox = document.getElementById('style-toggle-checkbox');
    const styleControls = document.getElementById('style-controls');
    const fontSizeSlider = document.getElementById('font-size');
    const fontSizeValue = document.getElementById('font-size-value');
    const textColorPicker = document.getElementById('text-color');
    const backgroundColorPicker = document.getElementById('background-color');

    // Показать или скрыть элементы управления стилями
    styleToggleCheckbox.addEventListener('change', () => {
        if (styleToggleCheckbox.checked) {
            styleControls.style.display = 'block';
        } else {
            styleControls.style.display = 'none';
        }
    });

    // Изменение размера шрифта
    fontSizeSlider.addEventListener('input', () => {
        const size = fontSizeSlider.value + 'px';
        document.body.style.fontSize = size;
        fontSizeValue.textContent = size;
    }); 

    // Изменение цвета текста
    textColorPicker.addEventListener('input', () => {
        document.body.style.color = textColorPicker.value;
    });

    // Изменение цвета фона страницы
    backgroundColorPicker.addEventListener('input', () => {
        document.body.style.backgroundColor = backgroundColorPicker.value;
    });
});
