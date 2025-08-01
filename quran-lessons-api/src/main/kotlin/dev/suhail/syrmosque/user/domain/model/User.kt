package dev.suhail.syrmosque.user.domain.model

import java.time.LocalDate

data class User(
    val id: Long = 0,
    val name: String,
    val lastName: String,
    val username: String,
    val birthday: LocalDate,
    val email: String,
    val password: String,
    val role: Role,
    val studentProfile: StudentProfile? = null,
    val teacherProfile: TeacherProfile? = null
)
