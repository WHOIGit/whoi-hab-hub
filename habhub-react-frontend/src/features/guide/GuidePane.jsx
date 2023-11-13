import React from "react";
import clsx from "clsx";
import { useDrag } from "react-dnd";
import { makeStyles } from "@material-ui/styles";
import { Card, CardHeader, CardContent, IconButton } from "@material-ui/core";
import { Close } from "@material-ui/icons";
import Stepper from "@material-ui/core/Stepper";
import Step from "@material-ui/core/Step";
import StepButton from "@material-ui/core/StepButton";
import Button from "@material-ui/core/Button";
import Typography from "@material-ui/core/Typography";
import { useSelector, useDispatch } from "react-redux";
// local imports
import { changeActiveGuideStep } from "./guideSlice";
import { changeLayerVisibility } from "../data-layers/dataLayersSlice";
import { ITEM_TYPES, DATA_LAYERS } from "../../Constants";

export default function GuidePane({
  openGuide,
  handleGuideClose,
  left,
  bottom,
  transform,
  id,
}) {
  const useStyles = makeStyles((theme) => ({
    root: {
      margin: theme.spacing(1),
      width: 640,
      transition: "all 0.3s",
      zIndex: 2000,
      display: "none",
      cursor: "move",
    },
    guideOpen: {
      display: "block",
      position: "absolute",
      left: left,
      bottom: bottom,
      //left: "50%",
      //top: "50%",
      transform: transform,
    },
    rootContent: {
      width: "100%",
    },
    rootHeader: {
      paddingBottom: 0,
    },
    title: {
      color: theme.palette.primary.main,
      fontSize: "1.1rem",
    },
    backButton: {
      marginRight: theme.spacing(1),
    },
    instructions: {
      marginTop: theme.spacing(1),
      marginBottom: theme.spacing(1),
    },
  }));
  const dispatch = useDispatch();
  const classes = useStyles();
  const guideSteps = useSelector((state) => state.guide.guideSteps);
  const [activeStep, setActiveStep] = React.useState(0);
  const [completed, setCompleted] = React.useState({});

  const [, drag] = useDrag(
    () => ({
      type: ITEM_TYPES.PANE,
      item: { id, left, bottom },
      collect: (monitor) => ({
        isDragging: monitor.isDragging(),
      }),
    }),
    [id, left, bottom]
  );

  const guideStyle = clsx({
    [classes.root]: true, //always applies
    [classes.guideOpen]: openGuide, //only when open === true
  });

  const getStepContent = (stepId) => {
    const step = guideSteps.find((item) => item.stepId === stepId);
    return { __html: step.text };
  };

  const totalSteps = () => {
    return guideSteps.length;
  };

  const completedSteps = () => {
    return Object.keys(completed).length;
  };

  const isLastStep = () => {
    return activeStep === totalSteps() - 1;
  };

  const allStepsCompleted = () => {
    return completedSteps() === totalSteps();
  };

  const dispatchHandler = (newActiveStep) => {
    // dispatch active step to Redux state
    // activate Cell Concentration layer for Graph display if necessary
    console.log(newActiveStep);
    dispatch(
      changeActiveGuideStep({
        stepId: newActiveStep,
      })
    );

    if (newActiveStep === 4) {
      dispatch(
        changeLayerVisibility({
          layerID: DATA_LAYERS.cellConcentrationLayer,
          checked: true,
        })
      );
    }
  };

  const handleNext = () => {
    const newActiveStep =
      isLastStep() && !allStepsCompleted()
        ? // It's the last step, but not all steps have been completed,
          // find the first step that has been completed
          guideSteps.findIndex((step, i) => !(i in completed))
        : activeStep + 1;
    setActiveStep(newActiveStep);
    // dispatch active step to Redux state
    dispatchHandler(newActiveStep);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleStep = (stepId) => () => {
    setActiveStep(stepId);
    // dispatch active step to Redux state
    dispatchHandler(stepId);
  };

  // eslint-disable-next-line no-unused-vars
  const handleComplete = () => {
    const newCompleted = completed;
    newCompleted[activeStep] = true;
    setCompleted(newCompleted);
    handleNext();
  };

  return (
    <div className={guideStyle} ref={drag} id={id}>
      <Card>
        <CardHeader
          classes={{
            root: classes.rootHeader,
            title: classes.title,
          }}
          action={
            <React.Fragment>
              <IconButton onClick={handleGuideClose} aria-label="close">
                <Close />
              </IconButton>
            </React.Fragment>
          }
          title={"HABHub Guide"}
        />

        <CardContent>
          <div className={classes.rootContent}>
            <Stepper nonLinear activeStep={activeStep} alternativeLabel>
              {guideSteps.map((step) => (
                <Step key={step.stepId}>
                  <StepButton
                    onClick={handleStep(step.stepId)}
                    completed={completed[step.stepId]}
                  >
                    {step.label}
                  </StepButton>
                </Step>
              ))}
            </Stepper>
            <div>
              <div>
                <Typography className={classes.instructions}>
                  <div dangerouslySetInnerHTML={getStepContent(activeStep)} />
                </Typography>
                <div>
                  <Button
                    onClick={handleBack}
                    className={classes.backButton}
                    disabled={activeStep === 0}
                  >
                    Back
                  </Button>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleNext}
                  >
                    {activeStep === guideSteps.length - 1 ? "Finish" : "Next"}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
