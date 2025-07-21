import { useCallback } from "react";
import { useDropzone } from "react-dropzone";

import { useResumesContext } from "../../contexts/ResumesContext";

import fileUploadIcon from "../../assets/images/file-upload-icon.png";
import removeFileIcon from "../../assets/images/remove-icon.png";
import "./ResumeUploader.css";

export default function ResumeUploader() {
  const { tempUploadedResumeFile, setTempUploadedResumeFile } = useResumesContext();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    // Store uploaded resume file in state
    if (acceptedFiles[0]) {
      setTempUploadedResumeFile(acceptedFiles[0])
    }
  }, [setTempUploadedResumeFile]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      "application/pdf": [".pdf"],
      "application/msword": [".doc"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    },
    onDrop,
    onDropRejected: (rejectedFiles) => {
      console.log(rejectedFiles);
    }
  });

  const handleRemoveFileClick = () => {
    setTempUploadedResumeFile(null);
  }

  // Conditional rendering of resume uploader or temporarily uploaded file
  let resumeUploaderContent = null;

  if (tempUploadedResumeFile) {
    resumeUploaderContent = (
      <div className="temp-uploaded-file-container">
        <span className="temp-uploaded-file-name">{tempUploadedResumeFile.name}</span>
        <img className="action-icon" src={removeFileIcon} title="remove" onClick={handleRemoveFileClick} alt="file-remove" />
      </div>
    );
  } else {
    resumeUploaderContent = (
      <div {...getRootProps()}>
        <div className={`drag-drop-container ${isDragActive ? "drag-active" : ""}`}>
          <img className="icon" src={fileUploadIcon} alt="file-upload" />
          <span className="drag-drop-instructions"><strong>Choose a file</strong> or drag it here</span>
        </div>
        <input id="file" name="file" {...getInputProps()} />
      </div>
    )
  }

  return (
    <>
      <label htmlFor="file">Upload a resume:</label>
      {resumeUploaderContent}
    </>
  )
}
