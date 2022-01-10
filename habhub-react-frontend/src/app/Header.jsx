import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";

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
