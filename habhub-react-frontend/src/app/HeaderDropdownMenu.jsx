import React, { useState } from "react";
import makeStyles from '@mui/styles/makeStyles';
import withStyles from '@mui/styles/withStyles';
import IconButton from "@mui/material/IconButton";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import MenuIcon from "@mui/icons-material/Menu";

import logoNehab from "../images/logo-nehab.png";
import logoNehabon from "../images/logo-nehabon.png";
import logoPhytoArm from "../images/logo-phytoarm.png";

const useStyles = makeStyles((theme) => ({
  root: {
    color: theme.palette.secondary.dark,
    marginRight: theme.spacing(2),
  },
  menuImg: {
    width: "200px",
  },
  menuImg2: {
    width: "170px",
  },
}));

const StyledMenu = withStyles({
  paper: {
    border: "1px solid #d3d4d5",
  },
})((props) => (
  <Menu
    elevation={0}
    getContentAnchorEl={null}
    anchorOrigin={{
      vertical: "bottom",
      horizontal: "center",
    }}
    transformOrigin={{
      vertical: "top",
      horizontal: "center",
    }}
    {...props}
  />
));

export default function HeaderDropdownMenu() {
  const classes = useStyles();
  const [anchorEl, setAnchorEl] = useState(null);

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
        size="large">
        <MenuIcon />
      </IconButton>

      <StyledMenu
        id="dropdown-menu"
        anchorEl={anchorEl}
        keepMounted
        open={Boolean(anchorEl)}
        onClose={handleClose}
      >
        <MenuItem>Network Sites</MenuItem>
        <MenuItem onClick={handleClose}>
          <a
            href="https://northeasthab.whoi.edu/"
            target="_blank"
            rel="noreferrer"
          >
            <img
              src={logoNehab}
              alt="NeHAB Logo"
              className={classes.menuImg2}
            />
          </a>
        </MenuItem>
        <MenuItem onClick={handleClose}>
          <a
            href="https://northeasthab.whoi.edu/bloom-monitoring/habon-ne/"
            target="_blank"
            rel="noreferrer"
          >
            <img
              src={logoNehabon}
              alt="NeHABON Logo"
              className={classes.menuImg}
            />
          </a>
        </MenuItem>
        <MenuItem onClick={handleClose}>
          <a href="#">
            <img
              src={logoPhytoArm}
              alt="PhytoArm Logo"
              className={classes.menuImg}
            />
          </a>
        </MenuItem>
      </StyledMenu>
    </React.Fragment>
  );
}
