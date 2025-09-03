package dev.suhail.syrmosque.user.domain

import java.time.LocalDate

data class User(
    val id: Long = 0,
    val name: String,
    val lastName: String,
    val username: String,
    val birthday: LocalDate,
    val email: String,
    val password: String,
    val role: Role,
    var studentProfile: StudentProfile? = null,
    var teacherProfile: TeacherProfile? = null,
){
    val fullName: String = "$name $lastName"

    fun assignStudentProfile(profile: StudentProfile): StudentProfile {
        if (this.studentProfile != null) return this.studentProfile!!
        if (this.role == Role.TEACHER) throw IllegalArgumentException("A Teacher must not have a student profile")
        studentProfile = profile
        return studentProfile!!
    }

    fun assignTeacherProfile(profile: TeacherProfile): TeacherProfile {
        if (this.teacherProfile != null) return this.teacherProfile!!
        if (this.role == Role.STUDENT) throw IllegalArgumentException("A Student must not have a teacher profile")
        teacherProfile = profile
        return teacherProfile!!
    }



}

enum class Role {
    ADMIN, TEACHER, STUDENT, USER
}
