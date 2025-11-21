// app/frontend/script-register.js

const apiURL = "http://127.0.0.1:8000";

document.getElementById("registerForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const rol = document.getElementById("rol")?.value || "cliente"; // Valor por defecto

    const response = await fetch(`${apiURL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password, rol })
    });

    const data = await response.json();

    if (response.ok) {
        alert("Usuario registrado correctamente");
        window.location.href = "login.html";
    } else {
        alert(data.detail || "Error al registrarse");
    }
});