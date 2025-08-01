package dev.suhail.syrmosque.user.adapter.out.persistence.entity

import dev.suhail.syrmosque.user.domain.model.Role
import jakarta.persistence.*
import java.time.LocalDate

@Entity
@Table(name = "users")
data class UserEntity(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(nullable = false)
    val name: String,

    @Column(name = "last_name", nullable = false)
    val lastName: String,

    @Column(nullable = false, unique = true)
    val username: String,

    @Column(nullable = false)
    val birthday: LocalDate,

    @Column(nullable = false, unique = true)
    val email: String,

    @Column(nullable = false)
    val password: String,

    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    val role: Role,

    @OneToOne(mappedBy = "user", cascade = [CascadeType.ALL], orphanRemoval = true)
    val studentProfile: StudentProfileEntity? = null,

    @OneToOne(mappedBy = "user", cascade = [CascadeType.ALL], orphanRemoval = true)
    val teacherProfile: TeacherProfileEntity? = null,
)
