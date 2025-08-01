package dev.suhail.syrmosque.user.adapter.persistence.repository.jpa

import dev.suhail.syrmosque.user.adapter.persistence.entity.UserEntity
import org.springframework.data.jpa.repository.JpaRepository

interface UserJpaRepository : JpaRepository<UserEntity, Long> {
    fun existsByEmail(email: String): Boolean
}