import React from "react";
import { makeStyles } from "@material-ui/styles";
import { Grid, Typography } from "@material-ui/core";
import DotMarker from "../../images/dot-grey.svg";

const useStyles = makeStyles((theme) => ({
  root: {
    margin: theme.spacing(1),
    width: 300,
    transition: "all 0.3s",
    position: "absolute",
    bottom: 0,
    left: 0,
    zIndex: 2000,
  },
  legendGrid: {
    fontSize: ".8em",
  },
  dotSquare: {
    display: "block",
    width: "20px",
    height: "20px",
  },
}));

export default function LegendCellConcentration() {
  const classes = useStyles();

  const maxSquareSize = 30;
  const minSquareSize = 8;
  const strokeColor = "black";
  const strokeWidth = 4;
  const fillColor = "black";

  return (
    <>
      <Grid
        container
        spacing={3}
        justify="center"
        alignItems="center"
        className={classes.legendGrid}
      >
        {/*
        <Grid item>
          <Typography variant="caption" display="block" align="center">
            <svg width={minSquareSize} height={minSquareSize}>
              <line
                x1={0}
                y1={0}
                x2={minSquareSize}
                y2={minSquareSize}
                stroke={strokeColor}
                strokeWidth={2}
              ></line>
              <line
                x1={0}
                y1={minSquareSize}
                x2={minSquareSize}
                y2={0}
                stroke={strokeColor}
                strokeWidth={2}
              ></line>
            </svg>
          </Typography>
        </Grid>
      */}
        <Grid item>
          <Typography variant="caption" display="block" align="center">
            <div className={classes.dotSquare}>
              <img src={DotMarker} alt="No detection marker" />
            </div>
          </Typography>
        </Grid>
        <Grid item>
          <Typography variant="caption" display="block" align="center">
            <svg
              viewBox="0 0 100 100"
              width={minSquareSize}
              height={minSquareSize}
            >
              <polygon
                points="0 0, 100 100, 0 100"
                fill={fillColor}
                strokeWidth={strokeWidth}
                stroke={strokeColor}
              />
            </svg>
          </Typography>
        </Grid>
        <Grid item>
          <Typography variant="caption" display="block" align="center">
            <svg
              viewBox="0 0 100 100"
              width={(maxSquareSize / 5) * 2}
              height={(maxSquareSize / 5) * 2}
            >
              <polygon
                points="0 0, 100 100, 0 100"
                fill={fillColor}
                strokeWidth={strokeWidth}
                stroke={strokeColor}
              />
            </svg>
          </Typography>
        </Grid>
        <Grid item>
          <Typography variant="caption" display="block" align="center">
            <svg
              viewBox="0 0 100 100"
              width={(maxSquareSize / 5) * 3}
              height={(maxSquareSize / 5) * 3}
            >
              <polygon
                points="0 0, 100 100, 0 100"
                fill={fillColor}
                strokeWidth={strokeWidth}
                stroke={strokeColor}
              />
            </svg>
          </Typography>
        </Grid>
        <Grid item>
          <Typography variant="caption" display="block" align="center">
            <svg
              viewBox="0 0 100 100"
              width={(maxSquareSize / 5) * 4}
              height={(maxSquareSize / 5) * 4}
            >
              <polygon
                points="0 0, 100 100, 0 100"
                fill={fillColor}
                strokeWidth={strokeWidth}
                stroke={strokeColor}
              />
            </svg>
          </Typography>
        </Grid>
        <Grid item>
          <Typography variant="caption" display="block" align="center">
            <svg
              viewBox="0 0 100 100"
              width={maxSquareSize}
              height={maxSquareSize}
            >
              <polygon
                points="0 0, 100 100, 0 100"
                fill={fillColor}
                strokeWidth={strokeWidth}
                stroke={strokeColor}
              />
            </svg>
          </Typography>
        </Grid>
      </Grid>

      <Grid
        container
        spacing={1}
        justify="center"
        alignItems="center"
        className={classes.legendGrid}
      >
        <Grid item>
          <Typography
            variant="caption"
            display="block"
            align="center"
            className={classes.legendText}
          >
            ND
          </Typography>
        </Grid>

        <Grid item>
          <Typography
            variant="caption"
            display="block"
            align="center"
            className={classes.legendText}
          >
            &gt;100
          </Typography>
        </Grid>
        <Grid item>
          <Typography
            variant="caption"
            display="block"
            align="center"
            className={classes.legendText}
          >
            &gt;1000
          </Typography>
        </Grid>
        <Grid item>
          <Typography
            variant="caption"
            display="block"
            align="center"
            className={classes.legendText}
          >
            &gt;1x10<sup>4</sup>
          </Typography>
        </Grid>
        <Grid item>
          <Typography
            variant="caption"
            display="block"
            align="center"
            className={classes.legendText}
          >
            &gt;1x10<sup>5</sup>
          </Typography>
        </Grid>
        <Grid item>
          <Typography
            variant="caption"
            display="block"
            align="center"
            className={classes.legendText}
          >
            &gt;1x10<sup>6</sup>
          </Typography>
        </Grid>
      </Grid>

      <Typography variant="body2" align="center" gutterBottom>
        Cells L <sup>-1</sup>
      </Typography>
    </>
  );
}
