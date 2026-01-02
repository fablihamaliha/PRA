// State management
let currentUser = null;
let userPreferences = null;

// DOM Elements
const authModal = document.getElementById('authModal');
const preferencesModal = document.getElementById('preferencesModal');
const loginBtn = document.getElementById('loginBtn');
const signupBtn = document.getElementById('signupBtn');
const logoutBtn = document.getElementById('logoutBtn');
const myProfileBtn = document.getElementById('myProfileBtn');
const getRecommendationsBtn = document.getElementById('getRecommendationsBtn');
const recommendationsCTA = document.getElementById('recommendationsCTA');
const searchForm = document.getElementById('searchForm');
const productSearch = document.getElementById('productSearch');
const emptyState = document.getElementById('emptyState');
const loadingState = document.getElementById('loadingState');
const resultsSection = document.getElementById('resultsSection');
const recommendationsSection = document.getElementById('recommendationsSection');
const dealsGrid = document.getElementById('dealsGrid');
const recommendationsGrid = document.getElementById('recommendationsGrid');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkAuthStatus();
    setupEventListeners();
});

// Check if user is logged in
async function checkAuthStatus() {
    try {
        const response = await fetch('/current-user');
        const data = await response.json();

        if (data.authenticated) {
            currentUser = data.user;
            updateUIForLoggedInUser();
            loadUserPreferences();
        } else {
            updateUIForGuest();
        }
    } catch (error) {
        console.error('Error checking auth status:', error);
        updateUIForGuest();
    }
}

function updateUIForLoggedInUser() {
    document.getElementById('userSection').classList.remove('hidden');
    document.getElementById('guestSection').classList.add('hidden');
    document.getElementById('userName').textContent = currentUser.name.split(' ')[0];

    // Show profile matching option if user has preferences
    if (userPreferences && userPreferences.skin_type) {
        document.getElementById('matchProfileOption').classList.remove('hidden');
    }
}

function updateUIForGuest() {
    document.getElementById('userSection').classList.add('hidden');
    document.getElementById('guestSection').classList.remove('hidden');
}

// Load user preferences
async function loadUserPreferences() {
    try {
        const response = await fetch(`/skincare/profile/${currentUser.id}`);
        if (response.ok) {
            userPreferences = await response.json();

            // Show profile matching option if preferences exist
            if (userPreferences && userPreferences.skin_type) {
                document.getElementById('matchProfileOption')?.classList.remove('hidden');
            }
        }
    } catch (error) {
        console.error('Error loading preferences:', error);
    }
}

// Setup event listeners
function setupEventListeners() {
    // Auth modals
    loginBtn?.addEventListener('click', () => openAuthModal('signin'));
    signupBtn?.addEventListener('click', () => openAuthModal('signup'));
    document.getElementById('closeAuthModal')?.addEventListener('click', closeAuthModal);

    // Logout
    logoutBtn?.addEventListener('click', handleLogout);

    // Preferences
    myProfileBtn?.addEventListener('click', openPreferencesModal);
    getRecommendationsBtn?.addEventListener('click', openPreferencesModal);
    recommendationsCTA?.addEventListener('click', openPreferencesModal);
    document.getElementById('closePreferencesModal')?.addEventListener('click', closePreferencesModal);

    // Forms
    document.getElementById('loginForm')?.addEventListener('submit', handleLogin);
    document.getElementById('signupForm')?.addEventListener('submit', handleSignup);
    document.getElementById('preferencesForm')?.addEventListener('submit', handlePreferences);
    searchForm?.addEventListener('submit', handleSearch);

    // Tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => switchTab(e.target.dataset.tab));
    });

    // Close modal on overlay click
    authModal?.addEventListener('click', (e) => {
        if (e.target === authModal) closeAuthModal();
    });
    preferencesModal?.addEventListener('click', (e) => {
        if (e.target === preferencesModal) closePreferencesModal();
    });
}

// Modal functions
function openAuthModal(tab = 'signin') {
    authModal.classList.add('active');
    document.body.style.overflow = 'hidden';
    switchTab(tab);
}

function closeAuthModal() {
    authModal.classList.remove('active');
    document.body.style.overflow = '';
}

function openPreferencesModal() {
    if (!currentUser) {
        openAuthModal('signup');
        return;
    }

    // Reset all checkboxes first
    document.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
    document.querySelectorAll('input[type="radio"]').forEach(rb => rb.checked = false);

    // Pre-fill form if user has preferences
    if (userPreferences) {
        // Skin type
        const skinTypeRadio = document.querySelector(`input[name="skin_type"][value="${userPreferences.skin_type}"]`);
        if (skinTypeRadio) skinTypeRadio.checked = true;

        // Budget
        document.getElementById('budget_min').value = userPreferences.budget_min || 10;
        document.getElementById('budget_max').value = userPreferences.budget_max || 100;

        // Concerns
        if (userPreferences.concerns) {
            userPreferences.concerns.forEach(concern => {
                const checkbox = document.querySelector(`input[name="concerns"][value="${concern}"]`);
                if (checkbox) checkbox.checked = true;
            });
        }

        // Preferred ingredients
        if (userPreferences.preferred_ingredients) {
            userPreferences.preferred_ingredients.forEach(ingredient => {
                const checkbox = document.querySelector(`input[name="preferred_ingredients"][value="${ingredient}"]`);
                if (checkbox) checkbox.checked = true;
            });
        }

        // Avoided ingredients
        if (userPreferences.avoided_ingredients) {
            userPreferences.avoided_ingredients.forEach(ingredient => {
                const checkbox = document.querySelector(`input[name="avoided_ingredients"][value="${ingredient}"]`);
                if (checkbox) checkbox.checked = true;
            });
        }

        // Product preferences
        if (userPreferences.product_preferences) {
            userPreferences.product_preferences.forEach(pref => {
                const checkbox = document.querySelector(`input[name="preferences"][value="${pref}"]`);
                if (checkbox) checkbox.checked = true;
            });
        }
    }

    preferencesModal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closePreferencesModal() {
    preferencesModal.classList.remove('active');
    document.body.style.overflow = '';
}

function switchTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });

    document.getElementById('signinPanel').classList.toggle('active', tabName === 'signin');
    document.getElementById('signupPanel').classList.toggle('active', tabName === 'signup');
}

// Auth handlers
async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const alertEl = document.getElementById('loginAlert');

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (data.success) {
            showAlert(alertEl, data.message, 'success');
            setTimeout(async () => {
                closeAuthModal();
                await checkAuthStatus();

                // Check if user has preferences, if not prompt them (only once per session)
                if (!userPreferences && !sessionStorage.getItem('preferences_prompted')) {
                    sessionStorage.setItem('preferences_prompted', 'true');
                    setTimeout(() => {
                        openPreferencesModal();
                    }, 500);
                }
            }, 1000);
        } else {
            showAlert(alertEl, data.error, 'error');
        }
    } catch (error) {
        showAlert(alertEl, 'Network error. Please try again.', 'error');
    }
}

async function handleSignup(e) {
    e.preventDefault();
    const name = document.getElementById('signup-name').value;
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
    const alertEl = document.getElementById('signupAlert');

    try {
        const response = await fetch('/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });

        const data = await response.json();

        if (data.success) {
            showAlert(alertEl, data.message, 'success');
            setTimeout(() => {
                closeAuthModal();
                checkAuthStatus();
                openPreferencesModal(); // Open preferences after signup
            }, 1000);
        } else {
            showAlert(alertEl, data.error, 'error');
        }
    } catch (error) {
        showAlert(alertEl, 'Network error. Please try again.', 'error');
    }
}

async function handleLogout() {
    try {
        const response = await fetch('/logout', { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            currentUser = null;
            userPreferences = null;
            updateUIForGuest();
            showState(emptyState);
        }
    } catch (error) {
        console.error('Logout error:', error);
    }
}

// Preferences handler
async function handlePreferences(e) {
    e.preventDefault();
    const alertEl = document.getElementById('preferencesAlert');

    const formData = new FormData(e.target);
    const skinType = formData.get('skin_type');
    const concerns = formData.getAll('concerns');
    const preferredIngredients = formData.getAll('preferred_ingredients');
    const avoidedIngredients = formData.getAll('avoided_ingredients');
    const productPreferences = formData.getAll('preferences');
    const budgetMin = parseFloat(formData.get('budget_min'));
    const budgetMax = parseFloat(formData.get('budget_max'));

    if (!skinType) {
        showAlert(alertEl, 'Please select a skin type', 'error');
        return;
    }

    const preferences = {
        user_id: currentUser.id,
        skin_type: skinType,
        concerns: concerns,
        budget_min: budgetMin,
        budget_max: budgetMax,
        preferred_ingredients: preferredIngredients,
        avoided_ingredients: avoidedIngredients,
        product_preferences: productPreferences
    };

    try {
        // Save preferences
        const saveResponse = await fetch('/skincare/quiz', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(preferences)
        });

        if (!saveResponse.ok) {
            throw new Error('Failed to save preferences');
        }

        userPreferences = preferences;

        // Show profile matching option now that preferences exist
        document.getElementById('matchProfileOption')?.classList.remove('hidden');

        // Get recommendations
        const recResponse = await fetch('/skincare/recommend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(preferences)
        });

        const recData = await recResponse.json();

        if (recData.recommendations) {
            closePreferencesModal();
            displayRecommendations(recData.recommendations);
        } else {
            showAlert(alertEl, 'Failed to get recommendations', 'error');
        }
    } catch (error) {
        console.error('Preferences error:', error);
        showAlert(alertEl, 'Error saving preferences. Please try again.', 'error');
    }
}

// Search handler
async function handleSearch(e) {
    e.preventDefault();
    const query = productSearch.value.trim();

    if (!query) return;

    showState(loadingState);

    try {
        const useLocation = document.getElementById('useLocation').checked;

        const response = await fetch('/deals/api/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                product_name: query,
                use_location: useLocation,
                max_results: 12
            })
        });

        const data = await response.json();

        if (data.success && data.data.all_deals) {
            displayDeals(query, data.data.all_deals, data.data.gpt_insights);
        } else {
            showState(emptyState);
        }
    } catch (error) {
        console.error('Search error:', error);
        showState(emptyState);
    }
}

// Display functions
function displayDeals(query, deals, gptInsights = null) {
    document.getElementById('searchedProduct').textContent = query;

    // Display GPT insights if available
    if (gptInsights) {
        const resultsHeader = document.querySelector('.results-header');
        const existingInsights = document.getElementById('gpt-insights');
        if (existingInsights) {
            existingInsights.remove();
        }

        const insightsDiv = document.createElement('div');
        insightsDiv.id = 'gpt-insights';
        insightsDiv.className = 'gpt-insights';
        insightsDiv.innerHTML = `
            <div class="gpt-insights-icon">✨</div>
            <div class="gpt-insights-text">${gptInsights}</div>
        `;
        resultsHeader.appendChild(insightsDiv);
    }

    // Filter deals based on profile matching if enabled
    const matchProfile = document.getElementById('matchProfile')?.checked;
    let filteredDeals = deals;

    if (matchProfile && userPreferences && userPreferences.skin_type) {
        // For skincare products, filter based on skin type in product name or description
        const skincareKeywords = ['moisturizer', 'cleanser', 'serum', 'cream', 'lotion', 'toner', 'mask', 'sunscreen', 'spf'];
        const isSkincareSearch = skincareKeywords.some(keyword => query.toLowerCase().includes(keyword));

        if (isSkincareSearch) {
            filteredDeals = deals.filter(deal => {
                const productText = `${deal.product_name} ${deal.description || ''}`.toLowerCase();

                // Match skin type
                const skinTypeMatch = productText.includes(userPreferences.skin_type);

                // Match preferred ingredients if any
                let ingredientMatch = true;
                if (userPreferences.preferred_ingredients && userPreferences.preferred_ingredients.length > 0) {
                    ingredientMatch = userPreferences.preferred_ingredients.some(ingredient => {
                        const ingredientName = ingredient.replace(/_/g, ' ');
                        return productText.includes(ingredientName);
                    });
                }

                // Avoid products with ingredients to avoid
                let avoidMatch = true;
                if (userPreferences.avoided_ingredients && userPreferences.avoided_ingredients.length > 0) {
                    avoidMatch = !userPreferences.avoided_ingredients.some(ingredient => {
                        const ingredientName = ingredient.replace(/_/g, ' ');
                        return productText.includes(ingredientName);
                    });
                }

                return skinTypeMatch || ingredientMatch && avoidMatch;
            });

            if (filteredDeals.length === 0) {
                filteredDeals = deals; // Show all if no matches
            }
        }
    }

    document.getElementById('resultsCount').textContent = `Found ${filteredDeals.length} deals${matchProfile && filteredDeals.length < deals.length ? ` (filtered for ${userPreferences.skin_type} skin)` : ''}`;

    dealsGrid.innerHTML = filteredDeals.map(deal => createDealCard(deal)).join('');

    showState(resultsSection);
}

function displayRecommendations(recommendations) {
    console.log('Displaying recommendations:', recommendations);

    if (!recommendations || recommendations.length === 0) {
        showAlert(document.getElementById('preferencesAlert'), 'No recommendations found. Try adjusting your preferences.', 'error');
        return;
    }

    recommendationsGrid.innerHTML = recommendations.map(rec => createRecommendationCard(rec)).join('');
    showState(recommendationsSection);
}

function createDealCard(deal) {
    const imageUrl = deal.image_url || `https://via.placeholder.com/300x200/6366F1/FFFFFF?text=${encodeURIComponent(deal.product_name.substring(0, 20))}`;
    const price = typeof deal.price === 'number' ? deal.price.toFixed(2) : '0.00';

    return `
        <div class="deal-card">
            <img src="${imageUrl}" alt="${deal.product_name}" class="deal-image"
                 onerror="this.src='https://via.placeholder.com/300x200/6366F1/FFFFFF?text=No+Image'">
            <div class="deal-info">
                <h3 class="deal-name">${deal.product_name}</h3>
                <p class="deal-seller">${deal.seller}</p>
                ${deal.original_price && deal.original_price > deal.price ?
                    `<p class="deal-original-price">Was: $${deal.original_price.toFixed(2)}</p>` : ''}
                <p class="deal-price">$${price}</p>
                <a href="${deal.url}" target="_blank" class="deal-btn">View Deal</a>
            </div>
        </div>
    `;
}

function createRecommendationCard(rec) {
    // Use 'name' field from API response (recommender returns 'name' not 'product_name')
    const productName = rec.name || rec.product_name || 'Product';
    const imageUrl = rec.image_url || 'https://via.placeholder.com/300x200/6366F1/FFFFFF?text=' + encodeURIComponent(productName.substring(0, 15));
    const price = rec.price ? parseFloat(rec.price) : null;

    // Escape product name for onclick attribute
    const escapedName = productName.replace(/'/g, "\\'").replace(/"/g, '&quot;');

    return `
        <div class="deal-card">
            <img src="${imageUrl}"
                 alt="${productName}" class="deal-image"
                 onerror="this.src='https://via.placeholder.com/300x200/6366F1/FFFFFF?text=No+Image'">
            <div class="deal-info">
                <h3 class="deal-name">${productName}</h3>
                <p class="deal-seller">${rec.brand || 'Recommended for you'}</p>
                ${rec.reason ? `<p style="font-size: 0.875rem; color: #6b7280; margin-bottom: 0.75rem;">${rec.reason}</p>` : ''}
                ${price ? `<p class="deal-price">$${price.toFixed(2)}</p>` : ''}
                <button class="deal-btn" onclick="window.searchForProduct('${escapedName}')">Find Best Price</button>
            </div>
        </div>
    `;
}

function searchForProduct(productName) {
    if (!productName || productName === 'undefined') {
        console.error('Invalid product name');
        return;
    }
    productSearch.value = productName;
    searchForm.dispatchEvent(new Event('submit'));
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Utility functions
function showState(state) {
    [emptyState, loadingState, resultsSection, recommendationsSection].forEach(s => s.classList.add('hidden'));
    state.classList.remove('hidden');
}

function showAlert(element, message, type = 'error') {
    element.textContent = message;
    element.className = `alert alert-${type}`;
    element.classList.remove('hidden');
    setTimeout(() => element.classList.add('hidden'), 5000);
}

// Make searchForProduct available globally
window.searchForProduct = searchForProduct;
