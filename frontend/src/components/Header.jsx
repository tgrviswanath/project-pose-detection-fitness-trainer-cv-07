import React from "react";
import { AppBar, Toolbar, Typography } from "@mui/material";
import FitnessCenterIcon from "@mui/icons-material/FitnessCenter";

export default function Header() {
  return (
    <AppBar position="static" color="primary">
      <Toolbar>
        <FitnessCenterIcon sx={{ mr: 1 }} />
        <Typography variant="h6" fontWeight="bold">
          Pose Detection Fitness Trainer
        </Typography>
      </Toolbar>
    </AppBar>
  );
}
