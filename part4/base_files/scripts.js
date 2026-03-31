// ------------------------------
// Variables globales
// ------------------------------
let allPlaces = [];

// ------------------------------
// Au chargement de la page
// ------------------------------
document.addEventListener("DOMContentLoaded", () => {
    setupLoginForm();
    setupIndexPage();
    setupPlacePage();
});

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

function setupPlacePage() {
    const detailsContainer = document.getElementById("place-details");
    if (!detailsContainer) return;

    const token = getCookie("token");
    toggleAuthLinks(token);

    const addReviewSection = document.getElementById("add-review");
    if (addReviewSection) {
        addReviewSection.style.display = token ? "block" : "none";
    }

    const placeId = getPlaceIdFromURL();
    if (placeId) {
        fetchPlaceDetails(token, placeId);
    }
}

function toggleAuthLinks(token) {
    const loginLink = document.getElementById("login-link");

    if (token) {
        if (loginLink) loginLink.style.display = "none";
    } else {
        if (loginLink) loginLink.style.display = "block";
    }
}

// ------------------------------
// Récupérer un cookie
// ------------------------------
function getCookie(name) {
    const matches = document.cookie.match(
        new RegExp("(?:^|; )" + name.replace(/([.$?*|{}()\[\]\\/+^])/g, "\\$1") + "=([^;]*)")
    );
    return matches ? decodeURIComponent(matches[1]) : null;
}

// ------------------------------
// Login utilisateur
// ------------------------------
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

// ------------------------------
// Fetch des places
// ------------------------------
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

// ------------------------------
// Affichage des places
// ------------------------------
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

// ------------------------------
// Filtrer les prix
// ------------------------------
function applyPriceFilter() {
    const filter = document.getElementById("price-filter");
    if (!filter) return;

    const selectedPrice = filter.value;
    const placeCards = document.querySelectorAll(".place-card");

    placeCards.forEach((card) => {
        const price = Number(card.getAttribute("data-price"));
        card.style.display = selectedPrice === "all" || price <= Number(selectedPrice) ? "block" : "none";
    });
}

function getPlaceIdFromURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get("id");
}

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

// Create HTML elements for the place details and append them to #place-details.
function displayPlaceDetails(place) {
    const container = document.getElementById("place-details");
    if (!container) return;

    container.replaceChildren();

    const title = document.createElement("h1");
    title.textContent = place.title || "Place";

    const description = document.createElement("p");
    const rawDescription = typeof place.description === "string" ? place.description.trim() : "";
    const isPlaceholderDescription =
        rawDescription.toLowerCase() === "created for ui check" ||
        rawDescription.toLowerCase() === "no description available";
    const placeDescription = rawDescription && !isPlaceholderDescription
        ? rawDescription
        : "No description";
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
    const ownerName = place.owner
        ? `${place.owner.first_name || ""} ${place.owner.last_name || ""}`.trim()
        : "Unknown";
    owner.append(ownerLabel, document.createTextNode(ownerName || "Unknown"));

    const amenitiesTitle = document.createElement("h3");
    amenitiesTitle.textContent = "Amenities";

    const amenitiesList = document.createElement("ul");
    const amenities = Array.isArray(place.amenities) ? place.amenities : [];
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

        const comment = document.createElement("p");
        comment.classList.add("review-comment");
        comment.textContent = review.comment || "";

        const rating = document.createElement("p");
        rating.classList.add("review-rating");
        rating.textContent = `Rating: ${review.rating}/5`;

        card.append(comment, rating);
        reviewsContainer.appendChild(card);
    });
}