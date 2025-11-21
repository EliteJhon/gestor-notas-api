const apiURL = "https://gestor-notas-api.onrender.com/";

document.getElementById("loginForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);

    const response = await fetch(`${apiURL}/auth/login`, {
        method: "POST",
        headers: { 
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: formData
    });

    const data = await response.json();

    if (response.ok) {

        // ⚠️ ESTO ERA LO QUE FALTABA
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("user", JSON.stringify(data.user));
        localStorage.setItem("rol", data.user.rol);

        window.location.href = "dashboard.html";

    } else {
        alert(data.detail || "Error al iniciar sesión");
    }
});
