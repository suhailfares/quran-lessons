package dev.suhail.syrmosque.user.adapter.web.dto

import dev.suhail.syrmosque.user.domain.User

data class RegisterUserResponse(
    val id: Long,
    val username: String,
    val email: String
) {
    companion object {
        fun from(user: User): RegisterUserResponse =
            RegisterUserResponse(user.id, user.username, user.email)
    }
}