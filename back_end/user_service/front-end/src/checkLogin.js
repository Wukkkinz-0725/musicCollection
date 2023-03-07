
async function checkLogin(navigate, requestOptions) {
    fetch("http://localhost:9001/v1/users/check", requestOptions)
      .then((response) => {
        console.log(response);
        if (response.status == 200) {
            navigate("/Main")
        }
        else {
            navigate('/Login');
        }
      })
      .catch((error) => {
        console.log("dealt with 401");
        navigate('/Login');
    });
}

export default checkLogin;