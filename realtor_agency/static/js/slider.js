document.addEventListener('DOMContentLoaded', () => {
    // --- Начало кода для обратного отсчета ---
    const countdownElement = document.getElementById('countdown');
    const hoursSpan = document.getElementById('hours');
    const minutesSpan = document.getElementById('minutes');
    const secondsSpan = document.getElementById('seconds');

    // Функция для обновления обратного отсчета
    function updateCountdown(endTime) {
        const now = new Date().getTime();
        const distance = endTime - now;

        if (distance < 0) {
            clearInterval(countdownInterval);
            countdownElement.innerHTML = "Время истекло!";
            return;
        }

        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        hoursSpan.textContent = String(hours).padStart(2, '0');
        minutesSpan.textContent = String(minutes).padStart(2, '0');
        secondsSpan.textContent = String(seconds).padStart(2, '0');
    }

    // Функция для инициализации обратного отсчета
    function initializeCountdown() {
        let endTime = localStorage.getItem('countdownEndTime');

        if (!endTime) {
            const now = new Date().getTime();
            endTime = now + (60 * 60 * 1000); // Добавляем 1 час
            localStorage.setItem('countdownEndTime', endTime);
        } else {
            endTime = parseInt(endTime, 10);
        }

        updateCountdown(endTime); // Обновляем сразу при загрузке

        // Устанавливаем интервал для обновления каждую секунду
        countdownInterval = setInterval(() => updateCountdown(endTime), 1000);
    }

    // Запуск инициализации обратного отсчета
    initializeCountdown();
    // --- Конец кода для обратного отсчета ---

    // --- Начало кода для слайдера ---
    const slides = document.querySelectorAll('.slide');
    const dots = document.querySelectorAll('.doti');
    const prev = document.querySelector('.prev');
    const next = document.querySelector('.next');
    const intervalInput = document.getElementById('interval');
    const setIntervalBtn = document.getElementById('set-interval');
    const slideNumber = document.querySelector('.slide-number');

    // Configuration Parameters
    const config = {
        loop: true,           // true or false
        navs: true,           // true or false
        pags: true,           // true or false
        auto: true,           // true or false
        stopMouseHover: true, // true or false
        delay: 5              // seconds
    };

    let current = 0;
    let slideInterval = config.delay * 1000;
    let timer = null;

    function showSlide(index) {
        slides.forEach((slide, i) => {
            slide.style.display = (i === index) ? 'block' : 'none';
            if (config.pags && dots[i]) {
                dots[i].classList.toggle('active', i === index);
            }
        });
        if (config.pags && slideNumber) {
            slideNumber.textContent = `${index + 1}/${slides.length}`;
        }
        current = index;
    }

    function nextSlide() {
        let index = (current + 1) % slides.length;
        if (index === 0 && !config.loop) {
            stopAutoSlide();
            return;
        }
        showSlide(index);
    }

    function prevSlideFunc() {
        let index = (current - 1 + slides.length) % slides.length;
        if (index === slides.length - 1 && !config.loop) {
            stopAutoSlide();
            return;
        }
        showSlide(index);
    }

    function startAutoSlide() {
        if (config.auto && slides.length > 1 && !timer) {
            timer = setInterval(nextSlide, slideInterval);
            console.log(`Auto-sliding started with interval ${slideInterval} ms`);
        }
    }

    function stopAutoSlide() {
        if (config.auto && timer) {
            clearInterval(timer);
            timer = null;
            console.log('Auto-sliding stopped');
        }
    }

    // Event Listeners
    if (config.navs && slides.length > 1) {
        if (prev) {
            prev.addEventListener('click', () => {
                stopAutoSlide();
                prevSlideFunc();
                startAutoSlide();
            });
        }

        if (next) {
            next.addEventListener('click', () => {
                stopAutoSlide();
                nextSlide();
                startAutoSlide();
            });
        }
    } else {
        if (prev) prev.style.display = 'none';
        if (next) next.style.display = 'none';
    }

    if (config.pags && slides.length > 1) {
        dots.forEach(dot => {
            dot.addEventListener('click', () => {
                stopAutoSlide();
                const index = parseInt(dot.dataset.index);
                if (!isNaN(index)) {
                    showSlide(index);
                    startAutoSlide();
                }
            });
        });
    } else {
        const dotsContainer = document.querySelector('.dotsis');
        if (dotsContainer) dotsContainer.style.display = 'none';
        if (slideNumber) slideNumber.style.display = 'none';
    }

    if (config.auto && slides.length > 1) {
        if (setIntervalBtn && intervalInput) {
            setIntervalBtn.addEventListener('click', () => {
                const seconds = parseInt(intervalInput.value);
                if (seconds > 0) {
                    slideInterval = seconds * 1000;
                    console.log(`Slide interval set to ${slideInterval} ms`);
                    stopAutoSlide();
                    startAutoSlide();
                } else {
                    console.log('Invalid interval input');
                }
            });
        }
    } else {
        const sliderForm = document.getElementById('slider-form');
        if (sliderForm) sliderForm.style.display = 'none';
    }

    if (config.stopMouseHover && config.auto && slides.length > 1) {
        const slider = document.querySelector('.slider');
        if (slider) {
            slider.addEventListener('mouseenter', () => {
                stopAutoSlide();
                console.log('Mouse entered slider, auto-sliding stopped');
            });
            slider.addEventListener('mouseleave', () => {
                startAutoSlide();
                console.log('Mouse left slider, auto-sliding started');
            });
        }
    }

    // Initialize Slider
    if (slides.length > 0) {
        showSlide(current);
        startAutoSlide();
    }
    // --- Конец кода для слайдера ---
});
