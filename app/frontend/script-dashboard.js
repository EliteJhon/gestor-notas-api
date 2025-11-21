// app/frontend/script-dashboard.js

const apiURL = "https://gestor-notas-api.onrender.com";
const token = localStorage.getItem("token");
let user = null;
let rol = null;
let editingNoteId = null; // Track which note is being edited

try {
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
        user = JSON.parse(storedUser);
        rol = user.rol ?? localStorage.getItem("rol");
    } else {
        rol = localStorage.getItem("rol");
    }
} catch (e) {
    console.error("Error leyendo user desde localStorage:", e);
    rol = localStorage.getItem("rol");
}

if (!token) window.location.href = "login.html";

// Referencias a elementos
const notesList = document.getElementById("notesList");
const allNotesList = document.getElementById("allNotesList");
const usersList = document.getElementById("usersList");
const modal = document.getElementById("modalCrear");
const modalTitle = document.getElementById("modalTitle");
const btnOpenModalPrimary = document.getElementById("newNoteBtn");
const btnOpenModalSidebar = document.getElementById("crearNotaBtn");
const btnCloseModal = document.getElementById("closeModalBtn");
const btnSaveNote = document.getElementById("saveNoteBtn");
const adminItems = document.querySelectorAll(".admin-only");
const pageTitle = document.getElementById("pageTitle");

// Secciones
const sectionMyNotes = document.getElementById("sectionMyNotes");
const sectionAllNotes = document.getElementById("sectionAllNotes");
const sectionUsers = document.getElementById("sectionUsers");
const sectionExport = document.getElementById("sectionExport");

// Ocultar/mostrar elementos según rol
if (adminItems && adminItems.length > 0) {
    const isAdmin = rol === "admin" || rol === "administrador";
    adminItems.forEach(el => el.style.display = isAdmin ? "block" : "none");
}

function authHeaders(json = true) {
    const headers = {
        "Authorization": `Bearer ${token}`
    };
    if (json) headers["Content-Type"] = "application/json";
    return headers;
}

// Función para cerrar el modal completamente
function closeModal() {
    if (modal) {
        modal.classList.add("hidden");
        editingNoteId = null; // Reset edit mode
        
        // Limpiar formulario
        const titleEl = document.getElementById("noteTitle");
        const contentEl = document.getElementById("noteContent");
        const statusEl = document.getElementById("noteStatus");
        const destinatarioEl = document.getElementById("noteDestinatario");
        const destinatarioLabel = document.getElementById("destinatarioLabel");
        
        if (titleEl) titleEl.value = "";
        if (contentEl) contentEl.value = "";
        if (statusEl) statusEl.value = "pendiente";
        if (destinatarioEl) {
            destinatarioEl.value = "";
            destinatarioEl.style.display = "none";
        }
        if (destinatarioLabel) destinatarioLabel.style.display = "none";
        if (modalTitle) modalTitle.textContent = "Crear Nueva Nota";
        if (btnSaveNote) btnSaveNote.textContent = "Crear";
    }
}

// Función para ocultar todas las secciones Y el modal
function hideAllSections() {
    if (sectionMyNotes) sectionMyNotes.style.display = "none";
    if (sectionAllNotes) sectionAllNotes.style.display = "none";
    if (sectionUsers) sectionUsers.style.display = "none";
    if (sectionExport) sectionExport.style.display = "none";
    if (btnOpenModalPrimary) btnOpenModalPrimary.style.display = "none";
    // 🔧 IMPORTANTE: Cerrar el modal siempre que se cambia de vista
    closeModal();
}

// Función para actualizar menú activo
function updateActiveMenu(activeId) {
    document.querySelectorAll("#menuItems li").forEach(li => {
        li.classList.remove("active");
    });
    const activeEl = document.getElementById(activeId);
    if (activeEl) activeEl.classList.add("active");
}

// NAVEGACIÓN: Mis Notas
document.getElementById("misNotasBtn")?.addEventListener("click", () => {
    hideAllSections();
    if (sectionMyNotes) sectionMyNotes.style.display = "block";
    if (pageTitle) pageTitle.textContent = "Mis Notas";
    if (btnOpenModalPrimary) btnOpenModalPrimary.style.display = "block";
    updateActiveMenu("misNotasBtn");
    loadMyNotes();
});

// NAVEGACIÓN: Crear Nota (solo abre el modal, no cambia de vista)
document.getElementById("crearNotaBtn")?.addEventListener("click", () => {
    // Cerrar cualquier sección visible
    hideAllSections();
    // Mostrar Mis Notas como contexto
    if (sectionMyNotes) sectionMyNotes.style.display = "block";
    if (pageTitle) pageTitle.textContent = "Crear Nueva Nota";
    if (btnOpenModalPrimary) btnOpenModalPrimary.style.display = "none";
    updateActiveMenu("crearNotaBtn");
    
    // Reset edit mode
    editingNoteId = null;
    if (modalTitle) modalTitle.textContent = "Crear Nueva Nota";
    if (btnSaveNote) btnSaveNote.textContent = "Crear";
    
    // Abrir modal
    if (modal) {
        modal.classList.remove("hidden");
        if (rol === "admin" || rol === "administrador") {
            loadUsersForAssignment();
        }
    }
});

// NAVEGACIÓN: Ver Todas las Notas (Admin)
document.getElementById("allNotesBtn")?.addEventListener("click", async () => {
    hideAllSections();
    if (sectionAllNotes) sectionAllNotes.style.display = "block";
    if (pageTitle) pageTitle.textContent = "Todas las Notas";
    if (btnOpenModalPrimary) btnOpenModalPrimary.style.display = "block";
    updateActiveMenu("allNotesBtn");
    await loadAllNotes();
});

// NAVEGACIÓN: Ver Usuarios (Admin)
document.getElementById("usersBtn")?.addEventListener("click", async () => {
    hideAllSections();
    if (sectionUsers) sectionUsers.style.display = "block";
    if (pageTitle) pageTitle.textContent = "Usuarios";
    if (btnOpenModalPrimary) btnOpenModalPrimary.style.display = "none";
    updateActiveMenu("usersBtn");
    await loadUsers();
});

// NAVEGACIÓN: Exportar (Admin)
document.getElementById("exportBtn")?.addEventListener("click", async () => {
    hideAllSections();
    if (sectionExport) sectionExport.style.display = "block";
    if (pageTitle) pageTitle.textContent = "Exportar Notas";
    if (btnOpenModalPrimary) btnOpenModalPrimary.style.display = "none";
    updateActiveMenu("exportBtn");
    
    // Mostrar opciones de exportación
    showExportOptions();
});

// Función para mostrar opciones de exportación
function showExportOptions() {
    if (!sectionExport) return;
    
    sectionExport.innerHTML = `
        <div class="export-container">
            <div class="export-card">
                <div class="export-icon">📊</div>
                <h3>Exportar a Excel</h3>
                <p>Descarga todas las notas en formato Excel (.xlsx)</p>
                <button class="btn-export btn-excel" onclick="exportNotes('excel')">
                    Exportar Excel
                </button>
            </div>
            <div class="export-card">
                <div class="export-icon">📄</div>
                <h3>Exportar a PDF</h3>
                <p>Descarga todas las notas en formato PDF</p>
                <button class="btn-export btn-pdf" onclick="exportNotes('pdf')">
                    Exportar PDF
                </button>
            </div>
        </div>
    `;
}

// Cerrar modal con botón
if (btnCloseModal) {
    btnCloseModal.addEventListener("click", () => {
        closeModal();
        // Si estamos en la vista de crear nota, volver a Mis Notas
        if (pageTitle && pageTitle.textContent === "Crear Nueva Nota") {
            hideAllSections();
            if (sectionMyNotes) sectionMyNotes.style.display = "block";
            if (pageTitle) pageTitle.textContent = "Mis Notas";
            if (btnOpenModalPrimary) btnOpenModalPrimary.style.display = "block";
            updateActiveMenu("misNotasBtn");
            loadMyNotes();
        }
    });
}

// Cerrar modal al hacer clic fuera de él
if (modal) {
    modal.addEventListener("click", (e) => {
        if (e.target === modal) {
            closeModal();
            // Si estamos en la vista de crear nota, volver a Mis Notas
            if (pageTitle && pageTitle.textContent === "Crear Nueva Nota") {
                hideAllSections();
                if (sectionMyNotes) sectionMyNotes.style.display = "block";
                if (pageTitle) pageTitle.textContent = "Mis Notas";
                if (btnOpenModalPrimary) btnOpenModalPrimary.style.display = "block";
                updateActiveMenu("misNotasBtn");
                loadMyNotes();
            }
        }
    });
}

// Abrir modal desde botón del header
if (btnOpenModalPrimary) {
    btnOpenModalPrimary.addEventListener("click", () => {
        editingNoteId = null;
        if (modalTitle) modalTitle.textContent = "Crear Nueva Nota";
        if (btnSaveNote) btnSaveNote.textContent = "Crear";
        
        if (modal) {
            modal.classList.remove("hidden");
            if (rol === "admin" || rol === "administrador") {
                loadUsersForAssignment();
            }
        }
    });
}

function showLoading(container) {
    if (!container) return;
    container.innerHTML = `<div class="card"><p>Cargando...</p></div>`;
}

function renderNoteCard(note) {
    const statusClass = note.estado === "completado" ? "status-completado"
                      : note.estado === "en_progreso" ? "status-progreso"
                      : "status-pendiente";

    const title = String(note.titulo ?? "").replace(/</g, "&lt;");
    const content = String(note.contenido ?? "").replace(/</g, "&lt;");

    return `
        <div class="note-card" data-note-id="${note.id}">
            <h3>${title}</h3>
            <p>${content}</p>
            <span class="status-tag ${statusClass}">${note.estado.toUpperCase()}</span>
            <div class="note-actions">
                <button class="btn-secondary" onclick="openEditModal(${note.id})">Editar</button>
                <button class="btn-secondary" onclick="deleteNote(${note.id})">Eliminar</button>
            </div>
        </div>
    `;
}

function renderUserCard(user) {
    const username = String(user.username ?? "").replace(/</g, "&lt;");
    const email = String(user.email ?? "").replace(/</g, "&lt;");
    const rolText = String(user.rol ?? "").replace(/</g, "&lt;");
    
    return `
        <div class="user-card">
            <h3>${username}</h3>
            <p>${email}</p>
            <span class="rol-tag">${rolText}</span>
        </div>
    `;
}

async function loadMyNotes() {
    if (!notesList) return;
    showLoading(notesList);

    try {
        const res = await fetch(`${apiURL}/notes/my`, { method: "GET", headers: authHeaders(false) });
        if (!res.ok) {
            console.error("Error cargando notas:", res.status, await res.text());
            notesList.innerHTML = `<div class="card"><p>Error cargando las notas (status ${res.status})</p></div>`;
            return;
        }
        const notes = await res.json();
        if (!Array.isArray(notes) || notes.length === 0) {
            notesList.innerHTML = `<div class="card"><p>No hay notas registradas.</p></div>`;
            return;
        }
        notesList.innerHTML = notes.map(renderNoteCard).join("\n");
    } catch (err) {
        console.error("Excepción cargando notas:", err);
        notesList.innerHTML = `<div class="card"><p>Error inesperado cargando las notas.</p></div>`;
    }
}

async function loadAllNotes() {
    if (!allNotesList) return;
    showLoading(allNotesList);

    try {
        const res = await fetch(`${apiURL}/notes/`, { method: "GET", headers: authHeaders(false) });
        if (!res.ok) {
            console.error("Error cargando todas las notas:", res.status, await res.text());
            allNotesList.innerHTML = `<div class="card"><p>Error cargando las notas (status ${res.status})</p></div>`;
            return;
        }
        const notes = await res.json();
        if (!Array.isArray(notes) || notes.length === 0) {
            allNotesList.innerHTML = `<div class="card"><p>No hay notas registradas.</p></div>`;
            return;
        }
        allNotesList.innerHTML = notes.map(renderNoteCard).join("\n");
    } catch (err) {
        console.error("Excepción cargando todas las notas:", err);
        allNotesList.innerHTML = `<div class="card"><p>Error inesperado cargando las notas.</p></div>`;
    }
}

// 🔧 FIXED: Función para cargar usuarios con mejor manejo de errores y depuración
async function loadUsers() {
    if (!usersList) return;
    showLoading(usersList);

    // Verificar que el token existe
    if (!token) {
        usersList.innerHTML = `<div class="card"><p>Error: No hay token de autenticación. Por favor, inicia sesión nuevamente.</p></div>`;
        return;
    }

    try {
        const url = `${apiURL}/auth/users`;
        const headers = authHeaders(false);
        
        console.log("Intentando cargar usuarios desde:", url);
        console.log("Headers:", headers);
        
        const res = await fetch(url, { 
            method: "GET", 
            headers: headers,
            credentials: 'include' // Asegurar que se envíen cookies si es necesario
        });
        
        console.log("Respuesta recibida:", res.status, res.statusText);
        
        if (!res.ok) {
            let errorData;
            try {
                errorData = await res.json();
            } catch (e) {
                const errorText = await res.text();
                errorData = { detail: errorText || `Error ${res.status}: ${res.statusText}` };
            }
            
            console.error("Error cargando usuarios:", res.status, errorData);
            
            if (res.status === 401) {
                usersList.innerHTML = `<div class="card"><p>Error: No autorizado. Por favor, inicia sesión nuevamente.</p></div>`;
                // Redirigir al login después de 2 segundos
                setTimeout(() => {
                    window.location.href = "login.html";
                }, 2000);
            } else if (res.status === 403) {
                usersList.innerHTML = `<div class="card"><p>Error: No tienes permisos para ver usuarios. Solo los administradores pueden acceder.</p></div>`;
            } else {
                usersList.innerHTML = `<div class="card"><p>Error: ${errorData.detail || `Status ${res.status}`}</p></div>`;
            }
            return;
        }
        
        const users = await res.json();
        console.log("Usuarios recibidos:", users);
        
        if (!Array.isArray(users)) {
            console.error("La respuesta no es un array:", users);
            usersList.innerHTML = `<div class="card"><p>Error: Formato de respuesta inválido. Se esperaba un array.</p></div>`;
            return;
        }
        
        if (users.length === 0) {
            usersList.innerHTML = `<div class="card"><p>No hay usuarios registrados.</p></div>`;
            return;
        }
        
        usersList.innerHTML = users.map(renderUserCard).join("\n");
    } catch (err) {
        console.error("Excepción cargando usuarios:", err);
        
        // Mensajes más específicos según el tipo de error
        let errorMessage = "Error inesperado cargando usuarios";
        
        if (err.name === "TypeError" && err.message.includes("fetch")) {
            errorMessage = `Error de conexión: No se pudo conectar con el servidor. Verifica que el servidor FastAPI esté corriendo en ${apiURL}`;
        } else if (err.message) {
            errorMessage = `Error: ${err.message}`;
        }
        
        usersList.innerHTML = `<div class="card"><p>${errorMessage}</p></div>`;
    }
}

async function loadUsersForAssignment() {
    if (rol !== "admin" && rol !== "administrador") return;
    
    try {
        const res = await fetch(`${apiURL}/auth/users`, { method: "GET", headers: authHeaders(false) });
        if (res.ok) {
            const users = await res.json();
            const select = document.getElementById("noteDestinatario");
            const label = document.getElementById("destinatarioLabel");
            if (select && label) {
                select.innerHTML = '<option value="">Seleccionar usuario...</option>' +
                    users.map(u => `<option value="${u.id}">${u.username} (${u.rol})</option>`).join("");
                select.style.display = "block";
                label.style.display = "block";
            }
        }
    } catch (err) {
        console.error("Error cargando usuarios para asignación:", err);
    }
}

// 🔧 NEW: Función para cargar una nota individual
async function loadNoteById(noteId) {
    try {
        // Get all notes and find the one we need
        const res = await fetch(`${apiURL}/notes/my`, { method: "GET", headers: authHeaders(false) });
        if (!res.ok) {
            // Try all notes if user is admin
            if (rol === "admin" || rol === "administrador") {
                const allRes = await fetch(`${apiURL}/notes/`, { method: "GET", headers: authHeaders(false) });
                if (allRes.ok) {
                    const allNotes = await allRes.json();
                    return allNotes.find(n => n.id === noteId);
                }
            }
            return null;
        }
        const notes = await res.json();
        return notes.find(n => n.id === noteId);
    } catch (err) {
        console.error("Error cargando nota:", err);
        return null;
    }
}

// 🔧 NEW: Función para abrir modal de edición
window.openEditModal = async function(noteId) {
    editingNoteId = noteId;
    
    // Cambiar título del modal
    if (modalTitle) modalTitle.textContent = "Editar Nota";
    if (btnSaveNote) btnSaveNote.textContent = "Guardar Cambios";
    
    // Cargar datos de la nota
    const note = await loadNoteById(noteId);
    if (!note) {
        alert("No se pudo cargar la nota para editar");
        return;
    }
    
    // Llenar formulario
    const titleEl = document.getElementById("noteTitle");
    const contentEl = document.getElementById("noteContent");
    const statusEl = document.getElementById("noteStatus");
    const destinatarioEl = document.getElementById("noteDestinatario");
    const destinatarioLabel = document.getElementById("destinatarioLabel");
    
    if (titleEl) titleEl.value = note.titulo || "";
    if (contentEl) contentEl.value = note.contenido || "";
    if (statusEl) statusEl.value = note.estado || "pendiente";
    
    // Si es admin, cargar usuarios y mostrar selector
    if ((rol === "admin" || rol === "administrador") && destinatarioEl && destinatarioLabel) {
        await loadUsersForAssignment();
        if (note.destinatario_id) {
            destinatarioEl.value = note.destinatario_id;
        }
    }
    
    // Abrir modal
    if (modal) {
        modal.classList.remove("hidden");
    }
};

// Hacer exportNotes global para que funcione desde el HTML
window.exportNotes = async function(format) {
    try {
        const endpoint = format === "excel" ? "/notes/export/excel" : "/notes/export/pdf";
        const res = await fetch(`${apiURL}${endpoint}`, { method: "GET", headers: authHeaders(false) });
        
        if (!res.ok) {
            const errBody = await res.json().catch(() => null);
            alert(errBody?.detail ?? "Error al exportar notas");
            return;
        }

        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = format === "excel" ? "notas.xlsx" : "notas.pdf";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        alert("Archivo exportado correctamente");
    } catch (err) {
        console.error("Error exportando notas:", err);
        alert("Error inesperado al exportar notas");
    }
};

// 🔧 UPDATED: Manejar tanto crear como editar
if (btnSaveNote) {
    btnSaveNote.addEventListener("click", async () => {
        const titleEl = document.getElementById("noteTitle");
        const contentEl = document.getElementById("noteContent");
        const statusEl = document.getElementById("noteStatus");
        const destinatarioEl = document.getElementById("noteDestinatario");

        const titulo = titleEl?.value.trim() || "";
        const contenido = contentEl?.value.trim() || "";
        const estado = statusEl?.value || "pendiente";
        const destinatario_id = destinatarioEl?.value ? parseInt(destinatarioEl.value) : null;

        if (!titulo || !contenido) {
            alert("Por favor completa título y contenido.");
            return;
        }

        try {
            let res;
            
            if (editingNoteId) {
                // Modo edición: PUT request
                res = await fetch(`${apiURL}/notes/${editingNoteId}`, {
                    method: "PUT",
                    headers: authHeaders(true),
                    body: JSON.stringify({ titulo, contenido, estado, destinatario_id })
                });
            } else {
                // Modo creación: POST request
                res = await fetch(`${apiURL}/notes/`, {
                    method: "POST",
                    headers: authHeaders(true),
                    body: JSON.stringify({ titulo, contenido, estado, destinatario_id })
                });
            }

            if (!res.ok) {
                const errBody = await res.json().catch(()=>null);
                console.error("Error guardando nota:", res.status, errBody);
                alert(errBody?.detail ?? "Error al guardar la nota");
                return;
            }

            closeModal();

            // Recargar la vista actual
            if (sectionMyNotes && sectionMyNotes.style.display !== "none") {
                await loadMyNotes();
            } else if (sectionAllNotes && sectionAllNotes.style.display !== "none") {
                await loadAllNotes();
            }
            
            // Si estábamos en "Crear Nueva Nota", volver a Mis Notas
            if (pageTitle && pageTitle.textContent === "Crear Nueva Nota") {
                hideAllSections();
                if (sectionMyNotes) sectionMyNotes.style.display = "block";
                if (pageTitle) pageTitle.textContent = "Mis Notas";
                if (btnOpenModalPrimary) btnOpenModalPrimary.style.display = "block";
                updateActiveMenu("misNotasBtn");
                await loadMyNotes();
            }
        } catch (err) {
            console.error("Excepción guardando nota:", err);
            alert("Error inesperado al guardar la nota");
        }
    });
}

// 🔧 REMOVED: La función editNote antigua que usaba prompt()
// Ahora se usa openEditModal() que abre el modal

window.deleteNote = async function(id) {
    if (!confirm("¿Eliminar nota? Esta acción no se puede deshacer.")) return;

    try {
        const res = await fetch(`${apiURL}/notes/${id}`, { method: "DELETE", headers: authHeaders(false) });
        if (!res.ok) {
            const errBody = await res.json().catch(()=>null);
            console.error("Error eliminando nota:", res.status, errBody);
            alert(errBody?.detail ?? "Error al eliminar la nota");
            return;
        }

        // Recargar la vista actual
        if (sectionMyNotes && sectionMyNotes.style.display !== "none") {
            await loadMyNotes();
        } else if (sectionAllNotes && sectionAllNotes.style.display !== "none") {
            await loadAllNotes();
        }
    } catch (err) {
        console.error("Excepción deleteNote:", err);
        alert("Error inesperado al eliminar la nota");
    }
};

document.getElementById("logoutBtn")?.addEventListener("click", () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    localStorage.removeItem("rol");
    window.location.href = "login.html";
});

// Inicializar: cargar Mis Notas al entrar
document.addEventListener("DOMContentLoaded", () => {
    hideAllSections();
    if (sectionMyNotes) sectionMyNotes.style.display = "block";
    if (btnOpenModalPrimary) btnOpenModalPrimary.style.display = "block";
    updateActiveMenu("misNotasBtn");
    loadMyNotes();
});