import React, { useState, useEffect } from 'react';
import {Source, Layer} from 'react-map-gl';
import diamondIcon from '../map-icons/diamond.svg'

// filters for classifying stations by max values into five categories
const max1 = ['<', ['get', 'station_max'], 42];
const max2 = ['all', ['>=', ['get', 'station_max'], 42], ['<', ['get', 'station_max'], 60]];
const max3 = ['all', ['>=', ['get', 'station_max'], 60], ['<', ['get', 'station_max'], 80]];
const max4 = ['all', ['>=', ['get', 'station_max'], 80], ['<', ['get', 'station_max'], 100]];
const max5 = ['>=', ['get', 'station_max'], 100];

// filters for classifying stations by mean values into five categories
const mean1 = ['<', ['get', 'station_mean'], 20];
const mean2 = ['all', ['>=', ['get', 'station_mean'], 20], ['<', ['get', 'station_mean'], 40]];
const mean3 = ['all', ['>=', ['get', 'station_mean'], 40], ['<', ['get', 'station_mean'], 60]];
const mean4 = ['all', ['>=', ['get', 'station_mean'], 60], ['<', ['get', 'station_mean'], 80]];
const mean5 = ['>=', ['get', 'station_mean'], 80];

// colors to use for the gradient
const colors = ['fee5d9', 'fcae91', 'fb6a4a', 'de2d26', 'a50f15'];

const maxPaintCase = [
  'case',
  max1,
  colors[0],
  max2,
  colors[1],
  max3,
  colors[2],
  max4,
  colors[3],
  colors[4]
]

const meanPaintCase = [
  'case',
  mean1,
  colors[0],
  mean2,
  colors[1],
  mean3,
  colors[2],
  mean4,
  colors[3],
  colors[4]
]

const StationsLayer = ({mapRef}) => {
  const mapObj = mapRef.current.getMap();
  console.log(mapObj);

  useEffect(() => {
    const icons = colors.map(color => {
      const iconImg = new Image(36,36);
      iconImg.onload = () => mapObj.addImage('diamond-hexcolor-' + color, iconImg);
      iconImg.src = diamondIcon;
      console.log(iconImg);
    })
  }, [])

  const stationsSource = {
    id: 'stations-src',
    type: 'geojson',
    data: 'https://habhub.whoi.edu/api/v1/stations/',
    buffer: 0,
    maxzoom: 12,
  }

   const stationsLayer = {
     id: 'stations-layer',
     type: 'symbol',
     source: 'stations-src',
     layout: {
         'visibility': 'visible',
         'icon-image': ['concat', 'diamond-hexcolor-', maxPaintCase],
         //'icon-image': 'diamond',
         'text-field': [
             'number-format',
             ['get', 'station_max'],
             { 'min-fraction-digits': 1, 'max-fraction-digits': 1 }
         ],
         'text-font': ['Open Sans Semibold', 'Arial Unicode MS Bold'],
         'text-size': 10
     }
   }

   const stationsMaxLabelLayer = {
     id: 'stations-max-label-layer',
     type: 'symbol',
     source: 'stations-src',
     layout: {
       'visibility': 'visible',
       'text-field': [
           'number-format',
           ['get', 'station_max'],
           { 'min-fraction-digits': 1, 'max-fraction-digits': 1 }
       ],
       'text-font': ['Open Sans Semibold', 'Arial Unicode MS Bold'],
       'text-size': 10
     }
   }

  return (
    <Source {...stationsSource}>
      <Layer {...stationsMaxLabelLayer} />

    </Source>
  )
}

export default StationsLayer;
