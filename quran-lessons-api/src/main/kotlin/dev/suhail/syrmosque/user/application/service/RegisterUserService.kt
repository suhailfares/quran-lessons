package dev.suhail.syrmosque.user.application.service

import dev.suhail.syrmosque.user.application.command.RegisterUserCommand
import dev.suhail.syrmosque.user.domain.User
import dev.suhail.syrmosque.user.application.usecase.RegisterUserUseCase
import dev.suhail.syrmosque.user.domain.Role
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

        if(command.role != Role.STUDENT && command.role != Role.TEACHER) {
            throw IllegalArgumentException("User must be a student or a teacher")
        }

        val user = User(
            name = command.name,
            lastName = command.lastName,
            username = command.username,
            birthday = command.birthday,
            email = command.email,
            password = hashPassword(command.password),
            role = command.role
        )

        return userRepository.save(user)
    }

    private fun hashPassword(password: String): String {
        return password
    }
}