import axios from "axios";
const API_URL = process.env.REACT_APP_API_URL;

const baseURL = API_URL;

const axiosInstance = axios.create({
  baseURL: baseURL,
  timeout: 5000,
  headers: {
    "Content-Type": "application/json",
    accept: "application/json"
  }
});

export default axiosInstance;
