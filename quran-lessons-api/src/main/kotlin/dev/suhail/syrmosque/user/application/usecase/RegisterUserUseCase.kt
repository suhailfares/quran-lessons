package dev.suhail.syrmosque.user.application.usecase

import dev.suhail.syrmosque.user.application.command.RegisterUserCommand
import dev.suhail.syrmosque.user.domain.User

fun interface RegisterUserUseCase {
    fun register(command: RegisterUserCommand) : User
}