document.addEventListener("DOMContentLoaded", function () {

    const container = document.getElementById("container");
    const registerBtn = document.getElementById("register");
    const loginBtn = document.getElementById("login");

    if (registerBtn) {
        registerBtn.addEventListener("click", function () {
            container.classList.add("active");
        });
    }

    if (loginBtn) {
        loginBtn.addEventListener("click", function () {
            container.classList.remove("active");
        });
    }

});