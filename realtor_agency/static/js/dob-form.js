// static/js/dob-form.js

document.addEventListener('DOMContentLoaded', () => {
    const dobForm = document.getElementById('dob-form');
    const dobInput = document.getElementById('dob');
    const dobMessage = document.getElementById('dob-message');

    dobForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const dobValue = dobInput.value;
        if (!dobValue) {
            dobMessage.textContent = 'Please enter your date of birth.';
            dobMessage.style.color = '#dc3545'; // Красный цвет
            return;
        }

        const dobDate = new Date(dobValue);
        const today = new Date();
        let age = today.getFullYear() - dobDate.getFullYear();
        const monthDiff = today.getMonth() - dobDate.getMonth();
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dobDate.getDate())) {
            age--;
        }

        const dayOfWeek = dobDate.toLocaleDateString('en-US', { weekday: 'long' });

        if (age >= 18) {
            dobMessage.innerHTML = `
                You are ${age} years old.<br>
                You were born on a ${dayOfWeek}.
            `;
            dobMessage.style.color = '#28a745'; // Зеленый цвет
        } else {
            dobMessage.innerHTML = `
                You are ${age} years old.<br>
                You were born on a ${dayOfWeek}.<br>
                <strong>Note:</strong> You need parental permission to use this site.
            `;
            dobMessage.style.color = '#ffc107'; // Желтый цвет
            alert('You need parental permission to use this site.');
        }
    });
});
