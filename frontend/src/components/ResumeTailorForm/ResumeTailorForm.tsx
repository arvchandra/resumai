import { useState } from "react";

import useFetch from "../../hooks/useFetch";
import { fetchTailoredResumes } from "../../http";
import ResumeSelector from "../ResumeSelector/ResumeSelector";
import useUploadResumeFile from "../../hooks/useUploadResumeFile";
import { useResumesContext } from "../../contexts/ResumesContext";


import "./ResumeTailorForm.css";
import type Resume from "../../interfaces/Resume";

type ResumeToTailor = Resume | null;

export default function ResumeTailorForm() {
  const { fetchedData: tailoredResumes, isFetching, error } = useFetch(fetchTailoredResumes);
  const { selectedResume, tempUploadedResumeFile, setTempUploadedResumeFile, fetchResumes } = useResumesContext();
  const { isUploading: isUploadingResume, uploadTemporaryFile } = useUploadResumeFile();

  const [jobPostingUrl, setJobPostingUrl] = useState('');
  const [isTailoringResume, setIsTailoringResume] = useState(false);

  const disableTailorButton = isUploadingResume || isTailoringResume;

  const handleTailorResumeClick = async () => {
    setIsTailoringResume(true);

    let isFirstUserResumeUpload = false;

    // TODO: Remove the timeout.
    // This is a placeholder to emulate the loading time for the tailoring process.
    await new Promise((resolve) => setTimeout(resolve, 1000));

    try {
      let resumeToTailor: ResumeToTailor = null;

      // Select resume for tailoring
      if (tempUploadedResumeFile) {
        // If there is a pending resume file upload, then POST the file to the backend and
        // retrieve the uploaded resume object. This only occurs when a user uploads
        // a resume to the site for the first time.
        isFirstUserResumeUpload = true;
        resumeToTailor = await uploadTemporaryFile();
      } else if (selectedResume) {
        resumeToTailor = selectedResume;
      } else {
        throw new Error("Unable to select resume for tailoring.");
      }

      await new Promise((resolve) => setTimeout(resolve, 1000));

      const response = await fetch('http://127.0.0.1:8000/tailor/users/2/tailor-resume', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          resume_id: resumeToTailor?.id,
          job_posting_url: jobPostingUrl
        })
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Failed to tailor resume');
      }

      const data = await response.json();
      console.log(data);

      // Fetch user resumes if this tailoring request
      // involved uploading the user's first resume.
      if (isFirstUserResumeUpload) fetchResumes();
    } catch (err) {
      console.log(err);
    } finally {
      setTempUploadedResumeFile(null);
      setIsTailoringResume(false);
    }
  };

  return (
      <div className="resume-tailor-form">
        <ResumeSelector />
        <div className="form-field">
          <label htmlFor="job-posting-url">LinkedIn Job Posting URL</label>
          <input 
            type="text" 
            id="job-posting-url" 
            name="job-posting-url"
            placeholder="Enter URL" 
            value={jobPostingUrl} 
            onChange={(e) => setJobPostingUrl(e.target.value)}
          />
        </div>
        <div>
          <button className="btn btn-primary" onClick={handleTailorResumeClick} disabled={disableTailorButton}>
            {isUploadingResume ? "Uploading Resume..." : isTailoringResume ? "Tailoring..." : "Tailor Resume"}
          </button>
        </div>
      </div>
  )
}