import React, { useState } from "react";
import { makeStyles, withStyles } from "@material-ui/core/styles";
import IconButton from "@material-ui/core/IconButton";
import Menu from "@material-ui/core/Menu";
import MenuItem from "@material-ui/core/MenuItem";
import MenuIcon from "@material-ui/icons/Menu";
import ExitToAppIcon from "@material-ui/icons/ExitToApp";

import { useHistory } from "react-router-dom";

const useStyles = makeStyles(theme => ({
  root: {
    color: theme.palette.secondary.dark,
    marginRight: theme.spacing(2)
  },
  menuIcon: {
    marginRight: theme.spacing(1.5)
  }
}));

const StyledMenu = withStyles({
  paper: {
    border: "1px solid #d3d4d5"
  }
})(props => (
  <Menu
    elevation={0}
    getContentAnchorEl={null}
    anchorOrigin={{
      vertical: "bottom",
      horizontal: "center"
    }}
    transformOrigin={{
      vertical: "top",
      horizontal: "center"
    }}
    {...props}
  />
));

export default function HeaderDropdownMenu() {
  const history = useHistory();
  const classes = useStyles();
  const [anchorEl, setAnchorEl] = useState(null);

  function handleLogout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");

    history.push("/login");
  }

  function handleClick(event) {
    setAnchorEl(event.currentTarget);
  }

  function handleClose() {
    setAnchorEl(null);
  }

  return (
    <React.Fragment>
      <IconButton
        edge="start"
        className={classes.root}
        onClick={handleClick}
        aria-controls="dropdown-menu"
        aria-haspopup="true"
      >
        <MenuIcon />
      </IconButton>

      <StyledMenu
        id="dropdown-menu"
        anchorEl={anchorEl}
        keepMounted
        open={Boolean(anchorEl)}
        onClose={handleClose}
      >
        <MenuItem onClick={handleLogout}>
          <ExitToAppIcon className={classes.menuIcon} />
          Logout
        </MenuItem>
      </StyledMenu>
    </React.Fragment>
  );
}
