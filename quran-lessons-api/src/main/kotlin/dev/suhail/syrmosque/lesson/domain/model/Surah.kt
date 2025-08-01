package dev.suhail.syrmosque.lesson.domain.model

data class Surah(
    val id: Long = 0,
    val name: String,
    val arabicName: String,
    val index: Int,
    val versesCount: Int,
    val juzId: Long
)
