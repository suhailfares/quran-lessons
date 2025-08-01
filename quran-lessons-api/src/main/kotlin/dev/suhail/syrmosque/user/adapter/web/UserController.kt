package dev.suhail.syrmosque.user.adapter.web

import dev.suhail.syrmosque.user.adapter.web.dto.RegisterUserRequest
import dev.suhail.syrmosque.user.adapter.web.dto.RegisterUserResponse
import dev.suhail.syrmosque.user.application.usecase.RegisterUserUseCase
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/users")
class UserController(
    private val registerUserUseCase: RegisterUserUseCase
) {

    @PostMapping
    fun register(@RequestBody request: RegisterUserRequest): ResponseEntity<RegisterUserResponse> {
        val user = registerUserUseCase.register(request.toCommand())
        return ResponseEntity.status(HttpStatus.OK).body(RegisterUserResponse.from(user))
    }
}