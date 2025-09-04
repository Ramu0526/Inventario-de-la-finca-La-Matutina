document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;

    // Función para aplicar el tema guardado
    const applyTheme = (theme) => {
        if (theme === 'dark') {
            body.classList.add('dark-mode');
            themeToggle.textContent = '🌑'; // luna
        } else {
            body.classList.remove('dark-mode');
            themeToggle.textContent = '☀️'; // sol
        }
    };

    // Cargar el tema guardado en localStorage al iniciar la página
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);

    // Evento al hacer clic en el botón
    themeToggle.addEventListener('click', () => {
        let newTheme = body.classList.contains('dark-mode') ? 'light' : 'dark';
        localStorage.setItem('theme', newTheme); // Guardar la preferencia
        applyTheme(newTheme);
    });
});