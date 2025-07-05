import React, { useEffect } from "react";

import { useResumesContext } from "../../contexts/ResumesContext";

export default function ResumeSelector() {
  const { resumes, isFetchingResumes, selectedResume, setSelectedResume } = useResumesContext();

  // Set selected resume via dropdown selection
  const handleResumeSelect = (event: React.ChangeEvent<HTMLSelectElement>) => {
      const selectedResumeID = Number.parseInt(event.target.value);
      const selectedResume = resumes.find(resume => resume.id == selectedResumeID);
      if (selectedResume) {
        setSelectedResume(selectedResume);
      }
  }

  // Set the default resume as the selected resume on initial render
  useEffect(() => {
    if (!isFetchingResumes && resumes.length > 0 && !selectedResume) {
      const default_resume = resumes.find(resume => resume.is_default);
      if (default_resume) {
        setSelectedResume(default_resume);
      }
    }
  }, [resumes, isFetchingResumes, selectedResume, setSelectedResume]);
  
  // Construct dropdown for resume selection
  let resumesDropdown = null;
  if (isFetchingResumes) {
    resumesDropdown = ( 
      <select id="resume" name="resume" disabled>
        <option>Loading...</option>
      </select>
    );
  } else if (resumes.length > 0) {
    resumesDropdown = (
      <select id="resume" name="resume" value={selectedResume?.id ?? ""} onChange={handleResumeSelect}>
        {resumes.map((resume) => {
          return (
            <option key={resume.id} value={resume.id}>
              {resume.name}
            </option>
          )
        })}
      </select>
    );
  } else {
    resumesDropdown = (
      <>
        <select id="resume" name="resume" disabled>
          <option>No resumes available</option>
        </select>
      </>
    )
  }

  return (
    <div className="form-field">
      <label htmlFor="resume">Select a resume:</label>
      {resumesDropdown}
    </div>
  )
}