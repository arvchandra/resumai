import React, { use, useEffect, useState } from "react";

import type { JSX } from "react";

import { ResumeContext } from "../../contexts/ResumeContext";

import { resumesData } from "../../mocks/mockData";

export default function ResumeSelector() {
  const { updateResumeName } = use(ResumeContext);
  const [defaultResume, setDefaultResume] = useState('');
  const [resumeOptions, setResumeOptions] = useState<JSX.Element[]>([]);

  const handleResumeSelect = (event: React.ChangeEvent<HTMLSelectElement>) => {
      updateResumeName(event.target.value);
  }

  useEffect(() => {
    const resumeOptions: JSX.Element[] = [];

    resumesData.forEach((resume) => {
      if (resume.default) {
        setDefaultResume(resume.name);
        updateResumeName(resume.name);
      }
      
      resumeOptions.push(
        <option key={resume.id} value={resume.name}>
          {resume.name}
        </option>
      );
      setResumeOptions(resumeOptions);
    });
  }, [updateResumeName]);

  

  return (
    <div className="form-field">
      <label htmlFor="resume">Choose a resume:</label>
      <select id="resume" name="resume" value={defaultResume} onChange={handleResumeSelect}>
        {resumeOptions}
      </select>
    </div>
  )
}