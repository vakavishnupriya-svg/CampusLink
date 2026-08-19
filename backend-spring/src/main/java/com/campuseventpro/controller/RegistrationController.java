package com.campuseventpro.controller;

import com.campuseventpro.dto.ApiResponse;
import com.campuseventpro.dto.RegistrationRequest;
import com.campuseventpro.entity.Registration;
import com.campuseventpro.service.RegistrationService;
import jakarta.validation.Valid;
import org.springframework.core.io.InputStreamResource;
import org.springframework.data.domain.Page;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.ByteArrayInputStream;
import java.util.Optional;

@RestController
@RequestMapping("/api/registrations")
@CrossOrigin(origins = "*")
public class RegistrationController {

    private final RegistrationService registrationService;

    public RegistrationController(RegistrationService registrationService) {
        this.registrationService = registrationService;
    }

    @PostMapping
    public ResponseEntity<ApiResponse<Registration>> createRegistration(@Valid @RequestBody RegistrationRequest request) {
        try {
            Registration registration = registrationService.registerStudent(request);
            return ResponseEntity.status(HttpStatus.CREATED)
                    .body(new ApiResponse<>(true, "Registration Successful", registration));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(ApiResponse.error(e.getMessage()));
        }
    }

    @GetMapping
    public ResponseEntity<ApiResponse<Page<Registration>>> getAllRegistrations(
            @RequestParam(required = false) Long eventId,
            @RequestParam(required = false) String search,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(defaultValue = "registeredAt") String sortBy,
            @RequestParam(defaultValue = "desc") String sortDir
    ) {
        Page<Registration> pageResult = registrationService.getAllRegistrations(eventId, search, page, size, sortBy, sortDir);
        return ResponseEntity.ok(ApiResponse.success("Registrations retrieved successfully", pageResult));
    }

    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<Registration>> getRegistrationById(@PathVariable Long id) {
        Optional<Registration> regOpt = registrationService.getRegistrationById(id);
        return regOpt
                .map(registration -> ResponseEntity.ok(ApiResponse.success("Registration details", registration)))
                .orElseGet(() -> ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(ApiResponse.error("Registration not found with ID: " + id)));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<ApiResponse<Void>> deleteRegistration(@PathVariable Long id) {
        boolean deleted = registrationService.deleteRegistration(id);
        if (deleted) {
            return ResponseEntity.ok(ApiResponse.success("Registration deleted successfully"));
        } else {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(ApiResponse.error("Registration not found with ID: " + id));
        }
    }

    @GetMapping("/export")
    public ResponseEntity<InputStreamResource> exportRegistrations(
            @RequestParam(required = false) Long eventId,
            @RequestParam(required = false) String search,
            @RequestParam(defaultValue = "csv") String format
    ) {
        ByteArrayInputStream in = registrationService.exportRegistrationsToCsv(eventId, search);
        String filename = "event_registrations_2026." + (format.equalsIgnoreCase("excel") || format.equalsIgnoreCase("xlsx") ? "xlsx" : "csv");

        HttpHeaders headers = new HttpHeaders();
        headers.add("Content-Disposition", "attachment; filename=" + filename);

        return ResponseEntity
                .ok()
                .headers(headers)
                .contentType(MediaType.parseMediaType("application/csv"))
                .body(new InputStreamResource(in));
    }
}
