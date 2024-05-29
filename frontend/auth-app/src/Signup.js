import React, {useState}from 'react'
import {Link} from 'react-router-dom'

const Signup = () => {

    // creating states that are in the form component
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [success, setSuccess] = useState(false)

    const validateForm = () =>{
        if (!username || !password){
            setError("Username and Password are required")
            return false
        }
        setError("")
        return true;
        
    }
    
    const handleSubmit = async (event) =>{
        event.preventDefault();
        if (!validateForm())
        return;

         const formData = {
            username,
            password,
         };

         try {
            const response = await fetch ("http://localhost:8000/register", {
                method : "POST",
                headers: {
                    "Content-Type":"application/json",

                },
                body: JSON.stringify(formData),

            })
            if (response.ok){
                // registration successful, you can navigate to the login page or display a success message
                console.log("Registration successful");
                setSuccess(true)
                

            }else {
                const errorData = await response.json();
                setError(errorData.detail || 'Registration failed');
                setSuccess(false);
            }
         } catch (error){
            setError('An Error occured. Please try again later');
            setSuccess(false);
         }
    }

  return (
    <div>
        <form onSubmit={handleSubmit}>
        <div>
            <label>Username:</label>
            <input
             type="text"
             value={username}
             onChange={(e) => setUsername(e.target.value)}
             />   
        </div>
        <div>
            <label>Password:</label>
            <input
             type="password"
             value={password}
             onChange={(e) => setPassword(e.target.value)}
             />   
        </div>
           <button type ="submt">Sign In</button>
           {error && <p style={{color:"red"}}>{error}</p>}
           {success && <p style={{color:'green'}}>Account created successfully</p>}
        </form>
        <p>
            Already have an account? <Link to='/'>Login</Link>
        </p>
    </div>
  )
}

export default Signup