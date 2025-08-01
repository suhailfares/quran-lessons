package dev.suhail.syrmosque.user.application.service

import dev.suhail.syrmosque.user.application.command.RegisterUserCommand
import dev.suhail.syrmosque.user.domain.User
import dev.suhail.syrmosque.user.port.RegisterUserUseCase
import dev.suhail.syrmosque.user.port.UserRepository
import org.springframework.stereotype.Service

@Service
class RegisterUserService (
    private val userRepository: UserRepository
) : RegisterUserUseCase {
    override fun register(command: RegisterUserCommand): User {
        TODO("Not yet implemented")
    }
}