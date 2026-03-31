// ------------------------------
// Variables globales
// ------------------------------
let allPlaces = []; // stocke toutes les places

// ------------------------------
// Au chargement de la page
// ------------------------------
document.addEventListener("DOMContentLoaded", () => {
    checkAuthentication(); // vérifie token et fetch places

    // Initialize filter dropdown + listener only on index page
    const filter = document.getElementById('price-filter');
    if (filter) {
        filter.value = 'all';
        filter.addEventListener('change', applyPriceFilter);
    }

    // Gestion du formulaire login
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            document.getElementById('error-message').textContent = '';

            await loginUser(email, password);
        });
    }
});

// ------------------------------
// Vérifier authentification
// ------------------------------
function checkAuthentication() {
    const token = getCookie('token');
    const loginLink = document.getElementById('login-link');
    const loginButton = document.querySelector('.login-button');

    if (!token) {
        if (loginLink) loginLink.style.display = 'block';
        if (loginButton) loginButton.style.display = 'inline-block';
        fetchPlaces();
    } else {
        if (loginLink) loginLink.style.display = 'none';
        if (loginButton) loginButton.style.display = 'none';
        fetchPlaces(token);
    }
}

// ------------------------------
// Appliquer le filtre prix
// ------------------------------
function applyPriceFilter() {
    const selectedPrice = document.getElementById('price-filter').value;
    const placeCards = document.querySelectorAll('.place-card');

    placeCards.forEach(card => {
        const price = Number(card.getAttribute("data-price"));

        if (selectedPrice === "all" || price <= Number(selectedPrice)) {
            card.style.display = "block";
        } else {
            card.style.display = "none";
        }
    });
}

// ------------------------------
// Récupérer un cookie
// ------------------------------
function getCookie(name) {
    let matches = document.cookie.match(
        new RegExp("(?:^|; )" + name.replace(/([.$?*|{}()\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)")
    );
    return matches ? decodeURIComponent(matches[1]) : null;
}

// ------------------------------
// Login utilisateur
// ------------------------------
async function loginUser(email, password) {
    try {
        const response = await fetch('http://localhost:5000/api/v1/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (response.ok) {
            const data = await response.json();
            document.cookie = `token=${data.access_token}; path=/`;
            window.location.href = 'index.html';
        } else {
            document.getElementById('error-message').textContent =
                'Incorrect email or password';
        }
    } catch (error) {
        document.getElementById('error-message').textContent =
            'Server error, please try again later';
    }
}

// ------------------------------
// Fetch des places
// ------------------------------
async function fetchPlaces(token) {
    try {
        const headers = {
            'Content-Type': 'application/json'
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch('http://localhost:5000/api/v1/places/', {
            method: 'GET',
            headers
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            console.error(`Erreur API: Status ${response.status}`, errorData);
            throw new Error(`Erreur ${response.status}: ${errorData.message || 'Impossible de charger les places'}`);
        }

        const data = await response.json();

        allPlaces = data;
        displayPlaces(allPlaces);
        applyPriceFilter(); // Appliquer le filtre initial

    } catch (error) {
        console.error("Erreur détaillée:", error);
        const container = document.getElementById("places-list");
        if (container) {
            container.innerHTML = `<p style="color: red; text-align: center;">Erreur: ${error.message}</p>`;
        }
    }
}

// ------------------------------
// Affichage des places
// ------------------------------
function displayPlaces(places) {
    const container = document.getElementById("places-list");
    if (!container) return;

    container.innerHTML = "";

    places.forEach(place => {
        const card = document.createElement("div");
        card.classList.add("place-card");

        // Stocker le prix pour le filtre
        card.setAttribute("data-price", place.price);

        card.innerHTML = `
            <h3>${place.title}</h3>
            <p><strong>Prix :</strong> ${place.price}€</p>
            <a href="place.html?id=${place.id}" class="details-button">View Details</a>
        `;

        container.appendChild(card);
    });
}