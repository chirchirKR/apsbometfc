document.addEventListener('DOMContentLoaded', () => {
 /* const showMessage = (id, message, success = false) => {
    const node = document.getElementById(id);
    if (!node) return;
    node.textContent = message;
    node.className = `form-message visible${success ? " success" : ""}`;
  };
*/
  document.querySelectorAll("[data-toggle-password]").forEach(button => {
    button.addEventListener("click", () => {
      const input = document.getElementById(button.dataset.togglePassword);
      if (!input) return;
      const reveal = input.type === "password";
      input.type = reveal ? "text" : "password";
      button.setAttribute("aria-label", reveal ? "Hide password" : "Show password");
    });
  });

 /* document.querySelectorAll("[data-demo-link]").forEach(link => {
    link.addEventListener("click", event => {
      event.preventDefault();
      alert("Add your Terms and Privacy Policy pages here.");
    });
  });

  const register = document.getElementById("register-form");
  if (register) register.addEventListener("submit", event => {
    event.preventDefault();
    const name = register.elements.name.value.trim();
    const email = register.elements.email.value.trim();
    const password = register.elements.password.value;
    const accepted = document.getElementById("terms").checked;
    if (!name || !email || !register.elements.email.validity.valid) return showMessage("register-message", "Enter your name and a valid email address.");
    if (password.length < 8 || !/\d/.test(password)) return showMessage("register-message", "Use at least 8 characters and include a number.");
    if (!accepted) return showMessage("register-message", "Please agree to the Terms and Privacy Policy to continue.");
    showMessage("register-message", "Looks good! This is a front-end demo, so no account was created.", true);
  });

  const login = document.getElementById("login-form");
  if (login) login.addEventListener("submit", event => {
    event.preventDefault();
    const email = login.elements.email.value.trim();
    const password = login.elements.password.value;
    if (!email || !login.elements.email.validity.valid || !password) return showMessage("login-message", "Enter a valid email and your password.");
    showMessage("login-message", "Form validated. Connect this page to your authentication backend to log in.", true);
  });

  const reset = document.getElementById("reset-form");
  if (reset) reset.addEventListener("submit", event => {
    event.preventDefault();
    const email = reset.elements.email.value.trim();
    if (!email || !reset.elements.email.validity.valid) return showMessage("reset-message", "Enter a valid email address.");
    showMessage("reset-message", "If this email belongs to an account, a reset link would be sent. (Demo: no email was sent.)", true);
  });*/
});
