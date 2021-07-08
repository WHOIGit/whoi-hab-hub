import axios from "axios";
const API_URL = process.env.REACT_APP_API_URL;

const baseURL = API_URL;

const axiosInstance = axios.create({
  baseURL: baseURL,
  //timeout: 5000,
  headers: {
    Authorization: localStorage.getItem("access_token")
      ? "JWT " + localStorage.getItem("access_token")
      : null,
    "Content-Type": "application/json",
    accept: "application/json"
  }
});

axiosInstance.interceptors.response.use(
  response => response,
  error => {
    const originalRequest = error.config;

    // If auth error is from the refresh view, send to login page and return error
    if (
      error.response.status === 401 &&
      originalRequest.url === baseURL + "api/v1/token/refresh/"
    ) {
      window.location.href = "/login/";
      return Promise.reject(error);
    }

    // If auth error is invalid access_token, go through refresh process
    if (
      error.response.data.code === "token_not_valid" &&
      error.response.status === 401 &&
      error.response.statusText === "Unauthorized"
    ) {
      const refreshToken = localStorage.getItem("refresh_token");

      if (refreshToken) {
        const tokenParts = JSON.parse(atob(refreshToken.split(".")[1]));

        // exp date in token is expressed in seconds, while now() returns milliseconds:
        const now = Math.ceil(Date.now() / 1000);
        console.log(tokenParts.exp);

        if (tokenParts.exp > now) {
          return axiosInstance
            .post("api/v1/token/refresh/", { refresh: refreshToken })
            .then(response => {
              localStorage.setItem("access_token", response.data.access);
              localStorage.setItem("refresh_token", response.data.refresh);

              axiosInstance.defaults.headers["Authorization"] =
                "JWT " + response.data.access;
              originalRequest.headers["Authorization"] =
                "JWT " + response.data.access;

              return axiosInstance(originalRequest);
            })
            .catch(err => {
              console.log(err);
            });
        } else {
          console.log("Refresh token is expired", tokenParts.exp, now);
          window.location.href = "/login/";
        }
      } else {
        console.log("Refresh token not available.");
        window.location.href = "/login/";
      }
    }

    // specific error handling done elsewhere
    return Promise.reject(error);
  }
);

export default axiosInstance;
