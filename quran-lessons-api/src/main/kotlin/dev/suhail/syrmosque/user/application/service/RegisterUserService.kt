package dev.suhail.syrmosque.user.application.service

import dev.suhail.syrmosque.user.application.command.RegisterUserCommand
import dev.suhail.syrmosque.user.domain.Role
import dev.suhail.syrmosque.user.domain.User
import dev.suhail.syrmosque.user.port.RegisterUserUseCase
import dev.suhail.syrmosque.user.port.UserRepository
import org.springframework.stereotype.Service

@Service
class RegisterUserService (
    private val userRepository: UserRepository
) : RegisterUserUseCase {
    override fun register(command: RegisterUserCommand): User {
        if (userRepository.existsByEmail(command.email)) {
            throw IllegalArgumentException("User with email ${command.email} already exists")
        }

        val user = User(
            name = command.name,
            lastName = command.lastName,
            username = command.username,
            birthday = command.birthday,
            email = command.email,
            password = hashPassword(command.password),
            role = Role.USER
        )

        return userRepository.save(user)
    }

    private fun hashPassword(password: String): String {
        return password
    }
}