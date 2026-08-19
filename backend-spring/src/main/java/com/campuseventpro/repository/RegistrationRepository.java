package com.campuseventpro.repository;

import com.campuseventpro.entity.Registration;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface RegistrationRepository extends JpaRepository<Registration, Long> {

    boolean existsByEventIdAndRollNumber(Long eventId, String rollNumber);

    List<Registration> findByEventId(Long eventId);

    @Query("SELECT r FROM Registration r WHERE " +
           "(:eventId IS NULL OR r.eventId = :eventId) AND " +
           "(:search IS NULL OR LOWER(r.fullName) LIKE LOWER(CONCAT('%', :search, '%')) OR LOWER(r.rollNumber) LIKE LOWER(CONCAT('%', :search, '%')) OR LOWER(r.email) LIKE LOWER(CONCAT('%', :search, '%')))")
    Page<Registration> searchRegistrations(
            @Param("eventId") Long eventId,
            @Param("search") String search,
            Pageable pageable
    );

    @Query("SELECT r FROM Registration r WHERE " +
           "(:eventId IS NULL OR r.eventId = :eventId) AND " +
           "(:search IS NULL OR LOWER(r.fullName) LIKE LOWER(CONCAT('%', :search, '%')) OR LOWER(r.rollNumber) LIKE LOWER(CONCAT('%', :search, '%')) OR LOWER(r.email) LIKE LOWER(CONCAT('%', :search, '%')))")
    List<Registration> searchRegistrationsList(
            @Param("eventId") Long eventId,
            @Param("search") String search
    );
}
