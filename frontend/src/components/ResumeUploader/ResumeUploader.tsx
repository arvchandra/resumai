import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";


enum ResumeType {
  Default = 0
}

interface FilePayload {
  file: File;
  user_id: 2;
  type: ResumeType.Default;
}

type FormDataKeys = keyof FilePayload


export default function ResumeUploader() {
  // const [file, setFile] = useState<File | undefined>();

  const handleUpload = async (file: File) => {
    if (file) {
      const formData = new FormData;
      formData.append('file', file);

      try {
        const result = await fetch('http://127.0.0.1:8000/tailor/users/2/resume/upload', {
          method: 'POST',
          body: formData
        });

        const data = await result.json();

        console.log(data);
      } catch (error) {
        console.error(error);
      }
    }
  }

  const onDrop = useCallback((acceptedFiles: File[]) => {
    // setFile(acceptedFiles[0]);

    handleUpload(acceptedFiles[0]);
    // const file = new FileReader;

    // file.readAsDataURL(acceptedFiles[0]);

    // file.onload = () => {
    //   const base64String = file.result as string;
    //   console.log(base64String);
    // }
  }, []);


  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    onDrop,
    onDropRejected: (rejectedFiles) => {
      console.log(rejectedFiles);
    }
  });

  

  function handleOnChange(e: React.FormEvent<HTMLInputElement>) {
    const target = e.target as HTMLInputElement & {
      files: FileList;
    }

    setFile(target.files[0]);
  }

  return (
    <div {...getRootProps()}>
      <input {...getInputProps()} />
      {
        isDragActive ?
          <p>Drop here ...</p> :
          <p>Drag 'n' drop your resume here</p>
      }

    </div>
    // <div className="form-field">
    //   <label htmlFor="resume">Upload Resume</label>
    //   <input
    //     id="resume" 
    //     type="file" 
    //     name="resume" 
    //     onChange={handleOnChange} 
    //     accept=".doc,.docx,.pdf"
    //   />
    // </div>
  )
}
