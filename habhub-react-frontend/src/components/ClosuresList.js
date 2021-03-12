import React, { useState, useEffect, useRef } from 'react';
import { makeStyles } from '@material-ui/styles'
import {
  List,
  ListItem,
  Typography,
  IconButton,
  Button
} from '@material-ui/core'

const expandWidth = window.outerWidth - 316;
const useStyles = makeStyles(theme => ({
  chartContainer: {
  },
  chartContainerExpand: {
    width: expandWidth,
    height: '100%',
  }
}))

export default function ClosuresList({results}) {
  const chartRef = useRef();
  const classes = useStyles()
  console.log(results);

  function renderClosureItem(closure) {
    console.log(closure);
    return (
      <ListItem>
        {closure.title}
      </ListItem>
    )
  }

  return (
    <List>
      {results.properties.closures.map(closure => renderClosureItem(closure))}
    </List>
  )
}
