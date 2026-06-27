if(localStorage.getItem("token")){

    window.location.href = "/"
}

const signupForm =
document.getElementById("signupForm")

signupForm.addEventListener(
    "submit",
    async (e) => {

    e.preventDefault()

    const username =
        document.getElementById("username").value

    const email =
        document.getElementById("email").value

    const password =
        document.getElementById("password").value

    try {

        const res = await fetch(
            "/api/auth/signup",
            {
                method:"POST",

                headers:{
                    "Content-Type":"application/json"
                },

                body:JSON.stringify({
                    username,
                    email,
                    password
                })
            }
        )

        const data = await res.json()

        if(data.success){

            localStorage.setItem(
                "token",
                data.token
            )

            localStorage.setItem(
                "username",
                data.user.username
            )

            window.location.href = "/"

        } else {

            alert(data.message)
        }

    } catch(err){

        console.error(err)

        alert("Signup failed")
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