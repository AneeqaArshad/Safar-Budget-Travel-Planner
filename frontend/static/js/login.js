const token =
    localStorage.getItem("token") ||
    sessionStorage.getItem("token")

if(token){
    window.location.href = "/"
}
const loginForm =
document.getElementById("loginForm")

loginForm.addEventListener(
    "submit",
    async (e) => {

    e.preventDefault()

    const email =
        document.getElementById("email").value

    const password =
        document.getElementById("password").value

    try {

        const res = await fetch(
            "/api/auth/login",
            {
                method: "POST",

                headers: {
                    "Content-Type":"application/json"
                },

                body: JSON.stringify({
                    email,
                    password
                })
            }
        )

        const data = await res.json()

        if(data.success){

            const rememberMe =document.getElementById("rememberMe").checked
            if (rememberMe) {
                localStorage.setItem("token",data.token)
                localStorage.setItem("username",data.user.username)
            } 
            else {
                sessionStorage.setItem("token", data.token)
                sessionStorage.setItem("username", data.user.username)
            }
            window.location.href = "/"

        } else {

            alert(data.message)
        }

    } catch(err){

        console.error(err)

        alert("Login failed")
    }
})
const togglePassword =
document.getElementById("togglePassword")

const passwordField =
document.getElementById("password")

togglePassword.addEventListener(
    "click",
    () => {

        if(passwordField.type === "password"){

            passwordField.type = "text"

        } else {

            passwordField.type = "password"
        }
    }
)