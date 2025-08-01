package dev.suhail.syrmosque.lesson.adapter.out.persistence.entity

import jakarta.persistence.Entity
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.JoinColumn
import jakarta.persistence.ManyToOne
import jakarta.persistence.Table

@Entity
@Table(name = "surah")
class SurahEntity (
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    val name: String,

    val arabicName: String,

    val index: Int,

    val versesCount: Int,

    @ManyToOne
    @JoinColumn(name = "juz_id")
    val juz: JuzEntity
)