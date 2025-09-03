package dev.suhail.syrmosque

import dev.suhail.syrmosque.user.domain.Role
import dev.suhail.syrmosque.user.domain.StudentProfile
import dev.suhail.syrmosque.user.domain.User
import org.junit.jupiter.api.Test
import org.springframework.boot.runApplication
import org.springframework.boot.test.context.SpringBootTest
import java.time.LocalDate

@SpringBootTest
class SyrmosqueApplicationTests {

	@Test
	fun contextLoads() {
        val user1 = User(
            id = 1,
            name = "Suhail",
            lastName = "Fares",
            username = "suhail",
            email = "suhail.fares@gmail.com",
            password = "suhelfares",
            birthday = LocalDate.of(1999, 12, 25),
            role = Role.USER
        )
        val sp1 = StudentProfile(userId = user1.id)

        user1.assignStudentProfile(sp1)

        println(user1.studentProfile)

	}



}