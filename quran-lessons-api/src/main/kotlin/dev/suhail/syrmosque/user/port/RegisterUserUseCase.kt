package dev.suhail.syrmosque.user.port

import dev.suhail.syrmosque.user.application.command.RegisterUserCommand
import dev.suhail.syrmosque.user.domain.User

fun interface RegisterUserUseCase {
    fun register(command: RegisterUserCommand) : User
}