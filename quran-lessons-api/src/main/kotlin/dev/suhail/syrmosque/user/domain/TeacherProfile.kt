package dev.suhail.syrmosque.user.domain

data class TeacherProfile(
    val id: Long = 0,
    val userId: Long,
    val studentIds: MutableList<Long>? = null,
)
