package com.campuseventpro.controller;

import com.campuseventpro.entity.TeacherCoordinator;
import com.campuseventpro.repository.TeacherCoordinatorRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/api/admin/teachers")
@CrossOrigin(origins = "*")
public class TeacherCoordinatorController {

    @Autowired
    private TeacherCoordinatorRepository teacherRepository;

    @GetMapping
    public ResponseEntity<List<TeacherCoordinator>> getAllTeachers() {
        return ResponseEntity.ok(teacherRepository.findAll());
    }

    @PutMapping("/{id}/status")
    public ResponseEntity<?> updateTeacherStatus(@PathVariable Long id, @RequestBody Map<String, String> payload) {
        Optional<TeacherCoordinator> teacherOpt = teacherRepository.findById(id);
        if (teacherOpt.isEmpty()) {
            Map<String, String> error = new HashMap<>();
            error.put("detail", "Teacher Coordinator not found");
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
        }

        String newStatus = payload.getOrDefault("status", "pending").toLowerCase();
        TeacherCoordinator teacher = teacherOpt.get();
        teacher.setStatus(newStatus);
        teacherRepository.save(teacher);

        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("message", "Teacher Coordinator status updated to " + newStatus);
        response.put("status", newStatus);
        return ResponseEntity.ok(response);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteTeacher(@PathVariable Long id) {
        if (!teacherRepository.existsById(id)) {
            Map<String, String> error = new HashMap<>();
            error.put("detail", "Teacher Coordinator not found");
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
        }
        teacherRepository.deleteById(id);

        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("message", "Teacher Coordinator account deleted");
        return ResponseEntity.ok(response);
    }
}
