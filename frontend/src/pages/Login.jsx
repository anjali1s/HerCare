import {useState} from "react";
import {useNavigate} from "react-router-dom";
import api from "../api/api";
import "./auth.css";


function Login(){

const navigate = useNavigate();


const [email,setEmail]=useState("");
const [password,setPassword]=useState("");
const [loading,setLoading]=useState(false);
const [error,setError]=useState("");



async function login(){

setLoading(true);
setError("");

try{

const res = await api.post(
"/login",
{
email,
password
}
);


localStorage.setItem(
"token",
res.data.access_token
);


navigate("/chat");


}
catch(error){

setError(
error.response?.data?.detail ||
"Invalid login details"
);

}

finally{

setLoading(false);

}

}



return (

<div className="auth-page">


{/* HEADER LIKE CHAT PAGE */}

<header className="auth-header">


<div>

<h1>
HerCare Plus
</h1>

<p>
Women's Health AI Assistant
</p>

</div>



<div className="auth-logo">

🌸

</div>


</header>





{/* CENTER LOGIN CARD */}

<div className="auth-container">


<div className="auth-card">



<div className="brand">


<div className="logo">

✨

</div>



<h1>
Welcome Back
</h1>


<p>
Your intelligent health assistant
</p>


</div>





<h2>
Login
</h2>





<input

type="email"

placeholder="Email address"

value={email}

onChange={
e=>setEmail(e.target.value)
}

/>





<input

type="password"

placeholder="Password"

value={password}

onChange={
e=>setPassword(e.target.value)
}

/>





{
error &&

<p className="error">

{error}

</p>

}





<button

onClick={login}

disabled={loading}

>


{
loading
?
"Signing in..."
:
"Login"
}


</button>





<div className="switch">


Don't have an account?


<span

onClick={
()=>navigate("/register")
}

>

Create account

</span>



</div>



</div>


</div>


</div>

);


}


export default Login;