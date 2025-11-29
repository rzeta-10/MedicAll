// email regex check
function validateEmail(email) {
    const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return re.test(email);
}

// basic phone validation
function validatePhone(phone) {
    const clean = phone.replace(/[\s\-\(\)\+]/g, '');
    return /^\d{10,15}$/.test(clean);
}

// password strength check
function validatePassword(pwd) {
    if (!pwd || pwd.length < 6) {
        return {
            valid: false,
            message: 'Password must be at least 6 characters',
            strength: 'weak'
        };
    }

    let strength = 'weak';
    if (pwd.length >= 8) strength = 'medium';
    if (pwd.length >= 12 && /[A-Z]/.test(pwd) && /[0-9]/.test(pwd)) strength = 'strong';

    return {
        valid: true,
        message: 'Password is valid',
        strength: strength
    };
}

function validatePastDate(d) {
    if (!d) return false;
    const date = new Date(d);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return date <= today;
}

function validateFutureDate(d) {
    if (!d) return false;
    const date = new Date(d);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return date >= today;
}

function validateTimeRange(start, end) {
    if (!start || !end) return false;
    return end > start;
}

// ui helpers
function showError(el, msg) {
    hideError(el);
    el.classList.add('is-invalid');
    el.classList.remove('is-valid');

    const err = document.createElement('div');
    err.className = 'invalid-feedback';
    err.textContent = msg;
    el.parentNode.appendChild(err);
}

function hideError(el) {
    el.classList.remove('is-invalid');
    const existing = el.parentNode.querySelector('.invalid-feedback');
    if (existing) existing.remove();
}

function showSuccess(el) {
    hideError(el);
    el.classList.add('is-valid');
    el.classList.remove('is-invalid');
}

function clearValidation(el) {
    el.classList.remove('is-valid', 'is-invalid');
    const existing = el.parentNode.querySelector('.invalid-feedback');
    if (existing) existing.remove();
}

// main validation logic
function validateField(field) {
    const val = field.value.trim();
    const type = field.type;
    const name = field.name;

    if (field.hasAttribute('required') && !val) {
        showError(field, 'This field is required');
        return false;
    }

    if (val) {
        if (type === 'email' || name === 'email') {
            if (!validateEmail(val)) {
                showError(field, 'Please enter a valid email address');
                return false;
            }
        } else if (type === 'tel' || name === 'phone') {
            if (!validatePhone(val)) {
                showError(field, 'Please enter a valid phone number (10-15 digits)');
                return false;
            }
        } else if (type === 'password') {
            const res = validatePassword(val);
            if (!res.valid) {
                showError(field, res.message);
                return false;
            }
        } else if (type === 'date') {
            if (name === 'dob' && !validatePastDate(val)) {
                showError(field, 'Date of birth cannot be in the future');
                return false;
            } else if (name === 'date' && !validateFutureDate(val)) {
                showError(field, 'Date must be today or in the future');
                return false;
            }
        }

        const min = field.getAttribute('minlength');
        if (min && val.length < parseInt(min)) {
            showError(field, `Minimum length is ${min} characters`);
            return false;
        }
    }

    if (val) {
        showSuccess(field);
    } else {
        clearValidation(field);
    }
    return true;
}

// init
function initFormValidation(selector) {
    const form = typeof selector === 'string'
        ? document.querySelector(selector)
        : selector;

    if (!form) return;

    const fields = form.querySelectorAll('input, textarea, select');
    fields.forEach(f => {
        f.addEventListener('blur', function () {
            validateField(this);
        });

        f.addEventListener('input', function () {
            if (this.classList.contains('is-invalid') || this.classList.contains('is-valid')) {
                validateField(this);
            }
        });
    });

    form.addEventListener('submit', function (e) {
        let valid = true;

        fields.forEach(f => {
            if (!validateField(f)) valid = false;
        });

        const start = form.querySelector('[name="start_time"]');
        const end = form.querySelector('[name="end_time"]');
        if (start && end && start.value && end.value) {
            if (!validateTimeRange(start.value, end.value)) {
                showError(end, 'End time must be after start time');
                valid = false;
            }
        }

        if (!valid) {
            e.preventDefault();
            const err = form.querySelector('.is-invalid');
            if (err) {
                err.scrollIntoView({ behavior: 'smooth', block: 'center' });
                err.focus();
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', function () {
    const forms = document.querySelectorAll('form');
    forms.forEach(f => initFormValidation(f));
});
