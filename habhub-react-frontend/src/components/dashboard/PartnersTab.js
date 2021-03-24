import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import { Typography, Link, Grid, Box } from "@material-ui/core";
import NsfLogo from "../../images/nsf-logo.jpg";
import NihLogo from "../../images/nih-new.png";
import NccosLogo from "../../images/nccos_logofile.jpeg";

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
  partnerLogo: {
    display: "block",
    margin: "0 auto",
  },
}));

export default function PartnersTab() {
  const classes = useStyles();

  return (
    <>
      <div className={classes.root}>
        <Typography variant="subtitle1" display="block" gutterBottom>
          Funders
        </Typography>
        <Typography variant="body2" display="block" gutterBottom>
          This site is supported by the Community Engagement Core of the{" "}
          <Link
            href="https://www2.whoi.edu/site/whcohh"
            target="_blank"
            rel="noreferrer"
          >
            Woods Hole Center for Oceans and Human Health (WHCOHH)
          </Link>{" "}
          through grants from the{" "}
          <Link href="https://nsf.gov" target="_blank" rel="noreferrer">
            National Science Foundation (NSF OCE-1841811)
          </Link>
          , the{" "}
          <Link
            href="https://www.niehs.nih.gov"
            target="_blank"
            rel="noreferrer"
          >
            National Institute of Environmental Health
          </Link>{" "}
          (NIEHS P01ES028949), and the{" "}
          <Link
            href="https://coastalscience.noaa.gov/research/stressor-impacts-mitigation/merhab/"
            target="_blank"
            rel="noreferrer"
          >
            National Oceanic and Atmospheric Administration MERHAB program
          </Link>{" "}
          (NA19NOS478018).
        </Typography>
        <Box mt={3}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Link
                href="https://nsf.gov"
                target="_blank"
                rel="noreferrer"
                className={classes.partnerLogo}
              >
                <img src={NsfLogo} alt="NSF Logo" width="120"></img>
              </Link>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Link
                href="https://www.niehs.nih.gov"
                target="_blank"
                rel="noreferrer"
                className={classes.partnerLogo}
              >
                <img src={NihLogo} alt="NIHES Logo" width="120"></img>
              </Link>
            </Grid>
            <Grid item xs={12}>
              <Link
                href="https://coastalscience.noaa.gov/research/stressor-impacts-mitigation/merhab/"
                target="_blank"
                rel="noreferrer"
                className={classes.partnerLogo}
              >
                <img src={NccosLogo} alt="NCCOS Logo" width="90%"></img>
              </Link>
            </Grid>
          </Grid>
        </Box>
      </div>
    </>
  );
}
