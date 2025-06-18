import ResumeSelector from "../ResumeSelector/ResumeSelector";

export default function ResumeSelectorUploader() {
    const resumeExists = true;

    return (
        <>
          {resumeExists && <ResumeSelector />}
          {!resumeExists && <span>Upload Resume Placeholder</span>}
        </>
    )
  }