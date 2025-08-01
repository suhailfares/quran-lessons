package dev.suhail.syrmosque.user.port

import dev.suhail.syrmosque.user.domain.User

interface UserRepository {
    fun save(user: User): User
    fun existsByEmail(email: String): Boolean
}