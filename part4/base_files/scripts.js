document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            // Récupérer les valeurs
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            // Vider ancien message d'erreur
            document.getElementById('error-message').textContent = '';

            // Appeler login
            await loginUser(email, password);
        });
    }
});

async function loginUser(email, password) {
    try {
        const response = await fetch('http://localhost:5000/api/v1/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        if (response.ok) {
            const data = await response.json();
            document.cookie = `token=${data.access_token}; path=/`;
            window.location.href = 'index.html';
        } else {
            // Afficher erreur login
            document.getElementById('error-message').textContent =
                'Incorrect email or password';
        }

    } catch (error) {
        // Erreur technique (serveur down, réseau, etc.)
        document.getElementById('error-message').textContent =
            'Server error, please try again later';
    }
}

function checkAuthentication() {
      const token = getCookie('token');
      const loginLink = document.getElementById('login-link');

      if (!token) {
          loginLink.style.display = 'block';
      } else {
          loginLink.style.display = 'none';
          // Fetch places data if the user is authenticated
          fetchPlaces(token);
      }
  }
  function getCookie(name) {
      // Function to get a cookie value by its name
      document.cookie = `token=&{data.name.acces_token}
  }