import { useState } from "react";

import { useResumesContext } from "../contexts/ResumesContext";
import { useResumeApi } from "../api/resumeApi.ts";

export default function useUploadResumeFile() {
  const { tempUploadedResumeFile } = useResumesContext();
  const { uploadUserResume } = useResumeApi();

  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");

  async function uploadTemporaryFile() {
    if (!tempUploadedResumeFile) return;

    setIsUploading(true);
    await new Promise((resolve) => setTimeout(resolve, 1000));

    const formData = new FormData;
    formData.append("file", tempUploadedResumeFile);

    try {
      const response = await uploadUserResume(formData);

      setIsUploading(false);

      const data = await response.json();
      return data["uploadedResume"];
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("An error occurred.");
      }
    }
  }

  return {
    uploadTemporaryFile,
    isUploading,
    error
  }
}
