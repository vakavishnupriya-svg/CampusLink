package com.campuseventpro.dto;

import jakarta.validation.constraints.*;

public class RegistrationRequest {

    @NotNull(message = "Event ID is required")
    private Long eventId;

    @NotBlank(message = "Full name is required")
    @Size(min = 3, max = 50, message = "Full Name must be between 3 and 50 characters")
    private String fullName;

    @NotBlank(message = "Roll number is required")
    @Pattern(regexp = "^\\S+$", message = "Roll number cannot contain spaces")
    private String rollNumber;

    @NotBlank(message = "Email is required")
    @Email(message = "Invalid email format")
    private String email;

    @NotBlank(message = "Phone number is required")
    @Pattern(regexp = "^[0-9]{10}$", message = "Invalid phone number. Must be exactly 10 digits")
    private String phone;

    public RegistrationRequest() {}

    public RegistrationRequest(Long eventId, String fullName, String rollNumber, String email, String phone) {
        this.eventId = eventId;
        this.fullName = fullName;
        this.rollNumber = rollNumber;
        this.email = email;
        this.phone = phone;
    }

    public Long getEventId() {
        return eventId;
    }

    public void setEventId(Long eventId) {
        this.eventId = eventId;
    }

    public String getFullName() {
        return fullName;
    }

    public void setFullName(String fullName) {
        this.fullName = fullName;
    }

    public String getRollNumber() {
        return rollNumber;
    }

    public void setRollNumber(String rollNumber) {
        this.rollNumber = rollNumber;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getPhone() {
        return phone;
    }

    public void setPhone(String phone) {
        this.phone = phone;
    }
}
