document.querySelectorAll(".toggle").forEach(toggle => {

    toggle.addEventListener("click", function () {

        let passwordInput = this.previousElementSibling;


        if (passwordInput.type === "password") {

            passwordInput.type = "text";

            this.textContent = "🙈";

        } else {

            passwordInput.type = "password";

            this.textContent = "👁";

        }

    });

});