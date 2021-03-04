import React from 'react'
import { makeStyles } from '@material-ui/styles'
import { Grid, Typography, Box } from '@material-ui/core'

const expandWidth = window.outerWidth - 296;
const useStyles = makeStyles(theme => ({
  root: {
    margin: theme.spacing(1),
    width: 300,
    transition: 'all 0.3s',
    position: 'absolute',
    bottom: 0,
    left: 0,
    zIndex: 2000,
  },
  legendGrid : {
    fontSize: ".8em",
  }
}))

export default function LegendCellAbundance() {
  const classes = useStyles()

  const maxSquareSize = 32;
  const minSquareSize = 8;
  const strokeColor = "black";
  const strokeWidth = 4;
  const fillColor = "white";

  return (
    <>
      <Grid
        container
        spacing={0}
        justify="center"
        alignItems="center"
        className={classes.legendGrid}
        >
        <Grid item xs={2}>
          <svg width={minSquareSize} height={minSquareSize}>
            <line x1={0} y1={0} x2={minSquareSize} y2={minSquareSize} stroke={strokeColor} strokeWidth={2}></line>
            <line x1={0} y1={minSquareSize} x2={minSquareSize} y2={0} stroke={strokeColor} strokeWidth={2}></line>
          </svg>
        </Grid>
        <Grid item xs={2}>
          <svg width={minSquareSize} height={minSquareSize}>
            <rect
              width={minSquareSize}
              height={minSquareSize}
              fill={fillColor}
              strokeWidth={strokeWidth}
              stroke={strokeColor}>
            </rect>
          </svg>
        </Grid>
        <Grid item xs={2}>
          <svg width={maxSquareSize / 5 * 2} height={maxSquareSize / 5 * 2}>
            <rect
              width={maxSquareSize / 5 * 2}
              height={maxSquareSize / 5 * 2}
              fill={fillColor}
              strokeWidth={strokeWidth}
              stroke={strokeColor}>
            </rect>
          </svg>
        </Grid>
        <Grid item xs={2}>
          <svg width={maxSquareSize / 5 * 3} height={maxSquareSize / 5 * 3}>
            <rect
              width={maxSquareSize / 5 * 3}
              height={maxSquareSize / 5 * 3}
              fill={fillColor}
              strokeWidth={strokeWidth}
              stroke={strokeColor}>
            </rect>
          </svg>
        </Grid>
        <Grid item xs={2}>
          <svg width={maxSquareSize / 5 * 4} height={maxSquareSize / 5 * 4}>
            <rect
              width={maxSquareSize / 5 * 4}
              height={maxSquareSize / 5 * 4}
              fill={fillColor}
              strokeWidth={strokeWidth}
              stroke={strokeColor}>
            </rect>
          </svg>
        </Grid>
        <Grid item xs={2}>
          <svg width={maxSquareSize} height={maxSquareSize}>
            <rect
              width={maxSquareSize}
              height={maxSquareSize}
              fill={fillColor}
              strokeWidth={strokeWidth}
              stroke={strokeColor}>
            </rect>
          </svg>
        </Grid>

        <Grid item xs={2}>
          ND
        </Grid>
        <Grid item xs={2}>
          >100
        </Grid>
        <Grid item xs={2}>
          >1000
        </Grid>
        <Grid item xs={2}>
          >1x10<sup>4</sup>
        </Grid>
        <Grid item xs={2}>
          >1x10<sup>5</sup>
        </Grid>
        <Grid item xs={2}>
          >1x10<sup>6</sup>
        </Grid>
      </Grid>


      <Typography variant="body2" align="center" gutterBottom>
         Cells L <sup>-1</sup>
      </Typography>

    </>
  )
}
