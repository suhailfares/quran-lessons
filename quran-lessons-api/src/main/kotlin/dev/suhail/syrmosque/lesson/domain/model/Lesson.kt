package dev.suhail.syrmosque.lesson.domain.model

import java.time.LocalDate

data class Lesson(
    val id: Long = 0,
    val name: String,
    val arabicName: String,
    val lessonType: LessonType,
    val teacherId: Long,
    val teacherProfileId: Long? = null,
    val studentId: Long,
    val date: LocalDate
)
