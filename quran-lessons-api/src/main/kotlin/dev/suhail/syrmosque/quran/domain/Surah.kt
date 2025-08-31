package dev.suhail.syrmosque.quran.domain

data class Surah(
    val id: Long = 0,
    val name: String,
    val arabicName: String,
    val index: Int,
    val versesCount: Int,
    val juzId: Long,
    val verses: List<Verse> = emptyList(),
)

data class Verse(
    val id: Long = 0,
    val index: Int,
)
