import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import axiosInstance from "../../app/apiAxios";

const initialState = {
  username: "",
  email: "",
  isFetching: false,
  isSuccess: false,
  isError: false,
  errorMessage: ""
};

export const loginUser = createAsyncThunk(
  "user/login",
  async ({ username, password }, thunkAPI) => {
    try {
      const response = await axiosInstance.post("api/v1/token/obtain/", {
        username: username,
        password: password
      });
      console.log(response);
      if (response.status === 200) {
        axiosInstance.defaults.headers["Authorization"] =
          "JWT " + response.data.access;
        localStorage.setItem("access_token", response.data.access);
        localStorage.setItem("refresh_token", response.data.refresh);
        return response.data;
      } else {
        return thunkAPI.rejectWithValue(response.data);
      }
    } catch (e) {
      console.log("Error", e.response.data);
      thunkAPI.rejectWithValue(e.response.data);
    }
  }
);

export const userSlice = createSlice({
  name: "userSlice",
  initialState: initialState,
  reducers: {
    clearState: state => {
      state.isError = false;
      state.isSuccess = false;
      state.isFetching = false;

      return state;
    }
  },
  extraReducers: {
    [loginUser.pending]: state => {
      state.isFetching = true;
    },
    [loginUser.fulfilled]: (state, { payload }) => {
      console.log(payload);
      //state.email = payload.email;
      //state.username = payload.name;
      state.isFetching = false;
      state.isSuccess = true;
      return state;
    },
    [loginUser.rejected]: (state, { payload }) => {
      console.log("payload", payload);
      state.isFetching = false;
      state.isError = true;
      state.errorMessage = payload.message;
    }
  }
});

// Action creators are generated for each case reducer function
export const { clearState } = userSlice.actions;

export default userSlice.reducer;

// Selector functions
export const userSelector = state => state.user;
