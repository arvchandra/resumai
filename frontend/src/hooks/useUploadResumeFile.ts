import { useState } from "react";

import { useResumesContext } from "../contexts/ResumesContext";

import useFetchWithAuth from "./useFetchWithAuth";

export default function useUploadResumeFile() {
  const { tempUploadedResumeFile } = useResumesContext();
  const fetchWithAuth = useFetchWithAuth();

  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");

  async function uploadTemporaryFile() {
    if (!tempUploadedResumeFile) return;

    setIsUploading(true);
    await new Promise((resolve) => setTimeout(resolve, 1000));

    const formData = new FormData;
    formData.append("file", tempUploadedResumeFile);

    try {
      const result = await fetchWithAuth("http://localhost:8000/tailor/users/2/resumes/upload/", {
        method: "POST",
        body: formData
      });

      setIsUploading(false);

      const data = await result.json();
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
