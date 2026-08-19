/* Campus Event Pro - Form Validation Helper */

class FormValidator {
  static validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(String(email).toLowerCase());
  }

  static validatePassword(password) {
    return password && password.length >= 6;
  }

  static validateRequired(value) {
    return value && value.trim().length > 0;
  }

  static bindValidation(formElement, callback) {
    if (!formElement) return;

    formElement.addEventListener('submit', (e) => {
      e.preventDefault();
      const formData = new FormData(formElement);
      const data = Object.fromEntries(formData.entries());

      let isValid = true;
      const inputs = formElement.querySelectorAll('input[required], select[required], textarea[required]');

      inputs.forEach(input => {
        if (!FormValidator.validateRequired(input.value)) {
          input.classList.add('is-invalid');
          isValid = false;
        } else {
          input.classList.remove('is-invalid');
        }

        if (input.type === 'email' && !FormValidator.validateEmail(input.value)) {
          input.classList.add('is-invalid');
          isValid = false;
        }
      });

      if (isValid) {
        callback(data);
      } else {
        APIClient.showToast('Please fill out all required fields correctly', 'error');
      }
    });
  }
}
