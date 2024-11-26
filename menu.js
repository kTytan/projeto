document.addEventListener('DOMContentLoaded', function () {
    const toggleButton = document.getElementById('toggleButton');
    const sideMenu = document.getElementById('sideMenu');

    toggleButton.addEventListener('click', function () {
        if (sideMenu.style.left === '-250px') {
            sideMenu.style.left = '0';
        } else {
            sideMenu.style.left = '-250px';
        }
    });
});