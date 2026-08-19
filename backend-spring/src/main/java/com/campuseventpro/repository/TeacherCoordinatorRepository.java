package com.campuseventpro.repository;

import com.campuseventpro.entity.TeacherCoordinator;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface TeacherCoordinatorRepository extends JpaRepository<TeacherCoordinator, Long> {
    Optional<TeacherCoordinator> findByEmail(String email);
    Optional<TeacherCoordinator> findByEmployeeId(String employeeId);
    List<TeacherCoordinator> findByStatus(String status);
}
