// static/js/contacts.js

document.addEventListener('DOMContentLoaded', () => {
    const tableBody = document.querySelector('#contacts-table tbody');
    const paginationContainer = document.getElementById('pagination');
    const filterInput = document.getElementById('filter-input');
    const filterBtn = document.getElementById('filter-btn');
    const addContactBtn = document.getElementById('add-contact-btn');
    const addContactModal = document.getElementById('add-contact-modal');
    const closeModal = document.querySelector('.modal .close');
    const addContactForm = document.getElementById('add-contact-form');
    const submitAddContactBtn = document.getElementById('submit-add-contact');
    const formMessage = document.getElementById('form-message');
    const rewardBtn = document.getElementById('reward-btn');
    const rewardText = document.getElementById('reward-text');
    const contactCard = document.getElementById('contact-card'); // Добавляем элемент для карточки
    
    let contactsData = [];
    let filteredData = [];
    let currentPage = 1;
    const rowsPerPage = 3; // Установить максимум 3 элемента на страницу
    let currentSortColumn = null;
    let currentSortOrder = 'asc'; // 'asc' или 'desc'

    // Функции для управления прелоадером внутри таблицы
    function showTablePreloader() {
        // Проверяем, существует ли уже строка с прелоадером
        if (!document.querySelector('#contacts-table tbody .preloader-row')) {
            const preloaderTr = document.createElement('tr');
            preloaderTr.classList.add('preloader-row');
            preloaderTr.innerHTML = `
                <td colspan="8" class="preloader-cell">
                    <div class="table-preloader">
                        <div class="dot"></div>
                        <div class="dot"></div>
                        <div class="dot"></div>
                    </div>
                </td>
            `;
            tableBody.innerHTML = ''; // Очищаем текущее содержимое таблицы
            tableBody.appendChild(preloaderTr);
        }
    }

    function hideTablePreloader() {
        const preloaderTr = document.querySelector('#contacts-table tbody .preloader-row');
        if (preloaderTr) {
            preloaderTr.remove();
        }
    }

    // Функция для загрузки контактов с сервера
    async function loadContacts() {
        showTablePreloader();
        try {
            const response = await fetch('/api/contacts/');
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            contactsData = data.contacts;
            filteredData = [...contactsData];
            renderTable();
            renderPagination();
        } catch (error) {
            console.error('Ошибка при загрузке контактов:', error);
            tableBody.innerHTML = '<tr><td colspan="8">Ошибка при загрузке контактов.</td></tr>';
        } finally {
            hideTablePreloader();
        }
    }

    // Функция для рендеринга таблицы
    function renderTable() {
        tableBody.innerHTML = '';
        const start = (currentPage - 1) * rowsPerPage;
        const end = start + rowsPerPage;
        const paginatedContacts = filteredData.slice(start, end);

        if (paginatedContacts.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="8">Контакты не найдены.</td></tr>';
            return;
        }

        paginatedContacts.forEach(contact => {
            const tr = document.createElement('tr');
            tr.dataset.id = contact.id;

            // Определение пути к изображению
            const imageUrl = contact.image ? contact.image : '';

            tr.innerHTML = `
                <td><input type="checkbox" class="select-checkbox" data-id="${contact.id}"></td>
                <td>${contact.employer__first_name}</td>
                <td>${contact.employer__last_name}</td>
                <td>
                    ${imageUrl ? `<img src="${imageUrl}" alt="Фото ${contact.employer__first_name}" class="contact-photo">` : 'No image'}
                </td>
                <td>${contact.employer__job}</td>
                <td>${contact.employer__phone_number}</td>
                <td><a href="mailto:${contact.employer__email}" class="email-link">${contact.employer__email}</a></td>
                <td><a href="${contact.website || '#'}" target="_blank" class="website-link">${contact.website || 'N/A'}</a></td>
            `;
            tableBody.appendChild(tr);
        });
    }

    // Функция для рендеринга пагинации
    function renderPagination() {
        paginationContainer.innerHTML = '';
        const totalPages = Math.ceil(filteredData.length / rowsPerPage);
        if (totalPages <=1 ) return; // Если страниц меньше или равно 1, пагинация не нужна

        for (let i = 1; i <= totalPages; i++) {
            const btn = document.createElement('button');
            btn.textContent = i;
            btn.classList.add('page-btn');
            if (i === currentPage) btn.classList.add('active');
            btn.addEventListener('click', () => {
                currentPage = i;
                showTablePreloader();
                setTimeout(() => { // Симуляция короткой задержки для прелоадера
                    renderTable();
                    renderPagination();
                    hideTablePreloader();
                }, 500); // 0.5 секунды
            });
            paginationContainer.appendChild(btn);
        }
    }

    // Функция для сортировки контактов
    function sortContacts(column) {
        if (currentSortColumn === column) {
            currentSortOrder = currentSortOrder === 'asc' ? 'desc' : 'asc';
        } else {
            currentSortColumn = column;
            currentSortOrder = 'asc';
        }

        filteredData.sort((a, b) => {
            let valA = a[column];
            let valB = b[column];

            // Приведение к верхнему регистру для строк
            if (typeof valA === 'string') valA = valA.toUpperCase();
            if (typeof valB === 'string') valB = valB.toUpperCase();

            if (valA < valB) return currentSortOrder === 'asc' ? -1 : 1;
            if (valA > valB) return currentSortOrder === 'asc' ? 1 : -1;
            return 0;
        });

        updateSortIndicators();
        currentPage = 1;
        showTablePreloader();
        setTimeout(() => { // Симуляция короткой задержки для прелоадера
            renderTable();
            renderPagination();
            hideTablePreloader();
        }, 500); // 0.5 секунды
    }

    // Функция для обновления индикаторов сортировки
    function updateSortIndicators() {
        const headers = document.querySelectorAll('#contacts-table th.sortable');
        headers.forEach(header => {
            header.classList.remove('asc', 'desc');
            if (header.dataset.column === currentSortColumn) {
                header.classList.add(currentSortOrder);
            }
        });
    }

    // Функция для фильтрации контактов
    function filterContacts() {
        showTablePreloader();
        setTimeout(() => { // Симуляция короткой задержки для прелоадера
            const query = filterInput.value.toLowerCase().trim();
            if (query === '') {
                filteredData = [...contactsData];
            } else {
                filteredData = contactsData.filter(contact => {
                    return (
                        contact.employer__first_name.toLowerCase().includes(query) ||
                        contact.employer__last_name.toLowerCase().includes(query) ||
                        contact.employer__job.toLowerCase().includes(query) ||
                        contact.employer__phone_number.toLowerCase().includes(query) ||
                        contact.employer__email.toLowerCase().includes(query) ||
                        (contact.website && contact.website.toLowerCase().includes(query))
                    );
                });
            }
            currentPage = 1;
            renderTable();
            renderPagination();
            hideTablePreloader();
            contactCard.innerHTML = ''; // Скрыть карточку при фильтрации
        }, 500); // 0.5 секунды
    }

    // Открытие модального окна
    addContactBtn.addEventListener('click', () => {
        addContactModal.style.display = 'block';
    });

    // Закрытие модального окна
    closeModal.addEventListener('click', () => {
        addContactModal.style.display = 'none';
        addContactForm.reset();
        submitAddContactBtn.disabled = true;
        formMessage.textContent = '';
        removeValidationClasses();
    });

    // Закрытие модального окна при клике вне его
    window.addEventListener('click', (e) => {
        if (e.target === addContactModal) {
            addContactModal.style.display = 'none';
            addContactForm.reset();
            submitAddContactBtn.disabled = true;
            formMessage.textContent = '';
            removeValidationClasses();
        }
    });

    // Валидация формы
    addContactForm.addEventListener('input', () => {
        validateForm();
    });

    function validateForm() {
        const website = document.getElementById('website').value.trim();
        const phone = document.getElementById('phone_number').value.trim();

        let isValid = true;
        formMessage.textContent = '';

        // Валидация URL
        if (website) {
            const urlPattern = /^(http:\/\/|https:\/\/).*\.(php|html)$/;
            if (!urlPattern.test(website)) {
                isValid = false;
                displayInvalid('website');
                formMessage.textContent = 'Неверный формат URL.';
            } else {
                displayValid('website');
            }
        } else {
            displayValid('website');
        }

        // Валидация номера телефона
        const phonePattern = /^(\+375\s?\(\d{2}\)\s?\d{3}[-\s]?\d{2}[-\s]?\d{2}|8\s?\(?0\d{2}\)?\s?\d{3}[-\s]?\d{2}[-\s]?\d{2}|8\d{10})$/;
        if (!phonePattern.test(phone)) {
            isValid = false;
            displayInvalid('phone_number');
            formMessage.textContent = 'Неверный формат номера телефона.';
        } else {
            displayValid('phone_number');
        }

        // Проверка всех обязательных полей
        const requiredFields = ['first_name', 'last_name', 'job_description', 'phone_number', 'email'];
        requiredFields.forEach(field => {
            const value = document.getElementById(field).value.trim();
            if (!value) {
                isValid = false;
                displayInvalid(field);
                formMessage.textContent = 'Пожалуйста, заполните все обязательные поля.';
            } else {
                if (field !== 'website' && field !== 'photo') displayValid(field);
            }
        });

        // Управление состоянием кнопки
        submitAddContactBtn.disabled = !isValid;
    }

    function displayValid(fieldId) {
        const field = document.getElementById(fieldId);
        field.classList.remove('invalid');
        field.classList.add('valid');
    }

    function displayInvalid(fieldId) {
        const field = document.getElementById(fieldId);
        field.classList.remove('valid');
        field.classList.add('invalid');
    }

    function removeValidationClasses() {
        const inputs = addContactForm.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            input.classList.remove('valid', 'invalid');
        });
    }

    // Обработка отправки формы добавления контакта
    addContactForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = {
            first_name: document.getElementById('first_name').value.trim(),
            last_name: document.getElementById('last_name').value.trim(),
            job_description: document.getElementById('job_description').value.trim(),
            phone_number: document.getElementById('phone_number').value.trim(),
            email: document.getElementById('email').value.trim(),
            website: document.getElementById('website').value.trim(),
            photo: document.getElementById('photo').value.trim(),
        };

        showTablePreloader();
        try {
            const response = await fetch('/api/contacts/add/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify(formData),
            });
            const data = await response.json();
            if (data.success) {
                contactsData.push(data.contact);
                filteredData = [...contactsData];
                renderTable();
                renderPagination();
                addContactModal.style.display = 'none';
                addContactForm.reset();
                submitAddContactBtn.disabled = true;
                formMessage.textContent = '';
                removeValidationClasses();
                alert('Контакт успешно добавлен!');
            } else {
                formMessage.textContent = data.error || 'Ошибка при добавлении контакта.';
            }
        } catch (error) {
            console.error('Ошибка при добавлении контакта:', error);
            formMessage.textContent = 'Ошибка при добавлении контакта.';
        } finally {
            hideTablePreloader();
        }
    });

    // Получение CSRF токена
    function getCSRFToken() {
        let cookieValue = null;
        const name = 'csrftoken';
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i=0; i<cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length+1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length+1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Сортировка при клике на заголовок столбца
    const sortableHeaders = document.querySelectorAll('#contacts-table th.sortable');
    sortableHeaders.forEach(header => {
        header.addEventListener('click', () => {
            const column = header.dataset.column;
            sortContacts(column);
        });
    });

    // Фильтрация при нажатии на кнопку "Find" и при вводе
    filterBtn.addEventListener('click', () => {
        filterContacts();
    });

    filterInput.addEventListener('input', () => {
        filterContacts();
    });

    // Обработка клика на строку таблицы для отображения полной информации
    tableBody.addEventListener('click', (e) => {
        const tr = e.target.closest('tr');
        if (tr && !e.target.classList.contains('select-checkbox')) {
            const contactId = tr.dataset.id;
            const contact = contactsData.find(c => c.id == contactId);
            if (contact) {
                // Отобразить карточку с полной информацией
                displayContactCard(contact);
            }
        }
    });

    // Функция для отображения карточки с полной информацией о контакте
    function displayContactCard(contact) {
        contactCard.innerHTML = ''; // Очистить предыдущую карточку

        const card = document.createElement('div');
        card.classList.add('contact-card');

        // Определение пути к изображению
        const imageUrl = contact.image ? contact.image : '';

        card.innerHTML = `
            <div class="contact-card-content">
                <div class="contact-card-image">
                    ${imageUrl ? `<img src="${imageUrl}" alt="Фото ${contact.employer__first_name} ${contact.employer__last_name}" class="card-photo">` : '<div class="no-image">No image</div>'}
                </div>
                <div class="contact-card-info">
                    <h3>${contact.employer__first_name} ${contact.employer__last_name}</h3>
                    <p><strong>Должность:</strong> ${contact.employer__job}</p>
                    <p><strong>Телефон:</strong> ${contact.employer__phone_number}</p>
                    <p><strong>Email:</strong> <a href="mailto:${contact.employer__email}" class="email-link">${contact.employer__email}</a></p>
                    <p><strong>Веб-сайт:</strong> <a href="${contact.website || '#'}" target="_blank" class="website-link">${contact.website || 'N/A'}</a></p>
                </div>
            </div>
        `;
        contactCard.appendChild(card);
    }

    // Премирование выбранных сотрудников
    rewardBtn.addEventListener('click', async () => {
        const selectedCheckboxes = document.querySelectorAll('.select-checkbox:checked');
        if (selectedCheckboxes.length === 0) {
            alert('Пожалуйста, выберите хотя бы одного контакта для премирования.');
            return;
        }

        const selectedIds = Array.from(selectedCheckboxes).map(cb => parseInt(cb.dataset.id));

        showTablePreloader();
        try {
            const response = await fetch('/api/contacts/reward/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify({ contact_ids: selectedIds }),
            });
            const data = await response.json();
            if (data.success) {
                rewardText.textContent = data.reward_text;
                rewardText.style.display = 'block';
                // Сброс выбранных чекбоксов
                selectedCheckboxes.forEach(cb => cb.checked = false);
            } else {
                alert(data.error || 'Ошибка при премировании контактов.');
            }
        } catch (error) {
            console.error('Ошибка при премировании контактов:', error);
            alert('Ошибка при премировании контактов.');
        } finally {
            hideTablePreloader();
        }
    });

    // Инициализация: загрузка контактов
    loadContacts();
});
