import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import {
  Typography,
  Link,
  List,
  ListItem,
  ListItemIcon,
} from "@material-ui/core";
import OpenInNewIcon from "@material-ui/icons/OpenInNew";
import FeedbackText from "./FeedbackText";

const useStyles = makeStyles((theme) => ({
  root: {
    padding: theme.spacing(2),
  },
  listItem: {
    paddingLeft: 0,
  },
  listItemIcon: {
    minWidth: "auto",
    marginLeft: "5px",
  },
}));

export default function LinksTab() {
  const classes = useStyles();

  return (
    <>
      <div className={classes.root}>
        <Typography variant="subtitle1" display="block" gutterBottom>
          More information about HABs impacting New England can be found at
          these links
        </Typography>

        <List>
          <ListItem className={classes.listItem}>
            <Typography variant="body2" display="block" gutterBottom>
              <Link
                href="https://northeasthab.whoi.edu/habs/alexandrium/"
                target="_blank"
                rel="noopener"
              >
                <em>Alexandrium catenella</em> / Paralytic Shellfish Poisoning
                (PSP)
              </Link>
            </Typography>
            <ListItemIcon className={classes.listItemIcon}>
              <Link
                href="https://northeasthab.whoi.edu/habs/alexandrium/"
                target="_blank"
                rel="noopener"
              >
                <OpenInNewIcon />
              </Link>
            </ListItemIcon>
          </ListItem>

          <ListItem className={classes.listItem}>
            <Typography variant="body2" display="block" gutterBottom>
              <Link
                href="https://northeasthab.whoi.edu/habs/dinophysis/"
                target="_blank"
                rel="noopener"
              >
                <em>Dinophysis acuminata and Dinophysis norvegica</em> /
                Diarrhetic Shellfish Poisoning (DSP)
              </Link>
            </Typography>
            <ListItemIcon className={classes.listItemIcon}>
              <Link
                href="https://northeasthab.whoi.edu/habs/dinophysis/"
                target="_blank"
                rel="noopener"
              >
                <OpenInNewIcon />
              </Link>
            </ListItemIcon>
          </ListItem>

          <ListItem className={classes.listItem}>
            <Typography variant="body2" display="block">
              <Link
                href="https://northeasthab.whoi.edu/habs/karenia-mikimotoi/"
                target="_blank"
                rel="noopener"
              >
                <em>Karenia mikimotoi</em>
              </Link>
            </Typography>
            <ListItemIcon className={classes.listItemIcon}>
              <Link
                href="https://northeasthab.whoi.edu/habs/karenia-mikimotoi/"
                target="_blank"
                rel="noopener"
              >
                <OpenInNewIcon />
              </Link>
            </ListItemIcon>
          </ListItem>

          <ListItem className={classes.listItem}>
            <Typography variant="body2" display="block" gutterBottom>
              <Link
                href="https://northeasthab.whoi.edu/habs/by-species/margalefidinium-polykrikoides/"
                target="_blank"
                rel="noopener"
              >
                <em>Margalefidinium polykrikoides</em>
                <br /> (Cochlodinium polykrikoides)
              </Link>
            </Typography>
            <ListItemIcon className={classes.listItemIcon}>
              <Link
                href="https://northeasthab.whoi.edu/habs/by-species/margalefidinium-polykrikoides/"
                target="_blank"
                rel="noopener"
              >
                <OpenInNewIcon />
              </Link>
            </ListItemIcon>
          </ListItem>

          <ListItem className={classes.listItem}>
            <Typography variant="body2" display="block" gutterBottom>
              <Link
                href="https://northeasthab.whoi.edu/habs/pseudo-nitzschia/"
                target="_blank"
                rel="noopener"
              >
                <em>Pseudo-nitzschia</em> / Amnesic Shellfish Poisoning
              </Link>
            </Typography>
            <ListItemIcon className={classes.listItemIcon}>
              <Link
                href="https://northeasthab.whoi.edu/habs/pseudo-nitzschia/"
                target="_blank"
                rel="noopener"
              >
                <OpenInNewIcon />
              </Link>
            </ListItemIcon>
          </ListItem>
        </List>
      </div>

      <FeedbackText />
    </>
  );
}
