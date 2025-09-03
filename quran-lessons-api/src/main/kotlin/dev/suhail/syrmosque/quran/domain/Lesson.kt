package dev.suhail.syrmosque.quran.domain

import java.time.LocalDate

data class Lesson(
    val id: Long = 0,
    val name: String,
    val arabicName: String,
    val teacherId: Long,
    val teacherProfileId: Long? = null,
    val studentIds: List<Long>,
    val surahId: Long,
    val date: LocalDate,
    val status: LessonStatus
)

enum class LessonStatus {
    UPCOMING,
    COMPLETED
}