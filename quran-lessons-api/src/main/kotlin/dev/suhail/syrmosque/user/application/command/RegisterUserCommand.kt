package dev.suhail.syrmosque.user.application.command

import dev.suhail.syrmosque.user.domain.Role
import java.time.LocalDate

data class RegisterUserCommand (
    val name: String,
    val lastName: String,
    val username: String,
    val birthday: LocalDate,
    val email: String,
    val password: String,
    val role: Role,
)