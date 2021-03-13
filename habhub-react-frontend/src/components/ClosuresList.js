import React, { useState, useEffect, useRef } from 'react';
import { makeStyles } from '@material-ui/styles'
import {
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Typography,
  TableContainer,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Paper,
  Box,
  Grid,
  Divider,
} from '@material-ui/core'
import DescriptionIcon from '@material-ui/icons/Description';

const expandWidth = window.outerWidth - 316;
const useStyles = makeStyles(theme => ({
  table: {

  },
}))

export default function ClosuresList({results}) {
  const chartRef = useRef();
  const classes = useStyles()

  function renderClosureItem(closure) {
    return (
      <Box mb={4}>
        <Grid
          container
          spacing={1}
          alignItems="center"
          className={classes.legendGrid}
          >
          <Grid item xs={9} >
            <Typography variant="subtitle1" display="block" gutterBottom>
              Closure Date: {closure.effective_date}
            </Typography>
            <Typography variant="body2" display="block" color="textSecondary" gutterBottom>
              Causative Species: <em>{closure.causative_organism}</em>
            </Typography>
          </Grid>
          <Grid item xs={3}  >
            {closure.document_link && (
              <Box align="center">
                <a href={closure.document_link} target="_blank">
                  <DescriptionIcon fontSize="large" />
                </a>
                <Typography variant="caption" display="block" color="textSecondary" gutterBottom>
                  Download notice
                </Typography>
              </Box>
            )}
          </Grid>
        </Grid>

        <TableContainer>
          <Table className={classes.table} size="small" aria-label="Species and Duration Table">
            <TableHead>
              <TableRow>
                <TableCell>Species</TableCell>
                <TableCell align="right">Closure Duration</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {closure.species.map((row) => (
                <TableRow key={row.species}>
                  <TableCell component="th" scope="row">
                    {row.species}
                  </TableCell>
                  <TableCell align="right">{row.duration}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    )
  }

  return (
    <List>
      {results.properties.closures.map(closure => renderClosureItem(closure))}
    </List>
  )
}
