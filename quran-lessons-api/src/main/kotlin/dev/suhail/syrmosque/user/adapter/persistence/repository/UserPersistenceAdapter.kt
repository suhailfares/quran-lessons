package dev.suhail.syrmosque.user.adapter.persistence.repository

import dev.suhail.syrmosque.user.adapter.persistence.mapper.UserMapper
import dev.suhail.syrmosque.user.adapter.persistence.repository.jpa.UserJpaRepository
import dev.suhail.syrmosque.user.domain.User
import dev.suhail.syrmosque.user.port.UserRepository
import org.springframework.stereotype.Repository

@Repository
class UserPersistenceAdapter(
    private val jpaRepository: UserJpaRepository,
    private val userMapper: UserMapper
) : UserRepository {
    override fun save(user: User): User {
        val userEntity = userMapper.toEntity(user)
        return userMapper.toDomain(jpaRepository.save(userEntity))
    }

    override fun existsByEmail(email: String): Boolean {
        return jpaRepository.existsByEmail(email)
    }
}