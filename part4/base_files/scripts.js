/**
 * ========================================
 * APPLICATION HBNB - Frontend JavaScript
 * ========================================
 * Gère l'authentification, l'affichage des places,
 * la pagination, et les détails des annonces
 */

// ========== VARIABLES GLOBALES ==========
/**
 * Stocke la liste complète des places récupérées depuis l'API
 * @type {Array<Object>}
 */
let allPlaces = [];
let token = null; // Contiendra le JWT de l’utilisateur pour les appels API

// ========== INITIALISATION À LA CHARGE ==========
/**
 * Lance les configurations nécessaires au chargement de la page
 * - Configure le formulaire de login
 * - Configure la page d'index (liste des places)
 * - Configure la page de détails d'une place
 */
document.addEventListener("DOMContentLoaded", () => {
    setupLoginForm();
    setupIndexPage();
    setupPlacePage();
    setupReviewPage();
});

// ========== SECTION 1 : CONFIGURATION DU FORMULAIRE DE LOGIN ==========
/**
 * Initialise le formulaire de connexion
 * Ajoute un écouteur d'événement au formulaire pour gérer la soumission
 * @function setupLoginForm
 */
function setupLoginForm() {
    const loginForm = document.getElementById("login-form");
    if (!loginForm) return;

    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;
        document.getElementById("error-message").textContent = "";

        await loginUser(email, password);
    });
}

// ========== SECTION 2 : CONFIGURATION DE LA PAGE INDEX ==========
/**
 * Initialise la page d'affichage des places
 * - Récupère le token d'authentification
 * - Affiche/masque les liens selon l'état de l'authentification
 * - Charge et affiche les places depuis l'API
 * - Active le filtre de prix
 * @function setupIndexPage
 */
function setupIndexPage() {
    const placesContainer = document.getElementById("places-list");
    if (!placesContainer) return;

    const token = getCookie("token");
    toggleAuthLinks(token);
    fetchPlaces(token);

    const filter = document.getElementById("price-filter");
    if (filter) {
        filter.value = "all";
        filter.addEventListener("change", applyPriceFilter);
    }
}

// ========== SECTION 3 : CONFIGURATION DE LA PAGE DE DÉTAILS D'UNE PLACE ==========
/**
 * Initialise la page de détails d'une place
 * - Récupère le token d'authentification
 * - Affiche/masque les liens selon l'état de l'authentification
 * - Montre la section d'ajout d'avis si l'utilisateur est connecté
 * - Charge les détails de la place à partir de l'URL
 * @function setupPlacePage
 */
function setupPlacePage() {
    const detailsContainer = document.getElementById("place-details");
    if (!detailsContainer) return;

    const token = getCookie("token");
    toggleAuthLinks(token);

    const addReviewSection = document.getElementById("add-review");
    if (addReviewSection) {
        if (token) {
            addReviewSection.style.display = "block";
        } else {
            addReviewSection.style.display = "none";
        }
    }

    const placeId = getPlaceIdFromURL();
    if (placeId) {
        fetchPlaceDetails(token, placeId);
    }
}

// ========== SECTION 4 : CONFIGURATION DE LA PAGE D'AJOUT D'UN AVIS ==========
/**
 * Initialise la page d'ajout d'un avis
 * - Vérifie l'authentification
 * - Récupère l'ID de la place depuis l'URL
 * - Prépare la liste des notes
 * - Gère la soumission du formulaire d'avis
 * @function setupReviewPage
 */
function setupReviewPage() {
    const reviewForm = document.getElementById("review-form") || document.getElementById("add-review-form");
    if (!reviewForm) return;

    const token = checkAuthentication();
    if (!token) return;

    toggleAuthLinks(token);

    const placeId = getPlaceIdFromURL();
    const reviewMessage = getOrCreateReviewMessage();

    if (!placeId) {
        reviewMessage.textContent = "Missing place ID in the URL.";
        reviewMessage.style.color = "red";
        reviewForm.style.display = "none";
        return;
    }

    const placeInfo = document.getElementById("review-place-info");
    if (placeInfo) {
        placeInfo.textContent = `Reviewing place ID: ${placeId}`;
    }

    const reviewInput = document.getElementById("review") || document.getElementById("review-comment");
    const ratingSelect = document.getElementById("rating") || document.getElementById("review-rating");
    if (ratingSelect && ratingSelect.options.length === 0) {
        for (let value = 1; value <= 5; value += 1) {
            const option = document.createElement("option");
            option.value = String(value);
            option.textContent = String(value);
            ratingSelect.appendChild(option);
        }
        ratingSelect.value = "5";
    }

    reviewForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const reviewText = reviewInput ? reviewInput.value.trim() : "";
        const rating = ratingSelect ? ratingSelect.value : "";

        reviewMessage.textContent = "";

        if (!reviewText) {
            reviewMessage.textContent = "Please write a review before submitting.";
            reviewMessage.style.color = "red";
            return;
        }

        const response = await submitReview(token, placeId, reviewText, rating);

        if (response.ok) {
            reviewMessage.textContent = "Review submitted successfully!";
            reviewMessage.style.color = "green";
            reviewForm.reset();
            if (ratingSelect) {
                ratingSelect.value = "5";
            }

            const detailsContainer = document.getElementById("place-details");
            if (detailsContainer) {
                await fetchPlaceDetails(token, placeId);
            }
        } else {
            const errorData = await response.json().catch(() => null);
            reviewMessage.textContent = errorData && errorData.error ? errorData.error : "Failed to submit review";
            reviewMessage.style.color = "red";
        }
    });
}

/**
 * Affiche ou masque le lien de connexion selon l'état de l'authentification
 * @function toggleAuthLinks
 * @param {string|null} token - Token d'authentification (null si non connecté)
 */
function toggleAuthLinks(token) {
    const loginLink = document.getElementById("login-link");

    if (token) {
        if (loginLink) loginLink.style.display = "none";
    } else {
        if (loginLink) loginLink.style.display = "block";
    }
}

// ========== SECTION 4 : GESTION DES COOKIES ==========
/**
 * Récupère la valeur d'un cookie par son nom
 * Utilise une expression régulière pour extraire la valeur du cookie
 * @function getCookie
 * @param {string} name - Nom du cookie à récupérer
 * @returns {string|null} Valeur du cookie ou null si non trouvé
 */
function getCookie(name) {
    const matches = document.cookie.match(
        new RegExp("(?:^|; )" + name.replace(/([.$?*|{}()\[\]\\/+^])/g, "\\$1") + "=([^;]*)")
    );

    if (matches) {
        return decodeURIComponent(matches[1]);
    }

    return null;
}

function checkAuthentication() {
    const token = getCookie('token');
    if (!token) {
        window.location.href = 'index.html';
        return null;
    }
    return token;
}

function getOrCreateReviewMessage() {
    let reviewMessage = document.getElementById("review-message");
    if (!reviewMessage) {
        reviewMessage = document.createElement("p");
        reviewMessage.id = "review-message";
        const reviewForm = document.getElementById("review-form");
        if (reviewForm) {
            reviewForm.appendChild(reviewMessage);
        } else {
            const legacyForm = document.getElementById("add-review-form");
            if (legacyForm) {
                legacyForm.appendChild(reviewMessage);
            }
        }
    }
    return reviewMessage;
}

// ========== SECTION 5 : AUTHENTIFICATION ==========
/**
 * Authentifie l'utilisateur via une requête POST à l'API
 * - Envoie l'email et le mot de passe au serveur
 * - Stocke le token reçu dans un cookie
 * - Redirige vers la page d'accueil en cas de succès
 * - Affiche un message d'erreur en cas d'échec
 * @async
 * @function loginUser
 * @param {string} email - Email de l'utilisateur
 * @param {string} password - Mot de passe de l'utilisateur
 */
async function loginUser(email, password) {
    try {
        const response = await fetch("http://localhost:5000/api/v1/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        if (response.ok) {
            const data = await response.json();
            document.cookie = `token=${data.access_token}; path=/`;
            window.location.href = "index.html";
        } else {
            document.getElementById("error-message").textContent = "Incorrect email or password";
        }
    } catch (error) {
        document.getElementById("error-message").textContent = "Server error, please try again later";
    }
}

// ========== SECTION 6 : GESTION DES PLACES ==========
/**
 * Récupère toutes les places depuis l'API
 * - Inclut le token d'authentification si disponible
 * - Affiche les places et applique le filtre de prix
 * - Gère les erreurs avec un message d'affichage
 * @async
 * @function fetchPlaces
 * @param {string|null} token - Token d'authentification (optionnel)
 */
async function fetchPlaces(token) {
    try {
        const headers = { "Content-Type": "application/json" };
        if (token) headers.Authorization = `Bearer ${token}`;

        const response = await fetch("http://localhost:5000/api/v1/places/", {
            method: "GET",
            headers
        });

        if (!response.ok) {
            throw new Error(`Erreur ${response.status}: Impossible de charger les places`);
        }

        const data = await response.json();
        allPlaces = data;
        displayPlaces(allPlaces);
        applyPriceFilter();
    } catch (error) {
        const container = document.getElementById("places-list");
        if (container) {
            const errorText = document.createElement("p");
            errorText.style.color = "red";
            errorText.style.textAlign = "center";
            errorText.textContent = `Erreur: ${error.message}`;
            container.replaceChildren(errorText);
        }
    }
}

/**
 * Affiche les places sous forme de cartes dans le DOM
 * Chaque carte contient:
 * - Titre de la place
 * - Prix
 * - Lien vers les détails
 * @function displayPlaces
 * @param {Array<Object>} places - Tableau des places à afficher
 */
function displayPlaces(places) {
    const container = document.getElementById("places-list");
    if (!container) return;

    container.replaceChildren();

    places.forEach((place) => {
        const card = document.createElement("div");
        card.classList.add("place-card");
        card.setAttribute("data-price", place.price);

        const title = document.createElement("h3");
        title.textContent = place.title;

        const price = document.createElement("p");
        const priceLabel = document.createElement("strong");
        priceLabel.textContent = "Prix : ";
        price.appendChild(priceLabel);
        price.append(document.createTextNode(`${place.price}€`));

        const detailsLink = document.createElement("a");
        detailsLink.classList.add("details-button");
        detailsLink.href = `place.html?id=${place.id}`;
        detailsLink.textContent = "View Details";

        card.append(title, price, detailsLink);
        container.appendChild(card);
    });
}

// ========== SECTION 7 : FILTRAGE PAR PRIX ==========
/**
 * Applique le filtre de prix aux cartes de place affichées
 * Affiche/cache les cartes selon le prix sélectionné dans le select
 * @function applyPriceFilter
 */
function applyPriceFilter() {
    const filter = document.getElementById("price-filter");
    if (!filter) return;

    const selectedPrice = filter.value;
    const placeCards = document.querySelectorAll(".place-card");

    placeCards.forEach((card) => {
        const price = Number(card.getAttribute("data-price"));

        if (selectedPrice === "all" || price <= Number(selectedPrice)) {
            card.style.display = "block";
        } else {
            card.style.display = "none";
        }
    });
}

// ========== SECTION 8 : GESTION DES DÉTAILS DE LA PLACE ==========
/**
 * Extrait l'ID de la place depuis les paramètres d'URL
 * Utilise l'API URLSearchParams
 * @function getPlaceIdFromURL
 * @returns {string|null} ID de la place ou null
 */
function getPlaceIdFromURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get("id");
}

/**
 * Récupère les détails complets d'une place depuis l'API
 * - Inclut le token d'authentification si disponible
 * - Affiche les détails et les avis associés
 * - Gère les erreurs avec un message d'affichage
 * @async
 * @function fetchPlaceDetails
 * @param {string|null} token - Token d'authentification (optionnel)
 * @param {string} placeId - ID de la place à récupérer
 */
async function fetchPlaceDetails(token, placeId) {
    try {
        const headers = { "Content-Type": "application/json" };
        if (token) headers.Authorization = `Bearer ${token}`;

        const response = await fetch(`http://localhost:5000/api/v1/places/${placeId}`, {
            method: "GET",
            headers
        });

        if (!response.ok) {
            throw new Error(`Erreur ${response.status}: Impossible de charger les details`);
        }

        const placeDetails = await response.json();
        displayPlaceDetails(placeDetails);
        displayReviews(placeDetails.reviews || []);
    } catch (error) {
        const container = document.getElementById("place-details");
        if (container) {
            const errorText = document.createElement("p");
            errorText.style.color = "red";
            errorText.style.textAlign = "center";
            errorText.textContent = `Erreur: ${error.message}`;
            container.replaceChildren(errorText);
        }
    }
}

/**
 * Affiche les détails complets d'une place dans le DOM
 * Inclut:
 * - Titre
 * - Description
 * - Prix
 * - Localisation (latitude, longitude)
 * - Propriétaire
 * - Liste des équipements (amenities)
 *
 * Remarque: Les descriptions placeholder ("Created for UI check", "No description available")
 * sont remplacées par "No description"
 *
 * @function displayPlaceDetails
 * @param {Object} place - Objet place contenant les détails
 * @param {string} place.title - Titre de la place
 * @param {string} place.description - Description (peut être vide ou placeholder)
 * @param {number} place.price - Prix de la place
 * @param {number} place.latitude - Latitude
 * @param {number} place.longitude - Longitude
 * @param {Object} place.owner - Object propriétaire {first_name, last_name}
 * @param {Array} place.amenities - Liste des équipements
 */
function displayPlaceDetails(place) {
    const container = document.getElementById("place-details");
    if (!container) return;

    container.replaceChildren();

    const title = document.createElement("h1");
    title.textContent = place.title || "Place";

    const description = document.createElement("p");

    let rawDescription = "";
    if (typeof place.description === "string") {
        rawDescription = place.description.trim();
    }

    const isPlaceholderDescription =
        rawDescription.toLowerCase() === "created for ui check" ||
        rawDescription.toLowerCase() === "no description available";

    let placeDescription = "No description";
    if (rawDescription && !isPlaceholderDescription) {
        placeDescription = rawDescription;
    }

    description.textContent = placeDescription;

    const price = document.createElement("p");
    const priceLabel = document.createElement("strong");
    priceLabel.textContent = "Price: ";
    price.append(priceLabel, document.createTextNode(`${place.price}€`));

    const location = document.createElement("p");
    const locationLabel = document.createElement("strong");
    locationLabel.textContent = "Location: ";
    location.append(
        locationLabel,
        document.createTextNode(`${place.latitude ?? "-"}, ${place.longitude ?? "-"}`)
    );

    const owner = document.createElement("p");
    const ownerLabel = document.createElement("strong");
    ownerLabel.textContent = "Owner: ";

    let ownerName = "Unknown";
    if (place.owner) {
        ownerName = `${place.owner.first_name || ""} ${place.owner.last_name || ""}`.trim();
    }

    owner.append(ownerLabel, document.createTextNode(ownerName || "Unknown"));

    const amenitiesTitle = document.createElement("h3");
    amenitiesTitle.textContent = "Amenities";

    const amenitiesList = document.createElement("ul");

    let amenities = [];
    if (Array.isArray(place.amenities)) {
        amenities = place.amenities;
    }

    if (amenities.length === 0) {
        const amenityItem = document.createElement("li");
        amenityItem.textContent = "No amenities listed.";
        amenitiesList.appendChild(amenityItem);
    } else {
        amenities.forEach((amenity) => {
            const amenityItem = document.createElement("li");
            amenityItem.textContent = amenity.name;
            amenitiesList.appendChild(amenityItem);
        });
    }

    container.append(title, description, price, location, owner, amenitiesTitle, amenitiesList);
}

// ========== SECTION 9 : GESTION DES AVIS ==========
/**
 * Affiche tous les avis (reviews) associés à une place
 * Chaque avis affiche:
 * - Commentaire
 * - Note (rating) sur 5
 *
 * Si aucun avis n'existe, affiche un message "No reviews yet."
 * @function displayReviews
 * @param {Array<Object>} reviews - Tableau des avis à afficher
 * @param {string} reviews[].comment - Commentaire de l'avis
 * @param {number} reviews[].rating - Note de l'avis (1-5)
 */
function displayReviews(reviews) {
    const reviewsContainer = document.getElementById("reviews-list");
    if (!reviewsContainer) return;

    reviewsContainer.replaceChildren();

    if (!reviews.length) {
        const empty = document.createElement("p");
        empty.textContent = "No reviews yet.";
        reviewsContainer.appendChild(empty);
        return;
    }

    reviews.forEach((review) => {
        const card = document.createElement("div");
        card.classList.add("review-card");

        const reviewer = document.createElement("p");
        reviewer.classList.add("review-author");
        reviewer.textContent = `By: ${review.reviewer_name || "Anonymous"}`;

        const comment = document.createElement("p");
        comment.classList.add("review-comment");
        comment.textContent = review.comment || "";

        const rating = document.createElement("p");
        rating.classList.add("review-rating");
        const stars = Math.max(0, Math.min(5, Number(review.rating) || 0));
        rating.textContent = `Rating: ${"★".repeat(stars)}${"☆".repeat(5 - stars)}`;

        card.append(reviewer, comment, rating);
        reviewsContainer.appendChild(card);
    });
}

/**
 * Envoie un avis à l'API
 * @async
 * @function submitReview
 * @param {string} token - JWT de l'utilisateur
 * @param {string} placeId - ID de la place
 * @param {string} reviewText - Texte de l'avis
 * @param {string|number} rating - Note de l'avis
 * @returns {Promise<Response>} Réponse de l'API
 */
async function submitReview(token, placeId, reviewText, rating) {
    return fetch("http://localhost:5000/api/v1/reviews/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
            text: reviewText,
            rating: Number(rating),
            place_id: placeId
        })
    });
}

