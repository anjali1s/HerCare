import {useState} from "react";
import {useNavigate} from "react-router-dom";
import api from "../api/api";


function Register(){


const navigate = useNavigate();


const [name,setName]=useState("");
const [email,setEmail]=useState("");
const [password,setPassword]=useState("");



async function register(){


try{


await api.post(
"/auth/register",
{
name,
email,
password
}
);


alert("Account created");

navigate("/login");


}

catch(error){

alert(
error.response?.data?.detail ||
"Registration failed"
);

}


}



return (

<div className="auth-container">


<div className="auth-card">


<h2>
Create Account
</h2>



<input

placeholder="Full Name"

onChange={
e=>setName(e.target.value)
}

/>



<input

placeholder="Email"

onChange={
e=>setEmail(e.target.value)
}

/>



<input

type="password"

placeholder="Password"

onChange={
e=>setPassword(e.target.value)
}

/>



<button onClick={register}>

Register

</button>



<div className="auth-link">

Already have account?

<button
onClick={()=>navigate("/login")}
>
Login
</button>


</div>


</div>


</div>

);


}


export default Register;