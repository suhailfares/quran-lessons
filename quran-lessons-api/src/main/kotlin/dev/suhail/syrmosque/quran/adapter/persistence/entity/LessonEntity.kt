package dev.suhail.syrmosque.quran.adapter.persistence.entity

import dev.suhail.syrmosque.user.adapter.persistence.entity.TeacherProfileEntity
import dev.suhail.syrmosque.user.adapter.persistence.entity.UserEntity
import jakarta.persistence.*
import java.time.LocalDate

@Entity
class LessonEntity(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    val name: String,

    val arabicName: String,

    @ManyToOne
    @JoinColumn(name = "teacher_id")
    val teacher: UserEntity,

    @ManyToOne
    @JoinColumn(name = "teacher_profile_id")
    val teacherProfile: TeacherProfileEntity? = null,

    @ManyToOne
    @JoinColumn(name = "student_id")
    val student: UserEntity,

    val date: LocalDate,
)