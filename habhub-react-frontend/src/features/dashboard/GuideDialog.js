import React from "react";
import DialogContent from "@material-ui/core/DialogContent";
import DialogContentText from "@material-ui/core/DialogContentText";
import DialogTitle from "@material-ui/core/DialogTitle";
import { makeStyles } from "@material-ui/core/styles";
import Stepper from "@material-ui/core/Stepper";
import Step from "@material-ui/core/Step";
import StepButton from "@material-ui/core/StepButton";
import Button from "@material-ui/core/Button";
import Typography from "@material-ui/core/Typography";

const useStyles = makeStyles((theme) => ({
  root: {
    width: "100%",
  },
  backButton: {
    marginRight: theme.spacing(1),
  },
  instructions: {
    marginTop: theme.spacing(1),
    marginBottom: theme.spacing(1),
  },
}));

function getSteps() {
  return [
    "Select HAB Species",
    "Select Data Layers",
    "Select Timeframe",
    "View and Save Data",
    "Learn More",
  ];
}

function getStepContent(stepIndex) {
  switch (stepIndex) {
    case 0:
      return `Add up to 6 HAB Species/Syndromes of interest at a time. 
                You can change the color indicated by clicking the square      
                to use the color picker tool and create your own custom color palette.`;
    case 1:
      return "What is an ad group anyways?";
    case 2:
      return "This is the bit I really care about!";
    default:
      return "Unknown stepIndex";
  }
}

export default function GuideDialog() {
  const classes = useStyles();
  const [activeStep, setActiveStep] = React.useState(0);
  const [completed, setCompleted] = React.useState({});
  const steps = getSteps();

  const totalSteps = () => {
    return steps.length;
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

  const handleNext = () => {
    const newActiveStep =
      isLastStep() && !allStepsCompleted()
        ? // It's the last step, but not all steps have been completed,
          // find the first step that has been completed
          steps.findIndex((step, i) => !(i in completed))
        : activeStep + 1;
    setActiveStep(newActiveStep);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleStep = (step) => () => {
    setActiveStep(step);
  };

  // eslint-disable-next-line no-unused-vars
  const handleComplete = () => {
    const newCompleted = completed;
    newCompleted[activeStep] = true;
    setCompleted(newCompleted);
    handleNext();
  };

  const handleReset = () => {
    setActiveStep(0);
    setCompleted({});
  };

  return (
    <div>
      <DialogTitle id="alert-dialog-title">
        {"Welcome to the WHOI HABHub!​"}
      </DialogTitle>
      <DialogContent>
        <DialogContentText id="alert-dialog-description">
          <div className={classes.root}>
            <Stepper nonLinear activeStep={activeStep} alternativeLabel>
              {steps.map((label, index) => (
                <Step key={label}>
                  <StepButton
                    onClick={handleStep(index)}
                    completed={completed[index]}
                  >
                    {label}
                  </StepButton>
                </Step>
              ))}
            </Stepper>
            <div>
              {activeStep === steps.length ? (
                <div>
                  <Typography className={classes.instructions}>
                    All steps completed
                  </Typography>
                  <Button onClick={handleReset}>Reset</Button>
                </div>
              ) : (
                <div>
                  <Typography className={classes.instructions}>
                    {getStepContent(activeStep)}
                  </Typography>
                  <div>
                    <Button onClick={handleBack} className={classes.backButton}>
                      Back
                    </Button>
                    <Button
                      variant="contained"
                      color="primary"
                      onClick={handleNext}
                    >
                      {activeStep === steps.length - 1 ? "Finish" : "Next"}
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </DialogContentText>
      </DialogContent>
    </div>
  );
}
