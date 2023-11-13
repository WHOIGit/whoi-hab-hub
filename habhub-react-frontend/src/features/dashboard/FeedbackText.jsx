import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import { Typography, Link } from "@material-ui/core";

const useStyles = makeStyles((theme) => ({
  root: {
    padding: theme.spacing(2),
  },
}));

export default function FeedbackText() {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <Typography variant="body2" display="block" gutterBottom>
        The HAB hub data is being developed as a data access and visualization
        portal for the New England Harmful Algal Bloom Observing Network (
        <Link
          href="https://northeasthab.whoi.edu/bloom-monitoring/habon-ne/"
          target="_blank"
          rel="noopener"
        >
          neHABON
        </Link>
        ). It is a work in progress and we welcome your feedback. Please send
        comments to <Link href="mailto:mrichlen@whoi.edu">Mindy Richlen</Link>{" "}
        and <Link href="mailto:mbrosnahan@whoi.edu">Mike Brosnahan</Link>
      </Typography>
    </div>
  );
}
