import axios from "axios";
const API_URL = import.meta.env.VITE_API_URL;
const API_TOKEN = import.meta.env.VITE_API_TOKEN;

const baseURL = API_URL;

const axiosInstance = axios.create({
  baseURL: baseURL,
  //timeout: 5000,
  headers: {
    "Content-Type": "application/json",
    accept: "application/json",
    Authorization: `Token ${API_TOKEN}`,
  },
});

export default axiosInstance;
