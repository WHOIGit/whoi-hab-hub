/* eslint-disable no-unused-vars */
import React, { useState, useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import Button from "@material-ui/core/Button";
import TextField from "@material-ui/core/TextField";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import Checkbox from "@material-ui/core/Checkbox";
import Link from "@material-ui/core/Link";
import Grid from "@material-ui/core/Grid";
import Typography from "@material-ui/core/Typography";
import { makeStyles } from "@material-ui/core/styles";
import Container from "@material-ui/core/Container";
import { useHistory } from "react-router-dom";
import { loginUser, userSelector, clearState } from "./userSlice";

const useStyles = makeStyles(theme => ({
  paper: {
    marginTop: theme.spacing(8),
    display: "flex",
    flexDirection: "column",
    alignItems: "center"
  },
  form: {
    width: "100%", // Fix IE 11 issue.
    marginTop: theme.spacing(1)
  },
  submit: {
    margin: theme.spacing(3, 0, 2)
  }
}));

export default function Login() {
  const classes = useStyles();
  const dispatch = useDispatch();
  const history = useHistory();
  const { isFetching, isSuccess, isError, errorMessage } = useSelector(
    userSelector
  );
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = event => {
    event.preventDefault();
    console.log(username, password);
    const payload = {
      username: username,
      password: password
    };
    dispatch(loginUser(payload));
  };

  useEffect(() => {
    return () => {
      dispatch(clearState());
    };
  }, []);

  useEffect(() => {
    if (isError) {
      console.log(errorMessage);
      //toast.error(errorMessage);
      dispatch(clearState());
    }
    if (isSuccess) {
      dispatch(clearState());
      history.push("/");
    }
  }, [isError, isSuccess]);

  /*
  function handleSubmit(event) {
    console.log(username, password);
    event.preventDefault();

    async function getToken() {
      try {
        const response = await axiosInstance.post("api/v1/token/obtain/", {
          username: username,
          password: password
        });
        axiosInstance.defaults.headers["Authorization"] =
          "JWT " + response.data.access;
        localStorage.setItem("access_token", response.data.access);
        localStorage.setItem("refresh_token", response.data.refresh);
        console.log(response.data);
        return response;
      } catch (error) {
        console.log(error);
        return error;
      }
    }

    getToken();
  }
  */

  return (
    <Container component="main" maxWidth="xs">
      <div className={classes.paper}>
        <Typography component="h1" variant="h5">
          Sign in
        </Typography>
        <form className={classes.form} onSubmit={handleSubmit} noValidate>
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            id="username"
            label="Username"
            name="username"
            autoComplete="username"
            autoFocus
            onInput={e => setUsername(e.target.value)}
          />
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            name="password"
            label="Password"
            type="password"
            id="password"
            autoComplete="current-password"
            onInput={e => setPassword(e.target.value)}
          />
          <FormControlLabel
            control={<Checkbox value="remember" color="primary" />}
            label="Remember me"
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            color="primary"
            className={classes.submit}
          >
            Sign In
          </Button>
          <Grid container>
            <Grid item xs>
              <Link href="#" variant="body2">
                Forgot password?
              </Link>
            </Grid>
            <Grid item>
              <Link href="#" variant="body2">
                {"Don't have an account? Sign Up"}
              </Link>
            </Grid>
          </Grid>
        </form>
      </div>
    </Container>
  );
}
