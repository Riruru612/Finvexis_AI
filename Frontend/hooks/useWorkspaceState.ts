import { useState, useCallback } from "react";
import type { DepartmentAnalysis } from "@/lib/mockAnalysis";

export type WorkspaceStatus = "idle" | "uploaded" | "analyzing" | "generating" | "complete" | "error";

export interface WorkspaceState {
  status: WorkspaceStatus;
  fileName: string | null;
  file: File | null;
  analysisData: DepartmentAnalysis | null;
  error: string | null;
  uploadFile: (file: File) => void;
  setAnalysisData: (data: DepartmentAnalysis) => void;
  setStatus: (status: WorkspaceStatus) => void;
  setError: (error: string | null) => void;
  clearFile: () => void;
  reset: () => void;
}

export function useWorkspaceState(): WorkspaceState {
  const [status, setStatus] = useState<WorkspaceStatus>("idle");
  const [fileName, setFileName] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [analysisData, setAnalysisData] = useState<DepartmentAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);

  const uploadFile = useCallback((uploadedFile: File) => {
    setFileName(uploadedFile.name);
    setFile(uploadedFile);
    setAnalysisData(null);
    setError(null);
    setStatus("uploaded");
  }, []);

  const clearFile = useCallback(() => {
    setFileName(null);
    setFile(null);
    setAnalysisData(null);
    setError(null);
    setStatus("idle");
  }, []);

  const reset = useCallback(() => {
    setFileName(null);
    setFile(null);
    setAnalysisData(null);
    setError(null);
    setStatus("idle");
  }, []);

  return { 
    status, 
    fileName, 
    file, 
    analysisData, 
    error, 
    uploadFile, 
    setAnalysisData, 
    setStatus, 
    setError, 
    clearFile, 
    reset 
  };
}
