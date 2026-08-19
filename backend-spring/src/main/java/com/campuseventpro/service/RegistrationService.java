package com.campuseventpro.service;

import com.campuseventpro.dto.RegistrationRequest;
import com.campuseventpro.entity.Event;
import com.campuseventpro.entity.Registration;
import com.campuseventpro.repository.EventRepository;
import com.campuseventpro.repository.RegistrationRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Optional;

@Service
public class RegistrationService {

    private final RegistrationRepository registrationRepository;
    private final EventRepository eventRepository;

    public RegistrationService(RegistrationRepository registrationRepository, EventRepository eventRepository) {
        this.registrationRepository = registrationRepository;
        this.eventRepository = eventRepository;
    }

    @Transactional
    public Registration registerStudent(RegistrationRequest request) {
        // 1. Check for duplicate registration
        if (registrationRepository.existsByEventIdAndRollNumber(request.getEventId(), request.getRollNumber())) {
            throw new IllegalArgumentException("You have already registered.");
        }

        // 2. Create and save registration
        Registration registration = new Registration(
                request.getEventId(),
                request.getFullName().trim(),
                request.getRollNumber().trim(),
                request.getEmail().trim(),
                request.getPhone().trim()
        );

        Registration saved = registrationRepository.save(registration);

        // 3. Update Seat Occupancy if event exists
        Optional<Event> eventOpt = eventRepository.findById(request.getEventId());
        if (eventOpt.isPresent()) {
            Event event = eventOpt.get();
            event.setSeatsTaken(event.getSeatsTaken() + 1);
            eventRepository.save(event);
            saved.setEventTitle(event.getTitle());
        }

        return saved;
    }

    public Page<Registration> getAllRegistrations(Long eventId, String search, int page, int size, String sortBy, String sortDir) {
        Sort sort = sortDir.equalsIgnoreCase("asc") ? Sort.by(sortBy).ascending() : Sort.by(sortBy).descending();
        Pageable pageable = PageRequest.of(page, size, sort);
        String searchParam = (search != null && !search.trim().isEmpty()) ? search.trim() : null;

        Page<Registration> registrations = registrationRepository.searchRegistrations(eventId, searchParam, pageable);
        registrations.forEach(r -> {
            eventRepository.findById(r.getEventId()).ifPresent(e -> r.setEventTitle(e.getTitle()));
        });
        return registrations;
    }

    public Optional<Registration> getRegistrationById(Long id) {
        Optional<Registration> regOpt = registrationRepository.findById(id);
        regOpt.ifPresent(r -> {
            eventRepository.findById(r.getEventId()).ifPresent(e -> r.setEventTitle(e.getTitle()));
        });
        return regOpt;
    }

    @Transactional
    public boolean deleteRegistration(Long id) {
        Optional<Registration> regOpt = registrationRepository.findById(id);
        if (regOpt.isPresent()) {
            Registration reg = regOpt.get();
            // Optionally decrement seats
            Optional<Event> eventOpt = eventRepository.findById(reg.getEventId());
            if (eventOpt.isPresent()) {
                Event event = eventOpt.get();
                if (event.getSeatsTaken() > 0) {
                    event.setSeatsTaken(event.getSeatsTaken() - 1);
                    eventRepository.save(event);
                }
            }
            registrationRepository.deleteById(id);
            return true;
        }
        return false;
    }

    public ByteArrayInputStream exportRegistrationsToCsv(Long eventId, String search) {
        String searchParam = (search != null && !search.trim().isEmpty()) ? search.trim() : null;
        List<Registration> list = registrationRepository.searchRegistrationsList(eventId, searchParam);
        
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        PrintWriter pw = new PrintWriter(out, true, StandardCharsets.UTF_8);

        // Write CSV Header
        pw.println("ID,Event ID,Event Title,Full Name,Roll Number,Email,Phone,Registration Date");

        DateTimeFormatter dtf = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        for (Registration r : list) {
            String eventTitle = eventRepository.findById(r.getEventId())
                    .map(Event::getTitle)
                    .orElse("Event #" + r.getEventId());
            pw.printf("%d,%d,\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\"%n",
                    r.getId(),
                    r.getEventId(),
                    eventTitle.replace("\"", "\"\""),
                    r.getFullName().replace("\"", "\"\""),
                    r.getRollNumber(),
                    r.getEmail(),
                    r.getPhone(),
                    r.getRegisteredAt() != null ? r.getRegisteredAt().format(dtf) : ""
            );
        }
        pw.flush();
        return new ByteArrayInputStream(out.toByteArray());
    }
}
