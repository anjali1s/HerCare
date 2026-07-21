import {useState} from "react";
import {useNavigate} from "react-router-dom";
import api from "../api/api";
import "./auth.css";


function Register(){

const navigate = useNavigate();


const [name,setName]=useState("");
const [email,setEmail]=useState("");
const [password,setPassword]=useState("");

const [loading,setLoading]=useState(false);
const [error,setError]=useState("");




async function register(){

setLoading(true);
setError("");


try{


await api.post(
"/register",
{
name,
email,
password
}
);



navigate("/");


}


catch(err){


setError(
err.response?.data?.detail ||
"Registration failed"
);


}


finally{

setLoading(false);

}


}




return (

<div className="auth-page">



{/* HEADER SAME AS CHAT PAGE */}

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







<div className="auth-container">


<div className="auth-card">





<div className="brand">


<div className="logo">

✨

</div>



<h1>
Create Account
</h1>


<p>
Start your personalized health journey
</p>


</div>







<input

type="text"

placeholder="Full name"

value={name}

onChange={
e=>setName(e.target.value)
}

/>






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

onClick={register}

disabled={loading}

>


{

loading

?

"Creating account..."

:

"Register"

}


</button>







<div className="switch">


Already have an account?


<span

onClick={
()=>navigate("/")
}

>

Login

</span>



</div>





</div>


</div>


</div>


);


}


export default Register;