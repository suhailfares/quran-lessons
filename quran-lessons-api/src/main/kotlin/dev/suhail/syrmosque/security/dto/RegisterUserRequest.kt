package dev.suhail.syrmosque.security.dto

import dev.suhail.syrmosque.user.application.command.RegisterUserCommand
import dev.suhail.syrmosque.user.domain.Role
import java.time.LocalDate

data class RegisterUserRequest (
    val name: String,
    val lastName: String,
    val username: String,
    val birthday: LocalDate,
    val email: String,
    val password: String,
    val role: Role
) {
    fun toCommand() = RegisterUserCommand(
        name, lastName, username, birthday, email, password, role
    )
}