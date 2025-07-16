import { AgGridReact } from 'ag-grid-react';
import { AllCommunityModule, ModuleRegistry } from "ag-grid-community";
import { useState } from "react";

import useFetch from "../../hooks/useFetch";
import { fetchTailoredResumes } from "../../http";
import ResumeSelector from "../ResumeSelector/ResumeSelector";
import useUploadResumeFile from "../../hooks/useUploadResumeFile";
import { useResumesContext } from "../../contexts/ResumesContext";


import "./ResumeTailorForm.css";
import type Resume from "../../interfaces/Resume";
import TailoredResumeTable from "../TailoredResumeTable/TailoredResumeTable";

ModuleRegistry.registerModules([AllCommunityModule]);

type ResumeToTailor = Resume | null;

export default function ResumeTailorForm() {
  const { fetchedData: tailoredResumes, isFetching, error } = useFetch(fetchTailoredResumes);
  const { selectedResume, tempUploadedResumeFile, setTempUploadedResumeFile, fetchResumes } = useResumesContext();
  const { isUploading: isUploadingResume, uploadTemporaryFile } = useUploadResumeFile();

  const [jobPostingUrl, setJobPostingUrl] = useState('');
  const [isTailoringResume, setIsTailoringResume] = useState(false);

  const disableTailorButton = isUploadingResume || isTailoringResume;


// Solution 2: ag-grid
  const [rowData, setRowData] = useState([
    { resume: "Google_may_24_2025", company: "Google", role: "Backend Engineer", URL: "www.linkedin.com/jobs/view/12345" },
    { resume: "Meta_april_4_2025", company: "Meta", role: "Product Engineer", URL: "www.linkedin.com/jobs/view/23456" },
    { resume: "Microsoft_june_17_2025", company: "Microsoft", role: "Full-Stack Engineer", URL: "www.linkedin.com/jobs/view/98765" },
  ]);

  const [colDefs, setColDefs] = useState([
    { field: "resume",
      cellStyle: {
            textAlign: 'left'
        } },
    { field: "company" },
    { field: "role" },
    { field: "URL" }
  ]);
//     const [rowData, setRowData] = useState([
//         { make: "Tesla", model: "Model Y", price: 64950, electric: true },
//         { make: "Ford", model: "F-Series", price: 33850, electric: false },
//         { make: "Toyota", model: "Corolla", price: 29600, electric: false },
//     ]);
//
//     // Column Definitions: Defines the columns to be displayed.
//     const [colDefs, setColDefs] = useState([
//         { field: "make" },
//         { field: "model" },
//         { field: "price" },
//         { field: "electric" }
//     ]);


// Solution 1: homecode
  const theadData = ["Resume Name", "Company", "Role", "URL"];
  const tbodyData = [
    {
    id: "1",
    items: ["Google_may_24_2025", "Google", "Backend Engineer", "www.linkedin.com/jobs/view/12345"]
    },
    {
    id: "2",
    items: ["Meta_april_4_2025", "Meta", "Product Engineer", "www.linkedin.com/jobs/view/23456"]
    },
    {
    id: "3",
    items: ["Microsoft_june_17_2025", "Microsoft", "Full-Stack Engineer", "www.linkedin.com/jobs/view/98765"]
    },
    ];

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
        <div className='ag-theme-quartz' style={{ height: 200, width: 750 }}>
            <AgGridReact
                rowData={rowData}
                columnDefs={colDefs}
            />
        </div>
        <div>
          <TailoredResumeTable theadData={theadData} tbodyData={tbodyData} />
        </div>
      </div>
  );
}