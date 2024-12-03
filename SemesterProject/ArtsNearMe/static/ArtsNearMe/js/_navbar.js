
$(document).ready(function () {
    // Dropdown toggle visibility
    $('#navbar').on('click', '#user-dropdown-btn', function (e) {
        e.stopPropagation();
        $('#user-dropdown-menu').toggleClass('hidden');
    });

    // Hide dropdown when clicking outside
    $(document).on('click', function () {
        $('#user-dropdown-menu').addClass('hidden');
    });

});

document.addEventListener("DOMContentLoaded", function() {
    const themeToggleButton = document.getElementById("theme-toggle-btn");
    const rootElement = document.documentElement; // <html> element

    // Get theme from localStorage or fallback to light.
    let savedTheme = localStorage.getItem("theme") || "light";
    console.log("Initial stored theme:", savedTheme);

});

