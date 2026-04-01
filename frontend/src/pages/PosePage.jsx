import React, { useState, useRef } from "react";
import {
  Box, CircularProgress, Alert, Typography, Paper,
  Chip, Grid, Divider, LinearProgress, Card, CardContent,
} from "@mui/material";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import WarningIcon from "@mui/icons-material/Warning";
import InfoIcon from "@mui/icons-material/Info";
import {
  RadarChart, PolarGrid, PolarAngleAxis, Radar,
  ResponsiveContainer, Tooltip,
} from "recharts";
import { detectPose } from "../services/poseApi";

const STATUS_ICON = {
  good: <CheckCircleIcon color="success" fontSize="small" />,
  warning: <WarningIcon color="warning" fontSize="small" />,
  info: <InfoIcon color="info" fontSize="small" />,
};

const STATUS_COLOR = { good: "success", warning: "warning", info: "info" };

const ANGLE_LABELS = {
  left_elbow: "L Elbow", right_elbow: "R Elbow",
  left_knee: "L Knee", right_knee: "R Knee",
  left_hip: "L Hip", right_hip: "R Hip",
  left_shoulder: "L Shoulder", right_shoulder: "R Shoulder",
};

export default function PosePage() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const fileRef = useRef();

  const handleFile = async (file) => {
    if (!file) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const r = await detectPose(fd);
      setResult(r.data);
    } catch (e) {
      setError(e.response?.data?.detail || "Pose detection failed.");
    } finally {
      setLoading(false);
    }
  };

  const radarData = result?.angles
    ? Object.entries(result.angles).map(([key, val]) => ({
        joint: ANGLE_LABELS[key] || key,
        angle: val,
        fullMark: 180,
      }))
    : [];

  return (
    <Box>
      {/* Drop zone */}
      <Paper
        variant="outlined"
        onClick={() => fileRef.current.click()}
        onDrop={(e) => { e.preventDefault(); handleFile(e.dataTransfer.files[0]); }}
        onDragOver={(e) => e.preventDefault()}
        sx={{ p: 3, mb: 2, textAlign: "center", cursor: "pointer", borderStyle: "dashed", "&:hover": { bgcolor: "action.hover" } }}
      >
        <input ref={fileRef} type="file" hidden accept=".jpg,.jpeg,.png,.bmp,.webp"
          onChange={(e) => handleFile(e.target.files[0])} />
        {loading
          ? <Box><CircularProgress size={28} sx={{ mb: 1 }} /><Typography color="text.secondary">Analyzing pose…</Typography></Box>
          : <Box sx={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 1 }}>
              <UploadFileIcon color="action" />
              <Typography color="text.secondary">
                Drag & drop or click — upload a fitness/exercise photo
              </Typography>
            </Box>
        }
      </Paper>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {result && (
        <Box>
          {!result.pose_detected && (
            <Alert severity="warning" sx={{ mb: 2 }}>
              No pose detected. Try a photo with a clearly visible full body.
            </Alert>
          )}

          {result.pose_detected && (
            <>
              <Box sx={{ display: "flex", gap: 1.5, mb: 2, flexWrap: "wrap" }}>
                <Chip label="✅ Pose detected" color="success" />
                <Chip label={`33 landmarks`} variant="outlined" size="small" />
                <Chip label={`${result.image_width} × ${result.image_height} px`} variant="outlined" size="small" />
              </Box>

              <Grid container spacing={2}>
                {/* Annotated image */}
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>Skeleton Overlay</Typography>
                  <Paper variant="outlined" sx={{ p: 1 }}>
                    <img src={`data:image/jpeg;base64,${result.annotated_image}`}
                      alt="pose" style={{ width: "100%", borderRadius: 4 }} />
                  </Paper>
                </Grid>

                {/* Radar chart of joint angles */}
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>Joint Angles (degrees)</Typography>
                  <ResponsiveContainer width="100%" height={280}>
                    <RadarChart data={radarData}>
                      <PolarGrid />
                      <PolarAngleAxis dataKey="joint" tick={{ fontSize: 11 }} />
                      <Radar name="Angle" dataKey="angle" stroke="#1976d2"
                        fill="#1976d2" fillOpacity={0.3} />
                      <Tooltip formatter={(v) => `${v}°`} />
                    </RadarChart>
                  </ResponsiveContainer>
                </Grid>
              </Grid>

              <Divider sx={{ my: 2 }} />

              {/* Joint angles table */}
              <Typography variant="subtitle2" gutterBottom>Joint Angles</Typography>
              <Grid container spacing={1} sx={{ mb: 2 }}>
                {Object.entries(result.angles).map(([key, val]) => (
                  <Grid item xs={6} sm={3} key={key}>
                    <Paper variant="outlined" sx={{ p: 1.5, textAlign: "center" }}>
                      <Typography variant="caption" color="text.secondary" display="block">
                        {ANGLE_LABELS[key] || key}
                      </Typography>
                      <Typography variant="h6" fontWeight="bold" color="primary">
                        {val}°
                      </Typography>
                      <LinearProgress variant="determinate" value={(val / 180) * 100}
                        sx={{ height: 4, borderRadius: 2, mt: 0.5 }} />
                    </Paper>
                  </Grid>
                ))}
              </Grid>

              {/* Fitness feedback */}
              {result.feedback.length > 0 && (
                <>
                  <Typography variant="subtitle2" gutterBottom>Fitness Feedback</Typography>
                  <Grid container spacing={1}>
                    {result.feedback.map((fb, i) => (
                      <Grid item xs={12} sm={6} key={i}>
                        <Card variant="outlined">
                          <CardContent sx={{ py: 1.5, "&:last-child": { pb: 1.5 } }}>
                            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                              {STATUS_ICON[fb.status]}
                              <Box>
                                <Chip label={fb.joint} size="small"
                                  color={STATUS_COLOR[fb.status]} sx={{ mb: 0.5 }} />
                                <Typography variant="body2">{fb.message}</Typography>
                              </Box>
                            </Box>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </>
              )}
            </>
          )}
        </Box>
      )}
    </Box>
  );
}
