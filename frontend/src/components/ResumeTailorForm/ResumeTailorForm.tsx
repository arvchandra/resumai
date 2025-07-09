import { use, useRef, useState } from "react";

import "./ResumeTailorForm.css";

import ResumeSelectorUploader from "../ResumeSelectorUploader/ResumeSelectorUploader";
import { ResumesContext } from "../../contexts/ResumesContext";


export default function ResumeTailorForm() {
  const [loading, setLoading] = useState(false);

  const logRef = useRef<HTMLTextAreaElement>(null);
  const jobUrlRef = useRef<HTMLInputElement>(null);

  const { selectedResume } = use(ResumesContext);

  const handleTailorResumeClick = async () => {
    setLoading(true);

    // TODO: Remove the timeout.
    // This is a placeholder to emulate the loading time for the tailoring process.
    await new Promise((resolve) => setTimeout(resolve, 1000));

    try {
      const response = await fetch('http://127.0.0.1:8000/tailor/users/2/tailor-resume', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          resume_id: selectedResume?.id,
          job_posting_url: jobUrlRef.current?.value
        })
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Failed to tailor resume');
      }

      const data = await response.json();
      console.log(data);
      if (logRef.current) {
        logRef.current.value = `Result of tailoring ${selectedResume?.name}:\n${JSON.stringify(data)}`;
      }
    } catch (err) {
      console.log(err);
    } finally {
      setLoading(false);
    }
  };

  return (
      <div className="resume-tailor-form">
        <ResumeSelectorUploader />
        <div className="form-field">
          <label htmlFor="job-posting-url">LinkedIn Job Posting URL</label>
          <input ref={jobUrlRef} type="text" id="job-posting-url" name="job-posting-url" placeholder="Enter URL" />
        </div>
        <div>
          <button className="btn btn-primary" onClick={handleTailorResumeClick}>{loading ? 'Tailoring...' : 'Tailor Resume'}</button>
        </div>
        <div className="form-field">
          <label htmlFor="app-log">Log:</label>
          <textarea ref={logRef} id="app-log" name="app-log" className="app-log" />
        </div>
      </div>
  )
}