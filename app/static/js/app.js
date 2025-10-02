// API Configuration
const API_BASE_URL = '/api';
let authToken = localStorage.getItem('authToken');
let currentUser = null;

// DOM Elements
const elements = {
    loginBtn: document.getElementById('login-btn'),
    logoutBtn: document.getElementById('logout-btn'),
    userInfo: document.getElementById('user-info'),
    openUserModal: document.getElementById('open-user-modal'),
    openDonorModal: document.getElementById('open-donor-modal'),
    viewDonors: document.getElementById('view-donors'),
    donorsSection: document.getElementById('donors-section'),
    donorsList: document.getElementById('donors-list'),
    loadingOverlay: document.getElementById('loading-overlay'),
    notifications: document.getElementById('notifications')
};

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    
    // Check if user is already logged in
    if (authToken) {
        checkAuthStatus();
    }
});

function initializeApp() {
    console.log('🚀 Sistema de Registro de Donantes iniciado');
    updateAuthUI();
}

function setupEventListeners() {
    // Modal controls
    setupModalControls();
    
    // Auth buttons
    elements.loginBtn?.addEventListener('click', () => openModal('login-modal'));
    elements.logoutBtn?.addEventListener('click', logout);
    
    // Action buttons
    elements.openUserModal?.addEventListener('click', () => {
        if (checkAuthRequired()) {
            openModal('user-modal');
        }
    });
    
    elements.openDonorModal?.addEventListener('click', () => {
        if (checkAuthRequired()) {
            openModal('donor-modal');
        }
    });
    
    elements.viewDonors?.addEventListener('click', () => {
        if (checkAuthRequired()) {
            loadDonors();
        }
    });
    
    // Form submissions
    setupFormHandlers();
}

function setupModalControls() {
    // Close modal when clicking X or outside
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('close') || e.target.classList.contains('modal')) {
            const modalId = e.target.getAttribute('data-modal') || e.target.id;
            if (modalId) {
                closeModal(modalId);
            }
        }
        
        if (e.target.getAttribute('data-close')) {
            closeModal(e.target.getAttribute('data-close'));
        }
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const activeModal = document.querySelector('.modal.active');
            if (activeModal) {
                closeModal(activeModal.id);
            }
        }
    });
}

function setupFormHandlers() {
    // Login form
    const loginForm = document.getElementById('login-form');
    loginForm?.addEventListener('submit', handleLogin);
    
    // User registration form
    const userForm = document.getElementById('user-form');
    userForm?.addEventListener('submit', handleUserRegistration);
    
    // Donor registration form
    const donorForm = document.getElementById('donor-form');
    donorForm?.addEventListener('submit', handleDonorRegistration);
}

// Modal Management
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // Focus on first input
        const firstInput = modal.querySelector('input');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
        
        // Reset form
        const form = modal.querySelector('form');
        if (form) {
            form.reset();
            clearFormErrors(form);
        }
    }
}

// Authentication
async function handleLogin(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const credentials = {
        email: formData.get('email'),
        password: formData.get('password')
    };
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(credentials)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.access_token;
            currentUser = data.user;
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            
            updateAuthUI();
            closeModal('login-modal');
            showNotification('¡Bienvenido! Has iniciado sesión correctamente.', 'success');
        } else {
            showNotification(data.message || 'Error al iniciar sesión', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showNotification('Error de conexión. Verifica que el servidor esté funcionando.', 'error');
    } finally {
        showLoading(false);
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    
    updateAuthUI();
    elements.donorsSection.classList.add('hidden');
    showNotification('Has cerrado sesión correctamente.', 'info');
}

async function checkAuthStatus() {
    if (!authToken) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/profile`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            currentUser = data.user;
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            updateAuthUI();
        } else {
            logout();
        }
    } catch (error) {
        console.error('Auth check error:', error);
        logout();
    }
}

function updateAuthUI() {
    if (authToken && currentUser) {
        elements.loginBtn.classList.add('hidden');
        elements.logoutBtn.classList.remove('hidden');
        elements.userInfo.textContent = `${currentUser.email} (${currentUser.role})`;
        elements.userInfo.classList.remove('hidden');
    } else {
        elements.loginBtn.classList.remove('hidden');
        elements.logoutBtn.classList.add('hidden');
        elements.userInfo.textContent = 'No autenticado';
        elements.userInfo.classList.add('hidden');
    }
}

function checkAuthRequired() {
    if (!authToken) {
        showNotification('Debes iniciar sesión para realizar esta acción.', 'warning');
        openModal('login-modal');
        return false;
    }
    return true;
}

// User Registration
async function handleUserRegistration(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const userData = {
        email: formData.get('email'),
        password: formData.get('password'),
        role: formData.get('role')
    };
    
    // Validate form
    if (!validateUserForm(userData)) return;
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(userData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            closeModal('user-modal');
            showNotification(`Usuario ${userData.email} registrado exitosamente.`, 'success');
        } else {
            showNotification(data.message || 'Error al registrar usuario', 'error');
        }
    } catch (error) {
        console.error('User registration error:', error);
        showNotification('Error de conexión al registrar usuario.', 'error');
    } finally {
        showLoading(false);
    }
}

// Donor Registration
async function handleDonorRegistration(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const donorData = {
        first_name: formData.get('first_name'),
        last_name: formData.get('last_name'),
        email: formData.get('email'),
        phone: formData.get('phone') || null,
        birth_date: formData.get('birth_date'),
        blood_type: formData.get('blood_type'),
        weight: parseFloat(formData.get('weight')),
        last_donation_date: formData.get('last_donation_date') || null,
        medical_notes: formData.get('medical_notes') || null
    };
    
    // Validate form
    if (!validateDonorForm(donorData)) return;
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/donors`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(donorData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            closeModal('donor-modal');
            showNotification(`Donante ${donorData.first_name} ${donorData.last_name} registrado exitosamente.`, 'success');
            
            // Refresh donors list if visible
            if (!elements.donorsSection.classList.contains('hidden')) {
                loadDonors();
            }
        } else {
            showNotification(data.message || 'Error al registrar donante', 'error');
        }
    } catch (error) {
        console.error('Donor registration error:', error);
        showNotification('Error de conexión al registrar donante.', 'error');
    } finally {
        showLoading(false);
    }
}

// Load Donors
async function loadDonors() {
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/donors`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayDonors(data.donors || []);
            elements.donorsSection.classList.remove('hidden');
        } else {
            showNotification(data.message || 'Error al cargar donantes', 'error');
        }
    } catch (error) {
        console.error('Load donors error:', error);
        showNotification('Error de conexión al cargar donantes.', 'error');
    } finally {
        showLoading(false);
    }
}

function displayDonors(donors) {
    if (donors.length === 0) {
        elements.donorsList.innerHTML = `
            <div class="text-center" style="padding: 2rem;">
                <i class="fas fa-users" style="font-size: 3rem; color: #ccc; margin-bottom: 1rem;"></i>
                <p style="color: #666;">No hay donantes registrados aún.</p>
            </div>
        `;
        return;
    }
    
    elements.donorsList.innerHTML = donors.map(donor => `
        <div class="donor-card">
            <div class="donor-info">
                <div class="donor-field">
                    <i class="fas fa-user"></i>
                    <strong>Nombre:</strong> ${donor.first_name} ${donor.last_name}
                </div>
                <div class="donor-field">
                    <i class="fas fa-envelope"></i>
                    <strong>Email:</strong> ${donor.email}
                </div>
                <div class="donor-field">
                    <i class="fas fa-tint"></i>
                    <strong>Tipo de Sangre:</strong> ${donor.blood_type}
                </div>
                <div class="donor-field">
                    <i class="fas fa-weight"></i>
                    <strong>Peso:</strong> ${donor.weight} kg
                </div>
                <div class="donor-field">
                    <i class="fas fa-calendar"></i>
                    <strong>Edad:</strong> ${calculateAge(donor.birth_date)} años
                </div>
                <div class="donor-field">
                    <i class="fas fa-${donor.is_eligible ? 'check-circle' : 'times-circle'}"></i>
                    <strong>Elegible:</strong> 
                    <span class="${donor.is_eligible ? 'text-success' : 'text-danger'}">
                        ${donor.is_eligible ? 'Sí' : 'No'}
                    </span>
                </div>
            </div>
            ${donor.medical_notes ? `
                <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #eee;">
                    <div class="donor-field">
                        <i class="fas fa-notes-medical"></i>
                        <strong>Notas:</strong> ${donor.medical_notes}
                    </div>
                </div>
            ` : ''}
        </div>
    `).join('');
}

// Form Validation
function validateUserForm(userData) {
    const errors = [];
    
    if (!userData.email || !isValidEmail(userData.email)) {
        errors.push('Email válido es requerido');
    }
    
    if (!userData.password || userData.password.length < 8) {
        errors.push('La contraseña debe tener al menos 8 caracteres');
    }
    
    if (!userData.role) {
        errors.push('Rol es requerido');
    }
    
    if (errors.length > 0) {
        showNotification(errors.join('. '), 'error');
        return false;
    }
    
    return true;
}

function validateDonorForm(donorData) {
    const errors = [];
    
    if (!donorData.first_name || donorData.first_name.length < 2) {
        errors.push('Nombre debe tener al menos 2 caracteres');
    }
    
    if (!donorData.last_name || donorData.last_name.length < 2) {
        errors.push('Apellidos deben tener al menos 2 caracteres');
    }
    
    if (!donorData.email || !isValidEmail(donorData.email)) {
        errors.push('Email válido es requerido');
    }
    
    if (!donorData.birth_date) {
        errors.push('Fecha de nacimiento es requerida');
    } else {
        const age = calculateAge(donorData.birth_date);
        if (age < 18 || age > 65) {
            errors.push('La edad debe estar entre 18 y 65 años');
        }
    }
    
    if (!donorData.blood_type) {
        errors.push('Tipo de sangre es requerido');
    }
    
    if (!donorData.weight || donorData.weight < 50 || donorData.weight > 200) {
        errors.push('Peso debe estar entre 50 y 200 kg');
    }
    
    if (errors.length > 0) {
        showNotification(errors.join('. '), 'error');
        return false;
    }
    
    return true;
}

// Utility Functions
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function calculateAge(birthDate) {
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
        age--;
    }
    
    return age;
}

function clearFormErrors(form) {
    const errorElements = form.querySelectorAll('.error-message');
    errorElements.forEach(el => el.remove());
    
    const inputElements = form.querySelectorAll('input, select, textarea');
    inputElements.forEach(el => el.classList.remove('error'));
}

// UI Feedback
function showLoading(show) {
    if (show) {
        elements.loadingOverlay.classList.remove('hidden');
    } else {
        elements.loadingOverlay.classList.add('hidden');
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    
    notification.innerHTML = `
        <i class="${icons[type] || icons.info}"></i>
        <span>${message}</span>
    `;
    
    elements.notifications.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
    
    // Click to remove
    notification.addEventListener('click', () => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    });
}

// Export functions for debugging
window.debugAPI = {
    openModal,
    closeModal,
    showNotification,
    loadDonors,
    currentUser: () => currentUser,
    authToken: () => authToken
};