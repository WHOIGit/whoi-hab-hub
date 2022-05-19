import React from "react";
import makeStyles from '@mui/styles/makeStyles';
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";

import HeaderDropdownMenu from "./HeaderDropdownMenu";
import logo from "../images/logo-habhub.png";

const useStyles = makeStyles((theme) => ({
  root: {
    flexGrow: 1,
  },
  toolBar: {
    boxShadow: "none",
  },
  menuButton: {
    color: theme.palette.secondary.dark,
    marginRight: theme.spacing(2),
  },
}));

export default function Header() {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <AppBar className={classes.toolBar} position="fixed" color="transparent">
        <Toolbar>
          <HeaderDropdownMenu />
          <div>
            <img src={logo} alt="HABHub Logo" />
          </div>
        </Toolbar>
      </AppBar>
    </div>
  );
}
