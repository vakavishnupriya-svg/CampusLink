/* Campus Event Pro - Event Registration Modal & Form Handling */

let currentRegisterEvent = null;

// Inject Registration Modal HTML into document body if not present
document.addEventListener('DOMContentLoaded', () => {
  if (!document.getElementById('event-reg-modal')) {
    const modalHTML = `
      <div id="event-reg-modal" class="modal-overlay">
        <div class="modal-container" style="max-width:540px;">
          <div class="modal-header">
            <h3 id="reg-modal-title" style="font-size:1.4rem;" class="text-gradient">📝 Register for Event</h3>
            <button class="modal-close" onclick="closeRegistrationModal()">&times;</button>
          </div>

          <div id="reg-modal-body">
            <p style="font-size:0.9rem; color:var(--text-muted); margin-bottom:1.25rem;">
              Fill in your details below to register for <strong id="modal-event-name-display" style="color:var(--text-main);">Event Name</strong>.
            </p>

            <form id="event-registration-form" novalidate>
              <input type="hidden" id="reg-event-id" value="" />

              <!-- Event Name Readonly Field -->
              <div class="form-group" style="margin-bottom:1.25rem;">
                <label class="form-label">Event Name</label>
                <div class="input-icon-group">
                  <span class="input-icon">📌</span>
                  <input type="text" id="reg-event-name-input" class="form-control form-control-with-icon" readonly style="opacity:0.8; background:rgba(255,255,255,0.05);" />
                </div>
              </div>

              <!-- Full Name Field -->
              <div class="form-group" id="group-fullname" style="margin-bottom:1.25rem;">
                <label class="form-label">Full Name *</label>
                <div class="input-icon-group">
                  <span class="input-icon">👤</span>
                  <input type="text" id="reg-fullname" class="form-control form-control-with-icon" placeholder="Full Name" required />
                </div>
                <div class="field-error-msg" id="err-fullname">Full Name must be between 3 and 50 characters.</div>
              </div>

              <!-- Roll Number Field -->
              <div class="form-group" id="group-rollno" style="margin-bottom:1.25rem;">
                <label class="form-label">Roll Number *</label>
                <div class="input-icon-group">
                  <span class="input-icon">🆔</span>
                  <input type="text" id="reg-rollno" class="form-control form-control-with-icon" placeholder="CSE123456" required />
                </div>
                <div class="field-error-msg" id="err-rollno">Roll number cannot contain spaces.</div>
              </div>

              <!-- Email Field -->
              <div class="form-group" id="group-email" style="margin-bottom:1.25rem;">
                <label class="form-label">Email Address *</label>
                <div class="input-icon-group">
                  <span class="input-icon">📧</span>
                  <input type="email" id="reg-email" class="form-control form-control-with-icon" placeholder="student@college.edu" required />
                </div>
                <div class="field-error-msg" id="err-email">Please enter a valid email address.</div>
              </div>

              <!-- Phone Field -->
              <div class="form-group" id="group-phone" style="margin-bottom:1.5rem;">
                <label class="form-label">Phone Number *</label>
                <div class="input-icon-group">
                  <span class="input-icon">📞</span>
                  <input type="tel" id="reg-phone" class="form-control form-control-with-icon" placeholder="9876543210" maxlength="10" required />
                </div>
                <div class="field-error-msg" id="err-phone">Invalid phone number. Must be exactly 10 digits.</div>
              </div>

              <div style="display:flex; justify-content:flex-end; gap:0.75rem; border-top:1px solid var(--border-color); padding-top:1.25rem;">
                <button type="button" class="btn btn-secondary btn-sm" onclick="closeRegistrationModal()">Cancel</button>
                <button type="submit" id="reg-submit-btn" class="btn btn-primary btn-sm">
                  <span id="btn-spinner" class="btn-spinner" style="display:none;"></span>
                  <span id="btn-text">Confirm Registration</span>
                </button>
              </div>
            </form>
          </div>

          <!-- Success Animation Screen -->
          <div id="reg-modal-success" style="display:none;" class="success-checkmark-wrapper">
            <div class="checkmark-circle">
              <span class="checkmark-icon">✓</span>
            </div>
            <h3 style="font-size:1.5rem; margin-bottom:0.5rem; color:#10B981;">Registration Successful</h3>
            <p style="color:var(--text-muted); font-size:0.95rem; margin-bottom:1.5rem;" id="success-subtext">
              Your seat has been reserved! Ticket QR code generated.
            </p>
            <button class="btn btn-primary" onclick="closeRegistrationModal()">Done</button>
          </div>
        </div>
      </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHTML);

    // Attach submit listener
    const form = document.getElementById('event-registration-form');
    if (form) {
      form.addEventListener('submit', handleRegistrationSubmit);
    }
  }
});

// Open Registration Modal
window.openRegistrationModal = function(eventId, eventTitle) {
  currentRegisterEvent = { id: eventId, title: eventTitle };

  const modal = document.getElementById('event-reg-modal');
  const eventIdInput = document.getElementById('reg-event-id');
  const eventNameInput = document.getElementById('reg-event-name-input');
  const eventNameDisplay = document.getElementById('modal-event-name-display');
  const form = document.getElementById('event-registration-form');
  const successScreen = document.getElementById('reg-modal-success');
  const bodyScreen = document.getElementById('reg-modal-body');

  if (!modal) return;

  // Reset form & state
  form.reset();
  resetFormValidationErrors();
  successScreen.style.display = 'none';
  bodyScreen.style.display = 'block';

  // Set event data
  eventIdInput.value = eventId;
  eventNameInput.value = eventTitle || `Event #${eventId}`;
  if (eventNameDisplay) eventNameDisplay.textContent = eventTitle || `Event #${eventId}`;

  // Pre-fill user data if available in localStorage
  const user = APIClient.getUser();
  if (user) {
    if (user.full_name) document.getElementById('reg-fullname').value = user.full_name;
    if (user.roll_number) document.getElementById('reg-rollno').value = user.roll_number;
    if (user.email) document.getElementById('reg-email').value = user.email;
    if (user.phone) document.getElementById('reg-phone').value = user.phone.replace(/[^0-9]/g, '').slice(-10);
  }

  modal.classList.add('active');
};

// Close Registration Modal
window.closeRegistrationModal = function() {
  const modal = document.getElementById('event-reg-modal');
  if (modal) modal.classList.remove('active');
};

// Reset Form Validation Errors
function resetFormValidationErrors() {
  ['fullname', 'rollno', 'email', 'phone'].forEach(field => {
    const group = document.getElementById(`group-${field}`);
    if (group) group.classList.remove('has-error');
  });
}

// Handle Form Submission
async function handleRegistrationSubmit(e) {
  e.preventDefault();
  resetFormValidationErrors();

  const eventId = parseInt(document.getElementById('reg-event-id').value);
  const fullName = document.getElementById('reg-fullname').value.trim();
  const rollNumber = document.getElementById('reg-rollno').value.trim();
  const email = document.getElementById('reg-email').value.trim();
  const phone = document.getElementById('reg-phone').value.trim();

  let isValid = true;

  // 1. Full Name Validation (3-50 chars)
  if (!fullName || fullName.length < 3 || fullName.length > 50) {
    showFieldError('fullname', 'Full Name must be between 3 and 50 characters.');
    isValid = false;
  }

  // 2. Roll Number Validation (No spaces, mandatory)
  if (!rollNumber) {
    showFieldError('rollno', 'Roll Number is required.');
    isValid = false;
  } else if (/\s/.test(rollNumber)) {
    showFieldError('rollno', 'Roll number cannot contain spaces.');
    isValid = false;
  }

  // 3. Email Validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email || !emailRegex.test(email)) {
    showFieldError('email', 'Please enter a valid email format.');
    isValid = false;
  }

  // 4. Phone Number Validation (Exactly 10 digits)
  const phoneRegex = /^[0-9]{10}$/;
  if (!phone || !phoneRegex.test(phone)) {
    showFieldError('phone', 'Invalid phone number. Must be exactly 10 digits.');
    isValid = false;
  }

  if (!isValid) return;

  // Disable submit button & show spinner
  const submitBtn = document.getElementById('reg-submit-btn');
  const btnSpinner = document.getElementById('btn-spinner');
  const btnText = document.getElementById('btn-text');

  submitBtn.disabled = true;
  btnSpinner.style.display = 'inline-block';
  btnText.textContent = 'Registering...';

  try {
    const payload = { eventId, fullName, rollNumber, email, phone };
    const response = await APIClient.request('/api/registrations', {
      method: 'POST',
      body: JSON.stringify(payload)
    });

    if (response && response.success === false) {
      APIClient.showToast(response.message || 'You have already registered.', 'error');
      if (response.message && response.message.includes('already registered')) {
        showFieldError('rollno', 'You have already registered for this event.');
      }
      return;
    }

    // Success! Show Checkmark Animation
    APIClient.showToast(response.message || 'Registration Successful', 'success');
    document.getElementById('reg-modal-body').style.display = 'none';
    document.getElementById('reg-modal-success').style.display = 'block';

    // Update UI elements across the page
    updateEventButtonState(eventId);
    updateEventSeatOccupancy(eventId);

    // Refresh catalog if function exists
    if (typeof fetchEvents === 'function') {
      fetchEvents();
    }
  } catch (err) {
    APIClient.showToast(err.message || 'Registration failed. Please try again.', 'error');
    if (err.message && err.message.includes('already registered')) {
      showFieldError('rollno', 'You have already registered for this event.');
    }
  } finally {
    submitBtn.disabled = false;
    btnSpinner.style.display = 'none';
    btnText.textContent = 'Confirm Registration';
  }
}

function showFieldError(field, message) {
  const group = document.getElementById(`group-${field}`);
  const errDiv = document.getElementById(`err-${field}`);
  if (group) group.classList.add('has-error');
  if (errDiv) errDiv.textContent = message;
}

// Update Event Button on Page
function updateEventButtonState(eventId) {
  const btn = document.getElementById(`btn-register-${eventId}`);
  if (btn) {
    btn.innerHTML = 'Registered ✓';
    btn.disabled = true;
    btn.className = 'btn btn-outline btn-sm';
    btn.style.opacity = '0.7';
  }
}

// Immediately Update Seat Occupancy Progress Bar
function updateEventSeatOccupancy(eventId) {
  const countSpan = document.getElementById(`seat-count-${eventId}`);
  const fillBar = document.getElementById(`seat-fill-${eventId}`);

  if (countSpan) {
    const text = countSpan.textContent; // e.g. "79/120 (66%)"
    const match = text.match(/(\d+)\/(\d+)/);
    if (match) {
      let current = parseInt(match[1]) + 1;
      let capacity = parseInt(match[2]);
      let newPercent = Math.min(100, Math.round((current / capacity) * 100));
      countSpan.textContent = `${current}/${capacity} (${newPercent}%)`;
      if (fillBar) fillBar.style.width = `${newPercent}%`;
    }
  }
}
