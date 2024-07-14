document.addEventListener('DOMContentLoaded', function () {
    const indexFileElements = document.querySelectorAll('.clickable-btn');

    indexFileElements.forEach(element => {
        element.addEventListener('click', event => setTimeout(() => event.target.disabled = true, 0));
    });
});
