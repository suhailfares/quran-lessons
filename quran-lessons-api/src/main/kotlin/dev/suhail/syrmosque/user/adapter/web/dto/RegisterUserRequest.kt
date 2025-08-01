package dev.suhail.syrmosque.user.adapter.web.dto

import dev.suhail.syrmosque.user.application.command.RegisterUserCommand
import java.time.LocalDate

data class RegisterUserRequest (
    val name: String,
    val lastName: String,
    val username: String,
    val birthday: LocalDate,
    val email: String,
    val password: String,
) {
    fun toCommand() = RegisterUserCommand(
        name, lastName, username, birthday, email, password,
    )
}