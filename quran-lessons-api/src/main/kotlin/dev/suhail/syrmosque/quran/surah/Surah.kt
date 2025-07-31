package dev.suhail.syrmosque.quran.surah

import dev.suhail.syrmosque.quran.juz.Juz
import jakarta.persistence.Entity
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.JoinColumn
import jakarta.persistence.ManyToOne
import jakarta.persistence.Table

@Entity
@Table(name = "surah")
class Surah (
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    val name: String,

    val arabicName: String,

    val index: Int,

    val versesCount: Int,

    @ManyToOne
    @JoinColumn(name = "juz_id")
    val juz: Juz
)