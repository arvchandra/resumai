import { useState, useEffect } from "react";

import Tooltip from '@mui/material/Tooltip';
import { isToday, format } from "date-fns";

import { useResumeApi } from "../../api/resumeApi.ts";
import { useTailoredResumesContext } from "../../contexts/TailoredResumesContext.tsx";

import linkedInIcon from "../../assets/images/linkedin-icon.png";
import downloadIcon from "../../assets/images/download-file-icon.png";

import "./TailoredResumeTable.css";

export default function TailoredResumeTable() {
  const { downloadTailoredUserResume } = useResumeApi();
  const { tailoredResumes, fetchTailoredResumes } = useTailoredResumesContext();

  const [tailoredResumesSearchText, setTailoredResumesSearchText] = useState("");

  // Fetch tailored resumes on initial load
  useEffect(() => {
    fetchTailoredResumes();
  }, []);

  const handleDownloadClick = async (tailoredResumeId: number, tailoredResumeName: string) => {
    try {
      // TODO replace with current user
      const response = await downloadTailoredUserResume(tailoredResumeId);

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Failed to download resume");
      }

      // Create a temporary link to trigger the download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = tailoredResumeName;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.log(err);
    }
  };

  // Build tailored resumes list
  let tailoredResumesItems = null;
  if (tailoredResumes) {
    tailoredResumesItems =
      tailoredResumes
        // Filter resumes based on search text
        .filter((resume) => {
          if (tailoredResumesSearchText === "") {
            return true;
          }

          const searchTextLower = tailoredResumesSearchText.toLowerCase();
          const companyLower = resume.company.toLowerCase();
          const roleLower = resume.role.toLowerCase();
          return (companyLower.includes(searchTextLower) || roleLower.includes(searchTextLower)) ? true : false;
        })
        // Render the filtered resumes
        .map((resume) => {
          const dateCreated = new Date(resume.created_at);
          const dateFormat = isToday(dateCreated) ? "h:mm aa" : "MMM d";
          const formattedDateCreatedShort = format(dateCreated, dateFormat);
          const formattedDateCreatedFull = format(dateCreated, "MMMM d, yyyy 'at' h:mm aa");

          return (
            <li className="resume-list-item" key={resume.id}>

              {/* Tailored Resume Link Button: Opens in new tab */}
              <Tooltip
                className="resume-list-item-content"
                title={`${resume.company} - ${resume.role}`}
                placement="top"
                followCursor
                enterDelay={1000}
                enterNextDelay={1000}
              >
                <div className="resume-link-btn" onClick={() => handleDownloadClick(resume.id, resume.name)}>
                  {resume.company} - {resume.role}
                </div>
              </Tooltip>

              {/* Created Date */}
              <Tooltip
                className="resume-list-item-content resume-date"
                title={formattedDateCreatedFull}
                placement="top"
                followCursor
              >
                <span>{formattedDateCreatedShort}</span>
              </Tooltip>

              {/* LinkedIn Job Posting Link Icon */}
              <Tooltip
                className="resume-list-item-content"
                style={{ whiteSpace: 'pre-line' }}
                title={<div>{`View job posting:\n${resume.job_posting_url}`}</div>}
                placement="top"
                followCursor
              >
                <img
                  className="icon"
                  src={linkedInIcon}
                  alt="LinkedIn Job Posting"
                  onClick={() => window.open(resume.job_posting_url, "_blank", "noopener,noreferrer")}
                />
              </Tooltip>

              {/* Download Icon: Downloads to disk */}
              <Tooltip
                className="resume-list-item-content"
                title="Download"
                placement="top"
                followCursor
              >
                <img
                  className="icon"
                  src={downloadIcon}
                  alt="Download"
                  onClick={() => handleDownloadClick(resume.id, resume.name)}
                />
              </Tooltip>

            </li>
          );
        });
  }

  return (
    <div className="form-field">
      <label>Tailored Resumes:</label>
      <input
        type="search"
        id="resumes-filter"
        name="resumes-filter"
        placeholder="Search tailored resumes..."
        value={tailoredResumesSearchText}
        onChange={(e) => setTailoredResumesSearchText(e.target.value)}
        autoComplete="off"
      />
      <div className="scrollable-container">
        {
          tailoredResumesItems && tailoredResumesItems.length > 0 ?
            (
              <ul className="resumes-list">
                {tailoredResumesItems}
              </ul>
            ) :
            <div className="no-results">No tailored resumes found.</div>
        }
      </div>
    </div>
  );
};
