package dev.suhail.syrmosque.lesson

import dev.suhail.syrmosque.user.TeacherProfile
import dev.suhail.syrmosque.user.User
import jakarta.persistence.Entity
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.JoinColumn
import jakarta.persistence.ManyToOne
import java.time.LocalDate

@Entity
class Lesson (
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    val name: String,

    val arabicName: String,

    val lessonType: LessonType,

    @ManyToOne
    @JoinColumn(name = "teacher_id")
    val teacher: User,

    @ManyToOne
    @JoinColumn(name = "teacher_profile_id")
    val teacherProfile: TeacherProfile? = null,

    @ManyToOne
    @JoinColumn(name = "student_id")
    val student: User,

    val date : LocalDate,
)