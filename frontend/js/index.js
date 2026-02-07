document.addEventListener('DOMContentLoaded', () => {
    const studioButtons = document.querySelectorAll('.js-navigate-studio');
    studioButtons.forEach(button => {
        button.addEventListener('click', () => {
            window.location.href = 'studio.html';
        });
    });
});
