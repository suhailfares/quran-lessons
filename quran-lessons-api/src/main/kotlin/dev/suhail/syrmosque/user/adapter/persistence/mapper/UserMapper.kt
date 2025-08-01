package dev.suhail.syrmosque.user.adapter.persistence.mapper

import dev.suhail.syrmosque.user.adapter.persistence.entity.UserEntity
import dev.suhail.syrmosque.user.domain.User
import org.springframework.stereotype.Component

@Component
class UserMapper {

    fun toEntity(domain: User): UserEntity {
        return UserEntity(
            id = domain.id,
            name = domain.name,
            lastName = domain.lastName,
            username = domain.username,
            birthday = domain.birthday,
            email = domain.email,
            password = domain.password,
            role = domain.role,
            studentProfile = null,  // handled elsewhere, or add conditional mapping
            teacherProfile = null   // same here
        )
    }

    fun toDomain(entity: UserEntity): User {
        return User(
            id = entity.id,
            name = entity.name,
            lastName = entity.lastName,
            username = entity.username,
            birthday = entity.birthday,
            email = entity.email,
            password = entity.password,
            role = entity.role,
            studentProfile = null,  // map if needed
            teacherProfile = null   // map if needed
        )
    }
}
