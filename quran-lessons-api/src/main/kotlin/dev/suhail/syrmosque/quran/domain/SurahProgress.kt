package dev.suhail.syrmosque.quran.domain

class SurahProgress (
    val id: Long = 0,
    val surahId: Long,
    val status: SurahProgressStatus,
    //this is a list of ids that the user of the verses that the user has learned
    val reachedVerseId: Long,
)

enum class SurahProgressStatus {
    LEARNING,
    COMPLETED
}

