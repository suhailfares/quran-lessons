package dev.suhail.syrmosque.security.controller

import dev.suhail.syrmosque.security.dto.AuthRequest
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/auth")
class AuthController {
    fun authenticate(@RequestBody request: AuthRequest) {

    }
}