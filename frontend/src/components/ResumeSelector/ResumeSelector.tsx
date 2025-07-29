import React, { useEffect, useRef } from "react";

import Modal from "../Modal/Modal";
import ResumeUploader from "../ResumeUploader/ResumeUploader";
import useUploadResumeFile from "../../hooks/useUploadResumeFile";
import { useResumesContext } from "../../contexts/ResumesContext";
import { useAuth } from "../../contexts/AuthContext";

import "./ResumeSelector.css";

export default function ResumeSelector() {
  const dialog = useRef<HTMLDialogElement>(null);

  const { userInfo } = useAuth();

  const {
    resumes,
    isFetchingResumes,
    selectedResume,
    tempUploadedResumeFile,
    fetchResumes,
    setSelectedResume,
    setTempUploadedResumeFile,
    addUploadedResume,
  } = useResumesContext();

  const { isUploading: isUploadingResume, uploadTemporaryFile } = useUploadResumeFile();

  // Fetch resumes on initial context load
  useEffect(() => {
    fetchResumes(userInfo!.id);
  }, []);

  // Set selected resume via dropdown selection
  const handleResumeSelect = (event: React.ChangeEvent<HTMLSelectElement>) => {
    if (event.target.value === "upload") {
      return handleUploadClick();
    }

    const selectedResumeID = Number.parseInt(event.target.value);
    const selectedResume = resumes.find(resume => resume.id == selectedResumeID);
    if (selectedResume) {
      setSelectedResume(selectedResume);
    }
  }

  /* Upload Modal methods ------------------------------------------- */

  // Handle resume upload click (via dropdown)
  const handleUploadClick = () => {
    if (dialog.current) {
      dialog.current.showModal();
    }
  }

  // Handle upload modal confirm click
  const handleUploadConfirm = async () => {
    if (dialog.current) {
      if (tempUploadedResumeFile) {
        // TODO: Error handling
        const uploadedResume = await uploadTemporaryFile();
        setTempUploadedResumeFile(null);
        addUploadedResume(uploadedResume);
        setSelectedResume(uploadedResume);
      }
      dialog.current.close();
    }
  }

  // Handle upload modal cancel click
  const handleUploadCancel = () => {
    if (dialog.current) {
      setTempUploadedResumeFile(null);
      dialog.current.close();
    }
  }

  /* ---------------------------------------------------------------- */
  // Conditional rendering of resume selection dropdown or 
  // resume upload component.

  let resumeSelectorContent = null;

  if (isFetchingResumes) {
    // Show resumes loading status while resumes are still being fetched
    resumeSelectorContent = (
      <>
        <label htmlFor="resume">Select a resume:</label>
        <select id="resume" name="resume" disabled>
          <option>Loading...</option>
        </select>
      </>
    );
  } else if (resumes.length === 0) {
    // If no user resumes were fetched, show the resume uploader
    resumeSelectorContent = <ResumeUploader />;
  } else {
    // If 1 or more user resumes were fetched, then construct a dropdown with resumes as options
    resumeSelectorContent = (
      <>
        <label htmlFor="resume">Select a resume:</label>
        <select id="resume" name="resume" value={selectedResume?.id ?? ""} onChange={handleResumeSelect}>
          {resumes.map((resume) => {
            return (
              <option key={resume.id} value={resume.id}>
                {resume.name}{resume.is_default && " (default)"}
              </option>
            )
          })}
          <option value="upload">Upload a new resume...</option>
        </select>
      </>
    );
  }

  /* ---------------------------------------------------------------- */
  // Construct resume uploader modal, which will initially be hidden

  const resumeUploaderModal = (
    <Modal
      dialogRef={dialog}
      confirmText={tempUploadedResumeFile ? (isUploadingResume ? "Uploading..." : "Upload") : ""}
      onConfirm={handleUploadConfirm}
      onCancel={handleUploadCancel}>
      <ResumeUploader />
    </Modal>
  );

  return (
    <>
      {resumeUploaderModal}
      <div className="form-field">
        {resumeSelectorContent}
      </div>
    </>
  );
}
