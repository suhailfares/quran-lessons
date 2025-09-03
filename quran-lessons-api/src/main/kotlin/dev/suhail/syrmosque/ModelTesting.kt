package dev.suhail.syrmosque

import dev.suhail.syrmosque.quran.domain.Juz
import dev.suhail.syrmosque.quran.domain.Surah
import dev.suhail.syrmosque.quran.domain.Verse
import dev.suhail.syrmosque.user.domain.Role
import dev.suhail.syrmosque.user.domain.StudentProfile
import dev.suhail.syrmosque.user.domain.TeacherProfile
import dev.suhail.syrmosque.user.domain.User

fun main(){

    val suhail = User(name = "Suhail", lastName = "Fares", username = "suhail", email = "", password = "jdflkj", birthday = java.time.LocalDate.now(), role = Role.USER)
    val jamel = User(name = "Jamel", lastName = "Fares", username = "jamel", email = "", password = "jdflkj", birthday = java.time.LocalDate.now(), role = Role.USER)

    val sp1 = StudentProfile(id = 1, userId = suhail.id)
    val tp1 = TeacherProfile(id = 1, userId = jamel.id)
    tp1.studentIds?.add(suhail.id)

    suhail.assignStudentProfile(sp1)

    val amma = Juz(30, name = "Amma", arabicName = "عمى", index = 30)
    val fatihahVerse1 = Verse(id = 1, index = 1)
    val fatihah = Surah(id = 1, name = "Al-Fatiah", arabicName = "Surah1", index = 1, versesCount = 1, juzId = 30, verses = listOf(fatihahVerse1))

    amma.surahs = listOf(fatihah)

    println(amma.name)
    println(fatihah.verses)
}