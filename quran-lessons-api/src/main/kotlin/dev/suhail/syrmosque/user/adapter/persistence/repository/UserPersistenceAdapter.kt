package dev.suhail.syrmosque.user.adapter.persistence.repository

import dev.suhail.syrmosque.user.domain.User
import dev.suhail.syrmosque.user.port.UserRepository
import org.springframework.stereotype.Repository

@Repository
class UserPersistenceAdapter (
    private val jpaRepository: UserJpaRepository,
) : UserRepository {
    override fun save(user: User): User {
        TODO("Not yet implemented")
    }

    override fun existsByEmail(email: String): Boolean {
        TODO("Not yet implemented")
    }
}