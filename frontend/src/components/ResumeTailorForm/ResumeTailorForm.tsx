import React, { useRef } from "react";

import "./ResumeTailorForm.css";

import ResumeSelectorUploader from "../ResumeSelectorUploader/ResumeSelectorUploader";


export default function ResumeTailorForm() {
  const logRef = useRef<HTMLTextAreaElement>(null);
  const jobUrlRef = useRef<HTMLInputElement>(null);

  const handleTailorClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    console.log(event.target);

    if (logRef.current && jobUrlRef.current) {
      const selectedResumeText = `Selected Resume:`;
      const jobURLText = `Job Posting URL: ${jobUrlRef.current.value}`;

      logRef.current.value = `${selectedResumeText}\n${jobURLText}`;
    }
  }

  return (
      <div className="resume-tailor-form">
        <ResumeSelectorUploader />
        <div className="form-field">
          <label htmlFor="job-posting-url">LinkedIn Job Posting URL</label>
          <input ref={jobUrlRef} type="text" id="job-posting-url" name="job-posting-url" placeholder="Enter URL" />
        </div>
        <div>
          <button className="btn btn-primary" onClick={handleTailorClick}>Tailor Resume</button>
        </div>
        <div className="form-field">
          <label htmlFor="app-log">Log:</label>
          <textarea ref={logRef} id="app-log" name="app-log" className="app-log" />
        </div>
      </div>
  )
}