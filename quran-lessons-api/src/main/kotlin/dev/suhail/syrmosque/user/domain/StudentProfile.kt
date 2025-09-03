package dev.suhail.syrmosque.user.domain

import dev.suhail.syrmosque.quran.domain.SurahProgress

data class StudentProfile(
    val id: Long = 0,
    val userId: Long,
    val teacherId: Long? = null,
    var quranProgress: List<SurahProgress> = emptyList(),
)
