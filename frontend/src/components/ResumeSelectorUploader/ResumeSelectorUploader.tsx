import ResumeSelector from "../ResumeSelector/ResumeSelector";
import ResumeUploader from "../ResumeUploader/ResumeUploader";
import { useState } from "react";

export default function ResumeSelectorUploader() {
    const [resumeExists, setResumeExists] = useState(false);

    function handleCheckboxChange(e: React.ChangeEvent<HTMLInputElement>) {
        setResumeExists(!resumeExists);
    }

    return (
        <>
          {resumeExists && <ResumeSelector />}
          {!resumeExists && <ResumeUploader />}
          <label>
            <input type="checkbox" onChange={handleCheckboxChange}  />Check here to toggle resume uploader
          </label>
        </>
    )
  }
