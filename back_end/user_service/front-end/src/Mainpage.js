import { useNavigate } from "react-router-dom";

function Mainpage() {

    const navigate = useNavigate();
    function handleResponse(response) {
        console.log(response);
        navigate("/");
    }

    function handleError(error) {
        console.log(error);
    }

    function Logout() {
        const requestOptions = {
            method: "POST",
            credentials: 'include',
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({}),
          };
        fetch("http://localhost:9001/v1/users/logout", requestOptions)
        .then((response) => handleResponse(response))
        .catch((error) => handleError(error));
    }


    return (
        <div>
            <div>
            <button onClick={Logout}>Log out</button>
            </div>
            <form>

            </form>
        </div>
    );
}

export default Mainpage;